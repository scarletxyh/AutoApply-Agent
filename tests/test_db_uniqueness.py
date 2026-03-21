from typing import Any

import pytest
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from app.models import Job


@pytest.mark.asyncio
async def test_job_url_uniqueness_on_conflict_do_nothing(test_session: Any) -> None:
    """
    Test that the native PostgreSQL `on_conflict_do_nothing` perfectly prevents
    duplicate URLs from being saved, while keeping the original record intact,
    without throwing any Python exceptions.
    """
    from app.models import Company

    # 0. Create a dummy company to satisfy the strict non-null foreign key constraint
    company = Company(name="Uniqueness Testing Corporation", careers_url="https://example.com/careers")
    test_session.add(company)
    await test_session.commit()

    unique_url = "https://example.com/strictly-unique-job-123"

    # 1. Prepare first valid Job
    job1_data = {
        "title": "Initial Software Engineer",
        "description_summary": "First job recorded",
        "url": unique_url,
        "company_id": company.id,
    }

    # Perform the first atomic insert
    stmt1 = insert(Job).values(**job1_data).on_conflict_do_nothing(index_elements=["url"])
    await test_session.execute(stmt1)
    await test_session.commit()

    # 2. Prevent a second insertion of the exact same URL
    job2_data = {
        "title": "Duplicate Imposter Job",
        "description_summary": "Trying to overwrite the first job",
        "url": unique_url,  # The identical URL
        "company_id": company.id,
    }

    stmt2 = insert(Job).values(**job2_data).on_conflict_do_nothing(index_elements=["url"])
    await test_session.execute(stmt2)
    await test_session.commit()

    # 3. Assertions and Verifications
    # Verify ONLY one job was actually created in the database
    result_count = await test_session.execute(select(func.count()).select_from(Job))
    count = result_count.scalar()
    assert count == 1, f"Expected exactly 1 job in database, got {count}"

    # Verify that the surviving job is strictly the FIRST one (it didn't get overwritten)
    result_job = await test_session.execute(select(Job).where(Job.url == unique_url))
    final_job = result_job.scalar_one()

    assert final_job.title == "Initial Software Engineer", (
        "The original job title was incorrectly modified!"
    )
    assert final_job.description_summary == "First job recorded", (
        "The original job summary was incorrectly modified!"
    )
