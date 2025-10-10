## Running API Backend

### Setup and Installation

Before running the FastAPI backend, make sure you’ve installed or updated all dependencies.
Run this whenever you:

-   Pull new changes from GitHub (`git pull`), or
-   Add or modify dependencies in `API/requirements.txt`

```
make api-install
```

### Running the FastAPI Server

Once dependencies are installed, start the backend with:

```bash
make api-run
```

### Running Tests

To verify that all repository and service logic works correctly, run the automated tests:

```
make api-test
```

## Database Setup

### Prerequisites

Make sure you have:

-   **Make** installed (for running setup commands)

### Step 1: Install PostgreSQL

```
make db-setup
```

### Step 2: Initialize Database and Schema

```
make db-init
```

### Step 3: Seed Development Data

```
make db-seed
```

### **Step 4 (Optional): Open Database Shell**

This opens the interactive PostgreSQL shell connected to your `course_gpt` database. Inside the shell, you can verify your tables were created successfully by running `\dt`.

```bash
make db-shell
```

**Note:** For local default password for postgres is `postgres`
