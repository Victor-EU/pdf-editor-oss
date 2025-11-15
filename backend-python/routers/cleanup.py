"""
File Cleanup Router
Provides endpoints for manual cleanup triggers and monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import logging

from models import ApiResponse
from scheduler import get_scheduler
from config import Settings, get_settings


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/cleanup/run", response_model=ApiResponse[dict])
async def trigger_cleanup(
    dry_run: bool = Query(False, description="If true, only simulate cleanup without deleting"),
    force: bool = Query(False, description="If true, delete all files regardless of age"),
    settings: Settings = Depends(get_settings)
):
    """
    Manually trigger file cleanup operation.

    Args:
        dry_run: Simulate cleanup without actually deleting files
        force: Delete all files regardless of retention period

    Returns:
        Cleanup operation metrics and results
    """
    try:
        logger.info(f"Manual cleanup triggered (dry_run={dry_run}, force={force})")

        # Get scheduler and cleanup service
        scheduler = get_scheduler()
        cleanup_service = scheduler.cleanup_service

        # Run cleanup
        metrics = await cleanup_service.cleanup_old_files(
            dry_run=dry_run,
            force=force
        )

        message = "Dry run completed" if dry_run else "Cleanup completed successfully"
        if metrics.errors:
            message += f" with {len(metrics.errors)} errors"

        return ApiResponse.success_response(
            message=message,
            data=metrics.to_dict()
        )

    except Exception as e:
        logger.error(f"Error during manual cleanup: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Cleanup operation failed: {str(e)}"
        )


@router.get("/cleanup/stats", response_model=ApiResponse[dict])
async def get_cleanup_stats():
    """
    Get file cleanup service statistics and current directory status.

    Returns:
        Cleanup service stats including retention policy, last run, and directory info
    """
    try:
        scheduler = get_scheduler()
        cleanup_service = scheduler.cleanup_service

        stats = cleanup_service.get_service_stats()

        return ApiResponse.success_response(
            message="Cleanup statistics retrieved successfully",
            data=stats
        )

    except Exception as e:
        logger.error(f"Error getting cleanup stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cleanup stats: {str(e)}"
        )


@router.get("/cleanup/scheduler", response_model=ApiResponse[dict])
async def get_scheduler_status():
    """
    Get background scheduler status and job information.

    Returns:
        Scheduler status including active jobs and next run times
    """
    try:
        scheduler = get_scheduler()
        status = scheduler.get_scheduler_status()

        return ApiResponse.success_response(
            message="Scheduler status retrieved successfully",
            data=status
        )

    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scheduler status: {str(e)}"
        )


@router.post("/cleanup/test-notification")
async def test_cleanup_notification():
    """
    Test endpoint to verify cleanup notifications are working.
    Returns current retention policy for users to understand file lifecycle.
    """
    try:
        scheduler = get_scheduler()
        settings = scheduler.settings

        return ApiResponse.success_response(
            message="File retention policy",
            data={
                "retention_minutes": settings.file_retention_minutes,
                "cleanup_interval_minutes": settings.cleanup_interval_minutes,
                "message": f"Files are automatically deleted {settings.file_retention_minutes} minutes after creation. "
                           f"Please download your files promptly.",
                "recommendation": "Download files immediately after processing"
            }
        )

    except Exception as e:
        logger.error(f"Error in test notification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed: {str(e)}"
        )
