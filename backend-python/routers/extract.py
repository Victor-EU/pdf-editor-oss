"""
PDF Text Extract Router
Production-ready implementation with proper OOP and error handling
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from pathlib import Path
from typing import Optional
import aiofiles
import uuid
import logging

from models import ApiResponse, FileResponse
from services.pdf_extract import PdfExtractService
from dependencies import get_pdf_extract_service
from config import Settings, get_settings
from exceptions import PDFEditorException

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/extract", response_model=ApiResponse[FileResponse])
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
    temp_file = None

    try:
        logger.info(f"Received extract request for {file.filename}")

        # Validate file extension
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.filename} (must be PDF)"
            )

        # Generate unique temporary path
        temp_file = settings.upload_dir / f"{uuid.uuid4()}_{file.filename}"

        # Save file asynchronously
        async with aiofiles.open(temp_file, 'wb') as f:
            content = await file.read()
            await f.write(content)

        logger.debug(f"Saved {file.filename} to {temp_file}")

        # Extract text using the service
        result = await extract_service.extract_text(
            temp_file,
            settings.output_dir,
            outputFileName,
            includePageNumbers
        )

        # Create response with camelCase field names
        file_response = FileResponse(
            file_name=result["filename"],
            file_path=None,
            file_size=result["size"],
            download_url=f"/download/{result['filename']}",
            original_size=None,
            compression_ratio=None,
            pages=result.get("pages")
        )

        logger.info(f"Text extraction completed successfully: {result['filename']}")
        return ApiResponse.success_response(
            f"Extracted {result['characters']} characters from {result['pages']} pages",
            file_response
        )

    except PDFEditorException as e:
        # Handle our custom exceptions
        logger.warning(f"PDF Editor exception: {e.message}", extra=e.details)
        raise HTTPException(status_code=e.status_code, detail=e.message)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in extract endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

    finally:
        # Cleanup temporary file
        if temp_file:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    logger.debug(f"Cleaned up temporary file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up {temp_file}: {str(e)}")
