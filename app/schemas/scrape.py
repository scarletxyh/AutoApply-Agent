"""Pydantic schemas for Scrape API requests and responses."""

from datetime import datetime

from pydantic import BaseModel

from app.models.scrape_run import ScrapeStatusEnum


class ScrapeRequest(BaseModel):
    """Schema for triggering a scrape run."""

    company_id: int


class ScrapeRunResponse(BaseModel):
    """Schema for scrape run status responses."""

    id: int
    company_id: int
    status: ScrapeStatusEnum
    jobs_found: int
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
