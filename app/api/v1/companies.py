"""API routes for company CRUD."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.company import Company
from app.models.job import Job
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("", response_model=list[CompanyResponse])
async def list_companies(
    db: AsyncSession = Depends(get_db),
) -> list[CompanyResponse]:
    """List all monitored companies with their job counts."""
    stmt = (
        select(Company, func.count(Job.id).label("job_count"))
        .outerjoin(Job, (Job.company_id == Company.id) & (Job.is_active == True))  # noqa: E712
        .group_by(Company.id)
        .order_by(Company.name)
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        CompanyResponse(
            id=company.id,
            name=company.name,
            careers_url=str(company.careers_url),
            description=company.description,
            created_at=company.created_at,
            job_count=job_count,
        )
        for company, job_count in rows
    ]


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
) -> CompanyResponse:
    """Get a single company by ID with its active job count."""
    stmt = (
        select(Company, func.count(Job.id).label("job_count"))
        .outerjoin(Job, (Job.company_id == Company.id) & (Job.is_active == True))  # noqa: E712
        .where(Company.id == company_id)
        .group_by(Company.id)
    )
    result = await db.execute(stmt)
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Company not found")

    company, job_count = row
    return CompanyResponse(
        id=company.id,
        name=company.name,
        careers_url=str(company.careers_url),
        description=company.description,
        created_at=company.created_at,
        job_count=job_count,
    )


@router.post("", response_model=CompanyResponse, status_code=201)
async def create_company(
    company_in: CompanyCreate,
    db: AsyncSession = Depends(get_db),
) -> CompanyResponse:
    """Add a new company to monitor."""
    # Check for duplicate name
    existing = await db.execute(select(Company).where(Company.name == company_in.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Company with this name already exists")

    company = Company(
        name=company_in.name,
        careers_url=str(company_in.careers_url),
        description=company_in.description,
    )
    db.add(company)
    await db.flush()
    await db.refresh(company)

    return CompanyResponse(
        id=company.id,
        name=company.name,
        careers_url=str(company.careers_url),
        description=company.description,
        created_at=company.created_at,
        job_count=0,
    )


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_in: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
) -> CompanyResponse:
    """Update a company's details."""
    stmt = select(Company).where(Company.id == company_id)
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    update_data = company_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "careers_url" and value is not None:
            value = str(value)
        setattr(company, field, value)

    await db.flush()
    await db.refresh(company)

    # Get job count
    count_result = await db.execute(
        select(func.count(Job.id)).where(
            (Job.company_id == company_id) & (Job.is_active == True)  # noqa: E712
        )
    )
    job_count = count_result.scalar_one()

    return CompanyResponse(
        id=company.id,
        name=company.name,
        careers_url=str(company.careers_url),
        description=company.description,
        created_at=company.created_at,
        job_count=job_count,
    )
