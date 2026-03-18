---
description: Sync local changes to AWS and restart the Docker container
---

This workflow automates the process of pushing current local changes to the AWS EC2 instance and rebuilding the application.

1. Ensure you are in the project root on your local machine.
// turbo
2. Sync all local source code and configuration files to the remote instance:
```bash
ssh -o ConnectTimeout=5 autoapply "mkdir -p /opt/autoapply-agent/app/schemas /opt/autoapply-agent/app/services /opt/autoapply-agent/app/api/v1" && \
scp -r app/ main.py pyproject.toml docker-compose.yml Dockerfile .env.example autoapply:/opt/autoapply-agent/
```

// turbo
3. Rebuild and restart the application on AWS:
```bash
ssh autoapply "cd /opt/autoapply-agent && docker compose up -d --build"
```

4. Verify health:
```bash
curl http://$(ssh autoapply "curl -s http://checkip.amazonaws.com"):8000/health
```
