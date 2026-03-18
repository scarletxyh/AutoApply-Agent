from typing import Any, Optional

from pydantic import BaseModel, Field


class RefineRequest(BaseModel):
    prompt_override: Optional[str] = Field(
        None, description="Optional custom system instructions to override the default prompt."
    )
    model_override: Optional[str] = Field(
        None, description="Optional Gemini model ID to use for this refinement."
    )


class RefineResponse(BaseModel):
    job_id: int
    title: str
    location: Optional[str]
    description_summary: str
    requirements: Optional[Any]
    cohort: Optional[str]
    seniority_level: Optional[str]
    salary_min: Optional[float]
    salary_max: Optional[float]
    model_used: str
    prompt_used: str
