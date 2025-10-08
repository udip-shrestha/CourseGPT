#!/bin/bash
set -e

echo "🐧 Installing PostgreSQL on Linux..."

# Detect package manager
if command -v apt-get >/dev/null 2>&1; then
  echo "📦 Installing PostgreSQL using apt-get..."
  sudo apt-get update
  sudo apt-get install -y postgresql postgresql-contrib
elif command -v yum >/dev/null 2>&1; then
  echo "📦 Installing PostgreSQL using yum..."
  sudo yum install -y postgresql-server postgresql-contrib
else
  echo "❌ Unsupported Linux distribution. Please install PostgreSQL manually."
  exit 1
fi

# Enable and start service
sudo systemctl enable postgresql || true
sudo systemctl start postgresql || true

echo "✅ PostgreSQL installed and service started."
echo "➡ Run 'psql --version' to verify installation."
