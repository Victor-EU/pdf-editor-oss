"""
Dependency Injection Container
Manages service instances for proper OOP architecture
"""

from functools import lru_cache
from config import Settings, get_settings
from services.pdf_merge import PdfMergeService
from services.pdf_split import PdfSplitService
from services.pdf_compress import PdfCompressService
from services.pdf_convert import PdfConvertService
from services.pdf_extract import PdfExtractService
from services.pdf_ocr import PdfOcrService

# Service instances cache
_service_instances = {}


@lru_cache()
def get_pdf_merge_service() -> PdfMergeService:
    """Get or create PdfMergeService instance"""
    if 'merge' not in _service_instances:
        settings = get_settings()
        _service_instances['merge'] = PdfMergeService(settings)
    return _service_instances['merge']


@lru_cache()
def get_pdf_split_service() -> PdfSplitService:
    """Get or create PdfSplitService instance"""
    if 'split' not in _service_instances:
        settings = get_settings()
        _service_instances['split'] = PdfSplitService(settings)
    return _service_instances['split']


@lru_cache()
def get_pdf_compress_service() -> PdfCompressService:
    """Get or create PdfCompressService instance"""
    if 'compress' not in _service_instances:
        settings = get_settings()
        _service_instances['compress'] = PdfCompressService(settings)
    return _service_instances['compress']


@lru_cache()
def get_pdf_convert_service() -> PdfConvertService:
    """Get or create PdfConvertService instance"""
    if 'convert' not in _service_instances:
        settings = get_settings()
        _service_instances['convert'] = PdfConvertService(settings)
    return _service_instances['convert']


@lru_cache()
def get_pdf_extract_service() -> PdfExtractService:
    """Get or create PdfExtractService instance"""
    if 'extract' not in _service_instances:
        settings = get_settings()
        _service_instances['extract'] = PdfExtractService(settings)
    return _service_instances['extract']


@lru_cache()
def get_pdf_ocr_service() -> PdfOcrService:
    """Get or create PdfOcrService instance"""
    if 'ocr' not in _service_instances:
        settings = get_settings()
        _service_instances['ocr'] = PdfOcrService(settings)
    return _service_instances['ocr']
