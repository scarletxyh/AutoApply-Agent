"""Integration and unit tests for the Resumes REST API."""

from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Resume


@pytest.mark.asyncio
async def test_upload_resume_success(client: AsyncClient, test_session: AsyncSession) -> None:
    """Test successfully uploading and parsing a standard LaTeX resume file."""
    fake_tex_content = b"\\documentclass{article}\\begin{document}John Doe Resume\\end{document}"

    mock_parsed_data = {
        "parsed_skills": ["Python", "Machine Learning"],
        "parsed_experience": [
            {
                "company": "Tech Corp",
                "role": "AI Engineer",
                "duration": "2024-2026",
                "bullets": ["Optimized algorithms."]
            }
        ]
    }

    # Intercept the Gemini call explicitly
    with patch("app.api.v1.resumes.parse_resume_tex", return_value=mock_parsed_data):
        response = await client.post(
            "/api/v1/resumes/upload",
            files={"file": ("john_doe.tex", fake_tex_content, "text/plain")},
        )

    assert response.status_code == 201, f"Failed: {response.content.decode()}"
    data = response.json()
    assert data["name"] == "john_doe"
    assert "Python" in data["parsed_skills"]
    assert data["is_original"] is True

    # Validate database integrity natively
    result = await test_session.execute(select(Resume).where(Resume.name == "john_doe"))
    db_resume = result.scalar_one_or_none()
    assert db_resume is not None
    assert db_resume.content_raw == fake_tex_content.decode("utf-8")
    assert db_resume.parsed_skills == ["Python", "Machine Learning"]


@pytest.mark.asyncio
async def test_upload_resume_invalid_format(client: AsyncClient) -> None:
    """Ensure the API aggressively rejects invalid files."""
    response = await client.post(
        "/api/v1/resumes/upload",
        files={"file": ("malicious.pdf", b"fake pdf content", "application/pdf")},
    )
    assert response.status_code == 400
    assert "LaTeX" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_resume(client: AsyncClient, test_session: AsyncSession) -> None:
    """Ensure the hard deletion removes the parsed schema permanently."""
    # 1. Insert a mock resume directly
    resume = Resume(
        name="test_deletion",
        content_raw="raw data",
        is_original=True,
    )
    test_session.add(resume)
    await test_session.commit()
    await test_session.refresh(resume)

    # 2. Invoke the DELETE endpoint
    response = await client.delete(f"/api/v1/resumes/{resume.id}")
    assert response.status_code == 204

    # 3. Assert it's wiped completely from Database
    result = await test_session.execute(select(Resume).where(Resume.id == resume.id))
    assert result.scalar_one_or_none() is None
