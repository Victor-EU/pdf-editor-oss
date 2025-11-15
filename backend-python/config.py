"""
Configuration Management for PDF Editor
Centralized configuration using environment variables and defaults
"""

from pathlib import Path
from typing import List, Optional

try:
    # Try Pydantic v2 (pydantic-settings package)
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    # Fall back to Pydantic v1
    from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with validation"""

    # Application Info
    app_name: str = "PDF Editor API"
    app_version: str = "2.0.0"
    app_description: str = "Open source PDF editing operations with FastAPI"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    reload: bool = False

    # CORS Configuration
    # For production, set CORS_ORIGINS env var: "https://yourdomain.com,https://www.yourdomain.com"
    # For development, defaults to common localhost ports
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:3001,http://localhost:5173",
        description="Comma-separated list of allowed origins"
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string to list"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    # File Storage Configuration
    upload_dir: Path = Path("./uploads")
    output_dir: Path = Path("./output")
    max_upload_size: int = 100 * 1024 * 1024  # 100MB in bytes
    allowed_extensions: List[str] = [".pdf"]

    # PDF Processing Configuration
    max_merge_files: int = 50
    max_pdf_pages: int = 5000
    default_dpi: int = 150
    supported_image_formats: List[str] = ["png", "jpeg", "jpg", "tiff", "tif"]

    # Compression Settings
    compression_levels: dict = {
        "low": {"object_compression": 0, "compress_streams": False},
        "medium": {"object_compression": 9, "compress_streams": True},
        "high": {"object_compression": 15, "compress_streams": True}
    }

    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "pdf_editor.log"

    # Security Configuration
    enable_rate_limiting: bool = True
    rate_limit_per_minute: int = 60

    # Cleanup Configuration
    auto_cleanup_enabled: bool = True
    cleanup_interval_minutes: int = 5  # Run cleanup every 5 minutes
    file_retention_minutes: int = 5  # Keep output files for 5 minutes

    # OCR Configuration
    tesseract_cmd: Optional[str] = Field(default=None, description="Path to tesseract executable (auto-detected if not set)")
    tesseract_language_data: Optional[str] = Field(default=None, description="Custom path to tessdata directory")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        if not self.upload_dir.exists():
            self.upload_dir.mkdir(parents=True, exist_ok=True)
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)

        # Validate max_upload_size
        if self.max_upload_size < 1024 * 1024:
            raise ValueError("max_upload_size must be at least 1MB")
        if self.max_upload_size > 500 * 1024 * 1024:
            raise ValueError("max_upload_size cannot exceed 500MB")


# Global settings instance
settings = Settings()


# Dependency for FastAPI
def get_settings() -> Settings:
    """Get settings instance for dependency injection"""
    return settings
