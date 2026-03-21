import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Job
from app.schemas.refine import RefineRequest, RefineResponse
from app.services.refinery import refine_job_parsing

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["Refinery"])


@router.post("/{job_id}/refine", response_model=RefineResponse)
async def refine_job(
    job_id: int, request: RefineRequest, db: AsyncSession = Depends(get_db)
) -> RefineResponse:
    """
    Test a refined prompt or different model on an existing job's raw data.
    This does NOT update the job in the database yet.
    """
    try:
        result = await refine_job_parsing(
            db=db,
            job_id=job_id,
            prompt_override=request.prompt_override,
            model_override=request.model_override,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Refinement failed for job {job_id}")
        raise HTTPException(status_code=500, detail=str(e))


from typing import Any
from app.models.models import CohortEnum, SeniorityEnum

@router.post("/{job_id}/apply-refinement", status_code=200)
async def apply_refinement(job_id: int, request: RefineRequest, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """
    Refine the job data AND save it back to the database.
    """
    try:
        refined_data = await refine_job_parsing(
            db=db,
            job_id=job_id,
            prompt_override=request.prompt_override,
            model_override=request.model_override,
        )

        # Fetch job and update
        stmt = select(Job).where(Job.id == job_id)
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        job.title = refined_data.title
        job.location = refined_data.location
        job.description_summary = refined_data.description_summary
        job.requirements = refined_data.requirements
        job.cohort = CohortEnum(refined_data.cohort) if refined_data.cohort else CohortEnum.OTHER
        job.seniority_level = SeniorityEnum(refined_data.seniority_level) if refined_data.seniority_level else None
        job.salary_min = refined_data.salary_min
        job.salary_max = refined_data.salary_max

        await db.commit()
        return {"status": "success", "message": f"Job {job_id} updated with refined data"}

    except Exception as e:
        logger.exception(f"Applying refinement failed for job {job_id}")
        raise HTTPException(status_code=500, detail=str(e))
