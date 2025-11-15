# File Cleanup System Documentation

## Overview

The PDF Editor now includes an **automatic file cleanup system** that manages temporary and output files to prevent disk space exhaustion and maintain user privacy.

## Key Features

✅ **Automatic Cleanup** - Runs every 5 minutes by default
✅ **Configurable Retention** - 5-minute retention period by default
✅ **Background Scheduler** - Non-blocking APScheduler integration
✅ **Manual Triggers** - API endpoints for on-demand cleanup
✅ **Comprehensive Metrics** - Detailed logging and statistics
✅ **Safe Operations** - Graceful error handling and recovery
✅ **Production-Ready** - Tested and validated

## How It Works

### Retention Policy

**Output Files (`output/` directory):**
- Files are automatically deleted 5 minutes after creation
- Users have a 5-minute window to download their processed files
- After 5 minutes, files are permanently removed

**Upload Files (`uploads/` directory):**
- Cleaned up immediately after processing (handled by routers)
- Temporary files don't accumulate

### Automatic Cleanup Schedule

- **Frequency**: Every 5 minutes (configurable)
- **Start**: Runs immediately on application startup
- **Ongoing**: Continues automatically in the background
- **Graceful Shutdown**: Stops cleanly when application stops

## Configuration

### Environment Variables

You can customize cleanup behavior via environment variables or `.env` file:

```bash
# .env
AUTO_CLEANUP_ENABLED=True           # Enable/disable automatic cleanup
CLEANUP_INTERVAL_MINUTES=5          # How often to run cleanup (minutes)
FILE_RETENTION_MINUTES=5            # How long to keep files (minutes)
```

### Configuration File

Edit `backend-python/config.py`:

```python
class Settings(BaseSettings):
    # Cleanup Configuration
    auto_cleanup_enabled: bool = True
    cleanup_interval_minutes: int = 5  # Run every 5 minutes
    file_retention_minutes: int = 5    # Keep files for 5 minutes
```

## API Endpoints

### 1. Manual Cleanup Trigger

Manually trigger a cleanup operation:

```bash
POST /api/cleanup/run
```

**Query Parameters:**
- `dry_run` (boolean, optional): Simulate cleanup without deleting (default: false)
- `force` (boolean, optional): Delete all files regardless of age (default: false)

**Example:**
```bash
# Dry run (simulation only)
curl -X POST "http://localhost:8080/api/cleanup/run?dry_run=true"

# Actual cleanup
curl -X POST "http://localhost:8080/api/cleanup/run"

# Force cleanup (delete everything)
curl -X POST "http://localhost:8080/api/cleanup/run?force=true"
```

**Response:**
```json
{
  "success": true,
  "message": "Cleanup completed successfully",
  "data": {
    "start_time": "2025-11-14T17:16:00",
    "duration_seconds": 0.05,
    "files_scanned": 8,
    "files_deleted": 8,
    "files_failed": 0,
    "bytes_freed": 488973,
    "bytes_freed_mb": 0.47,
    "error_count": 0
  }
}
```

### 2. Get Cleanup Statistics

Get current cleanup service statistics:

```bash
GET /api/cleanup/stats
```

**Example:**
```bash
curl http://localhost:8080/api/cleanup/stats
```

**Response:**
```json
{
  "success": true,
  "message": "Cleanup statistics retrieved successfully",
  "data": {
    "service": "FileCleanupService",
    "enabled": true,
    "retention_minutes": 5,
    "cleanup_interval_minutes": 5,
    "last_cleanup": "2025-11-14T17:16:00",
    "total_cleanups": 12,
    "total_files_deleted": 156,
    "total_bytes_freed": 15234567,
    "total_mb_freed": 14.53,
    "uploads_dir": {
      "exists": true,
      "path": "uploads",
      "file_count": 0,
      "total_size_mb": 0.0,
      "age_distribution": {
        "under_5m": 0,
        "5m_to_1h": 0,
        "1h_to_24h": 0,
        "over_24h": 0
      }
    },
    "output_dir": {
      "exists": true,
      "path": "output",
      "file_count": 3,
      "total_size_mb": 1.25,
      "age_distribution": {
        "under_5m": 2,
        "5m_to_1h": 1,
        "1h_to_24h": 0,
        "over_24h": 0
      },
      "oldest_file": "merged.pdf",
      "oldest_age_minutes": 6.5
    }
  }
}
```

