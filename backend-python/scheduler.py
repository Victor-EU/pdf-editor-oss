"""
Background Scheduler for Automated Tasks
Manages periodic tasks like file cleanup using APScheduler.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

from config import Settings, get_settings
from services.file_cleanup import FileCleanupService


logger = logging.getLogger(__name__)


class BackgroundScheduler:
    """
    Manages background scheduled tasks using APScheduler.

    Features:
    - Automatic file cleanup on configurable interval
    - Error handling and recovery
    - Graceful shutdown
    - Task monitoring and logging
    """

    def __init__(self, settings: Settings):
        """
        Initialize background scheduler.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.logger = logger
        self.scheduler = AsyncIOScheduler()
        self.cleanup_service = FileCleanupService(settings)
        self._is_running = False

        self.logger.info("BackgroundScheduler initialized")

    async def start(self):
        """Start the scheduler and add all jobs"""
        if self._is_running:
            self.logger.warning("Scheduler already running")
            return

        try:
            # Add file cleanup job if enabled
            if self.settings.auto_cleanup_enabled:
                self.scheduler.add_job(
                    func=self._run_file_cleanup,
                    trigger=IntervalTrigger(minutes=self.settings.cleanup_interval_minutes),
                    id="file_cleanup",
                    name="Automatic File Cleanup",
                    replace_existing=True,
                    max_instances=1,  # Prevent overlapping runs
                    coalesce=True,  # If missed, run once when scheduler restarts
                    misfire_grace_time=300  # Allow 5 minutes grace for missed jobs
                )

                self.logger.info(
                    f"Scheduled file cleanup job: every {self.settings.cleanup_interval_minutes} minutes"
                )

                # Run initial cleanup on startup (after 30 seconds delay)
                self.scheduler.add_job(
                    func=self._run_file_cleanup,
                    trigger='date',
                    run_date=datetime.now(),
                    id="file_cleanup_startup",
                    name="Initial File Cleanup on Startup",
                    replace_existing=True
                )

                self.logger.info("Scheduled initial cleanup job on startup")
            else:
                self.logger.info("Automatic file cleanup is disabled")

            # Start the scheduler
            self.scheduler.start()
            self._is_running = True

            self.logger.info("Background scheduler started successfully")
            self.logger.info(f"Active jobs: {len(self.scheduler.get_jobs())}")

        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {str(e)}", exc_info=True)
            raise

    async def shutdown(self):
        """Gracefully shutdown the scheduler"""
        if not self._is_running:
            return

        try:
            self.logger.info("Shutting down background scheduler...")

            # Wait for running jobs to complete (max 30 seconds)
            self.scheduler.shutdown(wait=True)

            self._is_running = False
            self.logger.info("Background scheduler shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during scheduler shutdown: {str(e)}", exc_info=True)

    async def _run_file_cleanup(self):
        """
        Execute file cleanup task.
        Wrapped with comprehensive error handling and logging.
        """
        job_start = datetime.now()
        self.logger.info("=" * 70)
        self.logger.info(f"FILE CLEANUP JOB STARTED at {job_start.isoformat()}")
        self.logger.info("=" * 70)

        try:
            # Run cleanup
            metrics = await self.cleanup_service.cleanup_old_files(
                dry_run=False,
                force=False
            )

            # Log results
            self.logger.info("FILE CLEANUP JOB COMPLETED")
            self.logger.info(f"Results: {metrics.to_dict()}")

            # Check for errors
            if metrics.errors:
                self.logger.warning(
                    f"Cleanup completed with {len(metrics.errors)} errors"
                )
            else:
                self.logger.info("Cleanup completed successfully with no errors")

        except Exception as e:
            self.logger.error(
                f"File cleanup job failed with exception: {str(e)}",
                exc_info=True
            )

        finally:
            job_end = datetime.now()
            duration = (job_end - job_start).total_seconds()
            self.logger.info(f"Job duration: {duration:.2f} seconds")
            self.logger.info("=" * 70)

    def get_scheduler_status(self) -> dict:
        """
        Get current scheduler status and job information.

        Returns:
            Dictionary with scheduler status
        """
        if not self._is_running:
            return {
                "running": False,
                "message": "Scheduler is not running"
            }

        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })

        return {
            "running": True,
            "state": "running" if self._is_running else "stopped",
            "jobs": jobs,
            "cleanup_service_stats": self.cleanup_service.get_service_stats()
        }


# Global scheduler instance
_scheduler_instance = None


def get_scheduler() -> BackgroundScheduler:
    """Get or create global scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        settings = get_settings()
        _scheduler_instance = BackgroundScheduler(settings)
    return _scheduler_instance
