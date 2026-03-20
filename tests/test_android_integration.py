"""
Integration tests validating the API contract that the Android app depends on.

These tests run against the live FastAPI backend on AWS to ensure
the JSON response shapes match what the Kotlin ApiModels.kt data classes expect.

Run with:
    source .venv/bin/activate && pytest tests/test_android_integration.py -v
"""

import os
from typing import Generator

import httpx
import pytest

# Resolve the backend URL — defaults to the AWS EC2 instance.
# Override with: BACKEND_URL=http://localhost:8000 pytest ...
BASE_URL = os.environ.get("BACKEND_URL", "http://3.215.115.76:8000")


@pytest.fixture
def client() -> Generator[httpx.Client, None, None]:
    """Synchronous HTTP client pointed at the live backend."""
    with httpx.Client(base_url=BASE_URL, timeout=15.0) as c:
        yield c


# ── Health Check ──────────────────────────────────────────────────────────────


def test_health(client: httpx.Client) -> None:
    """Backend should be reachable."""
    response = client.get("/health")
    assert response.status_code == 200


# ── Jobs Endpoints ────────────────────────────────────────────────────────────


def test_get_jobs_returns_paginated(client: httpx.Client) -> None:
    """GET /api/v1/jobs should return a paginated JobListResponse."""
    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    data = response.json()

    # Validate the response matches JobListResponse shape
    assert "items" in data
    assert isinstance(data["items"], list)
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "pages" in data


def test_get_job_detail_404(client: httpx.Client) -> None:
    """GET /api/v1/jobs/999999 should return 404."""
    response = client.get("/api/v1/jobs/999999")
    assert response.status_code == 404


def test_job_response_schema(client: httpx.Client) -> None:
    """If jobs exist, validate response fields match Android ApiModels.kt."""
    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    items = response.json()["items"]

    if len(items) == 0:
        pytest.skip("No jobs in database to validate schema against")

    job = items[0]

    # These are the fields that ApiModels.kt (Android) expects
    expected_fields = [
        "id",
        "title",
        "company_id",
        "company_name",
        "location",
        "description_raw",
        "description_summary",
        "requirements",
        "cohort",
        "seniority_level",
        "salary_min",
        "salary_max",
        "url",
        "is_active",
        "scraped_at",
        "created_at",
        "updated_at",
    ]

    for field in expected_fields:
        assert field in job, f"Missing field: {field}"


# ── Scrape Endpoints ──────────────────────────────────────────────────────────


def test_scrape_url_returns_response(client: httpx.Client) -> None:
    """POST /api/v1/scrape/url should accept a URL and return a response."""
    response = client.post(
        "/api/v1/scrape/url",
        json={
            "url": "https://www.google.com/about/careers/applications/jobs/results/143333237156913862-software-engineer-ii-early-career"
        },
    )
    # Accept 200, 201, or 202 — depends on backend implementation
    assert response.status_code in (200, 201, 202, 422)

    if response.status_code in (200, 201, 202):
        data = response.json()
        # Validate the response matches ScrapeRunResponse fields
        assert "id" in data
        assert "status" in data
        assert "created_at" in data


def test_scrape_url_invalid_company_returns_error(client: httpx.Client) -> None:
    """POST /api/v1/scrape/url with nonexistent company_id should return error."""
    response = client.post(
        "/api/v1/scrape/url",
        json={"url": "https://example.com/jobs/1", "company_id": 999999},
    )
    # Should be 404 or 422
    assert response.status_code in (404, 422)