### 3. Get Scheduler Status

Get background scheduler status:

```bash
GET /api/cleanup/scheduler
```

**Example:**
```bash
curl http://localhost:8080/api/cleanup/scheduler
```

**Response:**
```json
{
  "success": true,
  "message": "Scheduler status retrieved successfully",
  "data": {
    "running": true,
    "state": "running",
    "jobs": [
      {
        "id": "file_cleanup",
        "name": "Automatic File Cleanup",
        "next_run": "2025-11-14T17:21:00",
        "trigger": "interval[0:05:00]"
      }
    ]
  }
}
```

### 4. Get Retention Policy Info

Get information about file retention for users:

```bash
POST /api/cleanup/test-notification
```

**Response:**
```json
{
  "success": true,
  "message": "File retention policy",
  "data": {
    "retention_minutes": 5,
    "cleanup_interval_minutes": 5,
    "message": "Files are automatically deleted 5 minutes after creation. Please download your files promptly.",
    "recommendation": "Download files immediately after processing"
  }
}
```

## Logging

The cleanup system provides comprehensive logging:

### Log Levels

- **INFO**: Cleanup operations, files deleted, statistics
- **WARNING**: Non-critical errors, permission issues
- **ERROR**: Critical failures, exceptions
- **DEBUG**: Detailed file-by-file operations

### Log Examples

```
2025-11-14 17:16:00,123 - services.file_cleanup - INFO - FileCleanupService initialized
2025-11-14 17:16:00,123 - services.file_cleanup - INFO - Cleanup enabled: True
2025-11-14 17:16:00,123 - services.file_cleanup - INFO - Retention period: 5 minutes
2025-11-14 17:16:00,124 - scheduler - INFO - Scheduled file cleanup job: every 5 minutes

======================================================================
FILE CLEANUP JOB STARTED at 2025-11-14T17:16:00
======================================================================
2025-11-14 17:16:00,500 - services.file_cleanup - INFO - Starting file cleanup operation
2025-11-14 17:16:00,501 - services.file_cleanup - INFO - Scanning directory: output
2025-11-14 17:16:00,502 - services.file_cleanup - INFO - Deleted: merged.pdf (age: 6.5m, size: 90,086 bytes)
2025-11-14 17:16:00,503 - services.file_cleanup - INFO - Cleanup operation completed
2025-11-14 17:16:00,503 - services.file_cleanup - INFO - Files deleted: 8
2025-11-14 17:16:00,503 - services.file_cleanup - INFO - Space freed: 488,973 bytes (0.47 MB)
======================================================================
```

## Testing

### Manual Test Script

Run the included test script:

```bash
cd backend-python
python3 test_cleanup.py
```

### Testing Scenarios

1. **Dry Run Test:**
   ```bash
   curl -X POST "http://localhost:8080/api/cleanup/run?dry_run=true"
   ```

2. **Actual Cleanup:**
   ```bash
   curl -X POST "http://localhost:8080/api/cleanup/run"
   ```

3. **Force Delete Everything:**
   ```bash
   curl -X POST "http://localhost:8080/api/cleanup/run?force=true"
   ```

4. **Check Statistics:**
   ```bash
   curl http://localhost:8080/api/cleanup/stats
   ```

## Deployment Considerations

### Production Settings

For production, consider these settings:

```bash
# .env (production)
AUTO_CLEANUP_ENABLED=True
CLEANUP_INTERVAL_MINUTES=5         # Run every 5 minutes
FILE_RETENTION_MINUTES=15          # Keep files for 15 minutes (more generous)
```

### Monitoring

Monitor cleanup operations:

1. **Check Logs:**
   ```bash
   tail -f pdf_editor.log | grep -i cleanup
   ```

