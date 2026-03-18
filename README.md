# AutoApply-Agent

GenAI-powered job discovery tool that scrapes corporate career portals, parses job descriptions via Gemini LLM function calling, and serves a searchable, categorized job database.

## Features

- **Autonomous Scraping** — Playwright-based scraper monitors career portals
- **Two-Stage Extraction** — Fast DOM pre-parsing combined with focused LLM analysis ensures speed and cost-efficiency
- **Prompt Refinery & Configuration** — Built-in tools for in-context fine-tuning (Few-Shot) and iterative prompt engineering
- **Cohort Classification** — Auto-sorts roles into Backend, Testing, Embedded/Hardware, etc.
- **REST API** — Full CRUD with search, filtering, pagination, and system configuration
- **PostgreSQL** — Robust relational storage with async support

## Quick Start

### 1. Start PostgreSQL

```bash
docker-compose up -d db
```

### 2. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and set your GEMINI_API_KEY
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload
```

Visit **http://localhost:8000/docs** for interactive API documentation.

### 5. Run Tests

```bash
pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/jobs` | List/search jobs |
| `POST` | `/api/v1/jobs` | Create a job |
| `GET` | `/api/v1/jobs/{id}` | Get job details |
| `PUT` | `/api/v1/jobs/{id}` | Update a job |
| `DELETE` | `/api/v1/jobs/{id}` | Soft-delete a job |
| `GET` | `/api/v1/companies` | List companies |
| `POST` | `/api/v1/companies` | Add a company |
| `GET` | `/api/v1/companies/{id}` | Get company details |
| `POST` | `/api/v1/scrape` | Trigger a scrape run |
| `GET` | `/api/v1/scrape/{id}` | Get scrape status |
| `GET` | `/api/v1/scrape` | List scrape runs |
| `POST` | `/api/v1/scrape/url` | Direct structured scraping for a single job URL |
| `POST` | `/api/v1/jobs/{id}/refine` | Test prompt variations on a specific job |
| `POST` | `/api/v1/jobs/{id}/apply-refinement` | Update job data using a refined prompt |
| `GET` | `/api/v1/config/prompt` | Get the global few-shot system prompt |
| `PUT` | `/api/v1/config/prompt` | Set the global few-shot system prompt |

## Database Structure

```mermaid
erDiagram
    companies ||--o{ jobs : has
    companies ||--o{ scrape_runs : has
    system_config {
        int id PK
        varchar key UK
        text value
        text description
        timestamptz updated_at
    }
    alembic_version {
        varchar version_num PK
    }
    companies {
        int id PK
        varchar name UK
        varchar careers_url
        varchar description
        timestamptz created_at
    }
    jobs {
        int id PK
        varchar title
        int company_id FK
        varchar location
        text description_raw
        text description_summary
        jsonb requirements
        enum cohort
        enum seniority_level
        float salary_min
        float salary_max
        varchar url
        bool is_active
        timestamptz scraped_at
        timestamptz created_at
        timestamptz updated_at
    }
    scrape_runs {
        int id PK
        int company_id FK
        enum status
        int jobs_found
        timestamptz started_at
        timestamptz finished_at
        text error_message
        timestamptz created_at
    }
```

### `companies`

Stores the companies whose career portals are being monitored.

| Column | Type | Description |
|---|---|---|
| `id` | `SERIAL PK` | Auto-incrementing primary key |
| `name` | `VARCHAR(255) UNIQUE` | Company name (indexed) |
| `careers_url` | `VARCHAR(2048)` | URL of the careers portal |
| `description` | `VARCHAR(1024)` | Optional company description |
| `created_at` | `TIMESTAMPTZ` | Row creation timestamp |

### `jobs`

Parsed and categorized job postings, each linked to a company.

| Column | Type | Description |
|---|---|---|
| `id` | `SERIAL PK` | Auto-incrementing primary key |
| `title` | `VARCHAR(512)` | Job title (indexed) |
| `company_id` | `INT FK` | References `companies.id` (indexed) |
| `location` | `VARCHAR(255)` | Location or "Remote" (indexed) |
| `description_raw` | `TEXT` | Original unstructured description |
| `description_summary` | `TEXT` | LLM-generated summary |
| `requirements` | `JSONB` | Structured requirements (`must_have`, `nice_to_have`, `years_experience`) |
| `cohort` | `ENUM` | Category: Backend, Frontend, Fullstack, Data, ML/AI, DevOps, Testing, Embedded/Hardware, Mobile, Security, Other (indexed) |
| `seniority_level` | `ENUM` | Intern, Junior, Mid, Senior, Staff, Principal, Manager, Director, VP, Other |
| `salary_min` | `FLOAT` | Minimum annual salary (USD) |
| `salary_max` | `FLOAT` | Maximum annual salary (USD) |
| `url` | `VARCHAR(2048)` | Original job posting URL |
| `is_active` | `BOOLEAN` | Soft-delete flag (default: `true`) |
| `scraped_at` | `TIMESTAMPTZ` | When the job was scraped |
| `created_at` | `TIMESTAMPTZ` | Row creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | Last update timestamp |

### `scrape_runs`

Tracks each scraping operation against a company's career portal.

| Column | Type | Description |
|---|---|---|
| `id` | `SERIAL PK` | Auto-incrementing primary key |
| `company_id` | `INT FK` | References `companies.id` (indexed) |
| `status` | `ENUM` | pending, running, completed, failed |
| `jobs_found` | `INT` | Number of jobs discovered |
| `started_at` | `TIMESTAMPTZ` | Scrape start time |
| `finished_at` | `TIMESTAMPTZ` | Scrape end time |
| `error_message` | `TEXT` | Error details if failed |
| `created_at` | `TIMESTAMPTZ` | Row creation timestamp |

### `system_config`

Global system configuration, used for "in-context fine-tuning" and prompt management.

| Column | Type | Description |
|---|---|---|
| `id` | `SERIAL PK` | Auto-incrementing primary key |
| `key` | `VARCHAR(255) UNIQUE` | Configuration key (e.g., `global_system_prompt`) |
| `value` | `TEXT` | Configuration value |
| `description` | `TEXT` | Optional description of the configuration |
| `updated_at` | `TIMESTAMPTZ` | Last update timestamp |

### `alembic_version`

An internal administrative table automatically created and managed by Alembic. It stores a single row containing the version ID of the most recently applied database migration. This allows the system to track which schema updates have already been run and which are pending.

| Column | Type | Description |
|---|---|---|
| `version_num` | `VARCHAR(32) PK` | The current database migration revision ID |

## Docker (Local)

```bash
# Run everything (app + db)
docker-compose up

# Build only
docker build -t autoapply-agent .
```

## AWS EC2 Deployment

### Recommended Instance

| Config | Value |
|---|---|
| Instance type | `t3.medium` (2 vCPU, 4GB RAM) |
| AMI | Amazon Linux 2023 or Ubuntu 22.04 |
| Storage | 20 GB gp3 |
| Security group | Ports 22 (SSH), 8000 (API), 80/443 (optional) |

### Option A: Auto-deploy with User Data

When launching a new EC2 instance, paste the contents of [`deploy/ec2-user-data.sh`](deploy/ec2-user-data.sh) into the **User data** field. The instance will automatically install Docker, clone the repo, and start the stack on boot.

After launch:
```bash
ssh -i your-key.pem ec2-user@YOUR_EC2_IP
# Set your Gemini API key
nano /opt/autoapply-agent/.env
# Restart to pick up the key
cd /opt/autoapply-agent && docker compose restart app
```

### Option B: Manual SSH Deployment

```bash
ssh -i your-key.pem ec2-user@YOUR_EC2_IP

# Install Docker (Amazon Linux 2023)
sudo dnf install -y docker git
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user
newgrp docker

# Clone and deploy
sudo git clone https://github.com/scarletxyh/AutoApply-Agent.git /opt/autoapply-agent
sudo chown -R ec2-user:ec2-user /opt/autoapply-agent
cd /opt/autoapply-agent
cp .env.example .env
nano .env  # Set your GEMINI_API_KEY
sed -i 's/"5433:5432"/"5432:5432"/' docker-compose.yml
docker compose up -d --build
```

### Verify

```bash
curl http://YOUR_EC2_IP:8000/health
# {"status": "ok"}
```

Swagger docs at `http://YOUR_EC2_IP:8000/docs`

### Useful Commands

```bash
docker compose logs -f           # View logs
docker compose restart app       # Restart after config change
docker compose down && docker compose up -d --build  # Full rebuild
```

## Tech Stack

- **FastAPI** + **Uvicorn** (async Python web framework)
- **SQLAlchemy 2.0** (async ORM)
- **PostgreSQL 16** (database)
- **Alembic** (migrations)
- **Google Gemini** (LLM function calling)
- **Playwright** (web scraping)
- **GitHub Actions** (CI/CD)
