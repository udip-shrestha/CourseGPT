#!/bin/bash
set -e

PG_VERSION="17"
PG_CLUSTER_DIR="/etc/postgresql/${PG_VERSION}/main"
PG_DATA_DIR="/var/lib/postgresql/${PG_VERSION}/main"
PG_HBA="${PG_CLUSTER_DIR}/pg_hba.conf"

SEED_SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../Data" && pwd)"
SEED_DEST_DIR="${PG_DATA_DIR}/course_gpt"

verify_postgres() {
  echo "Verifying PostgreSQL..."
  if psql -U postgres -c "SELECT version();" >/dev/null 2>&1; then
    echo "✔ PostgreSQL is running."
  else
    echo "✖ PostgreSQL verification failed."
  fi
}

echo "Installing PostgreSQL (if missing)..."
if ! command -v psql >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y postgresql-${PG_VERSION} postgresql-client-${PG_VERSION}
fi

echo "Reinitializing PostgreSQL cluster with trust authentication..."
sudo service postgresql stop || true
sudo pg_dropcluster ${PG_VERSION} main --stop || true
sudo pg_createcluster ${PG_VERSION} main --start

echo "Configuring pg_hba.conf for trust authentication..."
sudo bash -c "cat > ${PG_HBA}" <<EOF
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
EOF

sudo service postgresql restart

sleep 2
verify_postgres

echo "Setting postgres password..."
psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';"

echo "Copying seed data..."
if [ -d "$SEED_SRC_DIR" ]; then
  sudo mkdir -p "$SEED_DEST_DIR"
  sudo cp -R "$SEED_SRC_DIR/"* "$SEED_DEST_DIR" || true
  sudo chown -R postgres:postgres "$SEED_DEST_DIR"
fi

echo "✔ PostgreSQL setup complete for Codespaces."
