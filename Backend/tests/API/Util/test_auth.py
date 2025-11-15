import pytest
import jwt
import importlib
from datetime import timedelta, datetime, timezone
from API.Util import auth  # adjust this import to match your project structure



def test_encrypt_and_verify_password_roundtrip():
    """Should hash password and verify it correctly."""
    password = "super_secret_password"

    hashed = auth.encrypt_password(password)
    assert hashed != password  # hash should not equal plain password

    assert auth.verify_password(hashed, password) is True
    assert auth.verify_password(hashed, "wrong_password") is False


def test_encrypt_access_token_and_decrypt_success(monkeypatch):
    """Should create and decode a valid JWT token successfully."""
    # Mock environment variables for test
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")

    importlib.reload(auth)  # reload to pick up env vars

    payload = {"sub": "user-123", "role": "instructor"}

    token = auth.encrypt_access_token(payload.copy())
    decoded = auth.decrypt_access_token(token)

    assert decoded["sub"] == "user-123"
    assert decoded["role"] == "instructor"
    assert "exp" in decoded


def test_encrypt_access_token_respects_expiration(monkeypatch):
    """Should respect custom expiration delta."""
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    importlib.reload(auth)

    short_exp = timedelta(seconds=1)
    payload = {"sub": "short-lived"}

    token = auth.encrypt_access_token(payload.copy(), expires_delta=short_exp)
    decoded = jwt.decode(token, "test-secret", algorithms=["HS256"])

    exp_timestamp = int(decoded["exp"])
    expected_range = int(datetime.now(timezone.utc).timestamp()) + 1
    assert abs(exp_timestamp - expected_range) < 3  # should be ~1 second ahead


def test_decrypt_access_token_invalid_signature(monkeypatch):
    """Should raise InvalidSignatureError when decoded with wrong secret."""
    monkeypatch.setenv("JWT_SECRET_KEY", "correct-secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    importlib.reload(auth)

    valid_token = auth.encrypt_access_token({"sub": "valid-user"})

    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(valid_token, "wrong-secret", algorithms=["HS256"])


def test_decrypt_access_token_expired(monkeypatch):
    """Should raise ExpiredSignatureError for expired tokens."""
    monkeypatch.setenv("JWT_SECRET_KEY", "expired-secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    importlib.reload(auth)

    expired_token = jwt.encode(
        {"sub": "old-user", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
        "expired-secret",
        algorithm="HS256"
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        auth.decrypt_access_token(expired_token)


def test_decrypt_access_token_malformed(monkeypatch):
    """Should raise DecodeError for malformed token."""
    monkeypatch.setenv("JWT_SECRET_KEY", "secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    importlib.reload(auth)

    malformed_token = "not.a.jwt"

    with pytest.raises(jwt.DecodeError):
        auth.decrypt_access_token(malformed_token)
