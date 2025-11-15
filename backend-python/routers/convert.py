"""
PDF Convert Router
Production-ready implementation with proper OOP and error handling
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional, List
import logging

from models import ApiResponse, FileResponse, ImageFormat
from services.pdf_convert import PdfConvertService
from dependencies import get_pdf_convert_service
from config import Settings, get_settings
from utils.file_handlers import FileHandler
from utils.response_builders import ResponseBuilder
from utils.error_handlers import handle_pdf_errors

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/convert", response_model=ApiResponse[List[FileResponse]])
@handle_pdf_errors
async def convert_pdf_to_images(
    file: UploadFile = File(...),
    image_format: ImageFormat = Form(ImageFormat.PNG),
    dpi: int = Form(150),
    pages: Optional[str] = Form("all"),
    settings: Settings = Depends(get_settings),
    convert_service: PdfConvertService = Depends(get_pdf_convert_service)
):
    """
    Convert PDF pages to images.

    Uses dependency injection for services and settings.
    Implements proper error handling with custom exceptions.
    """
    logger.info(f"Received convert request for {file.filename} to {image_format.value}")

    # Validate DPI
    if dpi < 72 or dpi > 300:
        raise HTTPException(
            status_code=400,
            detail="DPI must be between 72 and 300"
        )

    # Save uploaded file (includes PDF validation)
    temp_file = await FileHandler.save_upload_file(file, settings)

    try:
        # Convert PDF to images using the service
        results = await convert_service.convert_to_images(
            temp_file,
            settings.output_dir,
            image_format.value,
            dpi,
            pages
        )

        logger.info(f"Convert completed successfully: {len(results)} images created")

        message = ResponseBuilder.build_conversion_message(results, image_format.value)
        return ResponseBuilder.build_multiple_files_response(results, message)

    finally:
        await FileHandler.cleanup_files(temp_file)
