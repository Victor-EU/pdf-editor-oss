# PDF Editor Backend - Python/FastAPI

Modern, open-source PDF editor backend built with FastAPI and open source libraries.

## Features

- **PDF Merge**: Combine multiple PDF files into one
- **PDF Split**: Split PDFs by page ranges
- **PDF Compress**: Reduce PDF file size with configurable compression
- **PDF to Image**: Convert PDF pages to PNG, JPEG, or TIFF images

## Technology Stack

- **Framework**: FastAPI 0.104+
- **PDF Library**: pikepdf (based on QPDF)
- **Image Conversion**: pdf2image + Pillow
- **Python**: 3.9+

## Installation

### Prerequisites

- Python 3.9 or higher
- poppler-utils (for PDF to image conversion)

#### Install poppler-utils:

**macOS**:
```bash
brew install poppler
```

**Ubuntu/Debian**:
```bash
sudo apt-get install poppler-utils
```

### Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create directories:
```bash
mkdir uploads output
```

## Running the Server

### Development Mode:
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### Production Mode:
```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4
```

The API will be available at `http://localhost:8080`

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## API Endpoints

### Merge PDFs
`POST /api/merge`
- Upload multiple PDF files
- Returns merged PDF

### Split PDF
`POST /api/split`
- Upload PDF file
- Specify page ranges (e.g., "1-3,5-7")
- Returns split PDF files

### Compress PDF
`POST /api/compress`
- Upload PDF file
- Choose compression level (low/medium/high)
- Returns compressed PDF

### Convert to Images
`POST /api/convert`
- Upload PDF file
- Choose format (PNG/JPEG/TIFF)
- Specify DPI and pages
- Returns image files

### Download File
`GET /download/{filename}`
- Download processed files

## Project Structure

```
backend-python/
├── main.py              # FastAPI application
├── models.py            # Pydantic models
├── requirements.txt     # Python dependencies
├── routers/            # API route handlers
│   ├── merge.py
│   ├── split.py
│   ├── compress.py
│   ├── convert.py
│   └── download.py
├── services/           # Business logic
│   ├── pdf_merge.py
│   ├── pdf_split.py
│   ├── pdf_compress.py
│   └── pdf_convert.py
├── uploads/            # Temporary uploads
└── output/             # Processed files
```

## License

MIT License - Open Source
