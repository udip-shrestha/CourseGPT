#!/bin/bash
set -e

echo "🍎 Installing PostgreSQL on macOS..."

# Check if Homebrew is installed
if ! command -v brew >/dev/null 2>&1; then
  echo "❌ Homebrew not found. Please install it first: https://brew.sh"
  exit 1
fi

# Install PostgreSQL if not installed
if ! command -v psql >/dev/null 2>&1; then
  echo "📦 Installing PostgreSQL via Homebrew..."
  brew install postgresql
else
  echo "✅ PostgreSQL already installed ($(psql --version))"
fi

# Start PostgreSQL service
brew services start postgresql || true
echo "✅ PostgreSQL is running."

echo "➡ Run 'psql --version' to verify installation."
