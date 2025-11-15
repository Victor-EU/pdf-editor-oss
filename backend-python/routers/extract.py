"""
PDF Text Extract Router
Production-ready implementation with proper OOP and error handling
"""

from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import Optional
import logging

from models import ApiResponse, FileResponse
from services.pdf_extract import PdfExtractService
from dependencies import get_pdf_extract_service
from config import Settings, get_settings
from utils.file_handlers import FileHandler
from utils.response_builders import ResponseBuilder
from utils.error_handlers import handle_pdf_errors

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/extract", response_model=ApiResponse[FileResponse])
@handle_pdf_errors
async def extract_text_from_pdf(
    file: UploadFile = File(...),
    outputFileName: Optional[str] = Form(None),
    includePageNumbers: bool = Form(True),
    settings: Settings = Depends(get_settings),
    extract_service: PdfExtractService = Depends(get_pdf_extract_service)
):
    """
    Extract text from a PDF file and save as TXT.

    Uses dependency injection for services and settings.
    Implements proper error handling with custom exceptions.
    """
    logger.info(f"Received extract request for {file.filename}")

    # Save uploaded file (includes validation)
    temp_file = await FileHandler.save_upload_file(file, settings)

    try:
        # Extract text using the service
        result = await extract_service.extract_text(
            temp_file,
            settings.output_dir,
            outputFileName,
            includePageNumbers
        )

        # Build response
        message = ResponseBuilder.build_extraction_message(result)
        logger.info(f"Text extraction completed successfully: {result['filename']}")

        return ResponseBuilder.build_file_response(result, message)

    finally:
        # Cleanup temporary file
        await FileHandler.cleanup_files(temp_file)
