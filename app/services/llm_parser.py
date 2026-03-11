"""LLM-based job description parser using Gemini function calling."""

import json
import logging
from typing import Any

from google import genai
from google.genai import types

from app.config import settings
from app.schemas.job import JobCreate

logger = logging.getLogger(__name__)

# ── Function declaration for Gemini function calling ──────────────────────────

PARSE_JOB_FUNCTION = types.FunctionDeclaration(
    name="parse_job_posting",
    description="Parse a raw job posting into structured, normalized fields.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "title": types.Schema(
                type=types.Type.STRING,
                description="The job title, cleaned and normalized",
            ),
            "location": types.Schema(
                type=types.Type.STRING,
                description="Job location (city, state/country) or 'Remote'",
            ),
            "description_summary": types.Schema(
                type=types.Type.STRING,
                description="A concise 2-3 sentence summary of the role",
            ),
            "requirements": types.Schema(
                type=types.Type.OBJECT,
                description=(
                    "Structured requirements with keys: "
                    "'must_have' (list), 'nice_to_have' (list), "
                    "'years_experience' (string)"
                ),
                properties={
                    "must_have": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(type=types.Type.STRING),
                        description="Required skills and qualifications",
                    ),
                    "nice_to_have": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(type=types.Type.STRING),
                        description="Preferred but optional skills",
                    ),
                    "years_experience": types.Schema(
                        type=types.Type.STRING,
                        description="Required years of experience, e.g. '3-5 years'",
                    ),
                },
            ),
            "cohort": types.Schema(
                type=types.Type.STRING,
                description=(
                    "Job category. Must be one of: Backend, Frontend, "
                    "Fullstack, Data, ML/AI, DevOps, Testing, "
                    "Embedded/Hardware, Mobile, Security, Other"
                ),
                enum=[
                    "Backend", "Frontend", "Fullstack", "Data", "ML/AI",
                    "DevOps", "Testing", "Embedded/Hardware", "Mobile",
                    "Security", "Other",
                ],
            ),
            "seniority_level": types.Schema(
                type=types.Type.STRING,
                description=(
                    "Seniority level. Must be one of: Intern, Junior, "
                    "Mid, Senior, Staff, Principal, Manager, "
                    "Director, VP, Other"
                ),
                enum=[
                    "Intern", "Junior", "Mid", "Senior", "Staff",
                    "Principal", "Manager", "Director", "VP", "Other",
                ],
            ),
            "salary_min": types.Schema(
                type=types.Type.NUMBER,
                description="Minimum annual salary in USD, if mentioned",
            ),
            "salary_max": types.Schema(
                type=types.Type.NUMBER,
                description="Maximum annual salary in USD, if mentioned",
            ),
        },
        required=["title", "cohort"],
    ),
)

SYSTEM_PROMPT = (
    "You are a job posting parser. Given a raw job description, extract structured information "
    "using the parse_job_posting function. Be precise with cohort classification:\n"
    "- Backend: server-side, APIs, databases, microservices\n"
    "- Frontend: UI, React, Angular, CSS, browser\n"
    "- Fullstack: both frontend and backend\n"
    "- Data: analytics, data engineering, ETL, SQL-heavy\n"
    "- ML/AI: machine learning, AI, NLP, computer vision\n"
    "- DevOps: CI/CD, infrastructure, cloud, SRE\n"
    "- Testing: QA, test automation, SDET\n"
    "- Embedded/Hardware: firmware, RTOS, hardware, IoT\n"
    "- Mobile: iOS, Android, React Native, Flutter\n"
    "- Security: cybersecurity, penetration testing, security engineering\n"
    "- Other: anything that doesn't fit above\n\n"
    "Always call the parse_job_posting function with your analysis."
)


async def parse_job_description(
    raw_text: str, company_id: int, url: str | None = None
) -> JobCreate:
    """
    Parse a raw job description using Gemini function calling.

    Args:
        raw_text: The unstructured job description text.
        company_id: The ID of the company this job belongs to.
        url: Optional URL of the original job posting.

    Returns:
        A JobCreate schema populated with parsed fields.
    """
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured. Set it in your .env file.")

    client = genai.Client(api_key=settings.gemini_api_key)

    tool = types.Tool(function_declarations=[PARSE_JOB_FUNCTION])

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=f"Parse the following job posting:\n\n{raw_text}",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[tool],
            temperature=0.1,
        ),
    )

    # Extract function call from response
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
        logger.warning("Gemini did not return a function call, using defaults")
        return JobCreate(
            title="Untitled Position",
            company_id=company_id,
            description_raw=raw_text,
            url=url,
        )

    args: dict[str, Any] = dict(function_call.args) if function_call.args else {}
    logger.info(f"Parsed job: {args.get('title', 'unknown')} -> {args.get('cohort', 'Other')}")

    # Handle nested requirements dict
    requirements = args.get("requirements")
    if requirements and isinstance(requirements, str):
        try:
            requirements = json.loads(requirements)
        except json.JSONDecodeError:
            requirements = {"raw": requirements}

    return JobCreate(
        title=args.get("title", "Untitled Position"),
        company_id=company_id,
        location=args.get("location"),
        description_raw=raw_text,
        description_summary=args.get("description_summary"),
        requirements=requirements if isinstance(requirements, dict) else None,
        cohort=args.get("cohort", "Other"),
        seniority_level=args.get("seniority_level"),
        salary_min=args.get("salary_min"),
        salary_max=args.get("salary_max"),
        url=url,
    )
