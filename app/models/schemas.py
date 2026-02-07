from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class RiskBand(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UploadStatus(BaseModel):
    """Generic status response for upload endpoints."""

    success: bool = Field(..., description="Whether the upload was successfully processed.")
    message: str = Field(..., description="Human-readable status message.")


class AttendanceUploadSummary(UploadStatus):
    total_rows: int = Field(..., description="Total number of rows in the uploaded CSV.")
    valid_rows: int = Field(..., description="Number of rows that passed validation.")
    invalid_rows: int = Field(..., description="Number of rows that failed validation.")
    distinct_students: int = Field(..., description="Number of distinct students detected.")
    distinct_subjects: int = Field(..., description="Number of distinct subjects detected.")


class MarksUploadSummary(UploadStatus):
    total_rows: int = Field(..., description="Total number of rows in the uploaded CSV.")
    valid_rows: int = Field(..., description="Number of rows that passed validation.")
    invalid_rows: int = Field(..., description="Number of rows that failed validation.")
    distinct_students: int = Field(..., description="Number of distinct students detected.")
    distinct_subjects: int = Field(..., description="Number of distinct subjects detected.")


class PDFUploadSummary(UploadStatus):
    filename: str = Field(..., description="Original name of the uploaded file.")
    pages: int = Field(..., description="Number of pages detected in the PDF.")
    characters: int = Field(..., description="Number of extracted text characters.")


class StudentRiskRecord(BaseModel):
    """Risk classification for a single student in a subject."""

    student_id: str = Field(..., description="Normalized student identifier.")
    subject_code: str = Field(..., description="Normalized subject identifier.")
    attendance_percentage: float = Field(..., ge=0, le=100, description="Attendance percentage for this subject.")
    marks_percentage: float = Field(..., ge=0, le=100, description="Marks percentage for this subject.")
    combined_score: float = Field(..., ge=0, le=100, description="Combined score derived from attendance + marks.")
    risk_band: RiskBand = Field(..., description="Overall academic risk band for this student/subject.")


class InterventionAnalysisRequest(BaseModel):
    """
    Request body for /analyze/intervention.

    This model intentionally focuses on filtering and configuration, not raw data,
    because the raw data should already be present in the backend store.
    """

    subjects: Optional[List[str]] = Field(
        default=None,
        description="Optional list of subject codes to restrict analysis to. If omitted, all subjects are considered.",
    )
    include_bands: Optional[List[RiskBand]] = Field(
        default=None,
        description="Optional subset of risk bands to include. If omitted, all bands are included.",
    )
    max_students_per_band: int = Field(
        default=50,
        ge=1,
        description="Maximum number of students to return per risk band.",
    )


class StudentInterventionRecommendation(BaseModel):
    """AI-generated recommendation for a single student/subject pair."""

    student_id: str
    subject_code: str
    risk_band: RiskBand
    recommendation: str = Field(..., description="Actionable recommendation for intervention.")
    rationale: str = Field(..., description="Short explanation justifying the recommendation.")


class InterventionAnalysisResponse(BaseModel):
    """
    Response payload for /analyze/intervention.

    Combines deterministic risk calculations with AI-generated recommendations.
    """

    risk_summary: List[StudentRiskRecord] = Field(
        ..., description="Computed risk classification per student/subject."
    )
    recommendations: List[StudentInterventionRecommendation] = Field(
        ..., description="AI-generated recommendations for interventions."
    )


class AttendanceTrendPoint(BaseModel):
    """Aggregated attendance stats for a single time bucket."""

    period_start: str = Field(..., description="Start of the time bucket in ISO format.")
    period_end: str = Field(..., description="End of the time bucket in ISO format.")
    subject_code: Optional[str] = Field(
        default=None, description="Subject code if trends are per-subject; otherwise None."
    )
    average_attendance_percentage: float = Field(
        ..., ge=0, le=100, description="Average attendance percentage across the bucket."
    )


class TrendsAnalysisRequest(BaseModel):
    """
    Request body for /analyze/trends.

    Time ranges are expressed as ISO8601 strings and interpreted server-side.
    """

    start_date: Optional[str] = Field(
        default=None,
        description="Optional start date (inclusive) in ISO8601 format. If omitted, uses earliest available date.",
    )
    end_date: Optional[str] = Field(
        default=None,
        description="Optional end date (inclusive) in ISO8601 format. If omitted, uses latest available date.",
    )
    group_by_subject: bool = Field(
        default=True,
        description="Whether to compute trends per subject; if false, aggregates across all subjects.",
    )
    bucket: str = Field(
        default="W",
        description="Pandas-style resampling rule for bucketing dates (e.g., 'D', 'W', 'M').",
    )


class TrendsAnalysisResponse(BaseModel):
    trend_points: List[AttendanceTrendPoint] = Field(
        ..., description="Time-ordered attendance trend points."
    )
    ai_summary: str = Field(
        ..., description="AI-generated natural language summary of the trends."
    )


class QueryIntent(str, Enum):
    INTERVENTION_ANALYSIS = "intervention_analysis"
    ATTENDANCE_SUMMARY = "attendance_summary"
    PERFORMANCE_TRENDS = "performance_trends"
    UNKNOWN = "unknown"


class QueryRequest(BaseModel):
    """Natural language query payload for /query."""

    query: str = Field(..., min_length=1, description="Natural language query from admin/faculty.")


class QueryRoutingDecision(BaseModel):
    """Internal routing decision describing how a query will be handled."""

    intent: QueryIntent
    confidence: float = Field(
        ..., ge=0, le=1, description="Heuristic confidence score for the classified intent."
    )
    suggested_endpoint: Optional[str] = Field(
        default=None,
        description="Suggested API endpoint to call for this intent (for reference).",
    )
    parameters: Dict[str, object] = Field(
        default_factory=dict,
        description="Structured parameters inferred from the query, if any.",
    )


class QueryResponse(BaseModel):
    """
    Response payload for /query.

    This endpoint is NOT a chatbot; it describes how the system has chosen to
    handle the query and may optionally embed analysis results.
    """

    routing: QueryRoutingDecision
    # Optional field to hold results for simple orchestrations (e.g., auto-running an analysis).
    analysis_result: Optional[Dict[str, object]] = Field(
        default=None,
        description="Optional structured result from the invoked analysis, if any.",
    )

