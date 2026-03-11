"""ScrapeRun ORM model for tracking scrape operations."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ScrapeStatusEnum(str, enum.Enum):
    """Status of a scrape run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScrapeRun(Base):
    """Tracks the execution of a scraping operation against a company's career portal."""

    __tablename__ = "scrape_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    company: Mapped["Company"] = relationship(back_populates="scrape_runs")  # noqa: F821

    def __repr__(self) -> str:
        return f"<ScrapeRun(id={self.id}, status='{self.status}')>"
