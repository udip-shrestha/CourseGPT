import logging
from functools import wraps
from fastapi import HTTPException, status


logger = logging.getLogger(__name__)


def clean_service(func):
    """
    Decorator for service-layer methods.
    Responsibilities:
      • Logs function entry, success, and errors
      • Converts unexpected exceptions into standardized HTTP 500 responses
      • Preserves original HTTPExceptions
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        func_name = f"{self.__class__.__name__}.{func.__name__}"
        try:
            logger.debug(f"[Service] Entering {func_name} with args={args}, kwargs={kwargs}")
            result = func(self, *args, **kwargs)
            logger.debug(f"[Service] {func_name} completed successfully")
            return result

        except HTTPException as http_err:
            logger.warning(f"[Service] {func_name} raised HTTPException: {http_err.detail}")
            raise

        except Exception as e:
            logger.exception(f"[Service] Unhandled exception in {func_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error. Please contact support."
            )
    return wrapper
