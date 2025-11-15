"""
Data models and schemas for PDF Editor API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Generic, TypeVar
from enum import Enum

# Generic type for API responses
T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """Generic API response wrapper"""
    success: bool
    message: str
    data: Optional[T] = None

    @classmethod
    def success_response(cls, message: str, data: T):
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_response(cls, message: str):
        return cls(success=False, message=message, data=None)

class FileResponse(BaseModel):
    """Response model for file operations"""
    file_name: str = Field(..., alias="fileName")
    file_path: Optional[str] = Field(None, alias="filePath")
    file_size: int = Field(..., alias="fileSize")
    download_url: str = Field(..., alias="downloadUrl")
    original_size: Optional[int] = Field(None, alias="originalSize")
    compression_ratio: Optional[float] = Field(None, alias="compressionRatio")
    pages: Optional[int] = None

    class Config:
        populate_by_name = True  # Allow using both snake_case and camelCase
        by_alias = True  # Use aliases in JSON output

class MergeRequest(BaseModel):
    """Request model for PDF merge operation"""
    output_filename: Optional[str] = Field(None, description="Optional output filename")

class SplitRequest(BaseModel):
    """Request model for PDF split operation"""
    page_ranges: str = Field(..., description="Page ranges to split (e.g., '1-3,5-7')")
    output_filename: Optional[str] = Field(None, description="Optional output filename prefix")

class CompressionLevel(str, Enum):
    """Compression level options"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CompressRequest(BaseModel):
    """Request model for PDF compression"""
    compression_level: CompressionLevel = Field(
        CompressionLevel.MEDIUM,
        description="Compression level: low, medium, or high"
    )
    output_filename: Optional[str] = Field(None, description="Optional output filename")

class ImageFormat(str, Enum):
    """Image format options"""
    PNG = "png"
    JPEG = "jpeg"
    JPG = "jpg"
    TIFF = "tiff"

class ConvertRequest(BaseModel):
    """Request model for PDF to image conversion"""
    image_format: ImageFormat = Field(ImageFormat.PNG, description="Output image format")
    dpi: int = Field(150, ge=72, le=300, description="Image resolution (DPI)")
    pages: Optional[str] = Field(None, description="Page numbers to convert (e.g., '1,3,5' or 'all')")
