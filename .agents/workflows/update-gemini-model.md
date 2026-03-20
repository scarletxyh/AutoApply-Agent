---
description: Dynamically switch to the latest available Gemini Flash Lite preview model and restart the AWS server
---

This workflow automates querying the Google Gemini API to find the absolute latest supported `flash-lite-preview` model, updates your `.env` securely, syncs the change to AWS, and reboots the remote Docker container.

All steps execute securely inside your local Python virtual environment.

// turbo
1. Execute the Python model updater script:
```bash
source .venv/bin/activate && python -c '
import os, requests, re
from dotenv import load_dotenv

env_path = ".env"
load_dotenv(env_path)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: No GEMINI_API_KEY found in .env")
    exit(1)

r = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}")
data = r.json()

if "error" in data:
    print(f"API Error: {data[\"error\"]}")
    exit(1)

# Filter for models that actually support text generation
valid_models = [m["name"].split("/")[-1] for m in data.get("models", []) 
                if "generateContent" in m.get("supportedGenerationMethods", [])]

# Order of preference: flash-lite-preview, then any flash variant, then just the first available
target_model = next((m for m in valid_models if "flash-lite-preview" in m), None)
if not target_model:
    target_model = next((m for m in valid_models if "flash" in m), valid_models[0])

print(f"Dynamically selecting model: {target_model}")

# Read and safely update .env locally
with open(env_path, "r") as f:
    content = f.read()

new_content = re.sub(r"GEMINI_MODEL=.*", f"GEMINI_MODEL={target_model}", content)

with open(env_path, "w") as f:
    f.write(new_content)

print(f"Updated .env file locally with {target_model}")
'
```

// turbo-all
2. Securely copy the new `.env` file to AWS and cleanly restart the background parser:
```bash
scp .env autoapply:/opt/autoapply-agent/
ssh autoapply "cd /opt/autoapply-agent && docker compose restart app"
```

3. Verification (Optional): Test that the parsing endpoint is active with the new model.
```bash
# This sends a dummy health-check to the AWS instance
curl http://$(ssh autoapply "curl -s http://checkip.amazonaws.com"):8000/health
```
