"""FastAPI application entry point."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import companies, jobs, scrape, refine, prompt_config
from app.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import Company, Job, ScrapeRun  # noqa: F401

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: create tables on startup, dispose engine on shutdown."""
    logger.info("Starting AutoApply-Agent API server...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ensured.")
    yield
    await engine.dispose()
    logger.info("Database engine disposed. Goodbye!")


app = FastAPI(
    title="AutoApply-Agent API",
    description=(
        "GenAI-powered job discovery tool — scrapes career portals, "
        "parses job descriptions via LLM function calling, and serves "
        "a searchable, categorized job database."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(companies.router, prefix="/api/v1")
app.include_router(scrape.router, prefix="/api/v1")
app.include_router(refine.router, prefix="/api/v1")
app.include_router(prompt_config.router, prefix="/api/v1")


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}
