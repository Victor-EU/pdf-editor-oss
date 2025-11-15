"""
PDF Split Router
Production-ready implementation with proper OOP and error handling
"""

from fastapi import APIRouter, UploadFile, File, Form, Depends
from pathlib import Path
from typing import Optional, List
import logging

from models import ApiResponse, FileResponse
from services.pdf_split import PdfSplitService
from dependencies import get_pdf_split_service
from config import Settings, get_settings
from utils.file_handlers import FileHandler
from utils.response_builders import ResponseBuilder
from utils.error_handlers import handle_pdf_errors

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/split", response_model=ApiResponse[List[FileResponse]])
@handle_pdf_errors
async def split_pdf(
    file: UploadFile = File(...),
    splitMode: str = Form(...),
    splitPoints: List[str] = Form(...),
    outputFileNameBase: Optional[str] = Form(None),
    settings: Settings = Depends(get_settings),
    split_service: PdfSplitService = Depends(get_pdf_split_service)
):
    """
    Split a PDF file by page ranges.

    Uses dependency injection for services and settings.
    Implements proper error handling with custom exceptions.
    """
    # Convert splitPoints array to comma-separated string
    page_ranges = ','.join(splitPoints)
    logger.info(f"Received split request for {file.filename} with mode: {splitMode}, points: {page_ranges}")

    # Save uploaded file (includes validation)
    temp_file = await FileHandler.save_upload_file(file, settings)

    try:
        # Generate output prefix
        output_prefix = outputFileNameBase if outputFileNameBase else Path(file.filename).stem

        # Split PDF using the service
        results = await split_service.split_pdf(temp_file, page_ranges, settings.output_dir, output_prefix, splitMode)

        logger.info(f"Split completed successfully: {len(results)} files created")

        message = ResponseBuilder.build_split_message(results)
        return ResponseBuilder.build_multiple_files_response(results, message)

    finally:
        await FileHandler.cleanup_files(temp_file)
