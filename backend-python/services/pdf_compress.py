"""
PDF Compress Service
Compresses PDF files using pikepdf.
Production-ready OOP implementation with proper error handling.
"""

import pikepdf
from pathlib import Path
from typing import Dict, Any
import logging

from exceptions import PDFProcessingError, InvalidPDFError, ValidationError
from config import Settings

logger = logging.getLogger(__name__)


class PdfCompressService:
    """
    Service for compressing PDF files.
    Implements proper OOP with instance methods and dependency injection.
    """

    def __init__(self, settings: Settings):
        """
        Initialize PDF Compress Service with configuration.

        Args:
            settings: Application settings instance
        """
        self.settings = settings
        self.logger = logger
        self.logger.info("PdfCompressService initialized")

    def get_compression_settings(self, level: str) -> dict:
        """
        Get compression settings based on level.

        Args:
            level: Compression level (low, medium, high)

        Returns:
            dict: Compression settings for pikepdf
        """
        settings = {
            "low": {
                "compress_streams": True,
                "preserve_pdfa": True,
                "object_stream_mode": pikepdf.ObjectStreamMode.disable
            },
            "medium": {
                "compress_streams": True,
                "preserve_pdfa": True,
                "object_stream_mode": pikepdf.ObjectStreamMode.generate
            },
            "high": {
                "compress_streams": True,
                "preserve_pdfa": False,
                "object_stream_mode": pikepdf.ObjectStreamMode.generate,
                "recompress_flate": True
            }
        }
        return settings.get(level, settings["medium"])

    async def compress_pdf(
        self,
        input_path: Path,
        output_path: Path,
        compression_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        Compress a PDF file.

        Args:
            input_path: Path to input PDF file
            output_path: Path to save compressed PDF
            compression_level: Compression level (low, medium, high)

        Returns:
            dict: Information about compression (original size, compressed size, ratio)

        Raises:
            ValidationError: If input validation fails
            InvalidPDFError: If PDF file is invalid or corrupted
            PDFProcessingError: If compression operation fails
        """
        # Validate inputs
        self._validate_compress_inputs(input_path, compression_level)

        pdf = None

        try:
            self.logger.info(
                f"Starting compression for {input_path.name} with level: {compression_level}"
            )

            # Get original file size
            original_size = input_path.stat().st_size
            self.logger.debug(f"Original size: {original_size:,} bytes")

            # Get compression settings
            compress_settings = self.get_compression_settings(compression_level)
            self.logger.debug(f"Using compression settings: {compress_settings}")

            # Open and compress PDF
            try:
                pdf = pikepdf.Pdf.open(input_path)
                page_count = len(pdf.pages)
                self.logger.debug(f"PDF has {page_count} pages")

                # Check page limit
                if page_count > self.settings.max_pdf_pages:
                    raise ValidationError(
                        f"PDF has too many pages ({page_count} > {self.settings.max_pdf_pages})",
                        details={"pages": page_count, "max": self.settings.max_pdf_pages}
                    )

                # Save with compression settings
                pdf.save(output_path, **compress_settings)

            except pikepdf.PdfError as e:
                raise InvalidPDFError(
                    f"Invalid PDF file: {input_path.name}",
                    details={"file": input_path.name, "error": str(e)}
                )

            # Calculate compression results
            compressed_size = output_path.stat().st_size
            compression_ratio = (
                ((original_size - compressed_size) / original_size) * 100
                if original_size > 0 else 0
            )

            self.logger.info(
                f"Compression complete: {original_size:,} -> {compressed_size:,} bytes "
                f"({compression_ratio:.2f}% reduction)"
            )

            return {
                "filename": output_path.name,
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": round(compression_ratio, 2),
                "compression_level": compression_level,
                "pages": page_count
            }

        except (ValidationError, InvalidPDFError):
            # Re-raise our custom exceptions
            raise

        except Exception as e:
            self.logger.error(f"Unexpected error during PDF compression: {str(e)}", exc_info=True)
            raise PDFProcessingError(
                "compression",
                str(e),
                details={
                    "file": input_path.name,
                    "compression_level": compression_level
                }
            )

        finally:
            # Ensure resources are cleaned up
            if pdf is not None:
                try:
                    pdf.close()
                except:
                    pass

    def _validate_compress_inputs(self, input_path: Path, compression_level: str) -> None:
        """
        Validate compression operation inputs.

        Args:
            input_path: Path to input PDF
            compression_level: Requested compression level

        Raises:
            ValidationError: If validation fails
        """
        # Validate file exists
        if not input_path.exists():
            raise ValidationError(
                f"Input file not found: {input_path.name}",
                details={"file": str(input_path)}
            )

        # Validate file type
        if input_path.suffix.lower() != '.pdf':
            raise ValidationError(
                f"Invalid file type: {input_path.name} (must be PDF)",
                details={"file": input_path.name, "extension": input_path.suffix}
            )

        # Validate file size
        file_size = input_path.stat().st_size
        if file_size > self.settings.max_upload_size:
            raise ValidationError(
                f"File too large: {file_size:,} bytes exceeds maximum {self.settings.max_upload_size:,} bytes",
                details={"size": file_size, "max_size": self.settings.max_upload_size}
            )

        # Validate compression level
        valid_levels = ["low", "medium", "high"]
        if compression_level not in valid_levels:
            raise ValidationError(
                f"Invalid compression level: {compression_level}",
                details={
                    "provided": compression_level,
                    "valid_levels": valid_levels
                }
            )
