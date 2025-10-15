#!/usr/bin/env bash
set -euo pipefail

# CONFIG: adjust as needed
PERSISTENT_ROOT="/home/vm-user/sdmay26-37"
FRONTEND_DIR="${CI_PROJECT_DIR:-$PERSISTENT_ROOT}/Frontend"
WWW_DIR="/var/www/coursegpt"

echo "Deploy frontend: src=$FRONTEND_DIR/dist -> dest=$WWW_DIR (host=$(hostname))"

if [ ! -d "$FRONTEND_DIR/dist" ] || [ -z "$(ls -A "$FRONTEND_DIR/dist")" ]; then
  echo "Error: frontend dist missing at $FRONTEND_DIR/dist"
  exit 1
fi

# create target and sync (requires sudo)
sudo mkdir -p "$WWW_DIR"
sudo rsync -a --delete "$FRONTEND_DIR/dist/" "$WWW_DIR/"

echo "Frontend deployed to $WWW_DIR"