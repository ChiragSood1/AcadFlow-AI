import pandas as pd

from app.core.config import settings
from app.models.schemas import RiskBand, StudentRiskRecord


def _normalize_status(status: str) -> str:
    # turn many values into PRESENT or ABSENT
    if status is None:
        return "ABSENT"
    s = str(status).strip().lower()
    if s in {"p", "present", "1", "true", "t"}:
        return "PRESENT"
    if s in {"a", "absent", "0", "false", "f"}:
        return "ABSENT"
    # Default conservatively to absent if unknown
    return "ABSENT"


def compute_attendance_percentages(attendance_df: pd.DataFrame) -> pd.DataFrame:
    # get attendance % per student and subject
    df = attendance_df.copy()
    df["__status_norm"] = df["status"].apply(_normalize_status)

    grouped = df.groupby(["student_id", "subject"], as_index=False).agg(
        total_sessions=("__status_norm", "count"),
        present_sessions=("__status_norm", lambda s: (s == "PRESENT").sum()),
    )

    grouped["attendance_percentage"] = (
        grouped["present_sessions"] / grouped["total_sessions"] * 100.0
    )
    return grouped[["student_id", "subject", "attendance_percentage"]]


def compute_marks_percentages(marks_df: pd.DataFrame) -> pd.DataFrame:
    # get marks % per student and subject
    df = marks_df.copy()
    grouped = (
        df.groupby(["student_id", "subject"], as_index=False)[
            ["marks_obtained", "marks_total"]
        ]
        .sum()
    )
    grouped["marks_percentage"] = (
        grouped["marks_obtained"] / grouped["marks_total"] * 100.0
    )
    return grouped[["student_id", "subject", "marks_percentage"]]


def _classify_risk_band(
    combined_score: float,
    low_min: float,
    medium_min: float,
) -> RiskBand:
    # decide which band the student is in
    if combined_score >= low_min:
        return RiskBand.LOW
    if combined_score >= medium_min:
        return RiskBand.MEDIUM
    return RiskBand.HIGH


def compute_student_risks(
    attendance_df: pd.DataFrame,
    marks_df: pd.DataFrame,
):
    # use attendance and marks to get one risk record per student+subject
    thresholds = settings.risk_thresholds

    attendance_pct = compute_attendance_percentages(attendance_df)
    marks_pct = compute_marks_percentages(marks_df)

    merged = pd.merge(
        attendance_pct,
        marks_pct,
        on=["student_id", "subject"],
        how="inner",
        validate="one_to_one",
    )

    aw = thresholds.attendance_weight
    mw = thresholds.marks_weight

    merged["combined_score"] = (
        merged["attendance_percentage"] * aw + merged["marks_percentage"] * mw
    )

    def get_band_value(score: float) -> str:
        band = _classify_risk_band(
            combined_score=score,
            low_min=thresholds.marks_low_risk_min,
            medium_min=thresholds.marks_medium_risk_min,
        )
        return band.value

    merged["risk_band"] = merged["combined_score"].apply(get_band_value)

    records = []
    for row in merged.to_dict(orient="records"):
        records.append(
            StudentRiskRecord(
                student_id=row["student_id"],
                subject_code=row["subject"],
                attendance_percentage=row["attendance_percentage"],
                marks_percentage=row["marks_percentage"],
                combined_score=row["combined_score"],
                risk_band=RiskBand(row["risk_band"]),
            )
        )

    return records
