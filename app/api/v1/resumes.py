"""Router for resume-related interactions and parsing."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Resume
from app.schemas.resume import ResumeResponse
from app.services.llm_parser import parse_resume_tex

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Upload a LaTeX resume file, parse it synchronously via the LLM,
    and store exactly the JSONB schema representation.
    """
    if not file.filename or not file.filename.endswith(".tex"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Currently, only LaTeX (.tex) files are fully supported.",
        )

    content_bytes = await file.read()
    try:
        raw_text = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File could not be natively decoded as UTF-8 text.",
        )

    # Trigger LLM Agent
    parsed_data = await parse_resume_tex(raw_text)

    # Insert entirely
    resume_db = Resume(
        name=file.filename.replace(".tex", ""),
        content_raw=raw_text,
        parsed_skills=parsed_data.get("parsed_skills", []),
        parsed_experience=parsed_data.get("parsed_experience", []),
        is_original=True,
        target_job_id=None,
    )
    db.add(resume_db)
    await db.commit()
    await db.refresh(resume_db)

    return resume_db


@router.get("/", response_model=list[ResumeResponse])
async def list_resumes(db: AsyncSession = Depends(get_db)) -> Any:
    """Retrieve all parsed user resumes."""
    result = await db.execute(select(Resume).order_by(Resume.created_at.desc()))
    return result.scalars().all()


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(resume_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Permanently delete a resume."""
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume_db = result.scalar_one_or_none()

    if not resume_db:
        raise HTTPException(status_code=404, detail="Resume not explicitly found.")

    await db.delete(resume_db)
    await db.commit()
