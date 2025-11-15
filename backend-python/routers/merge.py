"""
PDF Merge Router
Production-ready implementation with proper OOP and error handling
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from pathlib import Path
from typing import List, Optional
import aiofiles
import uuid
import logging

from models import ApiResponse, FileResponse
from services.pdf_merge import PdfMergeService
from dependencies import get_pdf_merge_service
from config import Settings, get_settings
from exceptions import PDFEditorException

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/merge", response_model=ApiResponse[FileResponse])
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
    temp_files = []

    try:
        logger.info(f"Received merge request for {len(files)} files")

        # Save uploaded files temporarily
        for file in files:
            logger.debug(f"Processing upload: {file.filename}")

            # Validate file extension
            if not file.filename.endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {file.filename} (must be PDF)"
                )

            # Generate unique temporary path
            temp_path = settings.upload_dir / f"{uuid.uuid4()}_{file.filename}"

            # Save file asynchronously
            async with aiofiles.open(temp_path, 'wb') as f:
                content = await file.read()
                await f.write(content)

            temp_files.append(temp_path)
            logger.debug(f"Saved {file.filename} to {temp_path}")

        # Generate output filename
        if not output_filename:
            output_filename = "merged.pdf"
        elif not output_filename.endswith('.pdf'):
            output_filename += '.pdf'

        output_path = settings.output_dir / output_filename
        logger.debug(f"Output path: {output_path}")

        # Merge PDFs using the service (OOP with instance method)
        result = await merge_service.merge_pdfs(temp_files, output_path)

        # Create response with camelCase field names
        file_response = FileResponse(
            file_name=result["filename"],
            file_path=None,
            file_size=result["size"],
            download_url=f"/download/{result['filename']}",
            original_size=None,
            compression_ratio=None
        )

        logger.info(f"Merge completed successfully: {output_filename}")
        return ApiResponse.success_response("PDF files merged successfully", file_response)

    except PDFEditorException as e:
        # Handle our custom exceptions
        logger.warning(f"PDF Editor exception: {e.message}", extra=e.details)
        raise HTTPException(status_code=e.status_code, detail=e.message)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in merge endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

    finally:
        # Cleanup temporary files
        for temp_file in temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    logger.debug(f"Cleaned up temporary file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up {temp_file}: {str(e)}")
