# Tesseract OCR Setup Guide

## Overview

The PDF Editor uses Tesseract OCR for extracting text from scanned PDFs and images. Tesseract is **automatically detected** on your system, so in most cases, you just need to install it and the application will find it.

## Quick Start

### macOS (Homebrew)

```bash
# Install Tesseract
brew install tesseract

# Optional: Install additional languages
brew install tesseract-lang

# Verify installation
tesseract --version
```

### Linux (Ubuntu/Debian)

```bash
# Install Tesseract
sudo apt-get update
sudo apt-get install tesseract-ocr

# Optional: Install additional languages
sudo apt-get install tesseract-ocr-spa  # Spanish
sudo apt-get install tesseract-ocr-fra  # French
sudo apt-get install tesseract-ocr-deu  # German

# Verify installation
tesseract --version
```

### Linux (Fedora/RHEL)

```bash
# Install Tesseract
sudo dnf install tesseract

# Optional: Install language packs
sudo dnf install tesseract-langpack-spa  # Spanish

# Verify installation
tesseract --version
```

### Windows

1. **Download Installer**
   - Visit: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest installer (e.g., `tesseract-ocr-w64-setup-5.3.3.exe`)

2. **Run Installer**
   - Execute the installer
   - Choose default installation path: `C:\Program Files\Tesseract-OCR`
   - Check "Add to PATH" option (recommended)

3. **Verify Installation**
   ```cmd
   tesseract --version
   ```

## Configuration

### Automatic Detection (Recommended)

The application **automatically detects** Tesseract in the following locations:

**macOS:**
- `/opt/homebrew/bin/tesseract` (Apple Silicon)
- `/usr/local/bin/tesseract` (Intel)

**Linux:**
- `/usr/bin/tesseract`

**Windows:**
- `C:\Program Files\Tesseract-OCR\tesseract.exe`
- `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`

### Manual Configuration

If Tesseract is installed in a non-standard location, set the environment variable:

**Option 1: Environment Variable**
```bash
# macOS/Linux
export TESSERACT_CMD=/custom/path/to/tesseract

# Windows
set TESSERACT_CMD=C:\Custom\Path\tesseract.exe
```

**Option 2: .env File**
```bash
# Create or edit backend-python/.env
TESSERACT_CMD=/custom/path/to/tesseract
```

**Option 3: Python Code**
```python
from config import Settings

settings = Settings()
settings.tesseract_cmd = "/custom/path/to/tesseract"
```

## Language Support

### Check Available Languages

```bash
tesseract --list-langs
```

### Install Additional Languages

**macOS:**
```bash
brew install tesseract-lang
```

**Linux (Ubuntu/Debian):**
```bash
# List available language packs
apt-cache search tesseract-ocr

# Install specific language
sudo apt-get install tesseract-ocr-[LANG]

# Examples:
sudo apt-get install tesseract-ocr-spa  # Spanish
sudo apt-get install tesseract-ocr-fra  # French
sudo apt-get install tesseract-ocr-deu  # German
sudo apt-get install tesseract-ocr-ita  # Italian
sudo apt-get install tesseract-ocr-por  # Portuguese
sudo apt-get install tesseract-ocr-rus  # Russian
sudo apt-get install tesseract-ocr-chi-sim  # Chinese Simplified
sudo apt-get install tesseract-ocr-jpn  # Japanese
sudo apt-get install tesseract-ocr-kor  # Korean
sudo apt-get install tesseract-ocr-ara  # Arabic
sudo apt-get install tesseract-ocr-hin  # Hindi
```

**Windows:**
- Language data files are included with the installer
- Additional languages can be downloaded from: https://github.com/tesseract-ocr/tessdata

### Using Languages in OCR

```bash
# API request with language parameter
curl -X POST http://localhost:8080/api/ocr \
  -F "file=@document.pdf" \
  -F "language=spa"  # Spanish

# Multiple languages
curl -X POST http://localhost:8080/api/ocr \
  -F "file=@document.pdf" \
  -F "language=eng+spa"  # English + Spanish
```

**Supported Language Codes:**
- `eng` - English (default)
- `spa` - Spanish
- `fra` - French
- `deu` - German
- `ita` - Italian
- `por` - Portuguese
- `rus` - Russian
- `chi_sim` - Chinese Simplified
- `chi_tra` - Chinese Traditional
- `jpn` - Japanese
- `kor` - Korean
- `ara` - Arabic
- `hin` - Hindi

