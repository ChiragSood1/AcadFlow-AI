from fastapi import APIRouter, Depends, UploadFile

from app.api.deps import get_store
from app.models.schemas import AttendanceUploadSummary, MarksUploadSummary, PDFUploadSummary
from app.services.ingestion import ingest_attendance_csv, ingest_marks_csv, ingest_pdf
from app.services.normalization import normalize_attendance, normalize_marks

router = APIRouter()


@router.post(
    "/attendance",
    response_model=AttendanceUploadSummary,
    summary="Upload an attendance CSV file.",
)
async def upload_attendance(
    file: UploadFile,
    store=Depends(get_store),
):
    # read and check the attendance csv
    df, upload_summary = ingest_attendance_csv(file)
    # clean ids and subjects
    df = normalize_attendance(df)
    # save in memory
    store.attendance = df
    return upload_summary


@router.post(
    "/marks",
    response_model=MarksUploadSummary,
    summary="Upload a marks CSV file.",
)
async def upload_marks(
    file: UploadFile,
    store=Depends(get_store),
):
    # read and check the marks csv
    df, upload_summary = ingest_marks_csv(file)
    # clean ids and subjects
    df = normalize_marks(df)
    # save in memory
    store.marks = df
    return upload_summary


@router.post(
    "/pdf",
    response_model=PDFUploadSummary,
    summary="Upload an academic PDF document.",
)
async def upload_pdf(
    file: UploadFile,
    store=Depends(get_store),
):
    # read the pdf and pull out text
    text, upload_summary = ingest_pdf(file)
    # keep the text so we can use it later
    store.pdf_corpus[upload_summary.filename] = text
    return upload_summary

