"""Database models for AutoApply-Agent."""

import enum
from datetime import datetime
from typing import Any

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

# ── Enums ─────────────────────────────────────────────────────────────────────


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


class ScrapeStatusEnum(str, enum.Enum):
    """Status of a scrape run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ── Models ────────────────────────────────────────────────────────────────────


class Company(Base):
    """A company whose career portal is being monitored."""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    careers_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    jobs: Mapped[list["Job"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    scrape_runs: Mapped[list["ScrapeRun"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.name}')>"


class Job(Base):
    """A parsed and categorized job posting."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    location: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    description_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    requirements: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    cohort: Mapped[CohortEnum] = mapped_column(
        Enum(CohortEnum, name="cohort_enum"),
        nullable=False,
        index=True,
        default=CohortEnum.OTHER,
    )
    seniority_level: Mapped[SeniorityEnum | None] = mapped_column(
        Enum(SeniorityEnum, name="seniority_enum"), nullable=True
    )
    salary_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    company: Mapped[Company] = relationship(back_populates="jobs")
    targeted_resumes: Mapped[list["Resume"]] = relationship(
        back_populates="target_job", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, title='{self.title}', cohort='{self.cohort}')>"


class ScrapeRun(Base):
    """Tracks a scraping operation against a company's career portal."""

    __tablename__ = "scrape_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[ScrapeStatusEnum] = mapped_column(
        Enum(ScrapeStatusEnum, name="scrape_status_enum"),
        nullable=False,
        default=ScrapeStatusEnum.PENDING,
    )
    jobs_found: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company: Mapped[Company] = relationship(back_populates="scrape_runs")

    def __repr__(self) -> str:
        return f"<ScrapeRun(id={self.id}, status='{self.status}')>"


class SystemConfig(Base):
    """Global configuration settings, including the active LLM prompt."""

    __tablename__ = "system_config"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<SystemConfig(key='{self.key}')>"


class Resume(Base):
    """A user's resume, either original or polished for a specific job."""

    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_raw: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_skills: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    parsed_experience: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True)

    is_original: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    target_job_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    target_job: Mapped["Job | None"] = relationship(back_populates="targeted_resumes")

    def __repr__(self) -> str:
        return f"<Resume(id={self.id}, name='{self.name}', original={self.is_original})>"
