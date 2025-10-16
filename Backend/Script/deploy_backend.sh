#!/usr/bin/env bash
set -euo pipefail

# CONFIG: adjust
PERSISTENT_ROOT="/home/gitlab-runner/sdmay26-37"
BACKEND_DIR="$PERSISTENT_ROOT/Backend"
API_DIR="$BACKEND_DIR/API"
API_VENV="$API_DIR/.venv"
BRANCH="${CI_COMMIT_REF_NAME:-main}"

echo "Deploy backend on $(hostname) - root=$PERSISTENT_ROOT branch=$BRANCH"

if [ -n "${CI_PROJECT_DIR:-}" ] && [ "$CI_PROJECT_DIR" != "$PERSISTENT_ROOT" ]; then
  echo "Syncing CI workspace to persistent path"
  rsync -a --delete --exclude '.git' "$CI_PROJECT_DIR/" "$PERSISTENT_ROOT/"
fi

# Ensure persistent checkout is on expected branch (only if git present)
cd "$PERSISTENT_ROOT"
# if [ -d .git ]; then
#   git fetch --all --prune
#   git reset --hard "origin/$BRANCH"
#   git clean -fd
# fi

# mkdir -p "$(dirname "$API_VENV")"
echo "Setting up backend virtualenv at $API_VENV"
python3 -m venv "$API_VENV"
source "$API_VENV/bin/activate"
pip install --upgrade pip
if [ -f "$BACKEND_DIR/requirements.txt" ]; then
  pip install -r "$BACKEND_DIR/requirements.txt"
fi

# Restart backend service and cybot service (systemd)
echo "Restarting backend and cybot services"
sudo systemctl daemon-reload
sudo systemctl restart backend-coursegpt.service
sudo systemctl restart cybot.service 
sudo systemctl enable backend-coursegpt.service cybot.service

echo "Backend deploy complete"