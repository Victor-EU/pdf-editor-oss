"""
PDF Split Service
Splits PDF files by page ranges using pikepdf.
Production-ready OOP implementation with proper error handling.
"""

import pikepdf
from pathlib import Path
from typing import List, Tuple, Dict, Any
import logging
import re

from exceptions import (
    PDFProcessingError,
    InvalidPDFError,
    ValidationError,
    InsufficientPagesError
)
from config import Settings

logger = logging.getLogger(__name__)


class PdfSplitService:
    """
    Service for splitting PDF files by page ranges.
    Implements proper OOP with instance methods and dependency injection.
    """

    def __init__(self, settings: Settings):
        """
        Initialize PDF Split Service with configuration.

        Args:
            settings: Application settings instance
        """
        self.settings = settings
        self.logger = logger
        self.logger.info("PdfSplitService initialized")

    async def split_pdf(
        self,
        input_path: Path,
        page_ranges_str: str,
        output_dir: Path,
        output_prefix: str = "split",
        split_mode: str = "ranges"
    ) -> List[Dict[str, Any]]:
        """
        Split a PDF file by page ranges.

        Args:
            input_path: Path to input PDF file
            page_ranges_str: Page ranges string (e.g., "1-3,5-7,10")
            output_dir: Directory to save split PDFs
            output_prefix: Prefix for output filenames

        Returns:
            List of dicts with information about each split PDF

        Raises:
            ValidationError: If input validation fails
            InvalidPDFError: If PDF file is invalid
            InsufficientPagesError: If requested pages don't exist
            PDFProcessingError: If split operation fails
        """
        # Validate inputs
        self._validate_split_inputs(input_path, page_ranges_str)

        source_pdf = None
        split_pdfs = []

        try:
            self.logger.info(f"Starting split operation for {input_path.name} with ranges: {page_ranges_str}")

            # Open the source PDF
            try:
                source_pdf = pikepdf.Pdf.open(input_path)
                total_pages = len(source_pdf.pages)
                self.logger.debug(f"PDF has {total_pages} pages")
            except pikepdf.PdfError as e:
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

            # Handle split mode
            if split_mode == "pages":
                # Convert split points to ranges (split AT these pages)
                ranges = self._convert_split_points_to_ranges(page_ranges_str, total_pages)
                self.logger.debug(f"Split mode: AT pages. Generated {len(ranges)} ranges: {ranges}")
            else:
                # Parse as page ranges (extract specific ranges)
                ranges = self._parse_page_ranges(page_ranges_str, total_pages)
                self.logger.debug(f"Range mode: Parsed {len(ranges)} ranges: {ranges}")

            results = []

            # Create a split PDF for each range
            for idx, (start, end) in enumerate(ranges, 1):
                output_filename = f"{output_prefix}_part{idx}.pdf"
                output_path = output_dir / output_filename

                self.logger.debug(f"Creating split {idx}/{len(ranges)}: pages {start+1}-{end+1}")

                # Create new PDF with selected pages
                split_pdf = pikepdf.Pdf.new()
                split_pdfs.append(split_pdf)  # Track for cleanup

                try:
                    for page_num in range(start, end + 1):
                        split_pdf.pages.append(source_pdf.pages[page_num])

                    # Save split PDF
                    split_pdf.save(output_path)

                    file_size = output_path.stat().st_size
                    page_count = end - start + 1

                    self.logger.info(
                        f"Created {output_filename}: pages {start+1}-{end+1} "
                        f"({page_count} pages, {file_size:,} bytes)"
                    )

                    results.append({
                        "filename": output_filename,
                        "pages": page_count,
                        "size": file_size,
                        "page_range": f"{start+1}-{end+1}"
                    })

                except Exception as e:
                    raise PDFProcessingError(
                        "split",
                        f"Failed to create split part {idx}: {str(e)}",
                        details={"part": idx, "range": f"{start+1}-{end+1}"}
                    )

            self.logger.info(f"Successfully split PDF into {len(results)} parts")
            return results

        except (ValidationError, InvalidPDFError, InsufficientPagesError):
            # Re-raise our custom exceptions
            raise

        except Exception as e:
            self.logger.error(f"Unexpected error during PDF split: {str(e)}", exc_info=True)
            raise PDFProcessingError(
                "split",
                str(e),
                details={"file": input_path.name, "ranges": page_ranges_str}
            )

        finally:
            # Cleanup resources
            if source_pdf is not None:
                try:
                    source_pdf.close()
                except:
                    pass

            for split_pdf in split_pdfs:
                try:
                    split_pdf.close()
                except:
                    pass

    def _convert_split_points_to_ranges(self, points_str: str, total_pages: int) -> List[Tuple[int, int]]:
        """
        Convert split points to page ranges.

        Example: points_str="3,7" with total_pages=10 becomes:
        - Part 1: pages 1-3 (0-indexed: 0-2)
        - Part 2: pages 4-7 (0-indexed: 3-6)
        - Part 3: pages 8-10 (0-indexed: 7-9)

        Args:
            points_str: Comma-separated split points (e.g., "3,7")
            total_pages: Total number of pages in PDF

        Returns:
            List of (start_page, end_page) tuples (0-indexed)

        Raises:
            ValidationError: If split points are invalid
        """
        ranges = []
        parts = points_str.split(',')
        split_points = []

        # Parse and validate split points
        for part in parts:
            part = part.strip()
            if not part:
                continue

            try:
                point = int(part)
            except ValueError:
                raise ValidationError(
                    f"Invalid split point: '{part}' (must be a number)",
                    details={"point": part}
                )

            if point < 1:
                raise ValidationError(
                    f"Split point must be >= 1 (got {point})",
                    details={"point": point}
                )

            if point > total_pages:
                raise InsufficientPagesError(
                    required=point,
                    available=total_pages,
                    details={"point": point, "total_pages": total_pages}
                )

            split_points.append(point)

        if not split_points:
            raise ValidationError(
                "No valid split points provided",
                details={"input": points_str}
            )

        # Sort split points
        split_points.sort()

        # Convert to ranges
        start = 1
        for point in split_points:
            ranges.append((start - 1, point - 1))  # Convert to 0-indexed
            start = point + 1

        # Add final range if there are remaining pages
        if start <= total_pages:
            ranges.append((start - 1, total_pages - 1))

        return ranges

    def _parse_page_ranges(self, range_str: str, total_pages: int) -> List[Tuple[int, int]]:
        """
        Parse page range string into list of (start, end) tuples.

        Args:
            range_str: Page range string (e.g., "1-3,5-7,10")
            total_pages: Total number of pages in PDF

        Returns:
            List of (start_page, end_page) tuples (0-indexed)

        Raises:
            ValidationError: If range string is invalid
            InsufficientPagesError: If requested pages don't exist
        """
        ranges = []
        parts = range_str.split(',')

        for part in parts:
            part = part.strip()

            if not part:
                continue

            try:
                if '-' in part:
                    # Range like "1-3"
                    start_str, end_str = part.split('-', 1)
                    start, end = int(start_str.strip()), int(end_str.strip())
                else:
                    # Single page like "5"
                    start = end = int(part)

            except ValueError:
                raise ValidationError(
                    f"Invalid page range format: '{part}'",
                    details={"range": part, "expected_format": "1-3 or 5"}
                )

            # Validate range
            if start < 1:
                raise ValidationError(
                    f"Page numbers must be >= 1 (got {start})",
                    details={"start": start}
                )

            if end < 1:
                raise ValidationError(
                    f"Page numbers must be >= 1 (got {end})",
                    details={"end": end}
                )

            if start > end:
                raise ValidationError(
                    f"Invalid range: {start}-{end} (start > end)",
                    details={"start": start, "end": end}
                )

            if start > total_pages:
                raise InsufficientPagesError(
                    required=start,
                    available=total_pages,
                    details={"range": part, "total_pages": total_pages}
                )

            if end > total_pages:
                raise InsufficientPagesError(
                    required=end,
                    available=total_pages,
                    details={"range": part, "total_pages": total_pages}
                )

            # Convert to 0-indexed
            ranges.append((start - 1, end - 1))

        if not ranges:
            raise ValidationError(
                "No valid page ranges provided",
                details={"input": range_str}
            )

        return ranges

    def _validate_split_inputs(self, input_path: Path, page_ranges_str: str) -> None:
        """
        Validate split operation inputs.

        Args:
            input_path: Path to input PDF
            page_ranges_str: Page ranges string

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

        if not page_ranges_str or not page_ranges_str.strip():
            raise ValidationError(
                "Page ranges string cannot be empty",
                details={"provided": page_ranges_str}
            )
