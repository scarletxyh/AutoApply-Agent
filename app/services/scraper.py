"""Playwright-based web scraper for career portals."""

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Job
from app.services.llm_parser import parse_job_description

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from playwright.async_api import Page


async def extract_metadata_from_dom(page: "Page") -> dict[str, str | None]:
    """
    Extract basic job metadata directly from the DOM using common selectors.
    This saves LLM tokens and increases accuracy for standard fields.
    """
    result = await page.evaluate(
        """() => {
        const getMeta = (name) => {
            const selector = `meta[property="${name}"], meta[name="${name}"]`;
            return document.querySelector(selector)?.content;
        };

        // Try to find job title
        let title = getMeta('og:title') || getMeta('twitter:title') || document.title;
        // Clean up common title suffixes
        title = title.split('|')[0].split('-')[0].trim();

        // Try to find location
        let location = null;
        const locSelectors = [
            '[class*="location"]', '[id*="location"]',
            '.job-location', '.location-icon',
            'meta[name="job_location"]'
        ];
        for (const sel of locSelectors) {
            const el = document.querySelector(sel);
            if (el && el.textContent.trim().length > 2) {
                location = el.textContent.trim();
                break;
            }
        }

        // Try to find company
        let company = getMeta('og:site_name') || getMeta('application-name');

        return { title, location, company };
    }"""
    )
    return cast(dict[str, str | None], result)


async def run_scrape(
    db: AsyncSession, company_id: int, careers_url: str, single_url: bool = False
) -> int:
    """
    Scrape job listings or a single job page.

    1. Navigate to the page
    2. If single_url, process it directly.
    3. If careers_url, find links and process each.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.error("Playwright is not installed.")
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
            if single_url:
                job_links = [{"url": careers_url, "text": "Single Job Page"}]
            else:
                logger.info(f"Navigating to {careers_url}")
                await page.goto(careers_url, wait_until="networkidle", timeout=30000)
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
                    }""",
                )

            logger.info(f"Processing {len(job_links)} URLs")
            
            for link in job_links:
                try:
                    job_url = link["url"]
                    logger.info(f"Scraping job: {job_url}")

                    # Use longer timeout and 'domcontentloaded' for robustness
                    await page.goto(job_url, wait_until="domcontentloaded", timeout=60000)

                    # ── Stage 1: DOM Metadata ──────────
                    dom_data = await extract_metadata_from_dom(page)

                    raw_text = await page.inner_text("body")
                    if len(raw_text) > 15000:
                        raw_text = raw_text[:15000]

                    # ── Stage 2: Focused LLM Parse ─────
                    job_data = await parse_job_description(
                        raw_text=raw_text,
                        company_id=company_id,
                        db=db,
                        url=job_url,
                        pre_extracted_data=dom_data,
                    )

                    job = Job(
                        **job_data.model_dump(),
                        scraped_at=datetime.now(timezone.utc),
                    )
                    db.add(job)
                    await db.flush()
                    jobs_found += 1
                    logger.info(f"Stored job: {job_data.title}")

                except Exception as e:
                    logger.warning(f"Failed to scrape {link.get('url')}: {e}")
                    continue

            await db.commit()

        finally:
            await browser.close()

    return jobs_found
