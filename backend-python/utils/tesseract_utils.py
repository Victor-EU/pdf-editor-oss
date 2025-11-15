"""
Tesseract OCR Utilities
Smart detection and configuration of Tesseract installation
"""

import os
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)


class TesseractConfig:
    """
    Automatically detects and configures Tesseract OCR.

    Handles cross-platform installations and provides clear error messages.
    """

    # Common Tesseract installation locations
    COMMON_PATHS = [
        # macOS Homebrew (Intel)
        "/usr/local/bin/tesseract",
        # macOS Homebrew (Apple Silicon)
        "/opt/homebrew/bin/tesseract",
        # Linux standard
        "/usr/bin/tesseract",
        # Windows Program Files
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        # Windows user install
        r"C:\Users\%USERNAME%\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
    ]

    @staticmethod
    def find_tesseract() -> Optional[str]:
        """
        Automatically find Tesseract installation.

        Returns:
            Path to tesseract executable or None if not found
        """
        # 1. Check if tesseract is in PATH
        tesseract_path = shutil.which("tesseract")
        if tesseract_path:
            logger.info(f"Found Tesseract in PATH: {tesseract_path}")
            return tesseract_path

        # 2. Check common installation locations
        for path in TesseractConfig.COMMON_PATHS:
            # Expand environment variables (Windows)
            expanded_path = os.path.expandvars(path)

            if os.path.isfile(expanded_path):
                logger.info(f"Found Tesseract at: {expanded_path}")
                return expanded_path

        # 3. Check project local installation
        project_root = Path(__file__).parent.parent
        local_paths = [
            project_root / "bin" / "tesseract",
            project_root / "bin" / "tesseract.exe",
            project_root / "tesseract" / "tesseract",
            project_root / "tesseract" / "tesseract.exe",
        ]

        for local_path in local_paths:
            if local_path.exists():
                logger.info(f"Found Tesseract in project: {local_path}")
                return str(local_path)

        logger.warning("Tesseract not found in any standard location")
        return None

    @staticmethod
    def verify_tesseract(tesseract_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Verify that Tesseract is working and get version.

        Args:
            tesseract_path: Path to tesseract executable

        Returns:
            Tuple of (is_valid, version, error_message)
        """
        if not tesseract_path:
            return False, None, "No Tesseract path provided"

        if not os.path.isfile(tesseract_path):
            return False, None, f"Tesseract executable not found at: {tesseract_path}"

        try:
            # Run tesseract --version
            result = subprocess.run(
                [tesseract_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Extract version from output
                version_line = result.stdout.split('\n')[0]
                logger.info(f"Tesseract validation successful: {version_line}")
                return True, version_line, None
            else:
                error = result.stderr or "Unknown error"
                return False, None, f"Tesseract validation failed: {error}"

        except subprocess.TimeoutExpired:
            return False, None, "Tesseract validation timed out"
        except Exception as e:
            return False, None, f"Error running Tesseract: {str(e)}"

    @staticmethod
    def get_available_languages(tesseract_path: str) -> List[str]:
        """
        Get list of available Tesseract languages.

        Args:
            tesseract_path: Path to tesseract executable

        Returns:
            List of language codes
        """
        try:
            result = subprocess.run(
                [tesseract_path, "--list-langs"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Parse output (first line is header)
                lines = result.stdout.strip().split('\n')
                languages = [line.strip() for line in lines[1:] if line.strip()]
                logger.info(f"Available Tesseract languages: {', '.join(languages)}")
                return languages
            else:
                logger.warning("Could not retrieve Tesseract languages")
                return []

        except Exception as e:
            logger.warning(f"Error getting Tesseract languages: {str(e)}")
            return []

    @staticmethod
    def get_installation_instructions() -> str:
        """
        Get platform-specific installation instructions.

        Returns:
            Installation instructions string
        """
        import platform

        system = platform.system().lower()

        if system == "darwin":  # macOS
            return """
Tesseract is not installed. Please install it using Homebrew:

    brew install tesseract

For additional languages:
    brew install tesseract-lang

Then restart the application.
"""

        elif system == "linux":
            return """
Tesseract is not installed. Please install it using your package manager:

Ubuntu/Debian:
    sudo apt-get update
    sudo apt-get install tesseract-ocr

For additional languages:
    sudo apt-get install tesseract-ocr-[lang]
    Example: sudo apt-get install tesseract-ocr-spa

Fedora/RHEL:
    sudo dnf install tesseract

Then restart the application.
"""

        elif system == "windows":
            return """
Tesseract is not installed. Please install it:

1. Download the installer from:
   https://github.com/UB-Mannheim/tesseract/wiki

2. Run the installer (choose default location)

3. Add Tesseract to your PATH or set TESSERACT_CMD environment variable:
   set TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe

Then restart the application.
"""

        else:
            return """
Tesseract is not installed. Please install Tesseract OCR for your operating system.
Visit: https://github.com/tesseract-ocr/tesseract

Then restart the application.
"""

    @staticmethod
    def configure_tesseract(custom_path: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Complete Tesseract configuration.

        Args:
            custom_path: Optional custom path to tesseract

        Returns:
            Tuple of (success, tesseract_path, error_message)
        """
        logger.info("=" * 70)
        logger.info("TESSERACT CONFIGURATION")
        logger.info("=" * 70)

        # 1. Determine tesseract path
        if custom_path:
            logger.info(f"Using custom Tesseract path: {custom_path}")
            tesseract_path = custom_path
        else:
            logger.info("Auto-detecting Tesseract installation...")
            tesseract_path = TesseractConfig.find_tesseract()

        # 2. Validate tesseract
        if not tesseract_path:
            error_msg = "Tesseract not found!\n" + TesseractConfig.get_installation_instructions()
            logger.error(error_msg)
            return False, None, error_msg

        is_valid, version, error = TesseractConfig.verify_tesseract(tesseract_path)

        if not is_valid:
            error_msg = f"Tesseract validation failed: {error}\n" + TesseractConfig.get_installation_instructions()
            logger.error(error_msg)
            return False, tesseract_path, error_msg

        # 3. Get available languages
        languages = TesseractConfig.get_available_languages(tesseract_path)

        logger.info(f"✅ Tesseract configured successfully")
        logger.info(f"   Path: {tesseract_path}")
        logger.info(f"   Version: {version}")
        logger.info(f"   Languages: {len(languages)} available ({', '.join(languages[:5])}...)")
        logger.info("=" * 70)

        return True, tesseract_path, None


def get_tesseract_path(custom_path: Optional[str] = None) -> str:
    """
    Get and validate Tesseract path.

    Args:
        custom_path: Optional custom path from environment or config

    Returns:
        Valid tesseract path

    Raises:
        RuntimeError: If Tesseract is not found or invalid
    """
    success, path, error = TesseractConfig.configure_tesseract(custom_path)

    if not success:
        raise RuntimeError(
            f"Tesseract OCR is not configured correctly.\n\n{error}"
        )

    return path
