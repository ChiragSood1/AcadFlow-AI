from io import BytesIO
import pandas as pd
from fastapi import HTTPException, UploadFile

from app.models.schemas import AttendanceUploadSummary, MarksUploadSummary, PDFUploadSummary
from app.utils.pdf_parser import extract_text_from_pdf


ATTENDANCE_REQUIRED_COLUMNS = {"student_id", "subject", "date", "status"}
MARKS_REQUIRED_COLUMNS = {"student_id", "subject", "assessment", "marks_obtained", "marks_total"}


def _read_csv_from_upload(file: UploadFile):
    # read the raw bytes and turn into a DataFrame
    try:
        contents = file.file.read()
        buffer = BytesIO(contents)
        df = pd.read_csv(buffer)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse CSV file '{file.filename}': {exc}",
        ) from exc
    finally:
        file.file.close()

    return df


def ingest_attendance_csv(file: UploadFile):
    # read csv first
    df = _read_csv_from_upload(file)

    missing = ATTENDANCE_REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Attendance CSV is missing required columns: {', '.join(sorted(missing))}",
        )

    total_rows = len(df)
    # Drop rows with missing critical identifiers
    critical_cols = ["student_id", "subject", "date"]
    valid_mask = ~df[critical_cols].isnull().any(axis=1)
    valid_df = df.loc[valid_mask].copy()
    invalid_rows = total_rows - len(valid_df)

    upload_summary = AttendanceUploadSummary(
        success=True,
        message="Attendance CSV ingested successfully.",
        total_rows=total_rows,
        valid_rows=len(valid_df),
        invalid_rows=invalid_rows,
        distinct_students=valid_df["student_id"].nunique(),
        distinct_subjects=valid_df["subject"].nunique(),
    )
    return valid_df, upload_summary


def ingest_marks_csv(file: UploadFile):
    # read csv first
    df = _read_csv_from_upload(file)

    missing = MARKS_REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Marks CSV is missing required columns: {', '.join(sorted(missing))}",
        )

    total_rows = len(df)
    critical_cols = ["student_id", "subject"]
    valid_mask = ~df[critical_cols].isnull().any(axis=1)
    df = df.loc[valid_mask].copy()

    # Coerce numeric values; drop rows where parsing fails
    df["marks_obtained"] = pd.to_numeric(df["marks_obtained"], errors="coerce")
    df["marks_total"] = pd.to_numeric(df["marks_total"], errors="coerce")
    numeric_mask = ~df[["marks_obtained", "marks_total"]].isnull().any(axis=1)

    # keep only rows that can produce valid percentages
    range_mask = (
        (df["marks_total"] > 0)
        & (df["marks_obtained"] >= 0)
        & (df["marks_obtained"] <= df["marks_total"])
    )
    valid_df = df.loc[numeric_mask & range_mask].copy()

    invalid_rows = total_rows - len(valid_df)

    upload_summary = MarksUploadSummary(
        success=True,
        message="Marks CSV ingested successfully.",
        total_rows=total_rows,
        valid_rows=len(valid_df),
        invalid_rows=invalid_rows,
        distinct_students=valid_df["student_id"].nunique(),
        distinct_subjects=valid_df["subject"].nunique(),
    )
    return valid_df, upload_summary


def ingest_pdf(file: UploadFile):
    # read the pdf bytes and extract text
    try:
        contents = file.file.read()
        pdf_bytes = BytesIO(contents)
        text, pages = extract_text_from_pdf(pdf_bytes)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse PDF file '{file.filename}': {exc}",
        ) from exc
    finally:
        file.file.close()

    upload_summary = PDFUploadSummary(
        success=True,
        message="PDF ingested successfully.",
        filename=file.filename,
        pages=pages,
        characters=len(text),
    )
    return text, upload_summary

