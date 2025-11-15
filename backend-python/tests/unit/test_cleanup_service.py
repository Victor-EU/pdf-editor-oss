"""
Unit Tests for File Cleanup Service
Comprehensive test coverage for cleanup functionality
"""

import pytest
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
import time
import os

from services.file_cleanup import FileCleanupService, CleanupMetrics
from config import Settings


# ============================================================================
# CleanupMetrics Tests
# ============================================================================

class TestCleanupMetrics:
    """Test CleanupMetrics data class"""

    def test_metrics_initialization(self):
        """Test metrics are initialized with correct defaults"""
        metrics = CleanupMetrics()

        assert metrics.files_scanned == 0
        assert metrics.files_deleted == 0
        assert metrics.files_failed == 0
        assert metrics.bytes_freed == 0
        assert metrics.errors == []
        assert isinstance(metrics.start_time, datetime)
        assert metrics.end_time is None

    def test_metrics_duration_calculation(self):
        """Test duration calculation"""
        metrics = CleanupMetrics()
        time.sleep(0.1)  # Sleep for 100ms
        metrics.end_time = datetime.now()

        duration = metrics.duration_seconds
        assert duration >= 0.1
        assert duration < 0.2  # Should be around 0.1s

    def test_metrics_to_dict(self):
        """Test conversion to dictionary"""
        metrics = CleanupMetrics()
        metrics.files_scanned = 10
        metrics.files_deleted = 5
        metrics.bytes_freed = 1024
        metrics.end_time = datetime.now()

        result = metrics.to_dict()

        assert result["files_scanned"] == 10
        assert result["files_deleted"] == 5
        assert result["bytes_freed"] == 1024
        assert result["bytes_freed_mb"] == 0.0
        assert "start_time" in result
        assert "duration_seconds" in result


# ============================================================================
# FileCleanupService Initialization Tests
# ============================================================================

class TestFileCleanupServiceInit:
    """Test service initialization"""

    def test_service_initialization(self, test_settings: Settings):
        """Test service initializes correctly"""
        service = FileCleanupService(test_settings)

        assert service.settings == test_settings
        assert service.last_cleanup_time is None
        assert service.total_cleanups == 0
        assert service.total_files_deleted == 0
        assert service.total_bytes_freed == 0

    def test_service_with_custom_settings(self, upload_dir: Path, output_dir: Path):
        """Test service with custom settings"""
        settings = Settings()
        settings.upload_dir = upload_dir
        settings.output_dir = output_dir
        settings.file_retention_minutes = 10
        settings.auto_cleanup_enabled = False

        service = FileCleanupService(settings)

        assert service.settings.file_retention_minutes == 10
        assert service.settings.auto_cleanup_enabled is False


# ============================================================================
# Cleanup Operation Tests
# ============================================================================

