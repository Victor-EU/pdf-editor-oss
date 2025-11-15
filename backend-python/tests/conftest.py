"""
Pytest Configuration and Shared Fixtures
Provides reusable test fixtures and utilities
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Generator, AsyncGenerator
from datetime import datetime
import io

from fastapi.testclient import TestClient
from PIL import Image
import pikepdf

from config import Settings
from services.file_cleanup import FileCleanupService
from services.pdf_merge import PdfMergeService
from services.pdf_split import PdfSplitService
from services.pdf_compress import PdfCompressService
from services.pdf_convert import PdfConvertService
from services.pdf_extract import PdfExtractService


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )


# ============================================================================
# Event Loop Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Temporary Directory Fixtures
# ============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for tests"""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def upload_dir(temp_dir: Path) -> Path:
    """Create temporary upload directory"""
    upload = temp_dir / "uploads"
    upload.mkdir(exist_ok=True)
    return upload


@pytest.fixture
def output_dir(temp_dir: Path) -> Path:
    """Create temporary output directory"""
    output = temp_dir / "output"
    output.mkdir(exist_ok=True)
    return output


# ============================================================================
# Settings Fixtures
# ============================================================================

@pytest.fixture
def test_settings(upload_dir: Path, output_dir: Path) -> Settings:
    """Create test settings instance"""
    settings = Settings()
    settings.upload_dir = upload_dir
    settings.output_dir = output_dir
    settings.file_retention_minutes = 5
    settings.cleanup_interval_minutes = 5
    settings.auto_cleanup_enabled = True
    settings.max_upload_size = 10 * 1024 * 1024  # 10MB for tests
    settings.max_pdf_pages = 100
    return settings


# ============================================================================
# PDF File Fixtures
# ============================================================================

@pytest.fixture
def sample_pdf(temp_dir: Path) -> Path:
    """Create a simple test PDF file"""
    pdf_path = temp_dir / "sample.pdf"

    # Create a simple PDF with pikepdf
    pdf = pikepdf.Pdf.new()

    # Add a page
    page = pikepdf.Dictionary(
        Type=pikepdf.Name.Page,
        MediaBox=[0, 0, 612, 792],  # Letter size
    )
    pdf.pages.append(page)

    # Save the PDF
    pdf.save(pdf_path)

    return pdf_path


@pytest.fixture
def multi_page_pdf(temp_dir: Path) -> Path:
    """Create a multi-page test PDF file"""
    pdf_path = temp_dir / "multi_page.pdf"

    # Create PDF with multiple pages
    pdf = pikepdf.Pdf.new()

    for i in range(5):
        page = pikepdf.Dictionary(
            Type=pikepdf.Name.Page,
            MediaBox=[0, 0, 612, 792],
        )
        pdf.pages.append(page)

    pdf.save(pdf_path)

    return pdf_path


@pytest.fixture
def large_pdf(temp_dir: Path) -> Path:
    """Create a large test PDF file (10 pages)"""
    pdf_path = temp_dir / "large.pdf"

    pdf = pikepdf.Pdf.new()

    for i in range(10):
        page = pikepdf.Dictionary(
            Type=pikepdf.Name.Page,
            MediaBox=[0, 0, 612, 792],
        )
        pdf.pages.append(page)

    pdf.save(pdf_path)

    return pdf_path


@pytest.fixture
def corrupted_pdf(temp_dir: Path) -> Path:
    """Create a corrupted PDF file for error testing"""
    pdf_path = temp_dir / "corrupted.pdf"
    pdf_path.write_text("This is not a valid PDF file")
    return pdf_path


@pytest.fixture
def sample_pdf_list(temp_dir: Path) -> list[Path]:
    """Create multiple sample PDF files"""
    pdfs = []

    for i in range(3):
        pdf_path = temp_dir / f"sample_{i}.pdf"
        pdf = pikepdf.Pdf.new()

        # Add pages
        for j in range(2):
            page = pikepdf.Dictionary(
                Type=pikepdf.Name.Page,
                MediaBox=[0, 0, 612, 792],
            )
            pdf.pages.append(page)

        pdf.save(pdf_path)
        pdfs.append(pdf_path)

    return pdfs


