"""
OCR Router
Handles PDF OCR (Optical Character Recognition) extraction endpoints
"""

import uuid
import aiofiles
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends

from config import Settings
from dependencies import get_settings, get_pdf_ocr_service
from services.pdf_ocr import PdfOcrService
from models import ApiResponse, FileResponse
from exceptions import PDFProcessingError, ValidationError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ocr", response_model=ApiResponse[FileResponse])
async def ocr_pdf_text(
    file: UploadFile = File(..., description="PDF file to extract text from using OCR"),
    outputFileName: Optional[str] = Form(None, description="Optional output file name (without extension)"),
    language: str = Form('eng', description="OCR language code (e.g., 'eng', 'spa', 'fra')"),
    dpi: int = Form(300, description="DPI resolution for image conversion (higher = better quality, slower)"),
    includePageNumbers: bool = Form(True, description="Include page number markers in extracted text"),
    psm: int = Form(3, description="Page Segmentation Mode (3 = automatic, 6 = single block)"),
    settings: Settings = Depends(get_settings),
    ocr_service: PdfOcrService = Depends(get_pdf_ocr_service)
):
    """
    Extract text from a scanned PDF using OCR (Optical Character Recognition)

    This endpoint is designed for scanned PDFs or image-based PDFs that don't have
    selectable text. It converts each page to an image and uses Tesseract OCR to
    extract text.

    Parameters:
    - file: PDF file to process
    - outputFileName: Optional custom name for the output TXT file
    - language: Tesseract language code (default: 'eng' for English)
    - dpi: Image resolution for OCR (default: 300, higher = better quality but slower)
    - includePageNumbers: Whether to add "--- Page N ---" markers (default: True)
    - psm: Page Segmentation Mode for Tesseract (default: 3 for fully automatic)

    Returns:
    - FileResponse with the extracted text file information
    """
    try:
        logger.info(f"Received OCR request: {file.filename}")
        logger.info(f"Language: {language}, DPI: {dpi}, PSM: {psm}")

        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise ValidationError("Only PDF files are supported for OCR")

        # Validate language (basic check)
        valid_languages = ['eng', 'spa', 'fra', 'deu', 'ita', 'por', 'rus', 'chi_sim', 'chi_tra', 'jpn', 'kor']
        if language not in valid_languages:
            logger.warning(f"Language '{language}' may not be installed. Using anyway...")

        # Validate DPI range
        if dpi < 150 or dpi > 600:
            raise ValidationError("DPI must be between 150 and 600")

        # Validate PSM range
        if psm < 0 or psm > 13:
            raise ValidationError("PSM must be between 0 and 13")

        # Save uploaded file
        temp_file = settings.upload_dir / f"{uuid.uuid4()}_{file.filename}"
        async with aiofiles.open(temp_file, 'wb') as f:
            content = await file.read()
            await f.write(content)

        logger.info(f"Saved uploaded file: {temp_file}")

        # Perform OCR extraction
        result = await ocr_service.ocr_pdf(
            temp_file,
            settings.output_dir,
            outputFileName,
            language,
            dpi,
            includePageNumbers,
            psm
        )

        # Create response
        file_response = FileResponse(
            file_name=result["filename"],
            file_size=result["size"],
            download_url=f"/download/{result['filename']}",
            pages=result.get("pages")
        )

        logger.info(f"OCR extraction successful: {result['filename']}")

        return ApiResponse.success_response(
            f"OCR extracted {result['characters']} characters from {result['pages']} pages using {language} language",
            file_response
        )

    except (PDFProcessingError, ValidationError) as e:
        logger.error(f"OCR extraction error: {str(e)}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error during OCR: {str(e)}")
        raise PDFProcessingError("OCR", str(e))
