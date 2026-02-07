import pandas as pd


def normalize_student_ids(df: pd.DataFrame) -> pd.DataFrame:
    # make student ids simple and consistent
    if "student_id" not in df.columns:
        return df

    df = df.copy()
    df["student_id"] = df["student_id"].astype(str).str.strip().str.upper()
    return df


def normalize_subject_names(df: pd.DataFrame) -> pd.DataFrame:
    # make subject names simple and consistent
    if "subject" not in df.columns:
        return df

    df = df.copy()
    df["subject"] = df["subject"].astype(str).str.strip().str.upper()
    return df


def normalize_attendance(attendance: pd.DataFrame) -> pd.DataFrame:
    # run both normalizations for attendance
    df = normalize_student_ids(attendance)
    df = normalize_subject_names(df)
    return df


def normalize_marks(marks: pd.DataFrame) -> pd.DataFrame:
    # run both normalizations for marks
    df = normalize_student_ids(marks)
    df = normalize_subject_names(df)
    return df


def summarize_missing_values(df: pd.DataFrame):
    # count how many values are missing
    total_cells = df.size
    missing_cells = int(df.isnull().sum().sum())
    return missing_cells, total_cells - missing_cells

