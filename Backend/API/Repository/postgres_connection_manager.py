import threading
from typing import Any, Dict, List, Optional, Tuple
import psycopg
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
import logging


class PostgresConnectionManager:
    """
    PostgreSQL connection pool manager.
    Provides safe, typed query helpers with rollback on error.

    ---------------------------------------------------------------------------
    Helper Summary
    ---------------------------------------------------------------------------
    • insert_one(sql, params)       → Execute an INSERT ... RETURNING id statement
                                  and return the generated UUID string.

    • select_one(sql, params)   → Execute a SELECT query expected to return a
                                  single row (returns dict or None).

    • select_all(sql, params)   → Execute a SELECT query returning multiple rows
                                  as a list of dicts.

    • execute(sql, params)      → Execute any non-returning SQL statement such
                                  as INSERT (without RETURNING), UPDATE, DELETE,
                                  or DDL statements (CREATE/DROP TABLE, etc).

    • close_all()               → Gracefully close all pooled connections.
    """

    def __init__(self, db_url: str) -> None:
        self.db_url: str = db_url
        self.logger: logging.Logger = logging.getLogger(__name__)

        # So app doesnt crash if DB is not setup
        if self.database_available(db_url):
            self.pool: ConnectionPool = ConnectionPool(
                conninfo=db_url,
                min_size=1,
                max_size=10,
                timeout=10,
                open=True
            )
        else:
            self.pool = None
            self.logger.warning("Database not available - running without Postgres.")

    def database_available(self, db_url: str) -> bool:
        try:
            with psycopg.connect(db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Postgres: {e}")
            return False

    def get_connection(self):
        """Get a connection from the pool (usable with context manager)."""
        
        # So app doesnt crash if DB is not setup
        if self.pool is None:
            raise ConnectionError("Postgres not connected")
    
        return self.pool.connection()

    def insert_one(self, sql: str, params: Tuple[Any, ...] = ()) -> str:
        with self.get_connection() as conn, conn.cursor() as cur:
            try:
                cur.execute(sql, params)
                conn.commit()
                result = cur.fetchone()
                return str(result[0])
            except Exception as e:
                conn.rollback()
                self._log_db_error(e, sql)
                raise

    def select_one(self, sql: str, params: Tuple[Any, ...] = ()) -> Optional[Dict[str, Any]]:
        """Execute a SELECT query and return one row as a dict (or None if not found)."""
        with self.get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            try:
                cur.execute(sql, params)
                return cur.fetchone()
            except Exception as e:
                self._log_db_error(e, sql)
                raise

    def select_all(self, sql: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return all rows as a list of dicts."""
        with self.get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            try:
                cur.execute(sql, params)
                return cur.fetchall()
            except Exception as e:
                self._log_db_error(e, sql)
                raise

    def execute(self, sql: str, params: Tuple[Any, ...] = ()) -> None:
        """Execute a non-returning query (UPDATE/DELETE)."""
        with self.get_connection() as conn, conn.cursor() as cur:
            try:
                cur.execute(sql, params)
                conn.commit()
            except Exception as e:
                conn.rollback()
                self._log_db_error(e, sql)
                raise

    def close_all(self) -> None:
        """Close all connections in the pool."""
        if self.pool is not None:
            self.pool.close()

    def _log_db_error(self, error: Exception, sql: str) -> None:
        """Log database errors consistently for debugging."""
        msg: str = getattr(error, "pgerror", str(error))
        self.logger.error(f"[Postgres Error] {msg}")
        self.logger.debug(f"SQL: {sql}")
