"""Job ORM model with cohort classification."""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CohortEnum(str, enum.Enum):
    """Job role cohort categories."""

    BACKEND = "Backend"
    FRONTEND = "Frontend"
    FULLSTACK = "Fullstack"
    DATA = "Data"
    ML_AI = "ML/AI"
    DEVOPS = "DevOps"
    TESTING = "Testing"
    EMBEDDED_HARDWARE = "Embedded/Hardware"
    MOBILE = "Mobile"
    SECURITY = "Security"
    OTHER = "Other"


class SeniorityEnum(str, enum.Enum):
    """Job seniority levels."""

    INTERN = "Intern"
    JUNIOR = "Junior"
    MID = "Mid"
    SENIOR = "Senior"
    STAFF = "Staff"
    PRINCIPAL = "Principal"
    MANAGER = "Manager"
    DIRECTOR = "Director"
    VP = "VP"
    OTHER = "Other"


class Job(Base):
    """A parsed and categorized job posting."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    location: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    description_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    requirements: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    cohort: Mapped[CohortEnum] = mapped_column(
        Enum(CohortEnum, name="cohort_enum"), nullable=False, index=True, default=CohortEnum.OTHER
    )
    seniority_level: Mapped[SeniorityEnum | None] = mapped_column(
        Enum(SeniorityEnum, name="seniority_enum"), nullable=True
    )
    salary_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    company: Mapped["Company"] = relationship(back_populates="jobs")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, title='{self.title}', cohort='{self.cohort}')>"
