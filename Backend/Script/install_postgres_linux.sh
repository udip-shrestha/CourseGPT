#!/bin/bash
set -e

# ------------------------------------------
# PostgreSQL 17 Setup Script for Linux (Debian/Ubuntu-style)
# ------------------------------------------

PG_VERSION="17"
PG_SERVICE="postgresql"
PG_DATA_DIR="/var/lib/postgresql/${PG_VERSION}/main"   # Default for Debian-based
PG_BIN_DIR="/usr/lib/postgresql/${PG_VERSION}/bin"     # Default bin location

SEED_SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../Data" && pwd)"
SEED_DEST_DIR="${PG_DATA_DIR}/course_gpt"

# ------------------------------------------
# Helper: Verify PostgreSQL
# ------------------------------------------
verify_postgres() {
  echo "Verifying PostgreSQL installation..."
  if command -v psql >/dev/null 2>&1; then
    if sudo -u postgres psql -c "SELECT version();" >/dev/null 2>&1; then
      echo "PostgreSQL verification successful."
    else
      echo "Verification failed (server may not be running or access issue)."
    fi
  else
    echo "psql not found in PATH."
  fi
}

# ------------------------------------------
# Check Linux Distro (Debian/Ubuntu expected)
# ------------------------------------------
if ! command -v apt-get >/dev/null 2>&1; then
  echo "This script currently supports Debian/Ubuntu (apt-get) only."
  echo "For other distros, install PostgreSQL 17 manually."
  exit 1
fi

# ------------------------------------------
# Check and Install PostgreSQL
# ------------------------------------------
echo "Checking for existing PostgreSQL installation..."

if command -v psql >/dev/null 2>&1; then
  echo "PostgreSQL already installed."
  psql --version
else
  echo "Installing PostgreSQL ${PG_VERSION}..."
  sudo apt-get update -y

  # Official Postgres repo for exact version
  if ! apt-cache show "postgresql-${PG_VERSION}" >/dev/null 2>&1; then
    echo "Adding PostgreSQL APT repository..."
    sudo apt-get install -y wget gnupg lsb-release
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" \
      > /etc/apt/sources.list.d/pgdg.list'
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc \
      | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg

    sudo apt-get update -y
  fi

  sudo apt-get install -y "postgresql-${PG_VERSION}" "postgresql-client-${PG_VERSION}"
fi

# ------------------------------------------
# Ensure Service is Started
# ------------------------------------------
echo "Starting PostgreSQL service..."
sudo systemctl enable "${PG_SERVICE}"
sudo systemctl start "${PG_SERVICE}"

sleep 3

verify_postgres

# ------------------------------------------
# Ensure 'postgres' user exists in PostgreSQL
# ------------------------------------------
DB_USER="postgres"
DEFAULT_PG_PASSWORD="postgres"

echo "Setting password for PostgreSQL user '${DB_USER}'..."
sudo -u postgres psql -c "ALTER USER \"${DB_USER}\" WITH PASSWORD '${DEFAULT_PG_PASSWORD}';"
echo "Password for '${DB_USER}' set to '${DEFAULT_PG_PASSWORD}'."

# ------------------------------------------
# Copy Project Seed Data
# ------------------------------------------
echo "Copying seed data files..."
if [ -d "$SEED_SRC_DIR" ]; then
  sudo mkdir -p "$SEED_DEST_DIR"
  sudo cp -R "$SEED_SRC_DIR/"* "$SEED_DEST_DIR" || true
  sudo chown -R postgres:postgres "$SEED_DEST_DIR"
  echo "Copied seed data from '$SEED_SRC_DIR' to '$SEED_DEST_DIR'."
else
  echo "Seed source directory not found at '$SEED_SRC_DIR'."
fi

echo "PostgreSQL setup completed successfully."
