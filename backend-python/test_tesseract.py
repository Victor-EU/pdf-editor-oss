"""
Test script for Tesseract configuration
Verifies auto-detection and configuration
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.tesseract_utils import TesseractConfig


def test_tesseract_configuration():
    """Test Tesseract configuration"""
    print("=" * 70)
    print("TESSERACT CONFIGURATION TEST")
    print("=" * 70)
    print()

    # Test auto-detection
    print("1. Testing auto-detection...")
    tesseract_path = TesseractConfig.find_tesseract()

    if tesseract_path:
        print(f"   ✅ Found Tesseract: {tesseract_path}")
    else:
        print("   ❌ Tesseract not found")
        print()
        print("Installation Instructions:")
        print(TesseractConfig.get_installation_instructions())
        return False

    print()

    # Test validation
    print("2. Testing validation...")
    is_valid, version, error = TesseractConfig.verify_tesseract(tesseract_path)

    if is_valid:
        print(f"   ✅ Tesseract is valid")
        print(f"   Version: {version}")
    else:
        print(f"   ❌ Tesseract validation failed: {error}")
        return False

    print()

    # Test language detection
    print("3. Testing language detection...")
    languages = TesseractConfig.get_available_languages(tesseract_path)

    if languages:
        print(f"   ✅ Found {len(languages)} languages")
        print(f"   Available: {', '.join(languages[:10])}")
        if len(languages) > 10:
            print(f"   ... and {len(languages) - 10} more")
    else:
        print("   ⚠️  No languages found (Tesseract may still work)")

    print()

    # Test full configuration
    print("4. Testing full configuration...")
    success, path, error_msg = TesseractConfig.configure_tesseract()

    if success:
        print(f"   ✅ Configuration successful")
        print(f"   Path: {path}")
    else:
        print(f"   ❌ Configuration failed")
        print(f"   Error: {error_msg}")
        return False

    print()
    print("=" * 70)
    print("✅ ALL TESTS PASSED - Tesseract is configured correctly!")
    print("=" * 70)

    return True


if __name__ == "__main__":
    success = test_tesseract_configuration()
    sys.exit(0 if success else 1)
