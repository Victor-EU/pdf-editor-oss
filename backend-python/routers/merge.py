"""
PDF Merge Router
Production-ready implementation with proper OOP and error handling
"""

from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import List, Optional
import logging

from models import ApiResponse, FileResponse
from services.pdf_merge import PdfMergeService
from dependencies import get_pdf_merge_service
from config import Settings, get_settings
from utils.file_handlers import FileHandler
from utils.response_builders import ResponseBuilder
from utils.error_handlers import handle_pdf_errors

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/merge", response_model=ApiResponse[FileResponse])
@handle_pdf_errors
async def merge_pdfs(
    files: List[UploadFile] = File(...),
    output_filename: Optional[str] = Form(None),
    settings: Settings = Depends(get_settings),
    merge_service: PdfMergeService = Depends(get_pdf_merge_service)
):
    """
    Merge multiple PDF files into one.

    Uses dependency injection for services and settings.
    Implements proper error handling with custom exceptions.
    """
    logger.info(f"Received merge request for {len(files)} files")

    # Save all uploaded files (includes validation)
    temp_files = await FileHandler.save_multiple_files(files, settings)

    try:
        # Generate output filename with sanitization to prevent path traversal
        if not output_filename:
            output_filename = "merged.pdf"

        # Sanitize user-provided filename
        safe_filename = FileHandler.sanitize_filename(output_filename)
        output_path = settings.output_dir / safe_filename
        logger.debug(f"Output path: {output_path}")

        # Merge PDFs using the service
        result = await merge_service.merge_pdfs(temp_files, output_path)

        logger.info(f"Merge completed successfully: {output_filename}")
        return ResponseBuilder.build_file_response(result, "PDF files merged successfully")

    finally:
        # Cleanup temporary files
        await FileHandler.cleanup_file_list(temp_files)
