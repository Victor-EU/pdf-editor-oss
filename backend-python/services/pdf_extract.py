"""
PDF Text Extraction Service
Extracts text content from PDF files using PyMuPDF (fitz).
Production-ready OOP implementation with proper error handling.
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from exceptions import (
    PDFProcessingError,
    InvalidPDFError,
    ValidationError
)
from config import Settings

logger = logging.getLogger(__name__)


class PdfExtractService:
    """
    Service for extracting text from PDF files.
    Implements proper OOP with instance methods and dependency injection.
    """

    def __init__(self, settings: Settings):
        """
        Initialize PDF Extract Service with configuration.

        Args:
            settings: Application settings instance
        """
        self.settings = settings
        self.logger = logger
        self.logger.info("PdfExtractService initialized")

    async def extract_text(
        self,
        input_path: Path,
        output_dir: Path,
        output_filename: Optional[str] = None,
        include_page_numbers: bool = True
    ) -> Dict[str, Any]:
        """
        Extract text from a PDF file and save to TXT.

        Args:
            input_path: Path to input PDF file
            output_dir: Directory to save text file
            output_filename: Optional custom output filename (without extension)
            include_page_numbers: Whether to include page numbers in output

        Returns:
            Dict with information about the extracted text file

        Raises:
            ValidationError: If input validation fails
            InvalidPDFError: If PDF file is invalid
            PDFProcessingError: If extraction fails
        """
        # Validate inputs
        self._validate_extract_inputs(input_path)

        pdf_doc = None

        try:
            self.logger.info(f"Starting text extraction for {input_path.name}")

            # Open the PDF
            try:
                pdf_doc = fitz.open(input_path)
                total_pages = pdf_doc.page_count
                self.logger.debug(f"PDF has {total_pages} pages")
            except Exception as e:
                raise InvalidPDFError(
                    f"Invalid PDF file: {input_path.name}",
                    details={"file": input_path.name, "error": str(e)}
                )

            # Check page limit
            if total_pages > self.settings.max_pdf_pages:
                raise ValidationError(
                    f"PDF has too many pages ({total_pages} > {self.settings.max_pdf_pages})",
                    details={"pages": total_pages, "max": self.settings.max_pdf_pages}
                )

            # Extract text from all pages
            extracted_text = []
            char_count = 0

            for page_num in range(total_pages):
                page = pdf_doc[page_num]
                page_text = page.get_text()

                if include_page_numbers and page_text.strip():
                    extracted_text.append(f"--- Page {page_num + 1} ---\n")
                    extracted_text.append(page_text)
                    extracted_text.append("\n\n")
                elif page_text.strip():
                    extracted_text.append(page_text)
                    extracted_text.append("\n\n")

                char_count += len(page_text)

            full_text = "".join(extracted_text)

            # Generate output filename
            if output_filename:
                txt_filename = f"{output_filename}.txt"
            else:
                txt_filename = f"{input_path.stem}_extracted.txt"

            output_path = output_dir / txt_filename

            # Save text to file
            try:
                output_path.write_text(full_text, encoding='utf-8')
                file_size = output_path.stat().st_size

                self.logger.info(
                    f"Extracted text to {txt_filename}: "
                    f"{char_count} characters, {file_size:,} bytes"
                )

                return {
                    "filename": txt_filename,
                    "size": file_size,
                    "pages": total_pages,
                    "characters": char_count,
                    "lines": len(full_text.splitlines())
                }

            except Exception as e:
                raise PDFProcessingError(
                    "extract",
                    f"Failed to save text file: {str(e)}",
                    details={"output_file": txt_filename}
                )

        except (ValidationError, InvalidPDFError):
            # Re-raise our custom exceptions
            raise

        except Exception as e:
            self.logger.error(f"Unexpected error during text extraction: {str(e)}", exc_info=True)
            raise PDFProcessingError(
                "extract",
                str(e),
                details={"file": input_path.name}
            )

        finally:
            # Cleanup resources
            if pdf_doc is not None:
                try:
                    pdf_doc.close()
                except:
                    pass

    def _validate_extract_inputs(self, input_path: Path) -> None:
        """
        Validate text extraction inputs.

        Args:
            input_path: Path to input PDF

        Raises:
            ValidationError: If validation fails
        """
        if not input_path.exists():
            raise ValidationError(
                f"Input file not found: {input_path.name}",
                details={"file": str(input_path)}
            )

        if input_path.suffix.lower() != '.pdf':
            raise ValidationError(
                f"Invalid file type: {input_path.name} (must be PDF)",
                details={"file": input_path.name, "extension": input_path.suffix}
            )
