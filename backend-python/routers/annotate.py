"""
API Routes for PDF Annotation and Redaction
Provides endpoints for adding annotations and redactions to PDFs
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid
import json
import logging

from config import Settings, get_settings
from services.pdf_annotate import (
    get_annotation_service,
    AnnotationData,
    AnnotationType
)
from models import ApiResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/annotate", response_model=ApiResponse[dict])
async def annotate_pdf(
    file: UploadFile = File(..., description="PDF file to annotate"),
    annotations: str = Form(..., description="JSON string of annotations array"),
    settings: Settings = Depends(get_settings)
):
    """
    Add annotations to a PDF

    **Annotation Format:**
    ```json
    [
        {
            "annotation_type": "highlight|text|underline|strikeout|square|circle|line|arrow|freehand",
            "page_number": 0,
            "coordinates": [x0, y0, x1, y1],
            "color": [r, g, b],  // RGB 0-1, optional
            "text": "Note text",  // Optional, for text annotations
            "opacity": 0.5,  // Optional, 0-1
            "border_width": 1.0  // Optional
        }
    ]
    ```

    **Supported Annotation Types:**
    - `text`: Text comment/sticky note
    - `highlight`: Yellow highlighter effect
    - `underline`: Underline text
    - `strikeout`: Strike through text
    - `square`: Rectangle shape
    - `circle`: Circle/ellipse shape
    - `line`: Straight line
    - `arrow`: Arrow line
    - `freehand`: Freehand drawing (coordinates is flat array of points)

    Returns annotated PDF file for download.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Generate unique filename
    unique_id = str(uuid.uuid4())[:8]
    input_file = settings.upload_dir / f"annotate_input_{unique_id}.pdf"
    output_file = settings.output_dir / f"annotated_{unique_id}.pdf"

    try:
        # Save uploaded file
        content = await file.read()
        input_file.write_bytes(content)

        # Parse annotations
        try:
            annotations_data = json.loads(annotations)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format for annotations")

        # Convert to AnnotationData objects
        annot_objects = []
        for annot_dict in annotations_data:
            try:
                annot_type = AnnotationType(annot_dict["annotation_type"])
                annot = AnnotationData(
                    annotation_type=annot_type,
                    page_number=annot_dict["page_number"],
                    coordinates=annot_dict["coordinates"],
                    color=tuple(annot_dict.get("color", [1.0, 1.0, 0.0])),
                    text=annot_dict.get("text"),
                    opacity=annot_dict.get("opacity", 0.5),
                    border_width=annot_dict.get("border_width", 1.0)
                )
                annot_objects.append(annot)
            except (KeyError, ValueError) as e:
                logger.warning(f"Skipping invalid annotation: {str(e)}")
                continue

        if not annot_objects:
            raise HTTPException(status_code=400, detail="No valid annotations provided")

        # Add annotations
        annotation_service = get_annotation_service()
        result = annotation_service.add_annotations(
            input_path=input_file,
            output_path=output_file,
            annotations=annot_objects
        )

        return ApiResponse.success_response(
            message=f"Successfully added {result['annotations_added']} annotations",
            data={
                **result,
                "download_url": f"/api/download/{output_file.name}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Annotation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Annotation failed: {str(e)}")
    finally:
        # Cleanup input file
        if input_file.exists():
            input_file.unlink()


@router.post("/redact", response_model=ApiResponse[dict])
async def redact_pdf(
    file: UploadFile = File(..., description="PDF file to redact"),
    redactions: str = Form(..., description="JSON string of redaction areas"),
    fill_color: Optional[str] = Form("[0, 0, 0]", description="RGB fill color (0-1)"),
    settings: Settings = Depends(get_settings)
):
    """
    Apply redactions to a PDF (permanently removes content)

    **Redaction Format:**
    ```json
    [
        {
            "page": 0,
            "rect": [x0, y0, x1, y1]  // Area to redact
        },
        {
            "page": 1,
            "text": "Social Security Number"  // Redact specific text
        }
    ]
    ```

    **Important:**
    - Redaction permanently removes content from the PDF
    - Redacted areas are filled with the specified color (default: black)
    - You can redact by area (rect) or by text search

    Returns redacted PDF file for download.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Generate unique filename
    unique_id = str(uuid.uuid4())[:8]
    input_file = settings.upload_dir / f"redact_input_{unique_id}.pdf"
    output_file = settings.output_dir / f"redacted_{unique_id}.pdf"

    try:
        # Save uploaded file
        content = await file.read()
        input_file.write_bytes(content)

        # Parse redactions
        try:
            redaction_areas = json.loads(redactions)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format for redactions")

        # Parse fill color
        try:
            fill_color_tuple = tuple(json.loads(fill_color))
        except:
            fill_color_tuple = (0, 0, 0)  # Default black

        # Apply redactions
        annotation_service = get_annotation_service()
        result = annotation_service.add_redactions(
            input_path=input_file,
            output_path=output_file,
            redaction_areas=redaction_areas,
            fill_color=fill_color_tuple
        )

        return ApiResponse.success_response(
            message=f"Successfully applied {result['redactions_applied']} redactions",
            data={
                **result,
                "download_url": f"/api/download/{output_file.name}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Redaction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Redaction failed: {str(e)}")
    finally:
        # Cleanup input file
        if input_file.exists():
            input_file.unlink()


@router.get("/annotation-types")
async def get_annotation_types():
    """
    Get list of supported annotation types

    Returns all available annotation types with descriptions.
    """
    annotation_types = {
        "text": "Text comment or sticky note",
        "highlight": "Highlight text with color",
        "underline": "Underline text",
        "strikeout": "Strike through text",
        "square": "Draw rectangle",
        "circle": "Draw circle or ellipse",
        "line": "Draw straight line",
        "arrow": "Draw arrow",
        "freehand": "Freehand drawing",
        "redact": "Redaction marker (use /redact endpoint to apply)"
    }

    return ApiResponse.success_response(
        message="Annotation types retrieved",
        data={
            "types": annotation_types,
            "default_colors": {
                "highlight": [1.0, 1.0, 0.0],  # Yellow
                "text": [1.0, 0.0, 0.0],  # Red
                "underline": [0.0, 0.0, 1.0],  # Blue
                "redact": [0.0, 0.0, 0.0],  # Black
                "default": [1.0, 1.0, 0.0]  # Yellow
            }
        }
    )
