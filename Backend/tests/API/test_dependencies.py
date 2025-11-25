import os
import sys
import subprocess
import pytest
import testing.postgresql
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

import API.dependencies as deps

from API.Repository.sql_repository import SQLRepository
from API.Repository.chroma_vector_repository import ChromaVectorRepository
from API.Repository.postgres_connection_manager import PostgresConnectionManager
from API.Service.document_service import DocumentService
from API.Service.queries_service import QueryService
from API.Service.rag_service import RAGService
from API.Util.web_socket_manager import WebSocketManager
from API.Util.loaders import ILoader, TXTLoader
from API.Util.rag_strategy import IRAGStrategy, SimpleRAGStrategy


# ----------------------------------------------------------------------
# GLOBAL ENVIRONMENT OVERRIDES
# ----------------------------------------------------------------------
@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "testdb")
    monkeypatch.setenv("DB_USER", "user")
    monkeypatch.setenv("DB_PASSWORD", "pass")
    monkeypatch.setenv("CHROMA_DATA_PATH", "/tmp/chroma")
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("LLM_MODEL", "llama3")
    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:11434")


# ----------------------------------------------------------------------
# EPHEMERAL POSTGRES FIXTURE
# ----------------------------------------------------------------------
@pytest.fixture(scope="session")
def test_postgres_instance():
    """Start an ephemeral PostgreSQL instance for repository tests."""
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


# ----------------------------------------------------------------------
# TEST get_connection_manager() wiring using ephemeral DB
# ----------------------------------------------------------------------
def test_get_connection_manager_use_ephemeral_db(monkeypatch, test_postgres_instance):
    dsn = test_postgres_instance.dsn()

    dbname = dsn.get("dbname", dsn.get("database"))  # Windows uses "database"

    monkeypatch.setenv("DB_HOST", dsn["host"])
    monkeypatch.setenv("DB_PORT", str(dsn["port"]))
    monkeypatch.setenv("DB_NAME", dbname)
    monkeypatch.setenv("DB_USER", dsn["user"])
    monkeypatch.setenv("DB_PASSWORD", "")

    deps.get_connection_manager.cache_clear()
    cm = deps.get_connection_manager()

    with cm.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        assert cur.fetchone()[0] == 1


# ----------------------------------------------------------------------
# BASIC FACTORY TESTS
# ----------------------------------------------------------------------
def test_get_sql_repository():
    repo = deps.get_sql_repository()
    assert isinstance(repo, SQLRepository)


def test_get_vector_repository():
    repo = deps.get_vector_repository()
    assert isinstance(repo, ChromaVectorRepository)


# ----------------------------------------------------------------------
# TEST LOADER FACTORY (mocked)
# ----------------------------------------------------------------------
def test_get_loader_factory(monkeypatch):
    mock_sql = MagicMock()
    mock_sql.read_all_file_types.return_value = [
        {"mime_type": "text/plain", "class_name": "TXTLoader"},
    ]

    deps.get_loader_factory.cache_clear()
    factory = deps.get_loader_factory(sql_repo=mock_sql)

    loader = factory.get("text/plain")
    assert isinstance(loader, ILoader)
    assert isinstance(loader, TXTLoader)


# ----------------------------------------------------------------------
# TEST RAG STRATEGY FACTORY (mocked)
# ----------------------------------------------------------------------
def test_get_rag_strategy_factory(monkeypatch):
    mock_sql = MagicMock()
    mock_sql.read_all_rag_strategies.return_value = [
        {"id": 1, "class_name": "SimpleRAGStrategy"},
    ]

    deps.get_rag_strategy_factory.cache_clear()
    factory = deps.get_rag_strategy_factory(sql_repo=mock_sql)

    strat = factory.get("1")
    assert isinstance(strat, IRAGStrategy)
    assert isinstance(strat, SimpleRAGStrategy)


# ----------------------------------------------------------------------
# LLM (OLLAMA) TEST
# ----------------------------------------------------------------------
def test_get_llm_ollama():
    llm = deps.get_llm()

    from langchain_ollama import ChatOllama
    assert isinstance(llm, ChatOllama)


# ----------------------------------------------------------------------
# SERVICE FACTORY TESTS
# ----------------------------------------------------------------------
def test_get_rag_service():
    svc = deps.get_rag_service()
    assert isinstance(svc, RAGService)


def test_get_document_service():
    svc = deps.get_document_service()
    assert isinstance(svc, DocumentService)


def test_get_query_service():
    svc = deps.get_query_service()
    assert isinstance(svc, QueryService)


# ----------------------------------------------------------------------
# WEBSOCKET MANAGER TEST
# ----------------------------------------------------------------------
def test_get_web_socket_manager():
    m1 = deps.get_web_socket_manager()
    m2 = deps.get_web_socket_manager()
    assert isinstance(m1, WebSocketManager)
    assert m1 is m2


# ----------------------------------------------------------------------
# AUTHORIZATION TESTS
# ----------------------------------------------------------------------
def test_authorize_success(monkeypatch):
    mock_sql = MagicMock()
    mock_sql.read_instructor.return_value = {"id": "abc", "role": "ADMIN"}

    monkeypatch.setattr(deps, "decrypt_access_token", lambda tok: {"id": "abc"})

    auth = deps.authorize(token="VALID", sql_repo=mock_sql)
    assert auth["id"] == "abc"


def test_authorize_missing_token():
    with pytest.raises(HTTPException) as e:
        deps.authorize(token="")
    assert e.value.status_code == 401


def test_authorize_invalid_token(monkeypatch):
    monkeypatch.setattr(
        deps,
        "decrypt_access_token",
        lambda _: (_ for _ in ()).throw(Exception("bad token"))
    )

    with pytest.raises(HTTPException) as e:
        deps.authorize(token="INVALID")
    assert e.value.status_code == 401


def test_authorize_instructor_forbidden():
    with pytest.raises(HTTPException) as e:
        deps.authorize_instructor(
            instructor_id="X",
            auth={"id": "Y", "role": "INSTRUCTOR"},
        )
    assert e.value.status_code == 403


def test_authorize_admin():
    out = deps.authorize_admin({"id": "1", "role": "ADMIN"})
    assert out["role"] == "ADMIN"


def test_validate_course_not_found():
    mock_sql = MagicMock()
    mock_sql.read_course.return_value = None

    with pytest.raises(HTTPException) as e:
        deps.validate_course("course-1", sql_repo=mock_sql)

    assert e.value.status_code == 404
