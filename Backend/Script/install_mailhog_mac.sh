#!/bin/bash
set -e

# ------------------------------------------
# MailHog Setup Script for macOS (Homebrew)
# ------------------------------------------

BREW_PREFIX="$(brew --prefix)"
MAILHOG_BIN_DIR="${BREW_PREFIX}/bin"
MAILHOG_UI_URL="http://localhost:8025"
MAILHOG_SMTP_HOST="localhost"
MAILHOG_SMTP_PORT="1025"

# ------------------------------------------
# Helper: Verify MailHog
# ------------------------------------------
verify_mailhog() {
  echo "Verifying MailHog installation..."
  if command -v mailhog >/dev/null 2>&1; then
    if mailhog --help >/dev/null 2>&1; then
      echo "MailHog verification successful."
    else
      echo "Verification failed (MailHog may not be executable)."
    fi
  else
    echo "mailhog not found in PATH."
  fi
}

# ------------------------------------------
# Ensure not running as root
# ------------------------------------------
if [ "$EUID" -eq 0 ]; then
  echo "Do not run this script with sudo or as root."
  echo "MailHog should run under your macOS user account."
  exit 1
fi

# ------------------------------------------
# Check and Install MailHog
# ------------------------------------------
echo "Checking for existing MailHog installation..."

if command -v mailhog >/dev/null 2>&1; then
  echo "MailHog already installed."
  mailhog --version 2>/dev/null || true
else
  echo "Installing MailHog via Homebrew..."
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is required. Install it with:"
    echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    exit 1
  fi

  brew install mailhog
fi

# ------------------------------------------
# Add to PATH if not already
# ------------------------------------------
if [[ ":$PATH:" != *":${MAILHOG_BIN_DIR}:"* ]]; then
  echo "Adding MailHog to PATH..."
  echo "export PATH=\"${MAILHOG_BIN_DIR}:\$PATH\"" >> ~/.zshrc
  export PATH="${MAILHOG_BIN_DIR}:$PATH"
fi

verify_mailhog

echo "MailHog setup completed successfully."
echo "Run 'make mail-run' to start MailHog."
echo "Mail UI: ${MAILHOG_UI_URL}"
echo "SMTP: ${MAILHOG_SMTP_HOST}:${MAILHOG_SMTP_PORT}"