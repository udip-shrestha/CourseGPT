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
ifeq ($(OS),Windows_NT)
$(ACTIVATE_PATH):
	@echo Checking virtual environment...
	@if not exist "$(VENV_DIR)" ( \
		echo Virtual environment not found. Creating and installing dependencies... && \
		$(MAKE) install \
	) else ( \
		echo Virtual environment exists. \
	)
else
$(ACTIVATE_PATH):
	@echo "Checking virtual environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment not found. Creating and installing dependencies..."; \
		$(MAKE) install; \
	else \
		echo "Virtual environment exists."; \
	fi
endif

# -------------------------------------------
# Run API Tests with Coverage
# -------------------------------------------
ifeq ($(OS),Windows_NT)
api-coverage: $(ACTIVATE_PATH)
	@echo "Running API tests with coverage..."
	@cmd /C "( \
		set PYTHONPATH=. && \
		call $(VENV_DIR)\Scripts\activate && \
		pytest --cov=API --cov-report=term-missing --cov-report=xml --cov-report=html tests\\API -v \
	)"
else
api-coverage: $(ACTIVATE_PATH)
	@echo "Running API tests with coverage..."
	@bash -c "export PYTHONPATH=. && \
		source $(VENV_DIR)/bin/activate && \
		pytest --cov=API --cov-report=term-missing --cov-report=xml --cov-report=html tests/API -v"
endif


# ===========================================
# API Make Commands
# ===========================================

.PHONY: api-run api-test

# -------------------------------------------
# Run FastAPI backend
# -------------------------------------------
ifeq ($(OS),Windows_NT)
api-run: $(ACTIVATE_PATH)
	@echo "Launching FastAPI on http://$(API_HOST):$(API_PORT)"
	@cmd /C "( \
		call $(VENV_DIR)\Scripts\activate && \
		$(PYTHON) -m uvicorn API.main:app --host $(API_HOST) --port $(API_PORT) --reload --reload-dir $(API_RELOAD_DIR) \
	)"
else
api-run: $(ACTIVATE_PATH)
	@echo "Launching FastAPI on http://$(API_HOST):$(API_PORT)"
	@bash -c "source $(VENV_DIR)/bin/activate && \
		$(PYTHON) -m uvicorn API.main:app --host $(API_HOST) --port $(API_PORT) --reload --reload-dir $(API_RELOAD_DIR)"
endif

# -------------------------------------------
# Run API Tests
# -------------------------------------------
ifeq ($(OS),Windows_NT)
api-test: $(ACTIVATE_PATH)
	@echo "Running API tests..."
	@cmd /C "( \
		set PYTHONPATH=. && \
		call $(VENV_DIR)\Scripts\activate && \
		pytest tests\\API -v \
	)"
else
api-test: $(ACTIVATE_PATH)
	@echo "Running API tests..."
	@bash -c "export PYTHONPATH=. && \
		source $(VENV_DIR)/bin/activate && \
		pytest tests/API -v"
endif






# ===========================================
# Database Make Commands
# ===========================================

.PHONY: db-setup db-init db-seed db-shell db-deploy

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
	@bash Script/install_postgres_mac.sh
	@echo "db-setup complete."
else
	@echo "Checking PostgreSQL installation..."
	@bash Script/install_postgres_linux.sh
	@echo "db-setup complete."
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

# -------------------------------------------
# Deploy database (create if missing, keep data intact)
# -------------------------------------------
ifeq ($(OS),Windows_NT)
db-deploy:
	@echo "Checking if database $(DB_NAME) exists..."
	@psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$(DB_NAME)'" | findstr 1 >NUL 2>&1 && \
		echo "Database $(DB_NAME) already exists: skipping creation." || ( \
			echo "Creating database $(DB_NAME)..." && \
			psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d postgres -c "CREATE DATABASE $(DB_NAME)" )
	@echo "Applying schema to $(DB_NAME)..."
	@psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d $(DB_NAME) -f $(SCHEMA_FILE)
	@echo "Database deployed successfully."
else
db-deploy:
	@echo "Checking if database $(DB_NAME) exists..."
	@psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$(DB_NAME)'" | grep -q 1 && \
		echo "Database $(DB_NAME) already exists — skipping creation." || ( \
			echo "Creating database $(DB_NAME)..." && \
			psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d postgres -c "CREATE DATABASE $(DB_NAME)" )
	@echo "Applying schema to $(DB_NAME)..."
	@psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d $(DB_NAME) -f $(SCHEMA_FILE)
	@echo "Database deployed successfully."
endif
