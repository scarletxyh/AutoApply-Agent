---
description: Deploy local GitHub updates to the AWS server and rebuild the Docker container
---

This workflow pulls the latest codebase from GitHub to the AWS EC2 instance and rebuilds the server. It replaces the legacy SCP-entire-codebase approach.

> **Note:** Use this workflow for large changes, new modules, or full syncs. For quick fixes, the agent will modify AWS directly and SCP the file back locally.

1. Ensure all local changes are committed and pushed to your GitHub repository first.
```bash
git add .
git commit -m "Deploy to AWS"
git push origin current-branch
```

// turbo
2. Sync the `.env` configuration file to the remote instance manually, since it isn't tracked in Git:
```bash
scp .env autoapply:/opt/autoapply-agent/
```

// turbo
3. Pull the latest code from GitHub and restart the Docker container on AWS:
```bash
ssh autoapply "cd /opt/autoapply-agent && git fetch && git pull origin main && docker compose up -d --build"
```

4. Verify backend health dynamically:
```bash
curl http://$(ssh autoapply "curl -s http://checkip.amazonaws.com"):8000/health
```
