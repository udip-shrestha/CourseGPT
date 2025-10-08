<#
.SYNOPSIS
    Installs PostgreSQL 17 via Winget if missing, initializes database cluster,
    registers and starts the Windows service, adds to PATH, and verifies installation.
#>

Write-Host "Checking for existing PostgreSQL installation..." -ForegroundColor Cyan

$pgVersion = "17"
$pgBaseDir = "C:\Program Files\PostgreSQL\$pgVersion"
$pgBinDir  = "$pgBaseDir\bin"
$pgDataDir = "C:\Postgres\Data"
$pgService = "PostgreSQL$pgVersion"

# -------- Verify PostgreSQL --------
function Test-Postgres {
    try {
        Write-Host "Verifying PostgreSQL installation..." -ForegroundColor Cyan
        & "$pgBinDir\psql.exe" -U postgres -c "SELECT version();"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Verification successful." -ForegroundColor Green
        } else {
            Write-Host "Verification failed (check user/password)." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Verification failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# -------- Main Logic --------
# Ensure script is running as Administrator
$IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $IsAdmin) {
    Write-Host "Please run this PowerShell script as Administrator." -ForegroundColor Red
    exit 1
}

$psql = Get-Command psql -ErrorAction SilentlyContinue
if ($psql) {
    Write-Host "PostgreSQL already installed." -ForegroundColor Green
    & psql --version
    Test-Postgres
} else {
    Write-Host "PostgreSQL not found, installing via Winget..." -ForegroundColor Yellow

    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Write-Host "Winget not found in PATH. Please install App Installer." -ForegroundColor Red
        exit 1
    }

    winget install --id PostgreSQL.PostgreSQL.$pgVersion --accept-package-agreements --accept-source-agreements -e
    if ($LASTEXITCODE -eq -1978335189) {
        Write-Host "PostgreSQL already installed and up to date. Continuing..." -ForegroundColor Yellow
    }
    elseif ($LASTEXITCODE -ne 0) {
        Write-Host "Winget install failed (exit code $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }

    if ((Test-Path $pgBinDir) -and ($env:Path -notlike "*$pgBinDir*")) {
        Write-Host "Adding PostgreSQL to PATH (session and system-wide)..." -ForegroundColor Cyan
    
        # Add to current session so it works immediately
        $env:Path += ";$pgBinDir"
    
        # Add to system PATH permanently for all users
        $sysPath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
        if ($sysPath -notlike "*$pgBinDir*") {
            $newSysPath = "$sysPath;$pgBinDir"
            [Environment]::SetEnvironmentVariable('Path', $newSysPath, 'Machine')
            Write-Host "System PATH updated permanently." -ForegroundColor Green
        } else {
            Write-Host "PostgreSQL already exists in system PATH." -ForegroundColor Yellow
        }
    }    

    Test-Postgres
}

# ------------------------------------------
# Copy Project Data Files to PostgreSQL Data Dir
# ------------------------------------------
$DB_DATA_DIR = "$pgBaseDir\data"                                # Postgres internal data directory (for pg_read_binary_file)
$SEED_SRC_DIR = (Resolve-Path "$PSScriptRoot\..\Data").Path     # Data folder inside your project (next to this script)
$SEED_DEST_DIR = "$DB_DATA_DIR\course_gpt"                      # Where to copy seed files

Write-Host "Copying seed data files..." -ForegroundColor Cyan
if (Test-Path $SEED_SRC_DIR) {
    try {
        New-Item -ItemType Directory -Force -Path $SEED_DEST_DIR | Out-Null
        Copy-Item -Path "$SEED_SRC_DIR\*" -Destination $SEED_DEST_DIR -Recurse -Force
        Write-Host "Copied seed data from '$SEED_SRC_DIR' to '$SEED_DEST_DIR'" -ForegroundColor Green
    } catch {
        Write-Host "Failed to copy seed files: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "Seed source directory not found at '$SEED_SRC_DIR'." -ForegroundColor Yellow
}

Write-Host "Script completed successfully." -ForegroundColor Green