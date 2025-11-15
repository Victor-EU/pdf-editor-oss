"""
PDF Convert Router
Production-ready implementation with proper OOP and error handling
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from pathlib import Path
from typing import Optional, List
import aiofiles
import uuid
import logging

from models import ApiResponse, FileResponse, ImageFormat
from services.pdf_convert import PdfConvertService
from dependencies import get_pdf_convert_service
from config import Settings, get_settings
from exceptions import PDFEditorException

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/convert", response_model=ApiResponse[List[FileResponse]])
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
    temp_file = None

    try:
        logger.info(f"Received convert request for {file.filename} to {image_format.value}")

        # Validate file extension
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.filename} (must be PDF)"
            )

        # Validate DPI
        if dpi < 72 or dpi > 300:
            raise HTTPException(
                status_code=400,
                detail="DPI must be between 72 and 300"
            )

        # Generate unique temporary path
        temp_file = settings.upload_dir / f"{uuid.uuid4()}_{file.filename}"

        # Save file asynchronously
        async with aiofiles.open(temp_file, 'wb') as f:
            content = await file.read()
            await f.write(content)

        logger.debug(f"Saved {file.filename} to {temp_file}")

        # Convert PDF to images using the service (OOP with instance method)
        results = await convert_service.convert_to_images(
            temp_file,
            settings.output_dir,
            image_format.value,
            dpi,
            pages
        )

        # Create response with camelCase field names
        file_responses = [
            FileResponse(
                file_name=result["filename"],
                file_path=None,
                file_size=result["size"],
                download_url=f"/download/{result['filename']}",
                original_size=None,
                compression_ratio=None
            )
            for result in results
        ]

        message = f"PDF converted to {len(file_responses)} {image_format.value.upper()} image(s)"

        logger.info(f"Convert completed successfully: {len(file_responses)} images created")
        return ApiResponse.success_response(message, file_responses)

    except PDFEditorException as e:
        # Handle our custom exceptions
        logger.warning(f"PDF Editor exception: {e.message}", extra=e.details)
        raise HTTPException(status_code=e.status_code, detail=e.message)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in convert endpoint: {str(e)}", exc_info=True)
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