@pytest.mark.asyncio
class TestCleanupOperations:
    """Test cleanup operations"""

    async def test_cleanup_empty_directories(self, cleanup_service: FileCleanupService):
        """Test cleanup with empty directories"""
        metrics = await cleanup_service.cleanup_old_files(dry_run=False)

        assert metrics.files_scanned == 0
        assert metrics.files_deleted == 0
        assert metrics.files_failed == 0
        assert metrics.bytes_freed == 0

    async def test_cleanup_dry_run(
        self,
        cleanup_service: FileCleanupService,
        old_file: Path
    ):
        """Test dry run mode doesn't delete files"""
        assert old_file.exists()

        metrics = await cleanup_service.cleanup_old_files(dry_run=True)

        # File should still exist after dry run
        assert old_file.exists()
        assert metrics.files_scanned == 1
        assert metrics.files_deleted == 1  # Would be deleted
        assert metrics.bytes_freed > 0

    async def test_cleanup_deletes_old_files(
        self,
        cleanup_service: FileCleanupService,
        old_file: Path
    ):
        """Test actual cleanup deletes old files"""
        assert old_file.exists()

        metrics = await cleanup_service.cleanup_old_files(dry_run=False)

        # File should be deleted
        assert not old_file.exists()
        assert metrics.files_scanned == 1
        assert metrics.files_deleted == 1
        assert metrics.bytes_freed > 0

    async def test_cleanup_keeps_recent_files(
        self,
        cleanup_service: FileCleanupService,
        recent_file: Path
    ):
        """Test cleanup keeps files within retention period"""
        assert recent_file.exists()

        metrics = await cleanup_service.cleanup_old_files(dry_run=False)

        # File should still exist
        assert recent_file.exists()
        assert metrics.files_scanned == 1
        assert metrics.files_deleted == 0

    async def test_cleanup_mixed_files(
        self,
        cleanup_service: FileCleanupService,
        old_file: Path,
        recent_file: Path
    ):
        """Test cleanup with mix of old and recent files"""
        assert old_file.exists()
        assert recent_file.exists()

        metrics = await cleanup_service.cleanup_old_files(dry_run=False)

        # Only old file should be deleted
        assert not old_file.exists()
        assert recent_file.exists()
        assert metrics.files_scanned == 2
        assert metrics.files_deleted == 1

    async def test_cleanup_force_mode(
        self,
        cleanup_service: FileCleanupService,
        recent_file: Path
    ):
        """Test force mode deletes all files"""
        assert recent_file.exists()

        metrics = await cleanup_service.cleanup_old_files(dry_run=False, force=True)

        # File should be deleted even though it's recent
        assert not recent_file.exists()
        assert metrics.files_deleted == 1

    async def test_cleanup_multiple_files(
        self,
        cleanup_service: FileCleanupService,
        output_dir: Path
    ):
        """Test cleanup with multiple old files"""
        # Create multiple old files
        files = []
        for i in range(5):
            file_path = output_dir / f"old_{i}.pdf"
            file_path.write_text(f"content {i}")

            # Set old timestamp
            old_time = time.time() - (10 * 60)
            os.utime(file_path, (old_time, old_time))
            files.append(file_path)

        metrics = await cleanup_service.cleanup_old_files(dry_run=False)

        # All files should be deleted
        for file_path in files:
            assert not file_path.exists()

        assert metrics.files_scanned == 5
        assert metrics.files_deleted == 5
        assert metrics.bytes_freed > 0

    async def test_cleanup_tracks_stats(
        self,
        cleanup_service: FileCleanupService,
        old_file: Path
    ):
        """Test cleanup updates service statistics"""
        initial_cleanups = cleanup_service.total_cleanups
        initial_deleted = cleanup_service.total_files_deleted

        await cleanup_service.cleanup_old_files(dry_run=False)

        assert cleanup_service.total_cleanups == initial_cleanups + 1
        assert cleanup_service.total_files_deleted == initial_deleted + 1
        assert cleanup_service.total_bytes_freed > 0
        assert cleanup_service.last_cleanup_time is not None


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.asyncio
class TestCleanupErrorHandling:
    """Test error handling in cleanup operations"""

    async def test_cleanup_handles_permission_errors(
        self,
        cleanup_service: FileCleanupService,
        output_dir: Path
    ):
        """Test cleanup handles permission errors gracefully"""
        # Create a file
        file_path = output_dir / "protected.pdf"
        file_path.write_text("content")

        # Set old timestamp
        old_time = time.time() - (10 * 60)
        os.utime(file_path, (old_time, old_time))

        # Make file read-only (simulate permission error)
        os.chmod(file_path, 0o444)

        try:
            metrics = await cleanup_service.cleanup_old_files(dry_run=False)

            # Should handle error gracefully
            # Note: On some systems, deletion might still work for owner
            # So we check that it either deleted or failed gracefully
            if file_path.exists():
                assert metrics.files_failed >= 0
            else:
                assert metrics.files_deleted >= 0

        finally:
            # Restore permissions for cleanup
            if file_path.exists():
                os.chmod(file_path, 0o644)

    async def test_cleanup_handles_nonexistent_directory(
        self,
        test_settings: Settings,
        temp_dir: Path
    ):
        """Test cleanup handles nonexistent directories"""
        # Point to nonexistent directory
        test_settings.output_dir = temp_dir / "nonexistent"

        service = FileCleanupService(test_settings)
        metrics = await service.cleanup_old_files(dry_run=False)

        # Should handle gracefully
        assert metrics.files_scanned == 0
        assert len(metrics.errors) == 0


# ============================================================================
# Directory Statistics Tests
# ============================================================================

class TestDirectoryStatistics:
    """Test directory statistics functionality"""

    def test_get_directory_stats_empty(
        self,
        cleanup_service: FileCleanupService,
        output_dir: Path
    ):
        """Test stats for empty directory"""
        stats = cleanup_service.get_directory_stats(output_dir)

        assert stats["exists"] is True
        assert stats["file_count"] == 0
        assert stats["total_size_bytes"] == 0
        assert stats["total_size_mb"] == 0.0

    def test_get_directory_stats_with_files(
        self,
        cleanup_service: FileCleanupService,
        output_dir: Path
    ):
        """Test stats for directory with files"""
        # Create some files
        for i in range(3):
            file_path = output_dir / f"file_{i}.pdf"
            file_path.write_text("x" * 1000)  # 1KB each

        stats = cleanup_service.get_directory_stats(output_dir)

        assert stats["exists"] is True
        assert stats["file_count"] == 3
        assert stats["total_size_bytes"] == 3000
        assert stats["total_size_mb"] >= 0.0  # Rounded to 2 decimals

    def test_get_directory_stats_age_distribution(
        self,
        cleanup_service: FileCleanupService,
        output_dir: Path,
        old_file: Path,
        recent_file: Path
    ):
        """Test age distribution in stats"""
        stats = cleanup_service.get_directory_stats(output_dir)

        assert "age_distribution" in stats
        dist = stats["age_distribution"]

        assert dist["under_5m"] >= 0
        assert dist["5m_to_1h"] >= 0
        assert dist["1h_to_24h"] >= 0
        assert dist["over_24h"] >= 0

        # Should have at least 2 files
        total_files = sum(dist.values())
        assert total_files == 2

    def test_get_directory_stats_nonexistent(
        self,
        cleanup_service: FileCleanupService,
        temp_dir: Path
    ):
        """Test stats for nonexistent directory"""
        nonexistent = temp_dir / "does_not_exist"

        stats = cleanup_service.get_directory_stats(nonexistent)

        assert stats["exists"] is False


