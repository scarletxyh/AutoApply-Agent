from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ResumeBase(BaseModel):
    name: str
    content_raw: str
    parsed_skills: list[str] | None = None
    parsed_experience: list[Any] | None = None
    is_original: bool = True
    target_job_id: int | None = None
    is_active: bool = True


class ResumeCreate(ResumeBase):
    pass


class ResumeUpdate(BaseModel):
    name: str | None = None
    content_raw: str | None = None
    parsed_skills: list[str] | None = None
    parsed_experience: list[Any] | None = None
    is_original: bool | None = None
    target_job_id: int | None = None
    is_active: bool | None = None


class ResumeResponse(ResumeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
