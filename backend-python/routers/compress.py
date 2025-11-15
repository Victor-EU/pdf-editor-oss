"""
PDF Compress Router
Production-ready implementation with proper OOP and error handling
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from pathlib import Path
from typing import Optional
import aiofiles
import uuid
import logging

from models import ApiResponse, FileResponse, CompressionLevel
from services.pdf_compress import PdfCompressService
from dependencies import get_pdf_compress_service
from config import Settings, get_settings
from exceptions import PDFEditorException

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/compress", response_model=ApiResponse[FileResponse])
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
    temp_file = None

    try:
        logger.info(f"Received compress request for {file.filename} with level: {compression_level}")

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

        # Generate output filename
        if not output_filename:
            output_filename = f"compressed_{file.filename}"
        elif not output_filename.endswith('.pdf'):
            output_filename += '.pdf'

        output_path = settings.output_dir / output_filename
        logger.debug(f"Output path: {output_path}")

        # Compress PDF using the service (OOP with instance method)
        result = await compress_service.compress_pdf(temp_file, output_path, compression_level.value)

        # Create response with camelCase field names
        file_response = FileResponse(
            file_name=result["filename"],
            file_path=None,  # Not needed for downloads
            file_size=result["compressed_size"],
            download_url=f"/download/{result['filename']}",
            original_size=result["original_size"],
            compression_ratio=result["compression_ratio"]
        )

        message = f"PDF compressed successfully. Size reduced by {result['compression_ratio']}%"

        logger.info(f"Compress completed successfully: {output_filename}")
        return ApiResponse.success_response(message, file_response)

    except PDFEditorException as e:
        # Handle our custom exceptions
        logger.warning(f"PDF Editor exception: {e.message}", extra=e.details)
        raise HTTPException(status_code=e.status_code, detail=e.message)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in compress endpoint: {str(e)}", exc_info=True)
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
