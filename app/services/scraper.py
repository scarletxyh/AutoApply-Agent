"""Playwright-based web scraper for career portals."""

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Job
from app.services.llm_parser import parse_job_description

logger = logging.getLogger(__name__)


async def run_scrape(db: AsyncSession, company_id: int, careers_url: str) -> int:
    """
    Scrape job listings from a company's career portal.

    This is a skeleton implementation that demonstrates the scraping pipeline:
    1. Navigate to the careers page using Playwright
    2. Extract job listing links
    3. For each job, extract raw text
    4. Parse with LLM function calling
    5. Store in database

    Args:
        db: Async database session.
        company_id: The company being scraped.
        careers_url: URL of the company's careers page.

    Returns:
        Number of jobs found and stored.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.error(
            "Playwright is not installed. "
            "Run: pip install playwright && playwright install"
        )
        raise

    jobs_found = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        try:
            logger.info(f"Navigating to {careers_url}")
            await page.goto(careers_url, wait_until="networkidle", timeout=30000)

            # ── Step 1: Find job listing links ────────────────────────────
            # This is a generic heuristic — real implementations would need
            # company-specific selectors or a more sophisticated approach.
            job_links = await page.eval_on_selector_all(
                "a[href]",
                """(elements) => {
                    const keywords = ['job', 'position', 'career', 'opening', 'role', 'apply'];
                    return elements
                        .filter(el => {
                            const href = el.href.toLowerCase();
                            const text = el.textContent.toLowerCase();
                            return keywords.some(kw => href.includes(kw) || text.includes(kw));
                        })
                        .map(el => ({ url: el.href, text: el.textContent.trim() }))
                        .filter(item => item.text.length > 3)
                        .slice(0, 50);
                }""",
            )

            logger.info(f"Found {len(job_links)} potential job links")

            # ── Step 2: Visit each job page and extract text ──────────────
            for link in job_links:
                try:
                    job_url = link["url"]
                    logger.info(f"Scraping job: {link['text'][:60]}...")

                    await page.goto(job_url, wait_until="networkidle", timeout=20000)
                    raw_text = await page.inner_text("body")

                    # Trim excessively long text (LLM context limits)
                    if len(raw_text) > 15000:
                        raw_text = raw_text[:15000]

                    # ── Step 3: Parse with LLM ────────────────────────────
                    job_data = await parse_job_description(
                        raw_text=raw_text,
                        company_id=company_id,
                        url=job_url,
                    )

                    # ── Step 4: Store in database ─────────────────────────
                    job = Job(
                        **job_data.model_dump(),
                        scraped_at=datetime.now(timezone.utc),
                    )
                    db.add(job)
                    await db.flush()
                    jobs_found += 1

                    logger.info(f"Stored job: {job_data.title} [{job_data.cohort}]")

                except Exception as e:
                    logger.warning(f"Failed to scrape job link {link.get('url', '?')}: {e}")
                    continue

            await db.commit()

        finally:
            await browser.close()

    logger.info(f"Scrape completed: {jobs_found} jobs found")
    return jobs_found
