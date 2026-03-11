"""Pydantic schemas for Company API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, HttpUrl


class CompanyCreate(BaseModel):
    """Schema for creating a new company."""

    name: str
    careers_url: HttpUrl
    description: str | None = None


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""

    name: str | None = None
    careers_url: HttpUrl | None = None
    description: str | None = None


class CompanyResponse(BaseModel):
    """Schema for company API responses."""

    id: int
    name: str
    careers_url: str
    description: str | None = None
    created_at: datetime
    job_count: int = 0

    model_config = {"from_attributes": True}
