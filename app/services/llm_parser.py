"""LLM-based job description parser using Gemini function calling."""

import json
import logging
from typing import Any

from google import genai
from google.genai import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import SystemConfig
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
                    "Backend",
                    "Frontend",
                    "Fullstack",
                    "Data",
                    "ML/AI",
                    "DevOps",
                    "Testing",
                    "Embedded/Hardware",
                    "Mobile",
                    "Security",
                    "Other",
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
                    "Intern",
                    "Junior",
                    "Mid",
                    "Senior",
                    "Staff",
                    "Principal",
                    "Manager",
                    "Director",
                    "VP",
                    "Other",
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

tool = types.Tool(function_declarations=[PARSE_JOB_FUNCTION])

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
    "IMPORTANT: Here is a few-shot example of how you should structure your response:\n\n"
    "=== EXAMPLE INPUT ===\n"
    "We are looking for a Software Engineer to join our core backend team. "
    "You will build scalable microservices "
    "in Go and Python. Requirements: BS in CS, 3+ years of experience, "
    "strong understanding of PostgreSQL and AWS. "
    "Nice to have: experience with Kubernetes and GraphQL. Salary: $120,000 - $150,000.\n"
    "=== EXAMPLE OUTPUT ===\n"
    "{\n"
    '  "title": "Software Engineer",\n'
    '  "cohort": "Backend",\n'
    '  "seniority_level": "Mid",\n'
    '  "salary_min": 120000,\n'
    '  "salary_max": 150000,\n'
    '  "description_summary": "Join the core backend team to build scalable '
    'microservices using Go and Python. Play a key role in architecting '
    'cloud infrastructure on AWS.",\n'
    '  "requirements": {\n'
    '    "must_have": ["Go", "Python", "PostgreSQL", "AWS", "BS in CS"],\n'
    '    "nice_to_have": ["Kubernetes", "GraphQL"],\n'
    '    "years_experience": "3+ years"\n'
    "  }\n"
    "}\n\n"
    "Always call the parse_job_posting function with your final analysis."
)


async def parse_job_description(
    raw_text: str,
    company_id: int,
    db: AsyncSession,
    url: str | None = None,
    pre_extracted_data: dict[str, Any] | None = None,
) -> JobCreate:
    """
    Parse a raw job description using Gemini function calling.
    Optimized to focus on complex fields by providing pre-extracted metadata.
    """
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured. Set it in your .env file.")

    client = genai.Client(api_key=settings.gemini_api_key)
    # tool moved to module level

    # Provide pre-extracted data to Gemini to avoid redundant work and reduce tokens
    context_prefix = ""
    if pre_extracted_data:
        context_prefix = (
            "Pre-extracted metadata (use as reference, but verify against text):\n"
            f"- Title: {pre_extracted_data.get('title')}\n"
            f"- Location: {pre_extracted_data.get('location')}\n"
            f"- Company: {pre_extracted_data.get('company')}\n\n"
        )

    # Fetch dynamic prompt override if it exists
    stmt = select(SystemConfig).where(SystemConfig.key == "global_system_prompt")
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    active_prompt = config.value if config else SYSTEM_PROMPT

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=f"{context_prefix}Parse the following job posting:\n\n{raw_text}",
            config=types.GenerateContentConfig(
                system_instruction=(
                    f"{active_prompt}\n"
                    "Focus heavily on accurately capturing 'requirements' (skills) and "
                    "synthesizing a high-quality 'description_summary'."
                ),
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
            logger.warning("Gemini did not return a function call, merging with DOM defaults")
            return JobCreate(
                title=pre_extracted_data.get("title")
                if pre_extracted_data
                else "Untitled Position",
                location=pre_extracted_data.get("location") if pre_extracted_data else None,
                company_id=company_id,
                description_raw=raw_text,
                url=url,
            )

        args: dict[str, Any] = dict(function_call.args) if function_call.args else {}
    except Exception as e:
        logger.error(f"Gemini API failed: {e}. Saving raw HTML and DOM metadata.")
        return JobCreate(
            title=pre_extracted_data.get("title")
            if pre_extracted_data and pre_extracted_data.get("title")
            else "Untitled Position (LLM Failed)",
            location=pre_extracted_data.get("location") if pre_extracted_data else None,
            company_id=company_id,
            description_raw=raw_text,
            url=url,
            description_summary="LLM processing failed. See raw description.",
        )

    # Merge LLM results with DOM data (prefer DOM for title/location if valid)
    final_title = (
        pre_extracted_data.get("title")
        if pre_extracted_data and pre_extracted_data.get("title")
        else args.get("title")
    )
    final_location = (
        pre_extracted_data.get("location")
        if pre_extracted_data and pre_extracted_data.get("location")
        else args.get("location")
    )

    requirements = args.get("requirements")
    if requirements and isinstance(requirements, str):
        try:
            requirements = json.loads(requirements)
        except json.JSONDecodeError:
            requirements = {"raw": requirements}

    return JobCreate(
        title=final_title or "Untitled Position",
        company_id=company_id,
        location=final_location,
        description_raw=raw_text,
        description_summary=args.get("description_summary"),
        requirements=requirements if isinstance(requirements, dict) else None,
        cohort=args.get("cohort", "Other"),
        seniority_level=args.get("seniority_level"),
        salary_min=args.get("salary_min"),
        salary_max=args.get("salary_max"),
        url=url,
    )


PARSE_RESUME_FUNCTION = types.FunctionDeclaration(
    name="parse_resume_tex",
    description="Parse a raw LaTeX resume into structured skills and experience timelines.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "parsed_skills": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="List of core professional skills, languages, and technologies.",
            ),
            "parsed_experience": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "company": types.Schema(type=types.Type.STRING),
                        "role": types.Schema(type=types.Type.STRING),
                        "duration": types.Schema(type=types.Type.STRING),
                        "bullets": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(type=types.Type.STRING)
                        )
                    }
                ),
                description="Chronological list of professional experience with bullet points.",
            ),
        },
        required=["parsed_skills", "parsed_experience"],
    ),
)

RESUME_SYSTEM_PROMPT = (
    "You are an expert AI resume parser. "
    "Given raw LaTeX (.tex) source code of a resume, extract the individual's "
    "core 'parsed_skills' (programming languages, tools, frameworks) and "
    "their 'parsed_experience' (companies, roles, durations, and accomplishment bullets). "
    "Remove all LaTeX formatting commands and return only clean, readable text. "
    "Always call the parse_resume_tex function with your structured JSON."
)

async def parse_resume_tex(raw_text: str) -> dict[str, Any]:
    """Parse a raw LaTeX resume into structured JSON arrays via Gemini."""
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=settings.gemini_api_key)
    resume_tool = types.Tool(function_declarations=[PARSE_RESUME_FUNCTION])

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=f"Parse the following LaTeX resume into structured data:\n\n{raw_text}",
            config=types.GenerateContentConfig(
                system_instruction=RESUME_SYSTEM_PROMPT,
                tools=[resume_tool],
                temperature=0.1,
            ),
        )

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

        args = dict(function_call.args) if function_call and function_call.args else {}

        # Safely convert protobuf representations if necessary
        skills = args.get("parsed_skills", [])
        experience = args.get("parsed_experience", [])

        return {
            "parsed_skills": list(skills) if hasattr(skills, '__iter__') else [],
            "parsed_experience": list(experience) if hasattr(experience, '__iter__') else []
        }
    except Exception as e:
        logger.error(f"Gemini resume parsing gracefully failed: {e}")
        return {"parsed_skills": [], "parsed_experience": []}

