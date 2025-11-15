"""
PDF Merge Service
Merges multiple PDF files into a single document using pikepdf.
Production-ready OOP implementation with proper error handling.
"""

import pikepdf
from pathlib import Path
from typing import List, Dict, Any
import logging

from exceptions import PDFProcessingError, InvalidPDFError, ValidationError
from config import Settings

logger = logging.getLogger(__name__)


class PdfMergeService:
    """
    Service for merging multiple PDF files.
    Implements proper OOP with instance methods and dependency injection.
    """

    def __init__(self, settings: Settings):
        """
        Initialize PDF Merge Service with configuration.

        Args:
            settings: Application settings instance
        """
        self.settings = settings
        self.logger = logger
        self.logger.info("PdfMergeService initialized")

    async def merge_pdfs(self, file_paths: List[Path], output_path: Path) -> Dict[str, Any]:
        """
        Merge multiple PDF files into one.

        Args:
            file_paths: List of paths to PDF files to merge
            output_path: Path where merged PDF will be saved

        Returns:
            dict: Information about the merged PDF (pages, size, source_files)

        Raises:
            ValidationError: If input validation fails
            InvalidPDFError: If any PDF file is invalid or corrupted
            PDFProcessingError: If merge operation fails
        """
        # Validate inputs
        self._validate_merge_inputs(file_paths)

        merged_pdf = None
        try:
            self.logger.info(f"Starting merge operation for {len(file_paths)} PDF files")

            # Create a new PDF for the merged output
            merged_pdf = pikepdf.Pdf.new()
            total_pages = 0

            # Open each PDF and append its pages
            for idx, file_path in enumerate(file_paths, 1):
                self.logger.debug(f"Processing file {idx}/{len(file_paths)}: {file_path.name}")

                try:
                    with pikepdf.Pdf.open(file_path) as pdf:
                        page_count = len(pdf.pages)
                        self.logger.debug(f"Adding {page_count} pages from {file_path.name}")

                        # Append all pages from this PDF
                        merged_pdf.pages.extend(pdf.pages)
                        total_pages += page_count

                except pikepdf.PdfError as e:
                    raise InvalidPDFError(
                        f"Invalid PDF file: {file_path.name}",
                        details={"file": file_path.name, "error": str(e)}
                    )

            # Check if we exceeded max pages
            if total_pages > self.settings.max_pdf_pages:
                raise ValidationError(
                    f"Total pages ({total_pages}) exceeds maximum allowed ({self.settings.max_pdf_pages})",
                    details={"total_pages": total_pages, "max_pages": self.settings.max_pdf_pages}
                )

            # Save the merged PDF
            self.logger.debug(f"Saving merged PDF to {output_path}")
            merged_pdf.save(output_path)

            file_size = output_path.stat().st_size
            self.logger.info(
                f"Successfully merged {len(file_paths)} PDFs into {output_path.name} "
                f"({total_pages} pages, {file_size:,} bytes)"
            )

            return {
                "filename": output_path.name,
                "pages": total_pages,
                "size": file_size,
                "source_files": len(file_paths)
            }

        except (ValidationError, InvalidPDFError):
            # Re-raise our custom exceptions
            raise

        except Exception as e:
            self.logger.error(f"Unexpected error during PDF merge: {str(e)}", exc_info=True)
            raise PDFProcessingError(
                "merge",
                str(e),
                details={"file_count": len(file_paths)}
            )

        finally:
            # Ensure resources are cleaned up
            if merged_pdf is not None:
                try:
                    merged_pdf.close()
                except:
                    pass

    def _validate_merge_inputs(self, file_paths: List[Path]) -> None:
        """
        Validate merge operation inputs.

        Args:
            file_paths: List of PDF file paths to validate

        Raises:
            ValidationError: If validation fails
        """
        if not file_paths:
            raise ValidationError("No PDF files provided for merging")

        if len(file_paths) < 2:
            raise ValidationError(
                "At least 2 PDF files are required for merging",
                details={"provided": len(file_paths)}
            )

        if len(file_paths) > self.settings.max_merge_files:
            raise ValidationError(
                f"Too many files: maximum {self.settings.max_merge_files} files allowed",
                details={"provided": len(file_paths), "max": self.settings.max_merge_files}
            )

        # Validate each file exists and is a PDF
        for file_path in file_paths:
            if not file_path.exists():
                raise ValidationError(
                    f"File not found: {file_path.name}",
                    details={"file": str(file_path)}
                )

            if file_path.suffix.lower() != '.pdf':
                raise ValidationError(
                    f"Invalid file type: {file_path.name} (must be PDF)",
                    details={"file": file_path.name, "extension": file_path.suffix}
                )
