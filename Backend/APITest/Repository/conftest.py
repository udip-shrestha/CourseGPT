import os
import uuid
import pytest
import testing.postgresql
from API.Repository.postgres_connection_manager import PostgresConnectionManager
from API.Repository.sql_repository import SQLRepository


@pytest.fixture(scope="session")
def postgres_instance():
    """Start an ephemeral PostgreSQL instance for repository tests."""
    pg = testing.postgresql.Postgresql()
    yield pg
    try:
        pg.stop()
    except ValueError:
        pass  # ignore unsupported signal errors on Windows


@pytest.fixture(scope="session")
def connection_manager(postgres_instance):
    """Provide a real Postgres connection manager for repo tests."""
    cm = PostgresConnectionManager(db_url=postgres_instance.url())
    yield cm
    cm.close_all()


@pytest.fixture(scope="session", autouse=True)
def setup_test_schema(connection_manager):
    """Run real schema initialization SQL once per session."""
    schema_path = os.path.join("DB", "schema_database.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    connection_manager.execute(schema_sql)
    yield
    connection_manager.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")

@pytest.fixture(autouse=True)
def clean_tables(connection_manager):
    """
    Clear all non-enum data between tests without dropping schema.
    """
    yield
    connection_manager.execute("""
        TRUNCATE TABLE
            documents,
            student_courses,
            queries,
            courses,
            students,
            instructors
        RESTART IDENTITY CASCADE;
    """)

@pytest.fixture
def repo(connection_manager):
    """Return a SQLRepository instance wired to the test database."""
    return SQLRepository(connection_manager)

@pytest.fixture
def temp_course(connection_manager):
    """Insert a temporary course record and return its UUID."""
    course_id = str(uuid.uuid4())
    sql = """
        INSERT INTO courses (id, name, institution, year, semester_id)
        VALUES (%s, %s, %s, %s, %s)
    """
    connection_manager.execute(sql, (course_id, "Temp Course", "Test U", 2025, 1))
    return course_id