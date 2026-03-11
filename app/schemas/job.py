"""Pydantic schemas for Job API requests and responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.models import CohortEnum, SeniorityEnum


class JobCreate(BaseModel):
    """Schema for creating a new job (from scraper or manual entry)."""

    title: str
    company_id: int
    location: str | None = None
    description_raw: str | None = None
    description_summary: str | None = None
    requirements: dict[str, Any] | None = None
    cohort: CohortEnum = CohortEnum.OTHER
    seniority_level: SeniorityEnum | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    url: str | None = None


class JobUpdate(BaseModel):
    """Schema for updating a job."""

    title: str | None = None
    location: str | None = None
    description_summary: str | None = None
    requirements: dict[str, Any] | None = None
    cohort: CohortEnum | None = None
    seniority_level: SeniorityEnum | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    url: str | None = None
    is_active: bool | None = None


class JobResponse(BaseModel):
    """Schema for job API responses."""

    id: int
    title: str
    company_id: int
    company_name: str | None = None
    location: str | None = None
    description_raw: str | None = None
    description_summary: str | None = None
    requirements: dict[str, Any] | None = None
    cohort: CohortEnum
    seniority_level: SeniorityEnum | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    url: str | None = None
    is_active: bool
    scraped_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobSearchParams(BaseModel):
    """Query parameters for searching/filtering jobs."""

    query: str | None = None
    cohort: CohortEnum | None = None
    location: str | None = None
    seniority_level: SeniorityEnum | None = None
    company_id: int | None = None
    is_active: bool | None = True
    min_salary: float | None = None
    page: int = 1
    page_size: int = 20


class JobListResponse(BaseModel):
    """Paginated list of jobs."""

    items: list[JobResponse]
    total: int
    page: int
    page_size: int
    pages: int
