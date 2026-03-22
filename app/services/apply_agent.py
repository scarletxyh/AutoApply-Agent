"""Core service for orchestrating Playwright and LLM autonomous job reasoning."""

import asyncio

from app.db.session import async_session_factory
from app.models.models import ApplicationRun, ApplicationStatusEnum


async def execute_autonomous_apply(application_run_id: int) -> None:
    """
    Main loop for background execution.
    Fetches the ApplicationRun state and triggers the Agentic loop.
    Currently heavily mocked placeholders until Phase 2 Playwright wiring.
    """
    async with async_session_factory() as session:
        # 1. Boot up sequence
        run = await session.get(ApplicationRun, application_run_id)
        if not run:
            return

        # 2. Transition to RUNNING
        run.status = ApplicationStatusEnum.RUNNING
        await session.commit()

        try:
            # TODO: Phase 2 -> Playwright Execution goes here.
            # Simulating an autonomous loop working via async sleeping
            await asyncio.sleep(8)

            # 3. Handle Completion Successfully
            run.status = ApplicationStatusEnum.SUCCESS
            await session.commit()

        except Exception as e:
            # 4. Bubble catastrophic freezes into the GUI
            run.status = ApplicationStatusEnum.FAILED
            run.error_logs = str(e)
            await session.commit()
