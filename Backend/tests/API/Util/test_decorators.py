import pytest
import logging
from fastapi import HTTPException, status
from API.Util.decorators import clean_service  # adjust import to match your project path


# ============================================================
# Dummy service class for testing
# ============================================================
class DummyService:
    @clean_service
    def success_method(self, x, y):
        """Simple method that succeeds."""
        return x + y

    @clean_service
    def http_error_method(self):
        """Simulates a known HTTP error."""
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    @clean_service
    def unexpected_error_method(self):
        """Simulates an unhandled exception."""
        raise ValueError("Unexpected failure")


# ============================================================
# Tests
# ============================================================

def test_clean_service_success(caplog):
    """Should return result and log entry/exit messages."""
    svc = DummyService()

    with caplog.at_level(logging.DEBUG):
        result = svc.success_method(2, 3)

    assert result == 5
    assert any("[Service] Entering DummyService.success_method" in msg for msg in caplog.messages)
    assert any("[Service] DummyService.success_method completed successfully" in msg for msg in caplog.messages)


def test_clean_service_http_exception_passthrough(caplog):
    """Should re-raise HTTPException without wrapping."""
    svc = DummyService()

    with caplog.at_level(logging.WARNING), pytest.raises(HTTPException) as exc:
        svc.http_error_method()

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Not found" in exc.value.detail
    assert any("raised HTTPException" in msg for msg in caplog.messages)


def test_clean_service_unhandled_exception_to_500(caplog):
    """Should catch unexpected exceptions and raise HTTP 500."""
    svc = DummyService()

    with caplog.at_level(logging.ERROR), pytest.raises(HTTPException) as exc:
        svc.unexpected_error_method()

    # Verify HTTP 500 conversion
    assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Internal server error" in exc.value.detail

    # Verify that the original error was logged as an exception
    assert any("Unhandled exception in DummyService.unexpected_error_method" in msg for msg in caplog.messages)
