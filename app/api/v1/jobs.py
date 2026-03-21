"""API routes for job CRUD and search."""

import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models import CohortEnum, Job, SeniorityEnum
from app.schemas.job import (
    JobCreate,
    JobListResponse,
    JobResponse,
    JobUpdate,
)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


def _job_to_response(job: Job) -> JobResponse:
    """Convert a Job ORM instance to a JobResponse schema."""
    return JobResponse(
        id=job.id,
        title=job.title,
        company_id=job.company_id,
        company_name=job.company.name if job.company else None,
        location=job.location,
        description_raw=job.description_raw,
        description_summary=job.description_summary,
        requirements=job.requirements,
        cohort=job.cohort,
        seniority_level=job.seniority_level,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        url=job.url,
        is_active=job.is_active,
        scraped_at=job.scraped_at,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.get("", response_model=JobListResponse)
async def list_jobs(
    query: str | None = Query(None, description="Search keyword in title or description"),
    cohort: CohortEnum | None = Query(None, description="Filter by cohort"),
    location: str | None = Query(None, description="Filter by location (partial match)"),
    seniority_level: SeniorityEnum | None = Query(None, description="Filter by seniority"),
    company_id: int | None = Query(None, description="Filter by company"),
    is_active: bool | None = Query(True, description="Filter by active status"),
    min_salary: float | None = Query(None, description="Minimum salary filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> JobListResponse:
    """List and search jobs with optional filters and pagination."""
    stmt = select(Job).options(selectinload(Job.company))

    # Apply filters
    if query:
        stmt = stmt.where(Job.title.ilike(f"%{query}%") | Job.description_raw.ilike(f"%{query}%"))
    if cohort:
        stmt = stmt.where(Job.cohort == cohort)
    if location:
        stmt = stmt.where(Job.location.ilike(f"%{location}%"))
    if seniority_level:
        stmt = stmt.where(Job.seniority_level == seniority_level)
    if company_id:
        stmt = stmt.where(Job.company_id == company_id)
    if is_active is not None:
        stmt = stmt.where(Job.is_active == is_active)
    if min_salary is not None:
        stmt = stmt.where(Job.salary_max >= min_salary)

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    # Paginate
    offset = (page - 1) * page_size
    stmt = stmt.order_by(Job.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    return JobListResponse(
        items=[_job_to_response(j) for j in jobs],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """Get a single job by ID."""
    stmt = select(Job).options(selectinload(Job.company)).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_to_response(job)


@router.post("", response_model=JobResponse, status_code=201)
async def create_job(
    job_in: JobCreate,
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """Create a new job posting."""
    job = Job(**job_in.model_dump())
    db.add(job)
    await db.flush()
    await db.refresh(job, attribute_names=["company"])
    return _job_to_response(job)


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    job_in: JobUpdate,
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """Update an existing job."""
    stmt = select(Job).options(selectinload(Job.company)).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = job_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    await db.flush()
    await db.refresh(job)
    return _job_to_response(job)


@router.delete("/{job_id}", status_code=204)
async def delete_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Permanently delete a job record from the database."""
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    await db.delete(job)
    await db.commit()
