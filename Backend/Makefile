# ===========================================
# Default Target - Show available commands
# ===========================================
help:
	@echo ""
	@echo "Available Make Commands:"
	@echo "-------------------------------------------"
	@echo "make help       -> Show this help message"
	@echo "make db-setup   -> Check and install PostgreSQL if needed"
	@echo "make db-init    -> Drop, create, and initialize the database schema"
	@echo "make db-seed    -> Seed database with sample data"
	@echo "-------------------------------------------"
	@echo ""




# ===========================================
# API Make Commands
# ===========================================

VENV_DIR := API/.venv
REQ_FILE := API/requirements.txt

# -----------------------------------
# Create venv if missing
# -----------------------------------
ifeq ($(wildcard $(VENV_DIR)),)
api-create-venv:
	@echo Creating virtual environment...
	python -m venv $(VENV_DIR)
else
api-create-venv:
	@echo Virtual environment already exists.
endif

# -----------------------------------
# Install dependencies if requirements.txt exists
# -----------------------------------
ifeq ($(wildcard $(REQ_FILE)),)
api-install:
	@echo ERROR: requirements.txt not found in API directory. && exit 1
else
api-install: api-create-venv
	@echo Activating virtual environment...
	@cmd /C "( \
		call $(VENV_DIR)\Scripts\activate && \
		echo Installing dependencies from requirements.txt... && \
		python -m pip install --upgrade pip && \
		python -m pip install -r $(REQ_FILE) \
	)"
endif

# -------------------------------------------
# Run FastAPI backend
# -------------------------------------------
ifeq ($(wildcard $(VENV_DIR)),)
api-run: api-install
	@echo Creating virtual environment and installing dependencies...
	@cmd /Q /C "( \
		call $(VENV_DIR)\Scripts\activate && \
		echo Launching FastAPI server... && \
		python -m uvicorn API.main:app --reload \
	)"
else
api-run:
	@echo Starting FastAPI server on port 8000...
	@cmd /Q /C "( \
		call $(VENV_DIR)\Scripts\activate && \
		echo Launching FastAPI server... && \
		python -m uvicorn API.main:app --reload \
	)"
endif





# ===========================================
# Database Make Commands
# ===========================================

DB_NAME = course_gpt
DB_USER = postgres
DB_HOST = localhost
DB_PORT = 5432

# Paths to your SQL scripts
SCHEMA_FILE = DB/schema_database.sql
SEED_FILE = DB/seed_database.sql

# Detect OS
ifeq ($(OS),Windows_NT)
	UNAME_S := Windows
else
	UNAME_S := $(shell uname -s)
endif

# -------------------------------------------
# db-setup: Windows uses PowerShell, others use Bash
# -------------------------------------------
db-setup:
ifeq ($(UNAME_S),Windows)
	@echo Checking PostgreSQL installation...
	@powershell -ExecutionPolicy Bypass -File Script/install_postgres_windows.ps1
	@echo db-setup complete. Please restart PowerShell.
else ifeq ($(UNAME_S),Darwin)
	@echo "Checking PostgreSQL installation..."
	@bash scripts/install_postgres_mac.sh
	@echo "db-setup complete."
else
	@echo "Checking PostgreSQL installation..."
	@bash scripts/install_postgres_linux.sh
	@echo "db-setup complete."
endif

# -------------------------------------------
# Initialize database and schema (clean setup)
# -------------------------------------------
db-init:
	@echo Dropping existing database if it exists...
	psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -c "DROP DATABASE IF EXISTS $(DB_NAME)"
	@echo Creating new database...
	psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -c "CREATE DATABASE $(DB_NAME)"
	@echo Applying schema...
	psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d $(DB_NAME) -f $(SCHEMA_FILE)
	@echo Fresh database initialized successfully.


# -------------------------------------------
# Seed database with sample data
# -------------------------------------------
db-seed:
	@echo Seeding database with initial data...
	psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d $(DB_NAME) -f $(SEED_FILE)
	@echo Database seeded successfully.
