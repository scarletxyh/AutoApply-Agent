---
description: Safely reset the remote database and re-run migrations
---

This workflow wipes the existing database on AWS and re-initializes it with the latest schema. **CAUTION: This will delete all scraped jobs.**

// turbo
1. Wipe the current database volumes on AWS:
```bash
ssh autoapply "cd /opt/autoapply-agent && docker compose down -v && docker compose up -d db"
```

2. Wait for DB to be healthy:
```bash
ssh autoapply "docker exec autoapply-agent-db-1 pg_isready -U autoapply"
```

// turbo
3. Run Alembic migrations to re-create the schema:
```bash
ssh autoapply "docker exec -e PYTHONPATH=/app/ -w /app/ autoapply-agent-app-1 alembic upgrade head"
```

4. Verify table existence:
```bash
ssh autoapply "docker exec autoapply-agent-db-1 psql -U autoapply -d autoapply -c '\dt'"
```
