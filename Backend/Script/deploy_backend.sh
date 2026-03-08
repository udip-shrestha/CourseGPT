#!/usr/bin/env bash
set -euo pipefail

PERSISTENT_ROOT="/home/gitlab-runner/sdmay26-37"
BACKEND_DIR="$PERSISTENT_ROOT/Backend"
API_DIR="$BACKEND_DIR/API"
API_VENV="$API_DIR/.venv"
DISCORD_ENV="$BACKEND_DIR/.env"
BRANCH="${CI_COMMIT_REF_NAME:-main}"

echo "Deploy backend on $(hostname) - root=$PERSISTENT_ROOT branch=$BRANCH"

if [ -n "${CI_PROJECT_DIR:-}" ] && [ "$CI_PROJECT_DIR" != "$PERSISTENT_ROOT" ]; then
  echo "Syncing CI workspace to persistent path"
  rsync -a --delete --exclude '.git' "$CI_PROJECT_DIR/" "$PERSISTENT_ROOT/"
fi

cd "$PERSISTENT_ROOT"

echo "Setting up backend virtualenv at $API_VENV"
python3 -m venv "$API_VENV"
source "$API_VENV/bin/activate"
pip install --upgrade pip
if [ -f "$BACKEND_DIR/requirements.txt" ]; then
  pip install -r "$BACKEND_DIR/requirements.txt"
fi

# -------------------------------------------------------
#  Inject GitLab CI/CD secret into Backend/.env
# -------------------------------------------------------
echo "Writing environment variables to $DISCORD_ENV"
mkdir -p "$(dirname "$DISCORD_ENV")"
cat > "$DISCORD_ENV" <<EOF
# ===========================================
# FastAPI Server Configuration
# ===========================================
API_BASE_URL=${API_BASE_URL:-}

# ===========================================
# PostgreSQL Database Configuration
# ===========================================
DB_NAME=${DB_NAME:-}
DB_HOST=${DB_HOST:-}
DB_PORT=${DB_PORT:-}
DB_USER=${DB_USER:-}
DB_PASSWORD=${DB_PASSWORD:-}
SCHEMA_FILE=${SCHEMA_FILE:-}
SEED_FILE=${SEED_FILE:-}
EXPORT_OLD_DATA_SCRIPT=${EXPORT_OLD_DATA_SCRIPT:-}
LOAD_OLD_DATA_SCRIPT=${LOAD_OLD_DATA_SCRIPT:-}
IMPORT_OLD_DATA_SCRIPT=${IMPORT_OLD_DATA_SCRIPT:-}

# ===========================================
# Chroma Vector Database Configuration
# ===========================================
CHROMA_CLIENT=${CHROMA_CLIENT:-}
CHROMA_HOST=${CHROMA_HOST:-}
CHROMA_PORT=${CHROMA_PORT:-}

# ===========================================
# JWT Secrets
# ===========================================
JWT_ALGORITHM=${JWT_ALGORITHM:-}
JWT_SECRET_KEY=${JWT_SECRET_KEY:-}

# ===========================================
# Discord Bot Configuration
# ===========================================
DISCORD_TOKEN=${DISCORD_TOKEN:-}

# ===========================================
# LLM Configuration
# ===========================================
LLM_PROVIDER=${LLM_PROVIDER:-}
LLM_BASE_URL=${LLM_BASE_URL:-}
LLM_MODEL=${LLM_MODEL:-}
HUGGINGFACEHUB_API_TOKEN=${HUGGINGFACEHUB_API_TOKEN:-}

# ===========================================
# Canvas LTI Configuration
# ===========================================
CANVAS_PUBLIC_KEY_B64=${CANVAS_PUBLIC_KEY_B64:-}
CANVAS_PRIVATE_KEY_B64=${CANVAS_PRIVATE_KEY_B64:-}
CANVAS_KEY_ID=${CANVAS_KEY_ID:-}
FRONTEND_BASE_URL=${FRONTEND_BASE_URL:-}
EOF


chmod 600 "$DISCORD_ENV"
chown gitlab-runner:gitlab-runner "$DISCORD_ENV"

# Restart backend service and cybot service (systemd)
echo "Restarting backend and cybot services"
sudo systemctl daemon-reload
sudo systemctl restart backend-coursegpt.service
sudo systemctl restart cybot.service 
sudo systemctl enable backend-coursegpt.service cybot.service

# Restart monitoring services (Docker Compose)  
echo "Restarting monitoring services (Docker Compose)"
cd "$PERSISTENT_ROOT"
docker compose down
docker compose up -d

echo "Backend deploy complete"