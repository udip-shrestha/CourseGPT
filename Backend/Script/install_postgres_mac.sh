#!/bin/bash
set -e

# ------------------------------------------
# PostgreSQL 17 Setup Script for macOS (Homebrew)
# ------------------------------------------

PG_VERSION="17"
BREW_PREFIX="$(brew --prefix)"
PG_BIN_DIR="${BREW_PREFIX}/opt/postgresql@${PG_VERSION}/bin"
PG_DATA_DIR="${BREW_PREFIX}/var/postgresql@${PG_VERSION}"
PG_SERVICE="postgresql@${PG_VERSION}"

SEED_SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../Data" && pwd)"
SEED_DEST_DIR="${PG_DATA_DIR}/course_gpt"

# ------------------------------------------
# Helper: Verify PostgreSQL
# ------------------------------------------
verify_postgres() {
  echo "Verifying PostgreSQL installation..."
  if command -v psql >/dev/null 2>&1; then
    if psql -U "$(whoami)" -c "SELECT version();" >/dev/null 2>&1; then
      echo "✅ PostgreSQL verification successful."
    else
      echo "⚠️ Verification failed (server may not be running or user access issue)."
    fi
  else
    echo "❌ psql not found in PATH."
  fi
}

# ------------------------------------------
# Ensure not running as root
# ------------------------------------------
if [ "$EUID" -eq 0 ]; then
  echo "❌ Do not run this script with sudo or as root."
  echo "   PostgreSQL should run under your macOS user account."
  exit 1
fi

# ------------------------------------------
# Check and Install PostgreSQL
# ------------------------------------------
echo "🔍 Checking for existing PostgreSQL installation..."

if command -v psql >/dev/null 2>&1; then
  echo "✅ PostgreSQL already installed."
  psql --version
else
  echo "📦 Installing PostgreSQL ${PG_VERSION} via Homebrew..."
  if ! command -v brew >/dev/null 2>&1; then
    echo "❌ Homebrew is required. Install it with:"
    echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    exit 1
  fi

  brew install "postgresql@${PG_VERSION}"

  echo "🔗 Linking PostgreSQL binaries..."
  brew link "postgresql@${PG_VERSION}" --force
fi

# ------------------------------------------
# Add to PATH if not already
# ------------------------------------------
if [[ ":$PATH:" != *":${PG_BIN_DIR}:"* ]]; then
  echo "🧩 Adding PostgreSQL to PATH..."
  echo "export PATH=\"${PG_BIN_DIR}:\$PATH\"" >> ~/.zshrc
  export PATH="${PG_BIN_DIR}:$PATH"
fi

# ------------------------------------------
# Fix Permissions & Initialize Cluster
# ------------------------------------------
echo "🗄 Ensuring PostgreSQL data directory permissions..."
mkdir -p "${PG_DATA_DIR}"
chown -R "$(whoami)" "${PG_DATA_DIR}" 2>/dev/null || true

if [ ! -f "${PG_DATA_DIR}/PG_VERSION" ]; then
  echo "⚙️ Initializing PostgreSQL database cluster at ${PG_DATA_DIR}..."
  initdb --locale=en_US.UTF-8 -E UTF8 -D "${PG_DATA_DIR}" -U "$(whoami)"
else
  echo "📁 PostgreSQL data directory already initialized."
fi

# ------------------------------------------
# Start PostgreSQL Service
# ------------------------------------------
echo "🚀 Starting PostgreSQL service..."
brew services start "${PG_SERVICE}"

sleep 3  # Give it a few seconds to start

verify_postgres

# ------------------------------------------
# Copy Project Seed Data
# ------------------------------------------
echo "📂 Copying seed data files..."
if [ -d "$SEED_SRC_DIR" ]; then
  mkdir -p "$SEED_DEST_DIR"
  cp -R "$SEED_SRC_DIR/"* "$SEED_DEST_DIR" || true
  echo "✅ Copied seed data from '$SEED_SRC_DIR' to '$SEED_DEST_DIR'."
else
  echo "⚠️ Seed source directory not found at '$SEED_SRC_DIR'."
fi

echo "🎉 PostgreSQL setup completed successfully."
