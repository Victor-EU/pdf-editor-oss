"""
PDF Annotation and Redaction Service using PyMuPDF (fitz)
Provides comprehensive annotation and redaction capabilities for PDFs
"""

import fitz  # PyMuPDF
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AnnotationType(str, Enum):
    """Supported annotation types"""
    TEXT = "text"  # Text comment/note
    HIGHLIGHT = "highlight"  # Yellow highlighter
    UNDERLINE = "underline"  # Underline text
    STRIKEOUT = "strikeout"  # Strike through text
    SQUARE = "square"  # Rectangle
    CIRCLE = "circle"  # Circle/Ellipse
    LINE = "line"  # Line
    ARROW = "arrow"  # Arrow
    FREEHAND = "freehand"  # Freehand drawing
    REDACT = "redact"  # Redaction annotation


@dataclass
class AnnotationData:
    """Data class for annotation information"""
    annotation_type: AnnotationType
    page_number: int
    coordinates: List[float]  # [x0, y0, x1, y1] or list of points for freehand
    color: Tuple[float, float, float] = (1.0, 1.0, 0.0)  # RGB (0-1), default yellow
    text: Optional[str] = None  # For text annotations
    opacity: float = 0.5  # 0.0 to 1.0
    border_width: float = 1.0


class PdfAnnotationService:
    """Service for adding annotations and redactions to PDFs"""

    def __init__(self):
        self.logger = logger

    def add_annotations(
        self,
        input_path: Path,
        output_path: Path,
        annotations: List[AnnotationData]
    ) -> Dict[str, Any]:
        """
        Add multiple annotations to a PDF

        Args:
            input_path: Path to input PDF
            output_path: Path for output PDF
            annotations: List of annotations to add

        Returns:
            Dictionary with operation results
        """
        self.logger.info(f"Adding {len(annotations)} annotations to PDF")

        try:
            # Open PDF
            doc = fitz.open(input_path)
            annotations_added = 0

            for annot_data in annotations:
                try:
                    page = doc[annot_data.page_number]

                    if annot_data.annotation_type == AnnotationType.TEXT:
                        self._add_text_annotation(page, annot_data)
                    elif annot_data.annotation_type == AnnotationType.HIGHLIGHT:
                        self._add_highlight(page, annot_data)
                    elif annot_data.annotation_type == AnnotationType.UNDERLINE:
                        self._add_underline(page, annot_data)
                    elif annot_data.annotation_type == AnnotationType.STRIKEOUT:
                        self._add_strikeout(page, annot_data)
                    elif annot_data.annotation_type == AnnotationType.SQUARE:
                        self._add_square(page, annot_data)
                    elif annot_data.annotation_type == AnnotationType.CIRCLE:
                        self._add_circle(page, annot_data)
                    elif annot_data.annotation_type == AnnotationType.LINE:
                        self._add_line(page, annot_data)
                    elif annot_data.annotation_type == AnnotationType.ARROW:
                        self._add_arrow(page, annot_data)
                    elif annot_data.annotation_type == AnnotationType.FREEHAND:
                        self._add_freehand(page, annot_data)
                    elif annot_data.annotation_type == AnnotationType.REDACT:
                        self._add_redaction_mark(page, annot_data)

                    annotations_added += 1

                except Exception as e:
                    self.logger.error(f"Failed to add annotation: {str(e)}")
                    continue

            # Save annotated PDF
            doc.save(output_path, garbage=4, deflate=True)
            doc.close()

            self.logger.info(f"Successfully added {annotations_added} annotations")

            return {
                "success": True,
                "annotations_added": annotations_added,
                "output_file": str(output_path),
                "file_size": output_path.stat().st_size
            }

        except Exception as e:
            self.logger.error(f"Annotation failed: {str(e)}")
            raise RuntimeError(f"Failed to annotate PDF: {str(e)}")

    def add_redactions(
        self,
        input_path: Path,
        output_path: Path,
        redaction_areas: List[Dict[str, Any]],
        fill_color: Tuple[float, float, float] = (0, 0, 0)  # Black by default
    ) -> Dict[str, Any]:
        """
        Add redactions to a PDF (permanently removes content)

        Args:
            input_path: Path to input PDF
            output_path: Path for output PDF
            redaction_areas: List of areas to redact [{page: int, rect: [x0,y0,x1,y1]}]
            fill_color: RGB color (0-1) to fill redacted areas

        Returns:
            Dictionary with operation results
        """
        self.logger.info(f"Adding {len(redaction_areas)} redactions to PDF")

        try:
            doc = fitz.open(input_path)
            redactions_applied = 0

            for redaction in redaction_areas:
                try:
                    page_num = redaction.get("page", 0)
                    rect = redaction.get("rect", [])
                    text = redaction.get("text", None)  # Optional: redact specific text

                    page = doc[page_num]

                    if text:
                        # Redact specific text
                        text_instances = page.search_for(text)
                        for inst in text_instances:
                            page.add_redact_annot(inst, fill=fill_color)
                    else:
                        # Redact area
                        redact_rect = fitz.Rect(rect)
                        page.add_redact_annot(redact_rect, fill=fill_color)

                    redactions_applied += 1

                except Exception as e:
                    self.logger.error(f"Failed to add redaction: {str(e)}")
                    continue

            # Apply all redactions (this permanently removes content)
            for page in doc:
                page.apply_redactions()

            # Save redacted PDF
            doc.save(output_path, garbage=4, deflate=True)
            doc.close()

            self.logger.info(f"Successfully applied {redactions_applied} redactions")

            return {
                "success": True,
                "redactions_applied": redactions_applied,
                "output_file": str(output_path),
                "file_size": output_path.stat().st_size
            }

        except Exception as e:
            self.logger.error(f"Redaction failed: {str(e)}")
            raise RuntimeError(f"Failed to redact PDF: {str(e)}")

    def _add_text_annotation(self, page: fitz.Page, annot_data: AnnotationData):
        """Add a text comment annotation"""
        rect = fitz.Rect(annot_data.coordinates)
        annot = page.add_text_annot(rect.tl, annot_data.text or "Note")
        annot.set_colors(stroke=annot_data.color)
        annot.set_opacity(annot_data.opacity)
        annot.update()

    def _add_highlight(self, page: fitz.Page, annot_data: AnnotationData):
        """Add highlight annotation"""
        rect = fitz.Rect(annot_data.coordinates)
        annot = page.add_highlight_annot(rect)
        annot.set_colors(stroke=annot_data.color)
        annot.set_opacity(annot_data.opacity)
        annot.update()

    def _add_underline(self, page: fitz.Page, annot_data: AnnotationData):
        """Add underline annotation"""
        rect = fitz.Rect(annot_data.coordinates)
        annot = page.add_underline_annot(rect)
        annot.set_colors(stroke=annot_data.color)
        annot.update()

    def _add_strikeout(self, page: fitz.Page, annot_data: AnnotationData):
        """Add strikeout annotation"""
        rect = fitz.Rect(annot_data.coordinates)
        annot = page.add_strikeout_annot(rect)
        annot.set_colors(stroke=annot_data.color)
        annot.update()

    def _add_square(self, page: fitz.Page, annot_data: AnnotationData):
        """Add rectangle annotation"""
        rect = fitz.Rect(annot_data.coordinates)
        annot = page.add_rect_annot(rect)
        annot.set_colors(stroke=annot_data.color)
        annot.set_opacity(annot_data.opacity)
        annot.set_border(width=annot_data.border_width)
        annot.update()

    def _add_circle(self, page: fitz.Page, annot_data: AnnotationData):
        """Add circle/ellipse annotation"""
        rect = fitz.Rect(annot_data.coordinates)
        annot = page.add_circle_annot(rect)
        annot.set_colors(stroke=annot_data.color)
        annot.set_opacity(annot_data.opacity)
        annot.set_border(width=annot_data.border_width)
        annot.update()

    def _add_line(self, page: fitz.Page, annot_data: AnnotationData):
        """Add line annotation"""
        coords = annot_data.coordinates
        p1 = fitz.Point(coords[0], coords[1])
        p2 = fitz.Point(coords[2], coords[3])
        annot = page.add_line_annot(p1, p2)
        annot.set_colors(stroke=annot_data.color)
        annot.set_border(width=annot_data.border_width)
        annot.update()

    def _add_arrow(self, page: fitz.Page, annot_data: AnnotationData):
        """Add arrow annotation"""
        coords = annot_data.coordinates
        p1 = fitz.Point(coords[0], coords[1])
        p2 = fitz.Point(coords[2], coords[3])
        annot = page.add_line_annot(p1, p2)
        annot.set_colors(stroke=annot_data.color)
        annot.set_border(width=annot_data.border_width)
        # Add arrowhead at the end
        annot.set_line_ends(0, 2)  # 2 = arrow
        annot.update()

    def _add_freehand(self, page: fitz.Page, annot_data: AnnotationData):
        """Add freehand drawing annotation"""
        # Freehand requires list of points
        points = annot_data.coordinates
        if len(points) < 4:
            return

        # Convert flat list to list of Points
        point_list = [fitz.Point(points[i], points[i+1]) for i in range(0, len(points)-1, 2)]

        annot = page.add_ink_annot([point_list])  # ink_annot expects list of point lists
        annot.set_colors(stroke=annot_data.color)
        annot.set_border(width=annot_data.border_width)
        annot.set_opacity(annot_data.opacity)
        annot.update()

    def _add_redaction_mark(self, page: fitz.Page, annot_data: AnnotationData):
        """Add redaction mark (not applied yet - needs apply_redactions())"""
        rect = fitz.Rect(annot_data.coordinates)
        page.add_redact_annot(rect, fill=(0, 0, 0))  # Black fill


# Singleton instance
_annotation_service: Optional[PdfAnnotationService] = None


def get_annotation_service() -> PdfAnnotationService:
    """Get or create annotation service instance"""
    global _annotation_service
    if _annotation_service is None:
        _annotation_service = PdfAnnotationService()
    return _annotation_service
