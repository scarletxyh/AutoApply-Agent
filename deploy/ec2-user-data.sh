#!/bin/bash
# =============================================================================
# AutoApply-Agent — EC2 User-Data Bootstrap Script
# =============================================================================
# Use this as the "User data" when launching an EC2 instance (Amazon Linux 2023
# or Ubuntu 22.04+). It installs Docker, clones the repo, and starts the stack.
#
# Instance recommendation: t3.medium (2 vCPU, 4GB RAM)
# AMI: Amazon Linux 2023 or Ubuntu 22.04
# Security group: open ports 22 (SSH), 80 (HTTP), 443 (HTTPS)
# =============================================================================

set -euo pipefail
exec > /var/log/user-data.log 2>&1

echo "========================================="
echo "AutoApply-Agent EC2 Bootstrap Starting..."
echo "========================================="

# ── Detect OS ─────────────────────────────────────────────────────────────────
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    OS="unknown"
fi

# ── Install Docker ────────────────────────────────────────────────────────────
echo "[1/6] Installing Docker..."
if [ "$OS" = "amzn" ]; then
    dnf update -y
    dnf install -y docker git
    systemctl enable docker
    systemctl start docker
    usermod -aG docker ec2-user
elif [ "$OS" = "ubuntu" ]; then
    apt-get update -y
    apt-get install -y ca-certificates curl gnupg
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
        https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
        | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin git
    systemctl enable docker
    systemctl start docker
    usermod -aG docker ubuntu
else
    echo "Unsupported OS: $OS"
    exit 1
fi

# ── Install Docker Compose (standalone, if not bundled) ───────────────────────
echo "[2/6] Ensuring Docker Compose..."
if ! docker compose version &>/dev/null; then
    COMPOSE_VERSION="v2.24.0"
    curl -fsSL "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# ── Clone the repository ─────────────────────────────────────────────────────
echo "[3/6] Cloning repository..."
APP_DIR="/opt/autoapply-agent"
git clone https://github.com/scarletxyh/AutoApply-Agent.git "$APP_DIR"
cd "$APP_DIR"

# ── Create .env file ─────────────────────────────────────────────────────────
echo "[4/6] Creating .env file..."
cat > .env <<'ENVFILE'
# Database (internal Docker network — use 'db' as hostname, port 5432)
DATABASE_URL=postgresql+asyncpg://autoapply:autoapply@db:5432/autoapply

# Google Gemini — REPLACE WITH YOUR ACTUAL KEY
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-3.1-flash-lite

# Server
APP_HOST=0.0.0.0
APP_PORT=8000
ENVFILE

echo "========================================="
echo "IMPORTANT: Edit /opt/autoapply-agent/.env"
echo "and set your GEMINI_API_KEY before the"
echo "app container can use LLM features."
echo "========================================="

# ── Update docker-compose for production ──────────────────────────────────────
echo "[5/6] Adjusting docker-compose for EC2..."
# On EC2 there's no local Postgres conflict, so use standard port 5432
sed -i 's/"5433:5432"/"5432:5432"/' docker-compose.yml

# ── Start the stack ───────────────────────────────────────────────────────────
echo "[6/6] Starting services..."
docker compose up -d --build

echo "========================================="
echo "AutoApply-Agent deployment complete!"
echo "API available at http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
echo "Swagger docs at http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000/docs"
echo "========================================="
echo "Logs: docker compose -f /opt/autoapply-agent/docker-compose.yml logs -f"