2. **Check Statistics:**
   ```bash
   curl http://localhost:8080/api/cleanup/stats
   ```

3. **Check Scheduler:**
   ```bash
   curl http://localhost:8080/api/cleanup/scheduler
   ```

### Health Checks

The cleanup system integrates with the existing health check:

```bash
GET /health
```

Response includes directory status:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "upload_dir_exists": true,
  "output_dir_exists": true
}
```

## Troubleshooting

### Issue: Files Not Being Deleted

**Check:**
1. Is cleanup enabled? `curl http://localhost:8080/api/cleanup/scheduler`
2. Check retention period: `curl http://localhost:8080/api/cleanup/stats`
3. Check file ages in statistics

**Solution:**
- Run manual cleanup: `curl -X POST http://localhost:8080/api/cleanup/run`
- Check logs for errors: `tail -f pdf_editor.log`

### Issue: Permission Errors

**Symptom:**
```
Permission denied deleting file.pdf
```

**Solution:**
- Ensure application has write permissions to `uploads/` and `output/` directories
- Check file ownership: `ls -la output/`
- Fix permissions: `chmod 755 uploads output`

### Issue: Scheduler Not Running

**Check:**
```bash
curl http://localhost:8080/api/cleanup/scheduler
```

**Solution:**
- Restart application
- Check logs for startup errors
- Verify APScheduler is installed: `pip3 install apscheduler==3.10.4`

## Architecture

### Components

1. **FileCleanupService** (`services/file_cleanup.py`)
   - Core cleanup logic
   - Directory scanning
   - File deletion
   - Metrics collection

2. **BackgroundScheduler** (`scheduler.py`)
   - APScheduler integration
   - Job scheduling
   - Lifecycle management

3. **Cleanup Router** (`routers/cleanup.py`)
   - API endpoints
   - Manual triggers
   - Statistics endpoints

4. **Main Application** (`main.py`)
   - Lifespan integration
   - Startup/shutdown hooks

### Data Flow

```
Application Startup
    ↓
Initialize Scheduler
    ↓
Start Background Job (every 5 minutes)
    ↓
FileCleanupService.cleanup_old_files()
    ↓
Scan directories → Check ages → Delete old files → Log metrics
    ↓
Sleep until next interval
```

## Metrics Collected

The system tracks:
- Files scanned
- Files deleted
- Files failed
- Bytes freed
- Errors encountered
- Duration
- Age distribution
- Directory statistics

## Dependencies

```txt
apscheduler==3.10.4        # Background job scheduling
aiofiles==23.2.1           # Async file operations
pydantic-settings==2.0.3   # Configuration management
```

## User Communication

### Frontend Integration

Display a notice to users:

```jsx
<Alert severity="warning">
  Your processed files will be automatically deleted after 5 minutes.
  Please download them immediately.
</Alert>
```

### Download Button

Add countdown timer:

```jsx
{timeRemaining > 0 ? (
  <Button>Download (expires in {timeRemaining}m)</Button>
) : (
  <Typography color="error">File expired</Typography>
)}
```

## Security Considerations

✅ **Path Traversal Protection**: Cleanup only affects configured directories
✅ **No User Input**: Automated system, no user-controlled paths
✅ **Graceful Errors**: Failed deletions don't crash the service
✅ **Audit Trail**: All operations logged with timestamps
✅ **Privacy**: Files are securely deleted after retention period

## Future Enhancements

- [ ] Email notifications before file deletion
- [ ] Extended retention for registered users
- [ ] Cloud storage integration
- [ ] Compression before deletion
- [ ] File recovery grace period
- [ ] Metrics dashboard
- [ ] Cleanup analytics

## Summary

The file cleanup system is **production-ready** and provides:
- ✅ Automatic cleanup every 5 minutes
- ✅ 5-minute retention period
- ✅ Comprehensive logging
- ✅ API endpoints for monitoring
- ✅ Manual trigger capability
- ✅ Safe error handling
- ✅ Zero configuration needed (works out of the box)

Users should **download files immediately** after processing!
