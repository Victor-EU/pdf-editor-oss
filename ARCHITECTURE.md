# Architecture Documentation

## Table of Contents
- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Backend Architecture](#backend-architecture)
- [Frontend Architecture](#frontend-architecture)
- [Data Flow](#data-flow)
- [Design Patterns](#design-patterns)
- [Security Considerations](#security-considerations)

---

## System Overview

The PDF Editor is built on a modern **client-server architecture** with clear separation of concerns:

- **Frontend**: React-based Single Page Application (SPA)
- **Backend**: Python FastAPI REST API
- **Communication**: HTTP/REST with JSON payloads and multipart/form-data for file uploads
- **Architecture Pattern**: Three-tier architecture (Presentation → Business Logic → Data Access)

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Client Browser                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         React Frontend (TypeScript)                   │  │
│  │  - Material-UI Components                            │  │
│  │  - PDF.js Viewer                                     │  │
│  │  - Axios HTTP Client                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/REST API
                        │ (JSON + Multipart Form Data)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Python)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  API Layer (Routers)                  │  │
│  │  - Request Validation (Pydantic)                     │  │
│  │  - Error Handling                                    │  │
│  │  - CORS Middleware                                   │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │              Business Logic (Services)                │  │
│  │  - PDF Processing                                    │  │
│  │  - Text Extraction                                   │  │
│  │  - OCR Processing                                    │  │
│  │  - File Management                                   │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │          External Libraries & Tools                   │  │
│  │  - pikepdf (QPDF)                                    │  │
│  │  - PyMuPDF (fitz)                                    │  │
│  │  - Tesseract OCR                                     │  │
│  │  - pdf2image + Pillow                                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   File System Storage                        │
│  - uploads/  (Temporary input files)                        │
│  - output/   (Processed output files)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Backend Architecture

### Directory Structure

```
backend-python/
├── main.py              # Application entry point
├── config.py            # Configuration management
├── models.py            # Pydantic data models
├── exceptions.py        # Custom exceptions
├── dependencies.py      # Dependency injection
├── routers/             # API route handlers
│   ├── merge.py         # PDF merge endpoint
│   ├── split.py         # PDF split endpoint
│   ├── compress.py      # PDF compress endpoint
│   ├── convert.py       # PDF to image endpoint
│   ├── extract.py       # Text extraction endpoint
│   ├── ocr.py           # OCR extraction endpoint
│   └── download.py      # File download endpoint
└── services/            # Business logic layer
    ├── pdf_merge.py     # Merge service
    ├── pdf_split.py     # Split service
    ├── pdf_compress.py  # Compress service
    ├── pdf_convert.py   # Convert service
    ├── pdf_extract.py   # Extract service
    └── pdf_ocr.py       # OCR service
```

### Layered Architecture

#### 1. **API Layer** (routers/)
- **Responsibility**: Handle HTTP requests/responses
- **Pattern**: Router pattern with FastAPI
- **Key Features**:
  - Request validation using Pydantic models
  - Multipart file upload handling
  - Error handling and HTTP status codes
  - CORS configuration
  - API documentation (OpenAPI/Swagger)

#### 2. **Business Logic Layer** (services/)
- **Responsibility**: Core PDF processing operations
- **Pattern**: Service pattern with dependency injection
- **Key Features**:
  - PDF manipulation using pikepdf
  - Text extraction using PyMuPDF
  - OCR processing using Tesseract
  - Image conversion using pdf2image
  - File cleanup and management

#### 3. **Data Access Layer**
- **Responsibility**: File system operations
- **Implementation**: Asynchronous file I/O using aiofiles
- **Storage**:
  - Temporary uploads: `uploads/` directory
  - Processed output: `output/` directory

### Key Design Decisions

#### Dependency Injection Pattern
```python
# dependencies.py
@lru_cache()
def get_pdf_merge_service() -> PdfMergeService:
    if 'merge' not in _service_instances:
        settings = get_settings()
        _service_instances['merge'] = PdfMergeService(settings)
    return _service_instances['merge']
```

**Benefits**:
- Singleton pattern for service instances
- Easy testing and mocking
- Centralized configuration management
- Efficient resource usage

#### Service Pattern
Each PDF operation has its own service class:

```python
class PdfMergeService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)

    async def merge_pdfs(
        self,
        input_files: List[Path],
        output_dir: Path,
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        # Business logic here
        pass
```

**Benefits**:
- Single Responsibility Principle
- Reusable business logic
- Easier unit testing
- Clear separation of concerns

#### Exception Handling
Custom exception hierarchy:

```python
class PDFEditorException(Exception):
    """Base exception"""

class ValidationError(PDFEditorException):
    """Validation errors"""

class PDFProcessingError(PDFEditorException):
    """Processing errors"""

class InvalidPDFError(PDFEditorException):
    """Invalid PDF file errors"""
```

---

## Frontend Architecture

### Directory Structure

```
frontend/src/
├── main.tsx             # Application entry point
├── App.tsx              # Root component
├── components/          # React components
│   ├── PDFViewer/       # PDF viewing component
│   │   ├── PDFViewer.tsx
│   │   └── PDFViewer.module.css
│   └── Operations/      # Operation panels
│       ├── MergePanel/
│       ├── SplitPanel/
│       ├── CompressPanel/
│       ├── ConvertPanel/
│       ├── ExtractPanel/
│       └── OcrPanel/
├── services/            # API client layer
│   └── api.ts           # Axios-based API client
├── theme/               # Material-UI theming
│   └── theme.ts         # Light green theme
├── styles/              # Global & shared styles
│   ├── globals.css      # Global styles
│   ├── variables.css    # CSS custom properties
│   ├── components.css   # Shared component styles
│   └── utilities.css    # Utility classes
└── types/               # TypeScript definitions
    └── index.ts         # Type definitions
```

### Component Architecture

#### Component Hierarchy

```
App (Root)
├── Header
├── Tabs Navigation
└── Tab Panels
    ├── PDFViewer Panel
    ├── MergePanel
    ├── SplitPanel
    ├── CompressPanel
    ├── ConvertPanel
    ├── ExtractPanel
    └── OcrPanel
```

#### Component Pattern
All operation panels follow a consistent pattern:

```typescript
export const OperationPanel = () => {
  // 1. State management
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 2. Event handlers
  const handleFileUpload = (event: ChangeEvent<HTMLInputElement>) => { }
  const handleDragDrop = (event: DragEvent) => { }
  const handleOperation = async () => { }

  // 3. Render UI
  return (
    <Box className={styles.container}>
      {/* Upload area, controls, action button */}
    </Box>
  )
}
```

### CSS Architecture

**Scalable CSS structure** using CSS Modules:

1. **Global Styles** (`styles/globals.css`)
   - CSS reset
   - Base HTML element styles
   - Global layout rules

2. **CSS Variables** (`styles/variables.css`)
   - Color palette (light green theme)
   - Spacing scale
   - Typography scale
   - Border radius values
   - Shadow definitions

3. **Shared Components** (`styles/components.css`)
   - Reusable component patterns
   - `.operation-container`
   - `.upload-area`
   - `.file-list`

4. **Component-Specific** (`.module.css` files)
   - Component-scoped styles
   - Uses `composes` to inherit shared styles
   - Local overrides only

**Example**:
```css
/* ExtractPanel.module.css */
.container {
  composes: operation-container from '../../../styles/components.css';
}

.uploadArea {
  composes: upload-area from '../../../styles/components.css';
}
```

### State Management

Currently using **React Hooks** for local component state:
- `useState` for component state
- `useEffect` for side effects (future)
- No global state management (not needed yet)

**Future Consideration**: If cross-component state sharing becomes necessary, consider:
- React Context API (lightweight)
- Zustand (modern, simple)
- Redux Toolkit (complex scenarios)

---

## Data Flow

### Upload → Process → Download Flow

```
1. User Action (Frontend)
   ↓
2. File Upload via Drag-and-Drop or File Input
   ↓
3. API Request (POST with multipart/form-data)
   │
   ├─→ File: Binary data
   ├─→ Parameters: JSON or form fields
   └─→ Headers: Content-Type: multipart/form-data
   ↓
4. Backend Processing
   │
   ├─→ Save to uploads/ (temporary)
   ├─→ Validate file (PDF format, size)
   ├─→ Process via service (merge, split, etc.)
   ├─→ Save result to output/
   └─→ Clean up uploads/
   ↓
5. API Response (JSON)
   {
     "success": true,
     "message": "...",
     "data": {
       "fileName": "output.pdf",
       "fileSize": 12345,
       "downloadUrl": "/download/output.pdf"
     }
   }
   ↓
6. Frontend Downloads File
   ├─→ GET /api/download/{fileName}
   ├─→ Receive blob response
   └─→ Trigger browser download
```

### Request Flow Example (Merge PDFs)

```typescript
// Frontend (MergePanel.tsx)
const handleMerge = async () => {
  const formData = new FormData()
  files.forEach(file => formData.append('files', file))
  formData.append('outputFileName', outputName)

  const response = await apiService.mergePdfs(files, outputName)
  const blob = await apiService.downloadFile(response.data.fileName)
  apiService.triggerDownload(blob, response.data.fileName)
}

// API Client (api.ts)
async mergePdfs(files: File[], outputFileName?: string) {
  const formData = new FormData()
  files.forEach(file => formData.append('files', file))
  if (outputFileName) formData.append('outputFileName', outputFileName)

  const response = await this.client.post('/merge', formData)
  return response.data
}

// Backend Router (merge.py)
@router.post("/merge")
async def merge_pdfs(
    files: List[UploadFile] = File(...),
    outputFileName: Optional[str] = Form(None),
    merge_service: PdfMergeService = Depends(get_pdf_merge_service)
):
    # Save files, validate, call service
    result = await merge_service.merge_pdfs(temp_files, ...)
    return ApiResponse.success_response(message, file_response)

// Service (pdf_merge.py)
async def merge_pdfs(self, input_files: List[Path], ...) -> Dict:
    pdf = pikepdf.Pdf.new()
    for file in input_files:
        src = pikepdf.Pdf.open(file)
        pdf.pages.extend(src.pages)
    pdf.save(output_path)
    return {"filename": ..., "size": ...}
```

---

## Design Patterns

### 1. **Repository Pattern** (Implicit)
Services act as repositories for PDF operations:
- Encapsulate data access (file system)
- Abstract business logic from API layer
- Provide clean interfaces

### 2. **Factory Pattern**
Dependency injection functions act as factories:
```python
def get_pdf_merge_service() -> PdfMergeService:
    return PdfMergeService(get_settings())
```

### 3. **Strategy Pattern**
Different compression levels use strategy pattern:
```python
# compress_level parameter determines strategy
if compress_level == "low":
    # Low compression strategy
elif compress_level == "medium":
    # Medium compression strategy
else:
    # High compression strategy
```

### 4. **Facade Pattern**
Service classes provide simple facades over complex libraries:
```python
class PdfOcrService:
    # Simplifies complex Tesseract + pdf2image interaction
    async def ocr_pdf(self, input_path, ...):
        images = convert_from_path(input_path, dpi=dpi)
        for image in images:
            text = pytesseract.image_to_string(image, lang=language)
        return result
```

### 5. **Template Method Pattern**
All operation panels follow template:
1. State initialization
2. File upload handling
3. Parameter configuration
4. Operation execution
5. Download result

---

## Security Considerations

### Input Validation

1. **File Type Validation**
   ```python
   if not file.filename.endswith('.pdf'):
       raise ValidationError("Only PDF files are supported")
   ```

2. **File Size Limits**
   - FastAPI's `File()` enforces size limits
   - Configurable via `config.py`

3. **Parameter Validation**
   - Pydantic models validate all inputs
   - Type safety with TypeScript frontend

### File Handling Security

1. **Temporary File Cleanup**
   ```python
   finally:
       if input_path.exists():
           input_path.unlink()
   ```

2. **UUID-based Filenames**
   ```python
   temp_file = settings.upload_dir / f"{uuid.uuid4()}_{file.filename}"
   ```

3. **Directory Isolation**
   - Uploads and outputs in separate directories
   - No direct path traversal allowed

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production**: Restrict `allow_origins` to specific domains

### Error Handling

- Never expose internal paths or stack traces to clients
- Log detailed errors server-side
- Return generic error messages to frontend

```python
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    raise PDFProcessingError("Processing failed")  # Generic message
```

---

## Performance Considerations

### 1. **Asynchronous I/O**
```python
async with aiofiles.open(temp_file, 'wb') as f:
    content = await file.read()
    await f.write(content)
```

### 2. **Service Instance Caching**
```python
@lru_cache()  # Singleton pattern
def get_pdf_merge_service() -> PdfMergeService:
    ...
```

### 3. **Lazy Loading** (Frontend)
- Components loaded on-demand
- PDF.js loads pages incrementally
- Images loaded as needed

### 4. **File Cleanup**
Automatic cleanup after processing:
```python
finally:
    for temp_file in temp_files:
        if temp_file.exists():
            temp_file.unlink()
```

---

## Scalability Considerations

### Current Limitations
1. **File Storage**: Local file system
2. **Processing**: Synchronous (one request at a time)
3. **State**: No session management

### Future Enhancements
1. **Cloud Storage**: S3, Azure Blob Storage
2. **Task Queue**: Celery with Redis/RabbitMQ
3. **Load Balancing**: Multiple backend instances
4. **Caching**: Redis for processed files
5. **Containerization**: Docker for easy deployment

---

## Testing Strategy

### Backend Testing
- **Unit Tests**: Test individual services
- **Integration Tests**: Test API endpoints
- **Test Framework**: pytest + pytest-asyncio

### Frontend Testing
- **Unit Tests**: Component testing
- **Integration Tests**: User interaction flows
- **Test Framework**: Vitest + React Testing Library

### Test Coverage Goals
- Services: 80%+ coverage
- API Routes: 90%+ coverage
- Components: 70%+ coverage

---

## Monitoring and Logging

### Logging Strategy
```python
logger = logging.getLogger(__name__)
logger.info(f"Processing {len(files)} files...")
logger.error(f"Failed to process: {str(e)}")
```

**Log Levels**:
- `INFO`: Operation progress
- `WARNING`: Recoverable issues
- `ERROR`: Operation failures
- `DEBUG`: Detailed diagnostic info

### Future: Monitoring
- **Metrics**: Prometheus
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: OpenTelemetry
- **Health Checks**: `/health` endpoint

---

## Deployment Architecture

### Development
```
Frontend: Vite dev server (localhost:3000)
Backend: Uvicorn (localhost:8080)
```

### Production (Recommended)
```
┌─────────────┐
│   Nginx     │  (Reverse Proxy + Static Files)
│  Port 80    │
└──────┬──────┘
       │
       ├─→ /api/*  ──→  Backend (Uvicorn + Gunicorn)
       │                 Port 8080
       │
       └─→ /*  ──────→  Frontend (Static Build)
                         Served by Nginx
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.

---

## Technology Decisions & Rationale

| Technology | Decision | Rationale |
|------------|----------|-----------|
| **FastAPI** | Async Python framework | Modern, fast, automatic API docs, type safety |
| **React** | UI framework | Component reusability, large ecosystem, TypeScript support |
| **pikepdf** | PDF library | Open source, fast (QPDF-based), comprehensive features |
| **PyMuPDF** | Text extraction | Fast, accurate text extraction, good documentation |
| **Tesseract** | OCR engine | Industry-standard, open source, multi-language support |
| **Material-UI** | Component library | Professional components, customizable theming, accessibility |
| **TypeScript** | Frontend language | Type safety, better IDE support, fewer runtime errors |
| **Pydantic** | Data validation | Automatic validation, OpenAPI generation, type hints |
| **CSS Modules** | Styling approach | Scoped styles, no naming conflicts, component co-location |

---

## Future Architecture Enhancements

1. **Microservices Architecture**
   - Separate services for each operation
   - API Gateway pattern
   - Independent scaling

2. **Event-Driven Architecture**
   - Message queue for long-running operations
   - WebSocket for real-time progress updates
   - Background job processing

3. **Multi-Tenant Support**
   - User authentication (JWT)
   - User-specific storage
   - Usage quotas and rate limiting

4. **Distributed Processing**
   - Horizontal scaling of backend
   - Load balancing across instances
   - Shared state via Redis

---

**Last Updated**: November 2024
**Version**: 1.0
