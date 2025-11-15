"""
File Cleanup Service
Manages automatic cleanup of temporary and output files based on retention policies.
Implements comprehensive error handling, logging, and metrics collection.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from config import Settings


logger = logging.getLogger(__name__)


@dataclass
class CleanupMetrics:
    """Metrics for a cleanup operation"""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    files_scanned: int = 0
    files_deleted: int = 0
    files_failed: int = 0
    bytes_freed: int = 0
    errors: List[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        """Calculate operation duration"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": round(self.duration_seconds, 2),
            "files_scanned": self.files_scanned,
            "files_deleted": self.files_deleted,
            "files_failed": self.files_failed,
            "bytes_freed": self.bytes_freed,
            "bytes_freed_mb": round(self.bytes_freed / 1024 / 1024, 2),
            "error_count": len(self.errors),
            "errors": self.errors[:10]  # Limit to first 10 errors
        }


class FileCleanupService:
    """
    Service for cleaning up temporary and output files.

    Features:
    - Age-based file deletion with configurable retention
    - Comprehensive error handling and recovery
    - Detailed metrics and logging
    - Safe deletion with validation
    - Support for both automatic and manual cleanup
    """

    def __init__(self, settings: Settings):
        """
        Initialize File Cleanup Service.

        Args:
            settings: Application settings instance
        """
        self.settings = settings
        self.logger = logger
        self.logger.info("FileCleanupService initialized")
        self.logger.info(f"Cleanup enabled: {settings.auto_cleanup_enabled}")
        self.logger.info(f"Retention period: {settings.file_retention_minutes} minutes")
        self.logger.info(f"Cleanup interval: {settings.cleanup_interval_minutes} minutes")

        # Track last cleanup time
        self.last_cleanup_time: Optional[datetime] = None
        self.total_cleanups: int = 0
        self.total_files_deleted: int = 0
        self.total_bytes_freed: int = 0

    async def cleanup_old_files(
        self,
        dry_run: bool = False,
        force: bool = False
    ) -> CleanupMetrics:
        """
        Clean up old files from uploads and output directories.

        Args:
            dry_run: If True, only scan and report, don't delete
            force: If True, ignore retention period and delete all files

        Returns:
            CleanupMetrics with operation details
        """
        metrics = CleanupMetrics()

        try:
            self.logger.info("=" * 60)
            self.logger.info("Starting file cleanup operation")
            self.logger.info(f"Mode: {'DRY RUN' if dry_run else 'ACTIVE'}")
            self.logger.info(f"Force: {force}")
            self.logger.info("=" * 60)

            # Calculate cutoff time
            if force:
                cutoff_time = datetime.now() + timedelta(days=1)  # Delete everything
                self.logger.warning("FORCE MODE: Deleting all files regardless of age")
            else:
                cutoff_time = datetime.now() - timedelta(
                    minutes=self.settings.file_retention_minutes
                )
                self.logger.info(
                    f"Retention cutoff: {cutoff_time.isoformat()} "
                    f"({self.settings.file_retention_minutes} minutes ago)"
                )

            # Clean uploads directory
            uploads_metrics = await self._cleanup_directory(
                directory=self.settings.upload_dir,
                cutoff_time=cutoff_time,
                dry_run=dry_run,
                dir_name="uploads"
            )

            # Clean output directory
            output_metrics = await self._cleanup_directory(
                directory=self.settings.output_dir,
                cutoff_time=cutoff_time,
                dry_run=dry_run,
                dir_name="output"
            )

            # Aggregate metrics
            metrics.files_scanned = uploads_metrics.files_scanned + output_metrics.files_scanned
            metrics.files_deleted = uploads_metrics.files_deleted + output_metrics.files_deleted
            metrics.files_failed = uploads_metrics.files_failed + output_metrics.files_failed
            metrics.bytes_freed = uploads_metrics.bytes_freed + output_metrics.bytes_freed
            metrics.errors.extend(uploads_metrics.errors)
            metrics.errors.extend(output_metrics.errors)
            metrics.end_time = datetime.now()

            # Update global stats
            if not dry_run:
                self.last_cleanup_time = datetime.now()
                self.total_cleanups += 1
                self.total_files_deleted += metrics.files_deleted
                self.total_bytes_freed += metrics.bytes_freed

            # Log summary
            self.logger.info("=" * 60)
            self.logger.info("Cleanup operation completed")
            self.logger.info(f"Files scanned: {metrics.files_scanned}")
            self.logger.info(f"Files deleted: {metrics.files_deleted}")
            self.logger.info(f"Files failed: {metrics.files_failed}")
            self.logger.info(f"Space freed: {metrics.bytes_freed:,} bytes ({metrics.bytes_freed / 1024 / 1024:.2f} MB)")
            self.logger.info(f"Duration: {metrics.duration_seconds:.2f} seconds")

            if metrics.errors:
                self.logger.warning(f"Errors encountered: {len(metrics.errors)}")
                for error in metrics.errors[:5]:  # Log first 5 errors
                    self.logger.warning(f"  - {error}")

            self.logger.info("=" * 60)

            return metrics

        except Exception as e:
            metrics.end_time = datetime.now()
            error_msg = f"Critical error during cleanup: {str(e)}"
            metrics.errors.append(error_msg)
            self.logger.error(error_msg, exc_info=True)
            return metrics

    async def _cleanup_directory(
        self,
        directory: Path,
        cutoff_time: datetime,
        dry_run: bool,
        dir_name: str
    ) -> CleanupMetrics:
        """
        Clean up files in a specific directory.

        Args:
            directory: Path to directory to clean
            cutoff_time: Delete files older than this
            dry_run: If True, don't actually delete
            dir_name: Name for logging

        Returns:
            CleanupMetrics for this directory
        """
        metrics = CleanupMetrics()

        try:
            if not directory.exists():
                self.logger.warning(f"Directory does not exist: {directory}")
                return metrics

            self.logger.info(f"Scanning directory: {directory}")

            # Get all files in directory
            files = list(directory.iterdir())

            if not files:
                self.logger.info(f"No files found in {dir_name}")
                return metrics

            self.logger.info(f"Found {len(files)} items in {dir_name}")

            for file_path in files:
                # Skip if not a file
                if not file_path.is_file():
                    self.logger.debug(f"Skipping non-file: {file_path.name}")
                    continue

                metrics.files_scanned += 1

                try:
                    # Get file stats
                    stat = file_path.stat()
                    file_size = stat.st_size
                    file_mtime = datetime.fromtimestamp(stat.st_mtime)
                    file_age_minutes = (datetime.now() - file_mtime).total_seconds() / 60

                    # Check if file should be deleted
                    if file_mtime < cutoff_time:
                        if dry_run:
                            self.logger.info(
                                f"[DRY RUN] Would delete: {file_path.name} "
                                f"(age: {file_age_minutes:.1f}m, size: {file_size:,} bytes)"
                            )
                            metrics.files_deleted += 1
                            metrics.bytes_freed += file_size
                        else:
                            # Actually delete the file
                            file_path.unlink()
                            self.logger.info(
                                f"Deleted: {file_path.name} "
                                f"(age: {file_age_minutes:.1f}m, size: {file_size:,} bytes)"
                            )
                            metrics.files_deleted += 1
                            metrics.bytes_freed += file_size
                    else:
                        self.logger.debug(
                            f"Keeping: {file_path.name} "
                            f"(age: {file_age_minutes:.1f}m, retention: {self.settings.file_retention_minutes}m)"
                        )

                except PermissionError as e:
                    error_msg = f"Permission denied deleting {file_path.name}: {str(e)}"
                    metrics.errors.append(error_msg)
                    metrics.files_failed += 1
                    self.logger.error(error_msg)

                except OSError as e:
                    error_msg = f"OS error deleting {file_path.name}: {str(e)}"
                    metrics.errors.append(error_msg)
                    metrics.files_failed += 1
                    self.logger.error(error_msg)

                except Exception as e:
                    error_msg = f"Unexpected error with {file_path.name}: {str(e)}"
                    metrics.errors.append(error_msg)
                    metrics.files_failed += 1
                    self.logger.error(error_msg, exc_info=True)

            self.logger.info(
                f"Directory {dir_name} summary: "
                f"{metrics.files_scanned} scanned, "
                f"{metrics.files_deleted} deleted, "
                f"{metrics.files_failed} failed"
            )

        except Exception as e:
            error_msg = f"Error scanning directory {dir_name}: {str(e)}"
            metrics.errors.append(error_msg)
            self.logger.error(error_msg, exc_info=True)

        return metrics

    def get_directory_stats(self, directory: Path) -> Dict[str, Any]:
        """
        Get statistics about a directory.

        Args:
            directory: Path to directory

        Returns:
            Dictionary with directory statistics
        """
        try:
            if not directory.exists():
                return {
                    "exists": False,
                    "path": str(directory)
                }

            files = [f for f in directory.iterdir() if f.is_file()]

            total_size = sum(f.stat().st_size for f in files)

            # Calculate age distribution
            now = datetime.now()
            age_distribution = {
                "under_5m": 0,
                "5m_to_1h": 0,
                "1h_to_24h": 0,
                "over_24h": 0
            }

            oldest_file = None
            oldest_age = 0

            for f in files:
                age_minutes = (now - datetime.fromtimestamp(f.stat().st_mtime)).total_seconds() / 60

                if age_minutes < 5:
                    age_distribution["under_5m"] += 1
                elif age_minutes < 60:
                    age_distribution["5m_to_1h"] += 1
                elif age_minutes < 1440:  # 24 hours
                    age_distribution["1h_to_24h"] += 1
                else:
                    age_distribution["over_24h"] += 1

                if age_minutes > oldest_age:
                    oldest_age = age_minutes
                    oldest_file = f.name

            return {
                "exists": True,
                "path": str(directory),
                "file_count": len(files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "age_distribution": age_distribution,
                "oldest_file": oldest_file,
                "oldest_age_minutes": round(oldest_age, 1)
            }

        except Exception as e:
            self.logger.error(f"Error getting directory stats: {str(e)}")
            return {
                "error": str(e),
                "path": str(directory)
            }

    def get_service_stats(self) -> Dict[str, Any]:
        """
        Get overall service statistics.

        Returns:
            Dictionary with service statistics
        """
        return {
            "service": "FileCleanupService",
            "enabled": self.settings.auto_cleanup_enabled,
            "retention_minutes": self.settings.file_retention_minutes,
            "cleanup_interval_minutes": self.settings.cleanup_interval_minutes,
            "last_cleanup": self.last_cleanup_time.isoformat() if self.last_cleanup_time else None,
            "total_cleanups": self.total_cleanups,
            "total_files_deleted": self.total_files_deleted,
            "total_bytes_freed": self.total_bytes_freed,
            "total_mb_freed": round(self.total_bytes_freed / 1024 / 1024, 2),
            "uploads_dir": self.get_directory_stats(self.settings.upload_dir),
            "output_dir": self.get_directory_stats(self.settings.output_dir)
        }