## Troubleshooting

### "Tesseract not found" Error

**Symptom:**
```
RuntimeError: Tesseract OCR is not configured correctly.
Tesseract not found!
```

**Solution:**
1. Install Tesseract (see Quick Start above)
2. Verify it's in your PATH: `tesseract --version`
3. If not in PATH, configure manually (see Configuration section)
4. Restart the application

### "Tesseract validation failed" Error

**Symptom:**
```
Tesseract validation failed: [error message]
```

**Solution:**
1. Check Tesseract is executable: `tesseract --version`
2. Verify file permissions (Linux/macOS)
3. Ensure PATH is correct
4. Try running with full path

### Language Not Available

**Symptom:**
```
Error: Failed loading language 'fra'
```

**Solution:**
1. Check available languages: `tesseract --list-langs`
2. Install missing language pack
3. Verify language code is correct

### Poor OCR Quality

**Symptom:**
Extracted text is inaccurate or garbled

**Solutions:**
1. **Increase DPI**
   ```bash
   curl -X POST http://localhost:8080/api/ocr \
     -F "file=@document.pdf" \
     -F "dpi=300"  # Higher quality (slower)
   ```

2. **Use Correct Language**
   - Always specify the document's language
   - Use combined languages if document is multilingual

3. **Pre-process Images**
   - Ensure scans are high quality
   - Clean, straight scans work best
   - Minimum 200 DPI recommended

4. **Adjust PSM (Page Segmentation Mode)**
   ```bash
   curl -X POST http://localhost:8080/api/ocr \
     -F "file=@document.pdf" \
     -F "psm=6"  # Assume uniform block of text
   ```

   **PSM Options:**
   - `3` - Fully automatic page segmentation (default)
   - `4` - Assume single column of text
   - `6` - Assume uniform block of text
   - `11` - Sparse text
   - `13` - Raw line (no layout analysis)

## Verification

### Test Tesseract Installation

```bash
# Create test image with text
echo "Hello World" | convert -pointsize 40 label:@- test.png

# Run OCR
tesseract test.png stdout

# Expected output: "Hello World"
```

### Test via API

```bash
# Start backend
cd backend-python
python3 main.py

# Check Tesseract configuration in logs
# You should see:
# ======================================================================
# TESSERACT CONFIGURATION
# ======================================================================
# ✅ Tesseract configured successfully
#    Path: /opt/homebrew/bin/tesseract
#    Version: tesseract 5.3.3
#    Languages: 120 available (eng, osd, snum, spa, fra...)
# ======================================================================

# Test OCR endpoint
curl http://localhost:8080/api/ocr -X POST \
  -F "file=@sample_scanned.pdf" \
  -F "language=eng"
```

## Project-Local Installation (Advanced)

You can install Tesseract locally in your project:

### Download Tesseract

**macOS/Linux:**
```bash
cd backend-python
mkdir -p bin

# Download static binary (example for macOS)
# Place tesseract binary in bin/

chmod +x bin/tesseract
```

**Set in .env:**
```bash
TESSERACT_CMD=./bin/tesseract
```

### Docker

```dockerfile
# In Dockerfile
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-eng && \
    apt-get clean
```

## Performance Tips

1. **DPI Settings**
   - 150 DPI: Fast, good for clean documents
   - 300 DPI: Standard, good quality/speed balance (default)
   - 600 DPI: High quality, slower

2. **Language Loading**
   - Only load languages you need
   - Multiple languages slow down processing

3. **Page Segmentation**
   - Choose appropriate PSM for document layout
   - PSM 3 (default) is slowest but most accurate

4. **Batch Processing**
   - Process multiple pages in parallel
   - Use async endpoints

## Resources

- **Tesseract GitHub**: https://github.com/tesseract-ocr/tesseract
- **Documentation**: https://tesseract-ocr.github.io/
- **Language Data**: https://github.com/tesseract-ocr/tessdata
- **Improving Quality**: https://tesseract-ocr.github.io/tessdoc/ImproveQuality

## Support

If you encounter issues:
1. Check application logs for detailed error messages
2. Verify Tesseract installation: `tesseract --version`
3. Test with a simple image first
4. Open an issue on GitHub with:
   - Operating system
   - Tesseract version
   - Error message
   - Sample file (if possible)

---

**Auto-Detection Status**: ✅ Enabled
**Manual Configuration**: Optional
**Cross-Platform**: ✅ Windows, macOS, Linux
