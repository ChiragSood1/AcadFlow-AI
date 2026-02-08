from datetime import datetime

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_store
from app.models.schemas import (
    AttendanceTrendPoint,
    InterventionAnalysisRequest,
    InterventionAnalysisResponse,
    RiskBand,
    TrendsAnalysisRequest,
    TrendsAnalysisResponse,
)
from app.services.ai_reasoning import ai_reasoning_service as ai_helper
from app.services.risk_engine import compute_student_risks

router = APIRouter()


@router.post(
    "/intervention",
    response_model=InterventionAnalysisResponse,
    summary="Compute academic risk and generate intervention recommendations.",
)
async def analyze_intervention(
    request: InterventionAnalysisRequest,
    store=Depends(get_store),
):
    # check that we have both attendance and marks data
    if not store.has_minimum_data():
        raise HTTPException(
            status_code=400,
            detail="Both attendance and marks data must be uploaded before analysis.",
        )

    # get all risk records for students
    student_risks = compute_student_risks(store.attendance, store.marks)

    # filter by subjects if provided
    if request.subjects:
        allowed_subjects = []
        for s in request.subjects:
            allowed_subjects.append(s.upper())

        filtered_risks = []
        for r in student_risks:
            if r.subject_code.upper() in allowed_subjects:
                filtered_risks.append(r)
        student_risks = filtered_risks

    if request.include_bands:
        allowed_bands = list(request.include_bands)
        filtered_risks = []
        for r in student_risks:
            if r.risk_band in allowed_bands:
                filtered_risks.append(r)
        student_risks = filtered_risks

    # limit number of students per band
    risks_by_band = {}
    for band in RiskBand:
        risks_by_band[band] = []

    for record in student_risks:
        current_list = risks_by_band[record.risk_band]
        if len(current_list) < request.max_students_per_band:
            current_list.append(record)

    limited_student_risks = []
    for band in RiskBand:
        for r in risks_by_band[band]:
            limited_student_risks.append(r)

    recommendations = await ai_helper.recommend_interventions(limited_student_risks)

    return InterventionAnalysisResponse(
        risk_summary=limited_student_risks,
        recommendations=recommendations,
    )


@router.post(
    "/trends",
    response_model=TrendsAnalysisResponse,
    summary="Analyze attendance trends over time.",
)
async def analyze_trends(
    request: TrendsAnalysisRequest,
    store=Depends(get_store),
):
    # need attendance first
    if store.attendance is None:
        raise HTTPException(
            status_code=400,
            detail="Attendance data must be uploaded before running trends analysis.",
        )

    df = store.attendance.copy()

    # Parse dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    # Filter by date range if provided
    if request.start_date:
        try:
            start = datetime.fromisoformat(request.start_date)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid start_date format: '{request.start_date}'. Use ISO format (YYYY-MM-DD).",
            )
        df = df[df["date"] >= start]
    if request.end_date:
        try:
            end = datetime.fromisoformat(request.end_date)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid end_date format: '{request.end_date}'. Use ISO format (YYYY-MM-DD).",
            )
        df = df[df["date"] <= end]

    if df.empty:
        trend_points = []
        ai_summary = await ai_helper.summarize_trends(trend_points)
        return TrendsAnalysisResponse(trend_points=trend_points, ai_summary=ai_summary)

    df["status_numeric"] = df["status"].astype(str).str.lower().map(
        {
            "p": 1,
            "present": 1,
            "1": 1,
            "t": 1,
            "true": 1,
            "a": 0,
            "absent": 0,
            "0": 0,
            "f": 0,
            "false": 0,
        }
    )
    df["status_numeric"] = df["status_numeric"].fillna(0)

    trend_points = []

    if request.group_by_subject:
        df = df.set_index("date")
        grouped = df.groupby("subject")
        for subject, subject_df in grouped:
            try:
                resampled = subject_df["status_numeric"].resample(request.bucket)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid bucket value: '{request.bucket}'. Use a valid pandas resample rule like D, W, or M.",
                )
            stats = resampled.agg(["mean"])
            for idx, row in stats.iterrows():
                period_start = idx
                period_end = idx
                trend_points.append(
                    AttendanceTrendPoint(
                        period_start=period_start.isoformat(),
                        period_end=period_end.isoformat(),
                        subject_code=str(subject),
                        average_attendance_percentage=float(row["mean"] * 100.0),
                    )
                )
    else:
        df = df.set_index("date")
        try:
            resampled = df["status_numeric"].resample(request.bucket).mean()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid bucket value: '{request.bucket}'. Use a valid pandas resample rule like D, W, or M.",
            )
        for idx, value in resampled.items():
            trend_points.append(
                AttendanceTrendPoint(
                    period_start=idx.isoformat(),
                    period_end=idx.isoformat(),
                    subject_code=None,
                    average_attendance_percentage=float(value * 100.0),
                )
            )

    ai_summary = await ai_helper.summarize_trends(trend_points)

    return TrendsAnalysisResponse(trend_points=trend_points, ai_summary=ai_summary)
