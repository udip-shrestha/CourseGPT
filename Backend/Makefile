# ===========================================
# Require .env file
# ===========================================
ifeq (,$(wildcard .env))
$(error .env file not found! Please create one in the project root before running Make.)
endif

include .env
export





# ===========================================
# Variable Definition
# ===========================================
ifeq ($(OS),Windows_NT)
	UNAME_S := Windows
	ACTIVATE_PATH := $(VENV_DIR)/Scripts/activate
	PYTHON := python
else
	UNAME_S := $(shell uname -s)
	ACTIVATE_PATH := $(VENV_DIR)/bin/activate
	PYTHON := python3
endif

ifeq ($(UNAME_S),Darwin)
    DB_USER := $(shell whoami)
endif





# ===========================================
# Default Target - Show available commands
# ===========================================

.PHONY: help

help:
	@echo ""
	@echo "Available Make Commands:"
	@echo "-------------------------------------------"
	@echo "make help       -> Show this help message"
	@echo ""
	@echo "make install    -> Install backend dependencies"
	@echo ""
	@echo "make api-run    -> Launch FastAPI backend on $${API_HOST}:$${API_PORT}"
	@echo "make api-test   -> Run all API tests with pytest"
	@echo ""
	@echo "make db-setup   -> Install PostgreSQL"
	@echo "make db-init    -> Drop, create, and initialize a fresh database"
	@echo "make db-seed    -> Populate database with sample data"
	@echo "make db-shell   -> Open interactive PostgreSQL shell"
	@echo "make db-deploy  -> Create database if missing, preserve data"
	@echo "-------------------------------------------"
	@echo ""





# ===========================================
# VENV Make Commands
# ===========================================

.PHONY: create-venv install

# -----------------------------------
# Create venv if missing
# -----------------------------------
ifeq ($(wildcard $(VENV_DIR)),)
create-venv:
	@echo Creating virtual environment...
	$(PYTHON) -m venv $(VENV_DIR)
else
create-venv:
	@echo Virtual environment already exists.
endif

# -----------------------------------
# Install dependencies if requirements.txt exists
# -----------------------------------
ifeq ($(wildcard $(REQ_FILE)),)
install:
	@echo ERROR: requirements.txt not found in API directory. && exit 1
else
install: create-venv
ifeq ($(OS),Windows_NT)
	@echo "Activating virtual environment and installing dependencies..."
	@cmd /C "( \
		call $(VENV_DIR)\Scripts\activate && \
		$(PYTHON) -m pip install -r $(REQ_FILE) \
	)"
else
	@echo "Activating virtual environment and installing dependencies..."
	@bash -c "source $(VENV_DIR)/bin/activate && \
		$(PYTHON) -m pip install --upgrade pip && \
		$(PYTHON) -m pip install -r $(REQ_FILE)"
endif
endif

# -------------------------------------------
# Ensure venv exists (cross-platform)
# -------------------------------------------
ifeq ($(wildcard $(ACTIVATE_PATH)),)
ensure-activate:
ifeq ($(OS),Windows_NT)
	@echo "Virtual environment not found. Creating and installing dependencies..."
	@$(MAKE) install
else
	@echo "Virtual environment not found. Creating and installing dependencies..."
	@$(MAKE) install
endif
else
ensure-activate:
	@echo "Found virtual environment."
endif





# ===========================================
# API Make Commands
# ===========================================

.PHONY: api-run api-run-8 api-test api-coverage

# -------------------------------------------
# Run FastAPI backend
# -------------------------------------------
ifeq ($(OS),Windows_NT)
api-run: ensure-activate
	@echo "Launching FastAPI on http://$(API_HOST):$(API_PORT)"
	@cmd /C "( \
		call $(VENV_DIR)\Scripts\activate && \
		$(PYTHON) -m uvicorn API.main:app --host $(API_HOST) --port $(API_PORT) --reload --reload-dir $(API_RELOAD_DIR) \
	)"
else
api-run: ensure-activate
	@echo "Launching FastAPI on http://$(API_HOST):$(API_PORT)"
	@bash -c "source $(VENV_DIR)/bin/activate && \
		$(PYTHON) -m uvicorn API.main:app --host $(API_HOST) --port $(API_PORT) --reload --reload-dir $(API_RELOAD_DIR)"
endif

# -------------------------------------------
# Run FastAPI backend with 8 workers
# -------------------------------------------
ifeq ($(OS),Windows_NT)
api-run-8: ensure-activate
	@echo "Launching FastAPI with 8 workers on http://$(API_HOST):$(API_PORT)"
	@cmd /C "( \
		call $(VENV_DIR)\Scripts\activate && \
		$(PYTHON) -m uvicorn API.main:app --host $(API_HOST) --port $(API_PORT) --workers 8 \
	)"
else
api-run-8: ensure-activate
	@echo "Launching FastAPI with 8 workers on http://$(API_HOST):$(API_PORT)"
	@bash -c "source $(VENV_DIR)/bin/activate && \
		$(PYTHON) -m uvicorn API.main:app --host $(API_HOST) --port $(API_PORT) --workers 8"
endif

# -------------------------------------------
# Run API Tests
# -------------------------------------------
ifeq ($(OS),Windows_NT)
api-test: ensure-activate
	@echo "Running API tests..."
	@cmd /C "( \
		set PYTHONPATH=. && \
		call $(VENV_DIR)\Scripts\activate && \
		pytest tests\\API -v  \
			--override-ini=asyncio_default_fixture_loop_scope=function \
			--override-ini=asyncio_mode=auto \
			--override-ini=addopts= \
	)"
