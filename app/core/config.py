from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class RiskThresholds(BaseSettings):
    # simple values that control how we rate risk
    attendance_low_risk_min: float = Field(85.0)
    attendance_medium_risk_min: float = Field(70.0)

    marks_low_risk_min: float = Field(75.0)
    marks_medium_risk_min: float = Field(50.0)

    attendance_weight: float = Field(0.4, ge=0.0, le=1.0)
    marks_weight: float = Field(0.6, ge=0.0, le=1.0)

    model_config = {"extra": "ignore"}


class AIConfig(BaseSettings):
    # basic AI settings, only for text explanations
    provider: str = Field(default="openai")
    api_key: Optional[str] = Field(default=None)
    model_name: str = Field(default="gpt-4.1-mini")
    max_tokens: int = Field(default=512)
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)

    model_config = {"extra": "ignore"}


class Settings(BaseSettings):
    # top level settings for the app
    app_name: str = "AI Academic Workflow Engine"
    environment: str = Field(default="local")

    risk_thresholds: RiskThresholds = RiskThresholds()
    ai: AIConfig = AIConfig()

    allowed_file_extensions: List[str] = Field(default=[".csv", ".pdf"])

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"


# create one settings object we can import everywhere
settings = Settings()

