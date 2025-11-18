import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from API.Routers.auth_router import router as auth_router
from API.Service.auth_service import AuthService


@pytest.fixture
def mock_auth_service() -> AuthService:
    """Provides a mocked AuthService instance."""
    return MagicMock(spec=AuthService)


@pytest.fixture
def client(mock_auth_service: AuthService) -> TestClient:
    """Create a test client with dependency overrides."""
    from API.dependencies import get_auth_service

    app = FastAPI()
    app.include_router(auth_router)
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
    return TestClient(app)


def test_login_success(client: TestClient, mock_auth_service: AuthService):
    """Should authenticate successfully and return JWT token."""
    mock_auth_service.login.return_value = {
        "access_token": "fake.jwt.token",
        "token_type": "bearer"
    }

    response = client.post(
        "/auth/login",
        data={"username": "instructor@isu.edu", "password": "password123"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "access_token": "fake.jwt.token",
        "token_type": "bearer"
    }
    mock_auth_service.login.assert_called_once_with(
        instructor_email="instructor@isu.edu",
        instructor_password="password123"
    )


def test_login_invalid_credentials(client: TestClient, mock_auth_service: AuthService):
    """Should return 401 if credentials are invalid."""
    from fastapi import HTTPException

    mock_auth_service.login.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )

    response = client.post(
        "/auth/login",
        data={"username": "bad@isu.edu", "password": "wrong"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid" in response.json()["detail"]
    mock_auth_service.login.assert_called_once_with(
        instructor_email="bad@isu.edu",
        instructor_password="wrong"
    )


def test_login_missing_fields(client: TestClient):
    """Should fail validation when username/password missing."""
    response = client.post("/auth/login", data={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_register_success(client: TestClient, mock_auth_service: AuthService):
    """Should register instructor and return token."""
    mock_auth_service.register.return_value = {
        "access_token": "new.jwt.token",
        "token_type": "bearer"
    }

    response = client.post(
        "/auth/register",
        data={
            "name": "Dr. Jane Doe",
            "title": "Professor",
            "university": "Iowa State University",
            "email": "jane@isu.edu",
            "password": "securepass"
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["access_token"] == "new.jwt.token"
    mock_auth_service.register.assert_called_once_with(
        name="Dr. Jane Doe",
        title="Professor",
        university="Iowa State University",
        email="jane@isu.edu",
        password="securepass"
    )


def test_register_duplicate_email(client: TestClient, mock_auth_service: AuthService):
    """Should return 400 if email already exists."""
    from fastapi import HTTPException

    mock_auth_service.register.side_effect = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email already registered"
    )

    response = client.post(
        "/auth/register",
        data={
            "name": "Dr. John Doe",
            "title": "Professor",
            "university": "Tech University",
            "email": "john@tech.edu",
            "password": "pass123"
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already" in response.json()["detail"]
    mock_auth_service.register.assert_called_once_with(
        name="Dr. John Doe",
        title="Professor",
        university="Tech University",
        email="john@tech.edu",
        password="pass123"
    )


def test_register_missing_fields(client: TestClient):
    """Should fail validation when required fields missing."""
    response = client.post("/auth/register", data={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

