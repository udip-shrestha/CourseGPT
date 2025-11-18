import pytest
from fastapi import FastAPI, status, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from API.Routers.queries_router import router as queries_router
from API.Service.queries_service import QueryService


# -------------------------------
# Fixtures
# -------------------------------

@pytest.fixture
def mock_query_service() -> QueryService:
    """Provides a mocked QueryService instance."""
    return MagicMock(spec=QueryService)


@pytest.fixture
def client(mock_query_service: QueryService) -> TestClient:
    """Creates a test client with dependency overrides."""
    from API.dependencies import get_query_service, validate_course

    app = FastAPI()
    app.include_router(queries_router)

    app.dependency_overrides[get_query_service] = lambda: mock_query_service
    app.dependency_overrides[validate_course] = lambda: {"id": "c1", "rag_strategy_id": 1}

    return TestClient(app)


# -------------------------------
# Tests for POST /queries
# -------------------------------

def test_ask_question_success(client: TestClient, mock_query_service: QueryService):
    mock_query_service.ask_question.return_value = {
        "answer": "Hello!",
        "sources": ["s1"]
    }

    response = client.post(
        "/courses/c1/queries",
        params={"question": "Hello?", "student_id": "stu1"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"answer": "Hello!", "sources": ["s1"]}

    mock_query_service.ask_question.assert_called_once_with(
        course_id="c1",
        course={"id": "c1", "rag_strategy_id": 1},
        student_id="stu1",
        question="Hello?"
    )


# -------------------------------
# Tests for GET /queries
# -------------------------------

def test_get_course_queries_success(client: TestClient, mock_query_service: QueryService):
    mock_query_service.get_course_queries.return_value = {
        "total": 2,
        "queries": [{"id": "q1"}, {"id": "q2"}]
    }

    response = client.get("/courses/c1/queries")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 2

    mock_query_service.get_course_queries.assert_called_once_with(
        course_id="c1",
        limit=10,
        offset=0,
        order_by="asked_at",
        order_dir="desc",
    )


# -------------------------------
# Tests for GET /students/{student_id}/queries
# -------------------------------

def test_get_student_queries_success(client: TestClient, mock_query_service: QueryService):
    mock_query_service.get_student_queries.return_value = {
        "total": 1,
        "queries": [{"id": "q1"}]
    }

    response = client.get("/courses/c1/students/stu1/queries")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 1

    mock_query_service.get_student_queries.assert_called_once_with(
        course_id="c1",
        student_id="stu1",
        limit=10,
        offset=0,
        order_by="asked_at",
        order_dir="desc",
    )


# -------------------------------
# Tests for GET /queries/{query_id}
# -------------------------------

def test_read_query_success(client: TestClient, mock_query_service: QueryService):
    mock_query_service.get_query.return_value = {"id": "q1", "answer": "hi"}

    response = client.get("/courses/c1/queries/q1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == "q1"

    mock_query_service.get_query.assert_called_once_with("c1", "q1")


def test_read_query_not_found(client: TestClient, mock_query_service: QueryService):
    mock_query_service.get_query.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Query not found",
    )

    response = client.get("/courses/c1/queries/missing")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


# -------------------------------
# Tests for DELETE /queries/{query_id}
# -------------------------------

def test_delete_query_success(client: TestClient, mock_query_service: QueryService):
    mock_query_service.delete_query.return_value = {
        "status": "deleted",
        "course_id": "c1",
        "query_id": "q1",
    }

    response = client.delete("/courses/c1/queries/q1")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""

    mock_query_service.delete_query.assert_called_once_with("c1", "q1")


def test_delete_query_not_found(client: TestClient, mock_query_service: QueryService):
    mock_query_service.delete_query.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Query not found",
    )

    response = client.delete("/courses/c1/queries/missing")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()
