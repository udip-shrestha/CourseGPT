#!/bin/bash
set -e

# ------------------------------------------
# MailHog Setup Script for Linux (Debian/Ubuntu-style)
# ------------------------------------------

MAILHOG_VERSION="v1.0.1"
MAILHOG_BINARY_URL="https://github.com/mailhog/MailHog/releases/download/${MAILHOG_VERSION}/MailHog_linux_amd64"
MAILHOG_INSTALL_PATH="/usr/local/bin/mailhog"

# ------------------------------------------
# Helper: Verify MailHog
# ------------------------------------------
verify_mailhog() {
  echo "Verifying MailHog installation..."
  if command -v mailhog >/dev/null 2>&1; then
    echo "MailHog verification successful."
    mailhog --help >/dev/null 2>&1 || true
  else
    echo "MailHog not found in PATH."
  fi
}

# ------------------------------------------
# Check Linux Distro (Debian/Ubuntu expected)
# ------------------------------------------
if ! command -v apt-get >/dev/null 2>&1; then
  echo "This script currently supports Debian/Ubuntu (apt-get) only."
  echo "For other distros, install MailHog manually."
  exit 1
fi

# ------------------------------------------
# Check and Install MailHog
# ------------------------------------------
echo "Checking for existing MailHog installation..."

if command -v mailhog >/dev/null 2>&1; then
  echo "MailHog already installed."
else
  echo "Installing MailHog..."

  sudo apt-get update -y
  sudo apt-get install -y wget

  sudo wget -O "${MAILHOG_INSTALL_PATH}" "${MAILHOG_BINARY_URL}"
  sudo chmod +x "${MAILHOG_INSTALL_PATH}"

  echo "MailHog installed to ${MAILHOG_INSTALL_PATH}."
fi

verify_mailhog

echo "MailHog setup completed successfully."
echo "Run 'make mail-run' to start MailHog."
echo "Web UI: http://localhost:8025"
echo "SMTP:   localhost:1025"