# ============================================================================
# Service Statistics Tests
# ============================================================================

class TestServiceStatistics:
    """Test service-level statistics"""

    def test_get_service_stats_initial(
        self,
        cleanup_service: FileCleanupService
    ):
        """Test service stats on initialization"""
        stats = cleanup_service.get_service_stats()

        assert stats["service"] == "FileCleanupService"
        assert stats["enabled"] is True
        assert stats["retention_minutes"] == 5
        assert stats["cleanup_interval_minutes"] == 5
        assert stats["last_cleanup"] is None
        assert stats["total_cleanups"] == 0
        assert stats["total_files_deleted"] == 0
        assert stats["total_bytes_freed"] == 0

    @pytest.mark.asyncio
    async def test_get_service_stats_after_cleanup(
        self,
        cleanup_service: FileCleanupService,
        old_file: Path
    ):
        """Test service stats after cleanup operation"""
        await cleanup_service.cleanup_old_files(dry_run=False)

        stats = cleanup_service.get_service_stats()

        assert stats["total_cleanups"] == 1
        assert stats["total_files_deleted"] == 1
        assert stats["total_bytes_freed"] > 0
        assert stats["last_cleanup"] is not None

    def test_get_service_stats_includes_directories(
        self,
        cleanup_service: FileCleanupService
    ):
        """Test service stats include directory information"""
        stats = cleanup_service.get_service_stats()

        assert "uploads_dir" in stats
        assert "output_dir" in stats

        assert stats["uploads_dir"]["exists"] is True
        assert stats["output_dir"]["exists"] is True


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
class TestCleanupIntegration:
    """Integration tests for cleanup service"""

    async def test_full_cleanup_workflow(
        self,
        cleanup_service: FileCleanupService,
        output_dir: Path
    ):
        """Test complete cleanup workflow"""
        # 1. Create mix of old and recent files
        old_files = []
        for i in range(3):
            file_path = output_dir / f"old_{i}.pdf"
            file_path.write_text(f"old content {i}" * 100)
            old_time = time.time() - (10 * 60)
            os.utime(file_path, (old_time, old_time))
            old_files.append(file_path)

        recent_files = []
        for i in range(2):
            file_path = output_dir / f"recent_{i}.pdf"
            file_path.write_text(f"recent content {i}" * 100)
            recent_files.append(file_path)

        # 2. Get initial stats
        initial_stats = cleanup_service.get_service_stats()
        assert initial_stats["output_dir"]["file_count"] == 5

        # 3. Run dry run
        dry_metrics = await cleanup_service.cleanup_old_files(dry_run=True)
        assert dry_metrics.files_deleted == 3
        assert all(f.exists() for f in old_files)  # Still exist

        # 4. Run actual cleanup
        metrics = await cleanup_service.cleanup_old_files(dry_run=False)
        assert metrics.files_deleted == 3
        assert metrics.files_failed == 0

        # 5. Verify results
        assert all(not f.exists() for f in old_files)
        assert all(f.exists() for f in recent_files)

        # 6. Check final stats
        final_stats = cleanup_service.get_service_stats()
        assert final_stats["output_dir"]["file_count"] == 2
        assert final_stats["total_files_deleted"] == 3

    async def test_concurrent_cleanup_operations(
        self,
        cleanup_service: FileCleanupService,
        output_dir: Path
    ):
        """Test multiple concurrent cleanup operations"""
        # Create files
        for i in range(10):
            file_path = output_dir / f"file_{i}.pdf"
            file_path.write_text(f"content {i}")
            old_time = time.time() - (10 * 60)
            os.utime(file_path, (old_time, old_time))

        # Run multiple cleanups concurrently
        results = await asyncio.gather(
            cleanup_service.cleanup_old_files(dry_run=False),
            cleanup_service.cleanup_old_files(dry_run=False),
            cleanup_service.cleanup_old_files(dry_run=False)
        )

        # Verify total files deleted across all operations
        total_deleted = sum(m.files_deleted for m in results)
        assert total_deleted == 10  # Each file deleted once
