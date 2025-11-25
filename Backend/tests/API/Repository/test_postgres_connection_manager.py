import subprocess
import sys
import uuid
import pytest
import testing.postgresql
from API.Repository.postgres_connection_manager import PostgresConnectionManager


@pytest.fixture
def pg_instance():
    """Standalone ephemeral PostgreSQL instance JUST for these tests."""
    pg = testing.postgresql.Postgresql()
    yield pg
    try:
        pg.stop()
    except:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pg.child_process.pid)], capture_output=True)
            pg.child_process.returncode = 0
            pg._owner = None
        pg.stop()


@pytest.fixture
def cm(pg_instance):
    """
    A fresh PostgresConnectionManager per test.
    This avoids using the global connection_manager from project conftest.
    """
    mgr = PostgresConnectionManager(pg_instance.url())
    yield mgr
    mgr.close_all()


@pytest.fixture
def ensure_items_table(cm):
    """Create a simple test table for these tests."""
    cm.execute("""
        CREATE EXTENSION IF NOT EXISTS pgcrypto;
    """)

    cm.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL
        );
    """)
    yield
    cm.execute("DROP TABLE IF EXISTS items;")


@pytest.fixture
def clean_items(cm, ensure_items_table):
    """Ensure table is empty before and after each test."""
    cm.execute("TRUNCATE items;")
    yield
    cm.execute("TRUNCATE items;")


def test_database_available_true(cm, pg_instance):
    assert cm.database_available(pg_instance.url()) is True


def test_database_available_false():
    mgr = PostgresConnectionManager("postgres://invalid-url")
    assert mgr.database_available("postgres://invalid-url") is False


def test_get_connection_success(cm):
    with cm.get_connection() as conn:
        assert conn is not None
        cur = conn.cursor()
        assert cur is not None


def test_get_connection_no_pool(pg_instance):
    mgr = PostgresConnectionManager(pg_instance.url())
    mgr.pool = None  # simulate missing pool
    with pytest.raises(ConnectionError):
        mgr.get_connection()


def test_insert_one_roundtrip(cm, clean_items):
    new_id = cm.insert_one(
        "INSERT INTO items (name) VALUES (%s) RETURNING id",
        ("Alpha",),
    )

    assert isinstance(new_id, str)
    uuid.UUID(new_id)  # verify valid uuid

    row = cm.select_one(
        "SELECT name FROM items WHERE id = %s",
        (new_id,),
    )
    assert row["name"] == "Alpha"


def test_insert_one_rollback_on_error(cm, clean_items):
    # missing NOT NULL field (name)
    with pytest.raises(Exception):
        cm.insert_one(
            "INSERT INTO items (name) VALUES (%s) RETURNING id",
            (None,),  # name is NOT NULL
        )

    # ensure table is still empty
    rows = cm.select_all("SELECT * FROM items;")
    assert rows == []


def test_select_one(cm, clean_items):
    new_id = cm.insert_one(
        "INSERT INTO items (name) VALUES (%s) RETURNING id",
        ("Bravo",),
    )

    row = cm.select_one("SELECT id, name FROM items WHERE id = %s", (new_id,))
    assert row["name"] == "Bravo"
    assert str(row["id"]) == new_id


def test_select_all(cm, clean_items):
    names = ["C1", "C2", "C3"]
    for n in names:
        cm.insert_one(
            "INSERT INTO items (name) VALUES (%s) RETURNING id",
            (n,),
        )

    rows = cm.select_all("SELECT name FROM items ORDER BY name ASC;")
    assert [r["name"] for r in rows] == sorted(names)


def test_execute_update(cm, clean_items):
    new_id = cm.insert_one(
        "INSERT INTO items (name) VALUES (%s) RETURNING id",
        ("Original",),
    )

    cm.execute(
        "UPDATE items SET name = %s WHERE id = %s",
        ("Updated", new_id),
    )

    row = cm.select_one("SELECT name FROM items WHERE id = %s", (new_id,))
    assert row["name"] == "Updated"


def test_execute_rollback_on_error(cm, clean_items):
    new_id = cm.insert_one(
        "INSERT INTO items (name) VALUES (%s) RETURNING id",
        ("KeepMe",),
    )

    with pytest.raises(Exception):
        cm.execute(
            "UPDATE items SET name = %s WHERE id = %s",
            (None, new_id),  # name is NOT NULL
        )

    row = cm.select_one("SELECT name FROM items WHERE id = %s", (new_id,))
    assert row["name"] == "KeepMe"


def test_close_all(cm):
    """
    Simply ensure close_all() does not error.
    We don't need to assert internal pool state.
    """
    cm.close_all()
