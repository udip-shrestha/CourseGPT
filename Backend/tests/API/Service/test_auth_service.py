import pytest
from fastapi import HTTPException, status
from unittest.mock import patch
from API.Service.auth_service import AuthService
from API.Repository.i_sql_repository import ISQLRepository


def test_login_success(auth_service: AuthService, mock_sql_repo: ISQLRepository):
    """Should authenticate instructor and return access token."""
    mock_sql_repo.read_instructor_by_email.return_value = {"id": "inst-1", "password": "hashed-pw"}

    with patch("API.Service.auth_service.verify_password", return_value=True) as mock_verify, \
         patch("API.Service.auth_service.encrypt_access_token", return_value="mock-token") as mock_encrypt:
        result = auth_service.login("user@isu.edu", "plainpass")

    mock_sql_repo.read_instructor_by_email.assert_called_once_with("user@isu.edu")
    mock_verify.assert_called_once_with("hashed-pw", "plainpass")
    mock_encrypt.assert_called_once_with({"id": "inst-1"})
    assert result == {"access_token": "mock-token", "token_type": "bearer", "instructor_id": "inst-1"}


def test_login_email_not_found(auth_service: AuthService, mock_sql_repo: ISQLRepository):
    """Should raise 404 if email not found."""
    mock_sql_repo.read_instructor_by_email.return_value = None
    with pytest.raises(HTTPException) as exc_info: auth_service.login("notfound@isu.edu", "pass")
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc_info.value.detail.lower()


def test_login_incorrect_password(auth_service: AuthService, mock_sql_repo: ISQLRepository):
    """Should raise 401 if password is incorrect."""
    mock_sql_repo.read_instructor_by_email.return_value = {"id": "inst-2", "password": "hashed"}

    with patch("API.Service.auth_service.verify_password", return_value=False) as mock_verify, \
         pytest.raises(HTTPException) as exc_info:
        auth_service.login("user@isu.edu", "wrongpw")

    mock_verify.assert_called_once_with("hashed", "wrongpw")
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "incorrect" in exc_info.value.detail.lower()


def test_register_success(auth_service: AuthService, mock_sql_repo: ISQLRepository):
    """Should register new instructor and return token."""
    mock_sql_repo.read_instructor_by_email.return_value = None
    mock_sql_repo.create_instructor.return_value = "inst-3"

    with patch("API.Service.auth_service.encrypt_password", return_value="hashed-pass") as mock_encrypt_pw, \
         patch("API.Service.auth_service.encrypt_access_token", return_value="mock-token") as mock_encrypt_token:
        result = auth_service.register("Jane", "Professor", "ISU", "jane@isu.edu", "mypw")

    mock_sql_repo.read_instructor_by_email.assert_called_once_with("jane@isu.edu")
    mock_encrypt_pw.assert_called_once_with("mypw")
    mock_sql_repo.create_instructor.assert_called_once_with(
        name="Jane", title="Professor", university="ISU", email="jane@isu.edu", encrypted_password="hashed-pass"
    )
    mock_encrypt_token.assert_called_once_with({"id": "inst-3"})
    assert result == {"access_token": "mock-token", "token_type": "bearer", "instructor_id": "inst-3"}


def test_register_duplicate_email(auth_service: AuthService, mock_sql_repo: ISQLRepository):
    """Should raise 400 if email already registered."""
    mock_sql_repo.read_instructor_by_email.return_value = {"id": "existing"}
    with pytest.raises(HTTPException) as exc_info: auth_service.register("John", "Prof", "ISU", "john@isu.edu", "pw")
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "registered" in exc_info.value.detail.lower()
