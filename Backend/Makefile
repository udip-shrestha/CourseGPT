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