# ============================================================================
# Image File Fixtures
# ============================================================================

@pytest.fixture
def sample_image(temp_dir: Path) -> Path:
    """Create a sample test image"""
    img_path = temp_dir / "sample.png"

    # Create a simple 100x100 red image
    img = Image.new('RGB', (100, 100), color='red')
    img.save(img_path)

    return img_path


# ============================================================================
# Service Fixtures
# ============================================================================

@pytest.fixture
def cleanup_service(test_settings: Settings) -> FileCleanupService:
    """Create file cleanup service instance"""
    return FileCleanupService(test_settings)


@pytest.fixture
def merge_service(test_settings: Settings) -> PdfMergeService:
    """Create PDF merge service instance"""
    return PdfMergeService(test_settings)


@pytest.fixture
def split_service(test_settings: Settings) -> PdfSplitService:
    """Create PDF split service instance"""
    return PdfSplitService(test_settings)


@pytest.fixture
def compress_service(test_settings: Settings) -> PdfCompressService:
    """Create PDF compress service instance"""
    return PdfCompressService(test_settings)


@pytest.fixture
def convert_service(test_settings: Settings) -> PdfConvertService:
    """Create PDF convert service instance"""
    return PdfConvertService(test_settings)


@pytest.fixture
def extract_service(test_settings: Settings) -> PdfExtractService:
    """Create PDF extract service instance"""
    return PdfExtractService(test_settings)


# ============================================================================
# API Client Fixtures
# ============================================================================

@pytest.fixture
def test_client() -> TestClient:
    """Create FastAPI test client"""
    from main import app
    return TestClient(app)


# ============================================================================
# Time Manipulation Fixtures
# ============================================================================

@pytest.fixture
def old_file(output_dir: Path) -> Path:
    """Create a file with old timestamp for cleanup testing"""
    file_path = output_dir / "old_file.pdf"
    file_path.write_text("old content")

    # Set modification time to 10 minutes ago
    import time
    old_time = time.time() - (10 * 60)  # 10 minutes ago
    import os
    os.utime(file_path, (old_time, old_time))

    return file_path


@pytest.fixture
def recent_file(output_dir: Path) -> Path:
    """Create a recent file for cleanup testing"""
    file_path = output_dir / "recent_file.pdf"
    file_path.write_text("recent content")
    return file_path


# ============================================================================
# Utility Functions
# ============================================================================

@pytest.fixture
def assert_pdf_valid():
    """Helper function to assert PDF validity"""
    def _assert_pdf_valid(pdf_path: Path):
        assert pdf_path.exists(), f"PDF file does not exist: {pdf_path}"
        assert pdf_path.suffix == ".pdf", f"File is not a PDF: {pdf_path}"

        # Try to open with pikepdf
        try:
            with pikepdf.Pdf.open(pdf_path) as pdf:
                assert len(pdf.pages) > 0, "PDF has no pages"
        except Exception as e:
            pytest.fail(f"PDF is invalid: {e}")

    return _assert_pdf_valid


@pytest.fixture
def get_pdf_page_count():
    """Helper function to get PDF page count"""
    def _get_page_count(pdf_path: Path) -> int:
        with pikepdf.Pdf.open(pdf_path) as pdf:
            return len(pdf.pages)
    return _get_page_count


@pytest.fixture
def create_test_pdf():
    """Factory fixture to create test PDFs on demand"""
    def _create_pdf(path: Path, num_pages: int = 1) -> Path:
        pdf = pikepdf.Pdf.new()

        for i in range(num_pages):
            page = pikepdf.Dictionary(
                Type=pikepdf.Name.Page,
                MediaBox=[0, 0, 612, 792],
            )
            pdf.pages.append(page)

        pdf.save(path)
        return path

    return _create_pdf
