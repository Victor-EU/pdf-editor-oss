# PDF Editor - Free with Open Source 📄

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Material-UI](https://img.shields.io/badge/Material--UI-7FD68D?style=for-the-badge&logo=mui&logoColor=white)](https://mui.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

**A modern, full-stack PDF editing application built entirely with open source technologies. Free to use, free to modify.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [API Docs](#-api-documentation) • [Contributing](#-contributing)

</div>

---

## 🌟 Overview

PDF Editor is a comprehensive web application that provides professional-grade PDF manipulation capabilities. Built with 100% open source technologies, it offers an intuitive light green-themed interface for viewing, editing, merging, splitting, compressing, converting, extracting text, and OCR from PDF documents.

### ✨ Key Highlights

- 🎨 **Modern UI Design** - Clean, light green interface with Material-UI
- ⚡ **High Performance** - Powered by pikepdf (QPDF) for fast processing
- 🏗️ **Modern Architecture** - FastAPI backend + React frontend
- 🔒 **Type-Safe** - Full TypeScript implementation
- 📱 **Responsive Design** - Works seamlessly across devices
- 🆓 **100% Open Source** - No licensing costs or restrictions

---

## 🚀 Features

### PDF Viewing
- **View** PDFs with Mozilla's PDF.js viewer
- **Navigate** pages with intuitive controls
- **Zoom** from 50% to 200%
- Powered by `react-pdf` (open source)

### PDF Operations
| Feature | Description | API Endpoint |
|---------|-------------|--------------|
| **Merge** | Combine multiple PDFs into one | `POST /api/merge` |
| **Split** | Divide PDF by pages or ranges | `POST /api/split` |
| **Compress** | Reduce file size (3 levels) | `POST /api/compress` |
| **Convert** | Export to PNG, JPEG, or TIFF | `POST /api/convert` |
| **Extract Text** | Extract text from PDF documents | `POST /api/extract` |
| **Extract Tables** | Extract tables to Excel with headers | `POST /api/table-extract` |
| **OCR Text** | Extract text from scanned PDFs using Tesseract OCR | `POST /api/ocr` |

---

## 🛠️ Technology Stack

### Complete PDF Processing Stack

| Function | Python Module | System Tool | Purpose |
|----------|---------------|-------------|---------|
| **View PDF** | react-pdf | PDF.js (Mozilla) | Render PDF in browser |
| **Merge PDFs** | pikepdf | QPDF | Combine multiple PDFs |
| **Split PDF** | pikepdf | QPDF | Divide PDF into parts |
| **Compress PDF** | pikepdf | QPDF | Reduce file size |
| **Convert to Image** | pdf2image | Poppler (pdftoppm) | PDF → PNG/JPEG/TIFF |
| **Extract Text** | PyMuPDF (fitz) | MuPDF | Extract text directly |
| **Extract Tables** | camelot-py + openpyxl | Ghostscript + OpenCV | Tables → Excel with headers |
| **OCR Text** | pdf2image + pytesseract | Poppler + Tesseract | Images → OCR → Text |

### Backend
- **Framework**: FastAPI 0.104+ (Python)
- **PDF Library**: pikepdf 8.10+ (based on QPDF)
- **Text Extraction**: PyMuPDF (fitz) 1.23+
- **OCR Engine**: Tesseract 5.0+ via pytesseract
- **Image Conversion**: pdf2image + Pillow + Poppler
- **Server**: Uvicorn (ASGI)
- **License**: All MIT/Apache 2.0

### Frontend
- **Framework**: React 18 + TypeScript
- **PDF Viewer**: React-PDF (Mozilla PDF.js)
- **UI Library**: Material-UI (light green theme)
- **Build Tool**: Vite
- **HTTP Client**: Axios

---

## 📦 Installation

### Prerequisites

- **Python 3.9+**
- **Node.js 16+**
- **poppler-utils** (required for PDF to image conversion)
- **Tesseract OCR** (required for OCR text extraction)

#### Install System Dependencies

**macOS**:
```bash
brew install poppler tesseract
```

**Ubuntu/Debian**:
```bash
sudo apt-get install poppler-utils tesseract-ocr
# Optional: Install additional language packs
sudo apt-get install tesseract-ocr-spa tesseract-ocr-fra tesseract-ocr-deu
```

**Windows**:
- Poppler: Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases)
- Tesseract: Download from [Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)

### Backend Setup

```bash
# Navigate to Python backend
cd backend-python

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir uploads output

# Run server
python main.py
```

The API will be available at `http://localhost:8080`

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The application will be available at `http://localhost:3000`

---

## 🎯 Usage

### Quick Start

1. **Start Backend**: `cd backend-python && python main.py`
2. **Start Frontend**: `cd frontend && npm run dev`
3. **Open Browser**: Navigate to `http://localhost:3000`

### Operations

#### View PDF
1. Click "View PDF" tab
2. Upload a PDF file
3. Use navigation and zoom controls

#### Merge PDFs
1. Click "Merge PDFs" tab
2. Upload 2 or more PDF files
3. Click "Merge PDFs" button
4. Download the combined result

#### Split PDF
1. Click "Split PDF" tab
2. Upload a PDF file
3. Enter page ranges (e.g., "1-3,5-7")
4. Download split files

#### Compress PDF
1. Click "Compress PDF" tab
2. Upload a PDF file
3. Select compression level (Low/Medium/High)
4. Download compressed file

#### Convert to Images
1. Click "Convert to Image" tab
2. Upload a PDF file
3. Select format (PNG/JPEG/TIFF) and DPI
4. Download generated images

#### Extract Text
1. Click "Extract Text" tab
2. Upload a PDF file
3. Choose whether to include page numbers
4. Download extracted text as TXT file

#### OCR Text Extraction
1. Click "OCR Text" tab
2. Upload a scanned PDF file
3. Select language (English, Spanish, French, etc.)
4. Adjust DPI quality (150-600, default 300)
5. Download OCR-extracted text as TXT file

---

## 📡 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

### Endpoints

```
GET  /                         - API information
GET  /health                   - Health check
POST /api/merge                - Merge multiple PDFs
POST /api/split                - Split PDF by page ranges
POST /api/compress             - Compress PDF file
POST /api/convert              - Convert PDF to images
POST /api/extract              - Extract text from PDF
POST /api/ocr                  - OCR text extraction from scanned PDFs
GET  /api/download/{filename}  - Download processed file
```

For detailed API documentation, see [API.md](docs/API.md)

---

## 🏗️ Project Structure

```
pdf-editor/
├── backend-python/          # Python/FastAPI backend
│   ├── main.py             # FastAPI application
│   ├── models.py           # Pydantic models
│   ├── requirements.txt    # Dependencies
│   ├── routers/           # API endpoints
│   │   ├── merge.py
│   │   ├── split.py
│   │   ├── compress.py
│   │   ├── convert.py
│   │   ├── extract.py
│   │   ├── ocr.py
│   │   └── download.py
│   ├── services/          # Business logic
│   │   ├── pdf_merge.py
│   │   ├── pdf_split.py
│   │   ├── pdf_compress.py
│   │   ├── pdf_convert.py
│   │   ├── pdf_extract.py
│   │   └── pdf_ocr.py
│   ├── uploads/           # Temporary uploads
│   └── output/            # Processed files
│
└── frontend/              # React/TypeScript frontend
    ├── src/
    │   ├── components/
    │   │   ├── PDFViewer/     # React-PDF viewer
    │   │   └── Operations/    # PDF operation panels
    │   ├── theme/            # Material-UI theme (light green)
    │   ├── services/         # API client
    │   └── App.tsx          # Main application
    └── public/
        └── favicon.svg      # Light green PDF icon
```

---

## 🔧 Development

### Backend Development

Run with auto-reload:
```bash
cd backend-python
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### Frontend Development

Run development server:
```bash
cd frontend
npm run dev
```

Build for production:
```bash
npm run build
```

---

## 🌟 Open Source Libraries

This project is built entirely with open source technologies:

| Library | Purpose | License |
|---------|---------|---------|
| **pikepdf** | PDF manipulation | MPL-2.0 |
| **pdf2image** | PDF to image conversion | MIT |
| **FastAPI** | Web framework | MIT |
| **React** | UI library | MIT |
| **PDF.js** | PDF viewer (Mozilla) | Apache 2.0 |
| **Material-UI** | Component library | MIT |
| **Pillow** | Image processing | HPND |
| **PyMuPDF** | Text extraction | AGPL-3.0 |
| **Tesseract OCR** | OCR engine (Google) | Apache 2.0 |

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🐛 Bug Reports

Please use the [GitHub issue tracker](https://github.com/Victor-EU/pdf-editor/issues) to report bugs.

---

## 💡 Roadmap

- [x] Complete open source transformation
- [x] Python/FastAPI backend
- [x] React-PDF viewer integration
- [x] Light green theme
- [x] Text extraction from PDFs
- [x] OCR support with Tesseract
- [ ] Docker containerization
- [ ] Unit and integration tests
- [ ] CI/CD pipeline
- [ ] PDF form filling
- [ ] Digital signatures
- [ ] Batch processing
- [ ] Cloud storage integration
- [ ] PDF watermarking
- [ ] PDF encryption/decryption

---

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

## 📧 Support

For support, please open an issue on [GitHub](https://github.com/Victor-EU/pdf-editor/issues).

---

<div align="center">

**Built with ❤️ using 100% open source technologies**

[![GitHub](https://img.shields.io/github/stars/Victor-EU/pdf-editor?style=social)](https://github.com/Victor-EU/pdf-editor)

</div>
