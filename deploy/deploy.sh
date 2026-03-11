#!/bin/bash
# =============================================================================
# AutoApply-Agent — Manual EC2 Deployment Script
# =============================================================================
# Run this AFTER SSHing into your EC2 instance if you didn't use user-data,
# or if you want to redeploy / update.
#
# Usage:
#   ssh -i your-key.pem ec2-user@YOUR_EC2_IP
#   curl -fsSL https://raw.githubusercontent.com/scarletxyh/AutoApply-Agent/main/deploy/deploy.sh | bash
#   # OR: git clone ... && cd AutoApply-Agent && bash deploy/deploy.sh
# =============================================================================

set -euo pipefail

APP_DIR="/opt/autoapply-agent"
REPO_URL="https://github.com/scarletxyh/AutoApply-Agent.git"

echo "🚀 AutoApply-Agent Deployment"
echo "=============================="

# ── Check Docker ──────────────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
    echo "❌ Docker is not installed. Please install Docker first or use ec2-user-data.sh"
    exit 1
fi

# ── Clone or update repo ─────────────────────────────────────────────────────
if [ -d "$APP_DIR" ]; then
    echo "📦 Updating existing deployment..."
    cd "$APP_DIR"
    git pull origin main
else
    echo "📦 Cloning repository..."
    sudo git clone "$REPO_URL" "$APP_DIR"
    sudo chown -R "$(whoami):$(whoami)" "$APP_DIR"
    cd "$APP_DIR"
fi

# ── Create .env if missing ────────────────────────────────────────────────────
if [ ! -f .env ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    # Fix DB URL for Docker internal networking
    sed -i 's|localhost:5433|db:5432|' .env
    echo ""
    echo "⚠️  IMPORTANT: Edit $APP_DIR/.env and set your GEMINI_API_KEY"
    echo "   nano $APP_DIR/.env"
    echo ""
fi

# ── Fix port mapping for EC2 (no local PG conflict) ──────────────────────────
sed -i 's/"5433:5432"/"5432:5432"/' docker-compose.yml

# ── Deploy ────────────────────────────────────────────────────────────────────
echo "🐳 Building and starting containers..."
docker compose down 2>/dev/null || true
docker compose up -d --build

echo ""
echo "✅ Deployment complete!"
echo ""

# Try to get public IP
PUBLIC_IP=$(curl -s --connect-timeout 2 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "YOUR_EC2_IP")
echo "🌐 API:     http://${PUBLIC_IP}:8000"
echo "📚 Docs:    http://${PUBLIC_IP}:8000/docs"
echo "❤️  Health:  http://${PUBLIC_IP}:8000/health"
echo ""
echo "📋 Useful commands:"
echo "   docker compose logs -f          # View logs"
echo "   docker compose restart app      # Restart app"
echo "   docker compose down             # Stop everything"
echo "   docker compose up -d --build    # Rebuild & restart"
