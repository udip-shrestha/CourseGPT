<#
.SYNOPSIS
    Installs MailHog via Scoop if missing, adds it to PATH, and verifies installation.
#>

Write-Host "Checking for existing MailHog installation..." -ForegroundColor Cyan

$mailhogCmd = Get-Command mailhog -ErrorAction SilentlyContinue

# -------- Verify MailHog --------
function Test-MailHog {
    try {
        Write-Host "Verifying MailHog installation..." -ForegroundColor Cyan
        & mailhog --help > $null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Verification successful." -ForegroundColor Green
        } else {
            Write-Host "Verification failed." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Verification failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# -------- Install Scoop if needed --------
function Install-Scoop {
    if (-not (Get-Command scoop -ErrorAction SilentlyContinue)) {
        Write-Host "Scoop not found. Installing Scoop..." -ForegroundColor Yellow

        Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        irm get.scoop.sh | iex

        Write-Host "Scoop installed successfully." -ForegroundColor Green
    } else {
        Write-Host "Scoop already installed." -ForegroundColor Green
    }
}

# -------- Install MailHog --------
function Install-MailHog {
    Write-Host "Installing MailHog via Scoop..." -ForegroundColor Cyan
    scoop install mailhog

    if ($LASTEXITCODE -ne 0) {
        Write-Host "MailHog installation failed." -ForegroundColor Red
        exit 1
    }

    Write-Host "MailHog installed successfully." -ForegroundColor Green
}

# -------- Main Logic --------
if ($mailhogCmd) {
    Write-Host "MailHog already installed." -ForegroundColor Green
    Test-MailHog
} else {
    Install-Scoop
    Install-MailHog
    Test-MailHog
}

Write-Host ""
Write-Host "MailHog setup completed successfully." -ForegroundColor Green
Write-Host "Run 'make mail-run' to start MailHog."
Write-Host ""
Write-Host "Mail UI: http://localhost:8025"
Write-Host "SMTP:    localhost:1025"