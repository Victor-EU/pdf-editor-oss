"""
Table Extraction Router
Handles PDF table extraction endpoints
"""

import uuid
import aiofiles
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends

from config import Settings
from dependencies import get_settings
from services.pdf_table_extract import PdfTableExtractService
from models import ApiResponse, FileResponse
from exceptions import PDFProcessingError, ValidationError

router = APIRouter()
logger = logging.getLogger(__name__)


def get_table_extract_service(settings: Settings = Depends(get_settings)) -> PdfTableExtractService:
    """Dependency injection for PdfTableExtractService"""
    return PdfTableExtractService(settings)


@router.post("/table-extract", response_model=ApiResponse[FileResponse])
async def extract_tables(
    file: UploadFile = File(..., description="PDF file to extract tables from"),
    outputFileName: Optional[str] = Form(None, description="Optional output file name (without extension)"),
    includeHeaders: bool = Form(True, description="Include table headers in extracted data"),
    settings: Settings = Depends(get_settings),
    table_service: PdfTableExtractService = Depends(get_table_extract_service)
):
    """
    Extract tables from a PDF file and export to Excel

    This endpoint automatically detects tables in a PDF using both lattice (bordered)
    and stream (non-bordered) methods, extracts their content including headers,
    and exports them to a formatted Excel file with one sheet per table.
    All pages in the PDF will be processed by default.

    Parameters:
    - file: PDF file containing tables
    - outputFileName: Optional custom name for the output Excel file
    - includeHeaders: Whether to treat first row as header and style accordingly (default: True)

    Returns:
    - FileResponse with the Excel file containing extracted tables
    """
    try:
        logger.info(f"Received table extraction request: {file.filename}")
        logger.info(f"Include headers: {includeHeaders}")

        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise ValidationError("Only PDF files are supported for table extraction")

        # Save uploaded file
        temp_file = settings.upload_dir / f"{uuid.uuid4()}_{file.filename}"
        async with aiofiles.open(temp_file, 'wb') as f:
            content = await file.read()
            await f.write(content)

        logger.info(f"Saved uploaded file: {temp_file}")

        # Extract tables (automatically detects lattice and stream tables)
        result = await table_service.extract_tables(
            temp_file,
            settings.output_dir,
            outputFileName,
            includeHeaders
        )

        # Create response
        file_response = FileResponse(
            file_name=result["filename"],
            file_size=result["size"],
            download_url=f"/download/{result['filename']}",
            pages=None  # Not applicable for table extraction
        )

        logger.info(f"Table extraction successful: {result['filename']}")

        # Create detailed message
        table_details_str = ", ".join([
            f"Table {t['table_number']} (Page {t['page']}, {t['rows']}×{t['columns']}, Acc: {t['accuracy']}%)"
            for t in result['table_details'][:3]  # Show first 3 tables
        ])

        if result['tables_count'] > 3:
            table_details_str += f" and {result['tables_count'] - 3} more..."

        message = (
            f"Extracted {result['tables_count']} table(s) with {result['total_rows']} total rows. "
            f"{table_details_str}"
        )

        return ApiResponse.success_response(message, file_response)

    except (PDFProcessingError, ValidationError) as e:
        logger.error(f"Table extraction error: {str(e)}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error during table extraction: {str(e)}")
        raise PDFProcessingError("Table Extraction", str(e))
