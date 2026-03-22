#!/bin/bash
set -e

MAILHOG_VERSION="v1.0.1"
MAILHOG_BINARY_URL="https://github.com/mailhog/MailHog/releases/download/${MAILHOG_VERSION}/MailHog_linux_amd64"
MAILHOG_INSTALL_PATH="/usr/local/bin/mailhog"

verify_mailhog() {
  echo "Verifying MailHog..."
  if command -v mailhog >/dev/null 2>&1; then
    echo "✔ MailHog is installed."
  else
    echo "✖ MailHog verification failed."
  fi
}

echo "Installing MailHog (if missing)..."
if ! command -v mailhog >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y wget
  sudo wget -O "${MAILHOG_INSTALL_PATH}" "${MAILHOG_BINARY_URL}"
  sudo chmod +x "${MAILHOG_INSTALL_PATH}"
fi

verify_mailhog

echo "✔ MailHog setup complete for Codespaces."
echo "Run 'make mail-run' to start MailHog."
echo "Web UI: http://localhost:8025"
echo "SMTP:   localhost:1025"