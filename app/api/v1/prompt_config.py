import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import SystemConfig
from app.schemas.prompt_config import PromptConfigRequest, PromptConfigResponse
from app.services.llm_parser import SYSTEM_PROMPT as DEFAULT_PROMPT

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/config", tags=["System Configuration"])

PROMPT_CONFIG_KEY = "global_system_prompt"


@router.get("/prompt", response_model=PromptConfigResponse)
async def get_global_prompt(db: AsyncSession = Depends(get_db)) -> PromptConfigResponse:
    """Retrieve the current active global prompt used for LLM extraction."""
    stmt = select(SystemConfig).where(SystemConfig.key == PROMPT_CONFIG_KEY)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()

    if config:
        return PromptConfigResponse(prompt=config.value, updated_at=config.updated_at)

    # Return default if not set in DB yet
    return PromptConfigResponse(prompt=DEFAULT_PROMPT, updated_at=datetime.utcnow())


@router.put("/prompt", response_model=PromptConfigResponse)
async def update_global_prompt(
    request: PromptConfigRequest, db: AsyncSession = Depends(get_db)
) -> PromptConfigResponse:
    """
    Update the global system prompt.
    This acts as 'pre-training' by setting few-shot examples and behavioral rules
    for all future job scrapes.
    """
    stmt = select(SystemConfig).where(SystemConfig.key == PROMPT_CONFIG_KEY)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()

    if config:
        config.value = request.prompt
    else:
        config = SystemConfig(
            key=PROMPT_CONFIG_KEY,
            value=request.prompt,
            description="Global system prompt for job parsing using few-shot configuration.",
        )
        db.add(config)

    await db.commit()
    await db.refresh(config)

    logger.info("Global system prompt updated.")

    return PromptConfigResponse(prompt=config.value, updated_at=config.updated_at)
