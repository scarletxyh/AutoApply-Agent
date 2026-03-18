import logging
from typing import Any

from google import genai
from google.genai import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Job
from app.schemas.refine import RefineResponse
from app.services.llm_parser import SYSTEM_PROMPT, tool

logger = logging.getLogger(__name__)


async def refine_job_parsing(
    db: AsyncSession,
    job_id: int,
    prompt_override: str | None = None,
    model_override: str | None = None,
) -> RefineResponse:
    """
    Re-processes a job's raw description using a refined prompt or model.
    """
    # 1. Fetch the job from DB
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise ValueError(f"Job with ID {job_id} not found")

    # 2. Setup Gemini client
    client = genai.Client(api_key=settings.gemini_api_key)
    model_id = model_override or settings.gemini_model
    prompt = prompt_override or SYSTEM_PROMPT

    logger.info(f"Refining job {job_id} using model {model_id}")

    # 3. Call Gemini
    response = client.models.generate_content(
        model=model_id,
        contents=f"Re-parse this job posting carefully:\n\n{job.description_raw}",
        config=types.GenerateContentConfig(
            system_instruction=prompt,
            tools=[tool],
            temperature=0.1,
        ),
    )

    # 4. Extract function call
    function_call = None
    if response.candidates:
        for candidate in response.candidates:
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if part.function_call:
                        function_call = part.function_call
                        break
            if function_call:
                break

    if not function_call:
        raise RuntimeError("Gemini failed to return a structured function call for refinement")

    args: dict[str, Any] = dict(function_call.args) if function_call.args else {}

    # 5. Return the refined data (don't save to DB yet, let user review)
    return RefineResponse(
        job_id=job.id,
        title=args.get("title") or job.title,
        location=args.get("location") or job.location,
        description_summary=args.get("description_summary", "No summary generated"),
        requirements=args.get("requirements"),
        cohort=args.get("cohort"),
        seniority_level=args.get("seniority_level"),
        salary_min=args.get("salary_min"),
        salary_max=args.get("salary_max"),
        model_used=model_id,
        prompt_used=prompt,
    )
