"""
Response builder utilities for API endpoints
Centralized response creation logic
"""

from typing import Dict, Any, List, Optional
from models import ApiResponse, FileResponse


class ResponseBuilder:
    """Centralized response building for PDF operations"""

    @staticmethod
    def build_file_response(
        result: Dict[str, Any],
        message: Optional[str] = None
    ) -> ApiResponse[FileResponse]:
        """
        Build a standard file response from service result

        Args:
            result: Dictionary containing service result data
            message: Optional custom success message

        Returns:
            ApiResponse with FileResponse data
        """
        file_response = FileResponse(
            file_name=result.get("filename"),
            file_path=None,  # Not needed for downloads
            file_size=result.get("size") or result.get("compressed_size"),
            download_url=f"/download/{result.get('filename')}",
            original_size=result.get("original_size"),
            compression_ratio=result.get("compression_ratio"),
            pages=result.get("pages")
        )

        default_message = message or "Operation completed successfully"
        return ApiResponse.success_response(default_message, file_response)

    @staticmethod
    def build_multiple_files_response(
        results: List[Dict[str, Any]],
        message: Optional[str] = None
    ) -> ApiResponse[List[FileResponse]]:
        """
        Build response for multiple files from service results

        Args:
            results: List of dictionaries containing service result data
            message: Optional custom success message

        Returns:
            ApiResponse with list of FileResponse data
        """
        file_responses = [
            FileResponse(
                file_name=result.get("filename"),
                file_path=None,
                file_size=result.get("size"),
                download_url=f"/download/{result.get('filename')}",
                original_size=result.get("original_size"),
                compression_ratio=result.get("compression_ratio"),
                pages=result.get("pages")
            )
            for result in results
        ]

        default_message = message or f"{len(file_responses)} file(s) processed successfully"
        return ApiResponse.success_response(default_message, file_responses)

    @staticmethod
    def build_compression_message(result: Dict[str, Any]) -> str:
        """
        Build specific message for compression operations

        Args:
            result: Dictionary containing compression result data

        Returns:
            Formatted compression message
        """
        compression_ratio = result.get("compression_ratio", 0)
        return f"PDF compressed successfully. Size reduced by {compression_ratio}%"

    @staticmethod
    def build_extraction_message(result: Dict[str, Any]) -> str:
        """
        Build specific message for text extraction operations

        Args:
            result: Dictionary containing extraction result data

        Returns:
            Formatted extraction message
        """
        characters = result.get("characters", 0)
        pages = result.get("pages", 0)
        return f"Extracted {characters} characters from {pages} pages"

    @staticmethod
    def build_conversion_message(result: Dict[str, Any], image_format: str) -> str:
        """
        Build specific message for conversion operations

        Args:
            result: Dictionary containing conversion result data
            image_format: The image format used

        Returns:
            Formatted conversion message
        """
        if isinstance(result, list):
            count = len(result)
            return f"PDF converted to {count} {image_format.upper()} image(s)"
        return f"PDF converted to {image_format.upper()}"

    @staticmethod
    def build_split_message(results: List[Dict[str, Any]]) -> str:
        """
        Build specific message for split operations

        Args:
            results: List of dictionaries containing split result data

        Returns:
            Formatted split message
        """
        count = len(results)
        return f"PDF split into {count} files"
