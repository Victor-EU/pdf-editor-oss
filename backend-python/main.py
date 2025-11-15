"""
PDF Editor Backend - FastAPI Application
A modern, open-source PDF editor backend using FastAPI and open source PDF libraries.

Production-ready implementation with proper OOP, configuration management,
and comprehensive error handling.

Version: 2.0.0
Author: PDF Editor Team
License: MIT
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from contextlib import asynccontextmanager

from routers import merge, split, compress, convert, download, extract, ocr, cleanup, annotate, table_extract
from config import settings
from scheduler import get_scheduler
from middleware.security_headers import SecurityHeadersMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format,
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler(settings.log_file)  # File output
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    Handles startup and shutdown events for background services.
    """
    # Startup
    logger.info("=" * 70)
    logger.info("APPLICATION STARTUP")
    logger.info("=" * 70)

    # Start background scheduler
    scheduler = get_scheduler()
    await scheduler.start()

    logger.info("All background services started successfully")
    logger.info("=" * 70)

    yield

    # Shutdown
    logger.info("=" * 70)
    logger.info("APPLICATION SHUTDOWN")
    logger.info("=" * 70)

    # Stop background scheduler
    await scheduler.shutdown()

    logger.info("All background services stopped successfully")
    logger.info("=" * 70)


# Create FastAPI app with settings and lifespan manager
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS Configuration from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Mount static files for downloads (using settings)
app.mount("/download", StaticFiles(directory=settings.output_dir), name="downloads")

# Include routers
app.include_router(merge.router, prefix="/api", tags=["merge"])
app.include_router(split.router, prefix="/api", tags=["split"])
app.include_router(compress.router, prefix="/api", tags=["compress"])
app.include_router(convert.router, prefix="/api", tags=["convert"])
app.include_router(extract.router, prefix="/api", tags=["extract"])
app.include_router(ocr.router, prefix="/api", tags=["ocr"])
app.include_router(table_extract.router, prefix="/api", tags=["table-extract"])
app.include_router(download.router, prefix="/api", tags=["download"])
app.include_router(cleanup.router, prefix="/api", tags=["cleanup"])
app.include_router(annotate.router, prefix="/api", tags=["annotate"])



@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "PDF Editor API - Open Source",
        "version": settings.app_version,
        "stack": {
            "framework": "FastAPI",
            "pdf_library": "pikepdf 8.10+",
            "image_converter": "pdf2image",
            "architecture": "OOP with Dependency Injection"
        },
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "upload_dir_exists": settings.upload_dir.exists(),
        "output_dir_exists": settings.output_dir.exists()
    }


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