else
api-test: ensure-activate
	@echo "Running API tests..."
	@bash -c "export PYTHONPATH=. && \
		source $(VENV_DIR)/bin/activate && \
		pytest tests/API -v --override-ini=asyncio_default_fixture_loop_scope=function --override-ini=asyncio_mode=auto --override-ini=addopts= "
endif

# -------------------------------------------
# Run API Tests with Coverage
# -------------------------------------------
ifeq ($(OS),Windows_NT)
api-coverage: ensure-activate
	@echo "Running API tests with coverage..."
	@cmd /C "( \
		set PYTHONPATH=. && \
		call $(VENV_DIR)\Scripts\activate && \
		pytest tests\\API -v --override-ini="addopts=" --cov=API --cov-report=term-missing --cov-report=xml --cov-report=html \
			--override-ini=asyncio_default_fixture_loop_scope=function \
			--override-ini=asyncio_mode=auto \
			--override-ini=addopts= \
	)"
else
api-coverage: ensure-activate
	@echo "Running API tests with coverage..."
	@bash -c "export PYTHONPATH=. && \
		source $(VENV_DIR)/bin/activate && \
		pytest tests/API -v --override-ini="addopts=" --cov=API --cov-report=term-missing --cov-report=xml --cov-report=html --override-ini=asyncio_default_fixture_loop_scope=function --override-ini=asyncio_mode=auto --override-ini=addopts= "
endif





# ===========================================
# Database Make Commands
# ===========================================

.PHONY: db-setup db-init db-seed db-shell

# -------------------------------------------
# db-setup: Windows uses PowerShell, others use Bash
# -------------------------------------------
db-setup:
ifeq ($(UNAME_S),Windows)
	@echo Checking PostgreSQL installation...
	@powershell -ExecutionPolicy Bypass -File Script/install_postgres_windows.ps1
	@echo db-setup complete. Please restart PowerShell.
else ifneq ($(CODESPACES),)
	@echo "Detected GitHub Codespace environment..."
	@bash Script/install_postgres_codespace.sh
	@echo "db-setup complete (Codespaces)."
else ifeq ($(UNAME_S),Darwin)
	@echo "Checking PostgreSQL installation..."
	@bash Script/install_postgres_mac.sh
	@echo "db-setup complete (macOS)."
else
	@echo "Checking PostgreSQL installation..."
	@bash Script/install_postgres_linux.sh
	@echo "db-setup complete (Linux)."
endif

# -------------------------------------------
# Initialize database and schema (clean setup)
# -------------------------------------------
db-init:
	@echo Dropping existing database if it exists...
	psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d postgres -c "DROP DATABASE IF EXISTS $(DB_NAME)"
	@echo Creating new database...
	psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d postgres -c "CREATE DATABASE $(DB_NAME)"
	@echo Applying schema...
	psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d $(DB_NAME) -f $(SCHEMA_FILE)
	@echo "Fresh database initialized successfully."

# -------------------------------------------
# Seed database with sample data
# -------------------------------------------
db-seed:
	@echo Seeding database with initial data...
	psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d $(DB_NAME) -f $(SEED_FILE)
	@echo Database seeded successfully.

# -------------------------------------------
# Open interactive PostgreSQL shell
# -------------------------------------------
db-shell:
	@echo "Connecting to PostgreSQL database '$(DB_NAME)'..."
	psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d $(DB_NAME)





# ===========================================
# Database Migration Commands (Export -> Load -> Import)
# ===========================================

.PHONY: db-dump-old db-load-old db-import-new migrate

# ---------------------------------------------------------
# Step 1: Export OLD schema data into LOAD_OLD_DATA_SCRIPT
# ---------------------------------------------------------
db-dump-old:
	@echo "=============================================="
	@echo " Exporting OLD database data -> $(LOAD_OLD_DATA_SCRIPT)"
	@echo "=============================================="
	psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d $(DB_NAME) \
		-f $(EXPORT_OLD_DATA_SCRIPT) > $(LOAD_OLD_DATA_SCRIPT)
	@echo "Export complete: $(LOAD_OLD_DATA_SCRIPT)"
	@echo ""

# ---------------------------------------------------------
# Step 2: Load OLD data (INSERTs) into temporary old_* tables
# ---------------------------------------------------------
db-load-old:
	@echo "=============================================="
	@echo " Loading exported OLD data -> temporary old_* tables"
	@echo "=============================================="
	psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d $(DB_NAME) \
		-f $(LOAD_OLD_DATA_SCRIPT)
	@echo "Old data loaded successfully."
	@echo ""

# ---------------------------------------------------------
# Step 3: Import old_* -> new schema (transform + insert)
# ---------------------------------------------------------
db-move-old:
	@echo "=============================================="
	@echo " Importing OLD data → NEW schema"
	@echo "=============================================="
	psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d $(DB_NAME) \
		-f $(IMPORT_OLD_DATA_SCRIPT)
	@echo "New schema imported successfully."
	@echo ""

# ---------------------------------------------------------
# Full migration pipeline (recommended)
# ---------------------------------------------------------
db-migrate:
	@echo "=============================================="
	@echo " FULL DB MIGRATION PIPELINE"
	@echo " Steps:"
	@echo "   1) db-dump-old     -> Export old schema data"
	@echo "   2) db-init         -> Reset DB using NEW schema"
	@echo "   3) db-load-old     -> Load old_* rows"
	@echo "   4) db-move-old   -> Import + transform → new tables"
	@echo "=============================================="
	$(MAKE) db-dump-old
	$(MAKE) db-init
	$(MAKE) db-load-old
	$(MAKE) db-move-old
	$(MAKE) db-seed
	@echo "=============================================="
	@echo " Migration completed successfully!"
	@echo "=============================================="

