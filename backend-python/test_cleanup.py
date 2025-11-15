"""
Test script for file cleanup functionality
Tests the cleanup service directly without needing full server
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import time

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Settings
from services.file_cleanup import FileCleanupService


async def test_cleanup():
    """Test file cleanup functionality"""
    print("=" * 70)
    print("FILE CLEANUP SYSTEM TEST")
    print("=" * 70)
    print()

    # Initialize settings and service
    settings = Settings()
    cleanup_service = FileCleanupService(settings)

    print(f"Configuration:")
    print(f"  - Retention period: {settings.file_retention_minutes} minutes")
    print(f"  - Cleanup interval: {settings.cleanup_interval_minutes} minutes")
    print(f"  - Auto cleanup enabled: {settings.auto_cleanup_enabled}")
    print()

    # Check current directory stats
    print("Current Directory Statistics:")
    print("-" * 70)
    stats = cleanup_service.get_service_stats()

    uploads_dir = stats['uploads_dir']
    output_dir = stats['output_dir']

    print(f"\nUploads Directory:")
    print(f"  Path: {uploads_dir['path']}")
    print(f"  Files: {uploads_dir.get('file_count', 0)}")
    print(f"  Size: {uploads_dir.get('total_size_mb', 0)} MB")

    print(f"\nOutput Directory:")
    print(f"  Path: {output_dir['path']}")
    print(f"  Files: {output_dir.get('file_count', 0)}")
    print(f"  Size: {output_dir.get('total_size_mb', 0)} MB")

    if output_dir.get('file_count', 0) > 0:
        print(f"  Age distribution: {output_dir.get('age_distribution', {})}")
        print(f"  Oldest file: {output_dir.get('oldest_file', 'N/A')}")
        print(f"  Oldest age: {output_dir.get('oldest_age_minutes', 0):.1f} minutes")
    print()

    # Test 1: Dry run
    print("=" * 70)
    print("TEST 1: DRY RUN (Simulation)")
    print("=" * 70)

    metrics = await cleanup_service.cleanup_old_files(dry_run=True, force=False)

    print(f"\nDry Run Results:")
    print(f"  Files scanned: {metrics.files_scanned}")
    print(f"  Files would be deleted: {metrics.files_deleted}")
    print(f"  Space would be freed: {metrics.bytes_freed:,} bytes ({metrics.bytes_freed / 1024 / 1024:.2f} MB)")
    print(f"  Duration: {metrics.duration_seconds:.2f} seconds")

    if metrics.errors:
        print(f"  Errors: {len(metrics.errors)}")
        for error in metrics.errors[:3]:
            print(f"    - {error}")
    print()

    # Test 2: Actual cleanup
    if metrics.files_deleted > 0:
        response = input(f"\nFound {metrics.files_deleted} files to delete. Proceed with actual cleanup? (y/N): ")
        if response.lower() == 'y':
            print("\n" + "=" * 70)
            print("TEST 2: ACTUAL CLEANUP")
            print("=" * 70)

            metrics = await cleanup_service.cleanup_old_files(dry_run=False, force=False)

            print(f"\nCleanup Results:")
            print(f"  Files scanned: {metrics.files_scanned}")
            print(f"  Files deleted: {metrics.files_deleted}")
            print(f"  Files failed: {metrics.files_failed}")
            print(f"  Space freed: {metrics.bytes_freed:,} bytes ({metrics.bytes_freed / 1024 / 1024:.2f} MB)")
            print(f"  Duration: {metrics.duration_seconds:.2f} seconds")

            if metrics.errors:
                print(f"  Errors: {len(metrics.errors)}")
                for error in metrics.errors[:3]:
                    print(f"    - {error}")
            print()

            # Show updated stats
            print("=" * 70)
            print("POST-CLEANUP STATISTICS")
            print("=" * 70)

            stats = cleanup_service.get_service_stats()
            output_dir = stats['output_dir']

            print(f"\nOutput Directory:")
            print(f"  Files: {output_dir.get('file_count', 0)}")
            print(f"  Size: {output_dir.get('total_size_mb', 0)} MB")
            print()
    else:
        print("No files to delete (all files within retention period)")

    print("=" * 70)
    print("TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_cleanup())
