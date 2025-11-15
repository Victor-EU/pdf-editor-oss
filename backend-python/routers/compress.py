"""
PDF Compress Router
Production-ready implementation with proper OOP and error handling
"""

from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import Optional
import logging

from models import ApiResponse, FileResponse, CompressionLevel
from services.pdf_compress import PdfCompressService
from dependencies import get_pdf_compress_service
from config import Settings, get_settings
from utils.file_handlers import FileHandler
from utils.response_builders import ResponseBuilder
from utils.error_handlers import handle_pdf_errors

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/compress", response_model=ApiResponse[FileResponse])
@handle_pdf_errors
async def compress_pdf(
    file: UploadFile = File(...),
    compression_level: CompressionLevel = Form(CompressionLevel.MEDIUM),
    output_filename: Optional[str] = Form(None),
    settings: Settings = Depends(get_settings),
    compress_service: PdfCompressService = Depends(get_pdf_compress_service)
):
    """
    Compress a PDF file.

    Uses dependency injection for services and settings.
    Implements proper error handling with custom exceptions.
    """
    logger.info(f"Received compress request for {file.filename} with level: {compression_level}")

    # Save uploaded file (includes validation)
    temp_file = await FileHandler.save_upload_file(file, settings)

    try:
        # Generate output filename with sanitization to prevent path traversal
        if not output_filename:
            output_filename = f"compressed_{file.filename}"

        # Sanitize user-provided filename
        safe_filename = FileHandler.sanitize_filename(output_filename)
        output_path = settings.output_dir / safe_filename
        logger.debug(f"Output path: {output_path}")

        # Compress PDF using the service
        result = await compress_service.compress_pdf(temp_file, output_path, compression_level.value)

        # Build response using utility
        message = ResponseBuilder.build_compression_message(result)
        logger.info(f"Compress completed successfully: {output_filename}")

        return ResponseBuilder.build_file_response(result, message)

    finally:
        # Cleanup temporary file
        await FileHandler.cleanup_files(temp_file)
