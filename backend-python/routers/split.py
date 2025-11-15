"""
PDF Split Router
Production-ready implementation with proper OOP and error handling
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from pathlib import Path
from typing import Optional, List
import aiofiles
import uuid
import logging

from models import ApiResponse, FileResponse
from services.pdf_split import PdfSplitService
from dependencies import get_pdf_split_service
from config import Settings, get_settings
from exceptions import PDFEditorException

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/split", response_model=ApiResponse[List[FileResponse]])
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
    temp_file = None

    try:
        # Convert splitPoints array to comma-separated string
        page_ranges = ','.join(splitPoints)
        logger.info(f"Received split request for {file.filename} with mode: {splitMode}, points: {page_ranges}")

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

        # Generate output prefix
        output_prefix = outputFileNameBase if outputFileNameBase else Path(file.filename).stem

        # Split PDF using the service (OOP with instance method)
        results = await split_service.split_pdf(temp_file, page_ranges, settings.output_dir, output_prefix, splitMode)

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

        logger.info(f"Split completed successfully: {len(file_responses)} files created")
        return ApiResponse.success_response(
            f"PDF split into {len(file_responses)} files",
            file_responses
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
        logger.error(f"Unexpected error in split endpoint: {str(e)}", exc_info=True)
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
