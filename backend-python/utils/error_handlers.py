"""
Error handling utilities for API endpoints
Centralized error handling and logging
"""

import logging
from functools import wraps
from typing import Callable
from fastapi import HTTPException

from exceptions import PDFEditorException

logger = logging.getLogger(__name__)


def handle_pdf_errors(func: Callable) -> Callable:
    """
    Decorator for standardized error handling in PDF operations

    Wraps endpoint functions with consistent error handling:
    - Catches PDFEditorException and converts to HTTPException
    - Re-raises HTTPException as-is
    - Catches unexpected exceptions and logs them
    - Returns 500 error for unexpected exceptions

    Usage:
        @router.post("/endpoint")
        @handle_pdf_errors
        async def my_endpoint(...):
            # endpoint logic
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except PDFEditorException as e:
            # Handle our custom exceptions
            logger.warning(f"PDF Editor exception in {func.__name__}: {e.message}", extra=e.details)
            raise HTTPException(status_code=e.status_code, detail=e.message)

        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise

        except Exception as e:
            # Handle unexpected errors
            logger.error(
                f"Unexpected error in {func.__name__}: {str(e)}",
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )

    return wrapper
