"""
PDF OCR Service
Handles OCR (Optical Character Recognition) text extraction from scanned PDFs using Tesseract
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

from config import Settings
from exceptions import PDFProcessingError, InvalidPDFError
from utils.tesseract_utils import get_tesseract_path

logger = logging.getLogger(__name__)


class PdfOcrService:
    """Service for extracting text from scanned PDFs using OCR"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logger

        # Configure Tesseract path (auto-detect or use configured path)
        try:
            tesseract_path = get_tesseract_path(settings.tesseract_cmd)
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

            self.logger.info("PdfOcrService initialized successfully")
            self.logger.info(f"Tesseract path: {tesseract_path}")

        except RuntimeError as e:
            self.logger.error(f"Failed to initialize Tesseract: {str(e)}")
            # Store error but don't fail initialization (will fail on first OCR attempt)
            self.tesseract_error = str(e)
            self.logger.warning("OCR functionality will not be available until Tesseract is installed")

    async def ocr_pdf(
        self,
        input_path: Path,
        output_dir: Path,
        output_filename: Optional[str] = None,
        language: str = 'eng',
        dpi: int = 300,
        include_page_numbers: bool = True,
        psm: int = 3
    ) -> Dict[str, Any]:
        """
        Extract text from a PDF using OCR (for scanned PDFs or images)

        Args:
            input_path: Path to input PDF file
            output_dir: Directory to save output TXT file
            output_filename: Optional custom output filename (without extension)
            language: Tesseract language code (e.g., 'eng', 'spa', 'fra')
            dpi: DPI resolution for PDF to image conversion (higher = better quality, slower)
            include_page_numbers: Whether to include page number markers in output
            psm: Page Segmentation Mode (3 = fully automatic, 6 = single uniform block)

        Returns:
            Dictionary with extraction results
        """
        try:
            self.logger.info(f"Starting OCR extraction from: {input_path}")
            self.logger.info(f"Language: {language}, DPI: {dpi}, PSM: {psm}")

            # Convert PDF pages to images
            self.logger.info("Converting PDF pages to images...")
            images = convert_from_path(
                str(input_path),
                dpi=dpi,
                fmt='png'
            )

            total_pages = len(images)
            self.logger.info(f"Converted {total_pages} pages to images")

            # Extract text from each page using OCR
            extracted_text = []
            char_count = 0

            # Configure Tesseract
            custom_config = f'--psm {psm}'

            for page_num, image in enumerate(images, start=1):
                self.logger.info(f"Processing page {page_num}/{total_pages} with OCR...")

                # Run OCR on the image
                page_text = pytesseract.image_to_string(
                    image,
                    lang=language,
                    config=custom_config
                )

                # Add page markers if requested
                if include_page_numbers and page_text.strip():
                    extracted_text.append(f"--- Page {page_num} ---\n")
                    extracted_text.append(page_text)
                    extracted_text.append("\n\n")
                elif page_text.strip():
                    extracted_text.append(page_text)
                    extracted_text.append("\n\n")

                char_count += len(page_text)
                self.logger.info(f"Page {page_num}: Extracted {len(page_text)} characters")

            # Combine all text
            full_text = "".join(extracted_text)

            # Generate output filename
            if output_filename:
                txt_filename = f"{output_filename}.txt"
            else:
                base_name = input_path.stem
                txt_filename = f"{base_name}_ocr.txt"

            output_path = output_dir / txt_filename

            # Save as TXT file
            output_path.write_text(full_text, encoding='utf-8')

            file_size = output_path.stat().st_size
            line_count = len(full_text.splitlines())

            self.logger.info(f"OCR extraction completed: {txt_filename}")
            self.logger.info(f"Total characters: {char_count}, Lines: {line_count}")

            return {
                "filename": txt_filename,
                "size": file_size,
                "pages": total_pages,
                "characters": char_count,
                "lines": line_count,
                "language": language,
                "dpi": dpi
            }

        except Exception as e:
            self.logger.error(f"OCR extraction failed: {str(e)}")
            raise PDFProcessingError("OCR", str(e))

        finally:
            # Clean up uploaded file
            if input_path.exists():
                input_path.unlink()
                self.logger.info(f"Cleaned up temporary file: {input_path}")
