"""
Custom Exception Classes for PDF Editor
Provides proper error handling hierarchy for production use
"""

from typing import Optional, Dict, Any


class PDFEditorException(Exception):
    """Base exception class for all PDF Editor exceptions"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class ValidationError(PDFEditorException):
    """Raised when input validation fails"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class FileNotFoundError(PDFEditorException):
    """Raised when a required file is not found"""

    def __init__(self, filename: str, details: Optional[Dict[str, Any]] = None):
        message = f"File not found: {filename}"
        super().__init__(message, status_code=404, details=details)


class InvalidPDFError(PDFEditorException):
    """Raised when PDF file is invalid or corrupted"""

    def __init__(self, message: str = "Invalid or corrupted PDF file", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class PDFProcessingError(PDFEditorException):
    """Raised when PDF processing operation fails"""

    def __init__(self, operation: str, message: str, details: Optional[Dict[str, Any]] = None):
        full_message = f"PDF {operation} failed: {message}"
        super().__init__(full_message, status_code=500, details=details)


class FileTooLargeError(PDFEditorException):
    """Raised when uploaded file exceeds size limit"""

    def __init__(self, size: int, max_size: int, details: Optional[Dict[str, Any]] = None):
        message = f"File size ({size} bytes) exceeds maximum allowed size ({max_size} bytes)"
        super().__init__(message, status_code=413, details=details)


class UnsupportedFormatError(PDFEditorException):
    """Raised when file format is not supported"""

    def __init__(self, format: str, supported_formats: list, details: Optional[Dict[str, Any]] = None):
        message = f"Unsupported format: {format}. Supported formats: {', '.join(supported_formats)}"
        super().__init__(message, status_code=415, details=details)


class InsufficientPagesError(PDFEditorException):
    """Raised when PDF doesn't have enough pages for the requested operation"""

    def __init__(self, required: int, available: int, details: Optional[Dict[str, Any]] = None):
        message = f"Insufficient pages: operation requires {required} pages, but only {available} available"
        super().__init__(message, status_code=422, details=details)


class ConfigurationError(PDFEditorException):
    """Raised when application configuration is invalid"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)
