"""API routes for triggering and monitoring scrape runs."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory, get_db
from app.models import Company, ScrapeRun, ScrapeStatusEnum
from app.schemas.scrape import ScrapeRequest, ScrapeRunResponse, ScrapeURLRequest
from app.services.scraper import run_scrape

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scrape", tags=["Scraping"])


async def _execute_scrape(
    scrape_run_id: int, company_id: int, careers_url: str, single_url: bool = False
) -> None:
    """Background task that runs the actual scraping operation."""
    async with async_session_factory() as db:
        # Get scrape run first to avoid UnboundLocalError in except block
        stmt = select(ScrapeRun).where(ScrapeRun.id == scrape_run_id)
        result = await db.execute(stmt)
        scrape_run = result.scalar_one_or_none()
        
        if not scrape_run:
            logger.error(f"Scrape run {scrape_run_id} not found in background task")
            return

        try:
            # Mark as running
            scrape_run.status = ScrapeStatusEnum.RUNNING
            scrape_run.started_at = datetime.now(timezone.utc)
            await db.commit()

            # Run the scraper
            jobs_found = await run_scrape(db, company_id, careers_url, single_url=single_url)

            # Mark as completed
            scrape_run.status = ScrapeStatusEnum.COMPLETED
            scrape_run.jobs_found = jobs_found
            scrape_run.finished_at = datetime.now(timezone.utc)
            await db.commit()

        except Exception as e:
            logger.exception(f"Scrape run {scrape_run_id} failed")
            scrape_run.status = ScrapeStatusEnum.FAILED
            scrape_run.error_message = str(e)
            scrape_run.finished_at = datetime.now(timezone.utc)
            await db.commit()


@router.post("", response_model=ScrapeRunResponse, status_code=202)
async def trigger_scrape(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> ScrapeRunResponse:
    """Trigger a new scrape run for a company. Runs asynchronously in the background."""
    # Verify company exists
    company_result = await db.execute(
        select(Company).where(Company.id == request.company_id)
    )
    company = company_result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Check for already-running scrapes
    running_result = await db.execute(
        select(ScrapeRun).where(
            (ScrapeRun.company_id == request.company_id)
            & (ScrapeRun.status.in_([ScrapeStatusEnum.PENDING, ScrapeStatusEnum.RUNNING]))
        )
    )
    if running_result.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail="A scrape is already in progress for this company"
        )

    # Create scrape run record
    scrape_run = ScrapeRun(company_id=request.company_id, status=ScrapeStatusEnum.PENDING)
    db.add(scrape_run)
    await db.commit() # Commit now so background task can see it
    await db.refresh(scrape_run)

    # Schedule background scrape
    background_tasks.add_task(
        _execute_scrape, scrape_run.id, company.id, company.careers_url
    )

    return ScrapeRunResponse.model_validate(scrape_run)


@router.post("/url", response_model=ScrapeRunResponse, status_code=202)
async def trigger_scrape_url(
    request: ScrapeURLRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> ScrapeRunResponse:
    """Trigger a scrape for a specific job URL."""
    # If company_id is provided, verify it
    if request.company_id:
        company_result = await db.execute(
            select(Company).where(Company.id == request.company_id)
        )
        if not company_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Company not found")
    
    # Create scrape run record
    scrape_run = ScrapeRun(
        company_id=request.company_id or 1, # Default to first company if none provided
        status=ScrapeStatusEnum.PENDING
    )
    db.add(scrape_run)
    await db.commit() # Commit now so background task can see it
    await db.refresh(scrape_run)

    # Schedule background scrape
    background_tasks.add_task(
        _execute_scrape, scrape_run.id, scrape_run.company_id, request.url, single_url=True
    )

    return ScrapeRunResponse.model_validate(scrape_run)


@router.get("/{run_id}", response_model=ScrapeRunResponse)
async def get_scrape_run(
    run_id: int,
    db: AsyncSession = Depends(get_db),
) -> ScrapeRunResponse:
    """Get the status of a scrape run."""
    stmt = select(ScrapeRun).where(ScrapeRun.id == run_id)
    result = await db.execute(stmt)
    scrape_run = result.scalar_one_or_none()
    if not scrape_run:
        raise HTTPException(status_code=404, detail="Scrape run not found")
    return ScrapeRunResponse.model_validate(scrape_run)


@router.get("", response_model=list[ScrapeRunResponse])
async def list_scrape_runs(
    company_id: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[ScrapeRunResponse]:
    """List scrape runs, optionally filtered by company."""
    stmt = select(ScrapeRun).order_by(ScrapeRun.created_at.desc()).limit(50)
    if company_id:
        stmt = stmt.where(ScrapeRun.company_id == company_id)
    result = await db.execute(stmt)
    runs = result.scalars().all()
    return [ScrapeRunResponse.model_validate(r) for r in runs]
