"""
File Download Router
Production-ready implementation with proper DI
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pathlib import Path
import logging

from config import Settings, get_settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/download/{filename}")
async def download_file(
    filename: str,
    settings: Settings = Depends(get_settings)
):
    """Download a processed file"""
    try:
        # Security: Prevent path traversal
        file_path = (settings.output_dir / filename).resolve()

        # Ensure the file is within output_dir
        if not str(file_path).startswith(str(settings.output_dir.resolve())):
            logger.warning(f"Path traversal attempt detected: {filename}")
            raise HTTPException(status_code=400, detail="Invalid filename")

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/octet-stream"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in download endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
