"""API endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """Health endpoint should return ok."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_create_company(client: AsyncClient) -> None:
    """Should create a company and return it."""
    payload = {
        "name": "Acme Corp",
        "careers_url": "https://acme.com/careers",
        "description": "A test company",
    }
    response = await client.post("/api/v1/companies", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Acme Corp"
    assert data["careers_url"] == "https://acme.com/careers"
    assert data["job_count"] == 0
    assert "id" in data


@pytest.mark.asyncio
async def test_create_company_duplicate(client: AsyncClient) -> None:
    """Should reject duplicate company names."""
    payload = {"name": "Duplicate Inc", "careers_url": "https://dup.com/jobs"}
    await client.post("/api/v1/companies", json=payload)
    response = await client.post("/api/v1/companies", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_list_companies(client: AsyncClient) -> None:
    """Should list all companies."""
    await client.post(
        "/api/v1/companies",
        json={"name": "Company A", "careers_url": "https://a.com/careers"},
    )
    await client.post(
        "/api/v1/companies",
        json={"name": "Company B", "careers_url": "https://b.com/careers"},
    )
    response = await client.get("/api/v1/companies")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_create_and_get_job(client: AsyncClient) -> None:
    """Should create a job and retrieve it."""
    # Create company first
    company_resp = await client.post(
        "/api/v1/companies",
        json={"name": "Test Co", "careers_url": "https://test.co/jobs"},
    )
    company_id = company_resp.json()["id"]

    # Create job
    job_payload = {
        "title": "Senior Backend Engineer",
        "company_id": company_id,
        "location": "San Francisco, CA",
        "cohort": "Backend",
        "seniority_level": "Senior",
        "salary_min": 150000,
        "salary_max": 200000,
    }
    job_resp = await client.post("/api/v1/jobs", json=job_payload)
    assert job_resp.status_code == 201
    job_data = job_resp.json()
    assert job_data["title"] == "Senior Backend Engineer"
    assert job_data["cohort"] == "Backend"

    # Get job
    get_resp = await client.get(f"/api/v1/jobs/{job_data['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Senior Backend Engineer"


@pytest.mark.asyncio
async def test_list_jobs_with_filters(client: AsyncClient) -> None:
    """Should filter jobs by cohort."""
    company_resp = await client.post(
        "/api/v1/companies",
        json={"name": "Filter Co", "careers_url": "https://filter.co/jobs"},
    )
    company_id = company_resp.json()["id"]

    # Create jobs in different cohorts
    await client.post(
        "/api/v1/jobs",
        json={"title": "Backend Dev", "company_id": company_id, "cohort": "Backend"},
    )
    await client.post(
        "/api/v1/jobs",
        json={"title": "Frontend Dev", "company_id": company_id, "cohort": "Frontend"},
    )
    await client.post(
        "/api/v1/jobs",
        json={"title": "QA Engineer", "company_id": company_id, "cohort": "Testing"},
    )

    # Filter by cohort
    response = await client.get("/api/v1/jobs", params={"cohort": "Backend"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["cohort"] == "Backend"


@pytest.mark.asyncio
async def test_update_job(client: AsyncClient) -> None:
    """Should update a job's fields."""
    company_resp = await client.post(
        "/api/v1/companies",
        json={"name": "Update Co", "careers_url": "https://update.co/jobs"},
    )
    company_id = company_resp.json()["id"]

    job_resp = await client.post(
        "/api/v1/jobs",
        json={"title": "Engineer", "company_id": company_id, "cohort": "Other"},
    )
    job_id = job_resp.json()["id"]

    update_resp = await client.put(
        f"/api/v1/jobs/{job_id}",
        json={"title": "Senior Engineer", "cohort": "Backend"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Senior Engineer"
    assert update_resp.json()["cohort"] == "Backend"


@pytest.mark.asyncio
async def test_delete_job(client: AsyncClient) -> None:
    """Should permanently hard-delete a job record."""
    company_resp = await client.post(
        "/api/v1/companies",
        json={"name": "Delete Co", "careers_url": "https://del.co/jobs"},
    )
    company_id = company_resp.json()["id"]

    job_resp = await client.post(
        "/api/v1/jobs",
        json={"title": "To Delete", "company_id": company_id, "cohort": "Other"},
    )
    job_id = job_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/jobs/{job_id}")
    assert del_resp.status_code == 204

    # The record should be physically stripped (404 Not Found)
    get_resp = await client.get(f"/api/v1/jobs/{job_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_job_not_found(client: AsyncClient) -> None:
    """Should return 404 for non-existent job."""
    response = await client.get("/api/v1/jobs/99999")
    assert response.status_code == 404
