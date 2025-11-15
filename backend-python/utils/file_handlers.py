"""
File handling utilities for PDF operations
Centralized file upload, validation, and cleanup logic
"""

import uuid
import aiofiles
import logging
import re
from pathlib import Path
from typing import Optional, List
from fastapi import UploadFile, HTTPException

from config import Settings

logger = logging.getLogger(__name__)


class FileHandler:
    """Centralized file handling for PDF operations"""

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize user-provided filename to prevent path traversal attacks

        Security measures:
        1. Remove path separators (/, \)
        2. Remove parent directory references (..)
        3. Remove null bytes
        4. Keep only safe characters (alphanumeric, dash, underscore, dot)
        5. Limit length to prevent DoS
        6. Ensure filename is not empty after sanitization

        Args:
            filename: Original filename from user input

        Returns:
            Sanitized filename safe for filesystem use

        Raises:
            HTTPException: If filename is invalid or dangerous
        """
        if not filename:
            raise HTTPException(status_code=400, detail="Filename cannot be empty")

        # Remove any path separators and null bytes
        filename = filename.replace('/', '').replace('\\', '').replace('\0', '')

        # Remove parent directory references
        filename = filename.replace('..', '')

        # Get basename to remove any remaining path components
        filename = Path(filename).name

        # Only allow safe characters: alphanumeric, dash, underscore, dot
        # This regex keeps letters, numbers, -, _, and .
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

        # Remove leading/trailing dots and spaces (security & filesystem compatibility)
        filename = filename.strip('. ')

        # Limit length to prevent DoS (max 255 is filesystem limit, use 200 for safety)
        max_length = 200
        if len(filename) > max_length:
            # Preserve extension if possible
            name_parts = filename.rsplit('.', 1)
            if len(name_parts) == 2:
                name, ext = name_parts
                filename = name[:max_length - len(ext) - 1] + '.' + ext
            else:
                filename = filename[:max_length]

        # Ensure filename is not empty after sanitization
        if not filename or filename == '.pdf':
            filename = f"unnamed_{uuid.uuid4().hex[:8]}.pdf"

        # Ensure it has .pdf extension
        if not filename.endswith('.pdf'):
            filename += '.pdf'

        logger.debug(f"Sanitized filename: {filename}")
        return filename

    @staticmethod
    def validate_pdf_file(file: UploadFile) -> None:
        """
        Validate that uploaded file is a PDF

        Args:
            file: The uploaded file to validate

        Raises:
            HTTPException: If file is not a valid PDF
        """
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.filename} (must be PDF)"
            )

        # Optional: Also check content type if provided
        if file.content_type and file.content_type != 'application/pdf':
            logger.warning(f"Content type mismatch: {file.content_type} for {file.filename}")

    @staticmethod
    async def save_upload_file(
        file: UploadFile,
        settings: Settings,
        validate: bool = True
    ) -> Path:
        """
        Save uploaded file to temporary location

        Args:
            file: The uploaded file
            settings: Application settings
            validate: Whether to validate PDF format (default: True)

        Returns:
            Path to saved temporary file

        Raises:
            HTTPException: If validation fails or filename is dangerous
        """
        if validate:
            FileHandler.validate_pdf_file(file)

        # Sanitize filename to prevent path traversal attacks
        safe_filename = FileHandler.sanitize_filename(file.filename or "unnamed.pdf")

        # Generate unique temporary path with sanitized filename
        temp_path = settings.upload_dir / f"{uuid.uuid4()}_{safe_filename}"

        # Save file asynchronously
        async with aiofiles.open(temp_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        logger.debug(f"Saved {file.filename} to {temp_path}")
        return temp_path

    @staticmethod
    async def save_multiple_files(
        files: List[UploadFile],
        settings: Settings,
        validate: bool = True
    ) -> List[Path]:
        """
        Save multiple uploaded files to temporary locations

        Args:
            files: List of uploaded files
            settings: Application settings
            validate: Whether to validate PDF format (default: True)

        Returns:
            List of paths to saved temporary files

        Raises:
            HTTPException: If any validation fails
        """
        temp_paths = []

        for file in files:
            temp_path = await FileHandler.save_upload_file(file, settings, validate)
            temp_paths.append(temp_path)

        return temp_paths

    @staticmethod
    async def cleanup_files(*file_paths: Path) -> None:
        """
        Clean up temporary files

        Args:
            *file_paths: Variable number of file paths to clean up
        """
        for file_path in file_paths:
            if file_path and isinstance(file_path, Path):
                try:
                    if file_path.exists():
                        file_path.unlink()
                        logger.debug(f"Cleaned up temporary file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {file_path}: {str(e)}")

    @staticmethod
    async def cleanup_file_list(file_paths: List[Path]) -> None:
        """
        Clean up a list of temporary files

        Args:
            file_paths: List of file paths to clean up
        """
        for file_path in file_paths:
            try:
                if file_path.exists():
                    file_path.unlink()
                    logger.debug(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up {file_path}: {str(e)}")
