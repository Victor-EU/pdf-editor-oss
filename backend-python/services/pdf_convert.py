"""
PDF Convert Service
Converts PDF pages to images using pdf2image.
Production-ready OOP implementation with proper error handling.
"""

from pdf2image import convert_from_path
from pathlib import Path
from typing import List, Dict, Any
import logging

from exceptions import (
    PDFProcessingError,
    InvalidPDFError,
    ValidationError,
    UnsupportedFormatError,
    InsufficientPagesError
)
from config import Settings

logger = logging.getLogger(__name__)


class PdfConvertService:
    """
    Service for converting PDF pages to images.
    Implements proper OOP with instance methods and dependency injection.
    """

    def __init__(self, settings: Settings):
        """
        Initialize PDF Convert Service with configuration.

        Args:
            settings: Application settings instance
        """
        self.settings = settings
        self.logger = logger
        self.logger.info("PdfConvertService initialized")

    def parse_page_numbers(self, pages_str: str, total_pages: int) -> List[int]:
        """
        Parse page numbers string into list of page numbers.

        Args:
            pages_str: Page numbers string (e.g., "1,3,5" or "all")
            total_pages: Total number of pages in PDF

        Returns:
            List of page numbers (1-indexed) to convert

        Raises:
            ValidationError: If page numbers are invalid
            InsufficientPagesError: If requested pages don't exist
        """
        if not pages_str or pages_str.strip().lower() == "all":
            return list(range(1, total_pages + 1))

        page_numbers = []
        parts = pages_str.split(',')

        for part in parts:
            part = part.strip()

            if not part:
                continue

            try:
                page_num = int(part)
            except ValueError:
                raise ValidationError(
                    f"Invalid page number format: '{part}'",
                    details={"part": part, "expected": "integer"}
                )

            # Validate page number
            if page_num < 1:
                raise ValidationError(
                    f"Page number must be >= 1 (got {page_num})",
                    details={"page": page_num}
                )

            if page_num > total_pages:
                raise InsufficientPagesError(
                    required=page_num,
                    available=total_pages,
                    details={"page": page_num, "total_pages": total_pages}
                )

            page_numbers.append(page_num)

        # Remove duplicates and sort
        page_numbers = sorted(set(page_numbers))

        if not page_numbers:
            raise ValidationError(
                "No valid page numbers provided",
                details={"input": pages_str}
            )

        return page_numbers

    async def convert_to_images(
        self,
        input_path: Path,
        output_dir: Path,
        image_format: str = "png",
        dpi: int = 150,
        pages_str: str = "all"
    ) -> List[Dict[str, Any]]:
        """
        Convert PDF pages to images.

        Args:
            input_path: Path to input PDF file
            output_dir: Directory to save images
            image_format: Output image format (png, jpeg, tiff)
            dpi: Image resolution (DPI)
            pages_str: Pages to convert (e.g., "1,3,5" or "all")

        Returns:
            List of dicts with information about each generated image

        Raises:
            ValidationError: If input validation fails
            InvalidPDFError: If PDF file is invalid
            UnsupportedFormatError: If image format is not supported
            InsufficientPagesError: If requested pages don't exist
            PDFProcessingError: If conversion operation fails
        """
        # Validate inputs
        self._validate_convert_inputs(input_path, image_format, dpi)

        try:
            self.logger.info(
                f"Starting conversion of {input_path.name} to {image_format.upper()} "
                f"(DPI: {dpi}, Pages: {pages_str})"
            )

            # Get total page count
            try:
                # Quick count at low DPI
                test_images = convert_from_path(input_path, dpi=72, first_page=1, last_page=1)
                if not test_images:
                    raise InvalidPDFError(
                        f"Failed to read PDF file: {input_path.name}",
                        details={"file": input_path.name}
                    )

                # Get total pages by converting at low DPI
                all_images = convert_from_path(input_path, dpi=72)
                total_pages = len(all_images)
                self.logger.debug(f"PDF has {total_pages} pages")

            except Exception as e:
                if isinstance(e, InvalidPDFError):
                    raise
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

            # Parse which pages to convert
            page_numbers = self.parse_page_numbers(pages_str, total_pages)
            self.logger.info(f"Converting {len(page_numbers)} pages: {page_numbers}")

            results = []
            base_name = input_path.stem

            # Convert specified pages
            for page_num in page_numbers:
                self.logger.debug(f"Converting page {page_num}/{total_pages}")

                try:
                    # Convert single page at requested DPI
                    images = convert_from_path(
                        input_path,
                        dpi=dpi,
                        first_page=page_num,
                        last_page=page_num
                    )

                    if not images:
                        raise PDFProcessingError(
                            "conversion",
                            f"Failed to convert page {page_num}",
                            details={"page": page_num}
                        )

                    image = images[0]
                    output_filename = f"{base_name}_page{page_num}.{image_format.lower()}"
                    output_path = output_dir / output_filename

                    # Save image with format-specific settings
                    self._save_image(image, output_path, image_format)

                    file_size = output_path.stat().st_size
                    width, height = image.size

                    self.logger.debug(
                        f"Created {output_filename} ({width}x{height}, {file_size:,} bytes)"
                    )

                    results.append({
                        "filename": output_filename,
                        "size": file_size,
                        "page": page_num,
                        "format": image_format.upper(),
                        "dpi": dpi,
                        "width": width,
                        "height": height
                    })

                except Exception as e:
                    if isinstance(e, PDFProcessingError):
                        raise
                    raise PDFProcessingError(
                        "conversion",
                        f"Failed to convert page {page_num}: {str(e)}",
                        details={"page": page_num}
                    )

            self.logger.info(
                f"Successfully converted {len(results)} pages to {image_format.upper()}"
            )
            return results

        except (ValidationError, InvalidPDFError, UnsupportedFormatError, InsufficientPagesError):
            # Re-raise our custom exceptions
            raise

        except Exception as e:
            self.logger.error(f"Unexpected error during PDF conversion: {str(e)}", exc_info=True)
            raise PDFProcessingError(
                "conversion",
                str(e),
                details={
                    "file": input_path.name,
                    "format": image_format,
                    "dpi": dpi,
                    "pages": pages_str
                }
            )

    def _save_image(self, image, output_path: Path, image_format: str) -> None:
        """
        Save image with format-specific settings.

        Args:
            image: PIL Image object
            output_path: Path to save image
            image_format: Image format

        Raises:
            PDFProcessingError: If save fails
        """
        try:
            if image_format.lower() in ["jpg", "jpeg"]:
                image.save(output_path, "JPEG", quality=85, optimize=True)
            elif image_format.lower() == "png":
                image.save(output_path, "PNG", optimize=True)
            elif image_format.lower() in ["tiff", "tif"]:
                image.save(output_path, "TIFF", compression="tiff_deflate")
            else:
                image.save(output_path, image_format.upper())
        except Exception as e:
            raise PDFProcessingError(
                "conversion",
                f"Failed to save image: {str(e)}",
                details={"output_path": str(output_path), "format": image_format}
            )

    def _validate_convert_inputs(
        self,
        input_path: Path,
        image_format: str,
        dpi: int
    ) -> None:
        """
        Validate conversion operation inputs.

        Args:
            input_path: Path to input PDF
            image_format: Requested image format
            dpi: Requested DPI

        Raises:
            ValidationError: If validation fails
            UnsupportedFormatError: If format is not supported
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

        # Validate image format
        format_lower = image_format.lower()
        supported_formats = [fmt.lower() for fmt in self.settings.supported_image_formats]

        if format_lower not in supported_formats:
            raise UnsupportedFormatError(
                format=image_format,
                supported_formats=self.settings.supported_image_formats,
                details={"provided": image_format}
            )

        # Validate DPI is reasonable (50-600)
        if dpi < 50:
            raise ValidationError(
                f"DPI too low: {dpi} (minimum 50)",
                details={"dpi": dpi, "min": 50}
            )

        if dpi > 600:
            raise ValidationError(
                f"DPI too high: {dpi} (maximum 600)",
                details={"dpi": dpi, "max": 600}
            )
