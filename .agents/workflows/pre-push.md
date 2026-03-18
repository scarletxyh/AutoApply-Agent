---
description: Run standard checks (linting, formatting) before pushing to remote
---

1. Activate virtual environment and run Ruff checks
// turbo
2. source .venv/bin/activate && ruff check . && ruff format --check .

3. If checks pass, proceed with git push
4. git push origin $(git branch --show-current)
