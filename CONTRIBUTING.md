# Contributing to PDF Editor

Thank you for your interest in contributing to PDF Editor! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

### Expected Behavior

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discriminatory language, or personal attacks
- Publishing others' private information
- Trolling or insulting/derogatory comments
- Other conduct which could reasonably be considered inappropriate

---

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.9+
- Node.js 16+
- Git
- poppler-utils
- Tesseract OCR

See the main [README.md](README.md) for installation instructions.

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pdf-editor.git
   cd pdf-editor
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/Victor-EU/pdf-editor.git
   ```

### Set Up Development Environment

#### Backend

```bash
cd backend-python

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p uploads output

# Run tests (when available)
# pytest
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Run linter
npm run lint
```

---

## Development Workflow

### 1. Create a Branch

Create a new branch for your feature or bug fix:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

**Branch naming conventions**:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Adding or updating tests
- `chore/` - Maintenance tasks

### 2. Make Changes

- Write clean, readable code
- Follow the code style guidelines (see below)
- Add comments for complex logic
- Update documentation as needed

### 3. Test Your Changes

```bash
# Backend
cd backend-python
pytest  # When tests are available

# Frontend
cd frontend
npm run lint
npm run build  # Ensure it builds successfully
```

### 4. Commit Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: Add batch PDF processing support

- Implement batch processing service
- Add API endpoint for batch operations
- Update frontend to support multiple file selection

Fixes #123"
```

**Commit message format**:
```
<type>: <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 5. Push Changes

```bash
git push origin feature/your-feature-name
```

### 6. Create Pull Request

1. Go to GitHub and create a Pull Request
2. Fill out the PR template with:
   - Description of changes
   - Related issue numbers
   - Testing performed
   - Screenshots (if applicable)

---

## Code Style Guidelines

### Python (Backend)

Follow **PEP 8** style guide:

```python
# Good
def merge_pdfs(
    self,
    input_files: List[Path],
    output_dir: Path,
    output_filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    Merge multiple PDF files into one.

    Args:
        input_files: List of PDF file paths to merge
        output_dir: Directory to save the merged PDF
        output_filename: Optional custom output filename

    Returns:
        Dictionary with merge result information

    Raises:
        PDFProcessingError: If merge operation fails
    """
    logger.info(f"Merging {len(input_files)} PDF files...")

    try:
        pdf = pikepdf.Pdf.new()
        for file_path in input_files:
            src = pikepdf.Pdf.open(file_path)
            pdf.pages.extend(src.pages)

        output_path = output_dir / f"{output_filename}.pdf"
        pdf.save(output_path)

        return {
            "filename": output_path.name,
            "size": output_path.stat().st_size,
            "pages": len(pdf.pages)
        }

    except Exception as e:
        logger.error(f"Failed to merge PDFs: {str(e)}")
        raise PDFProcessingError(f"Merge failed: {str(e)}")
```

**Key points**:
- Use type hints for all function parameters and return values
- Write docstrings for all public functions/classes
- Use f-strings for string formatting
- Keep functions focused and under 50 lines
- Use meaningful variable names
- Handle exceptions appropriately

### TypeScript (Frontend)

Follow **Airbnb TypeScript Style Guide**:

```typescript
// Good
interface FileResponse {
  fileName: string
  fileSize: number
  downloadUrl: string
  pages?: number
}

export const MergePanel: React.FC = () => {
  const [files, setFiles] = useState<File[]>([])
  const [outputName, setOutputName] = useState('merged_document')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleMerge = async (): Promise<void> => {
    if (files.length < 2) {
      setError('Please select at least 2 PDF files')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await apiService.mergePdfs(files, outputName)
      const blob = await apiService.downloadFile(response.data.fileName)
      apiService.triggerDownload(blob, response.data.fileName)

      // Reset state
      setFiles([])
      setOutputName('merged_document')
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to merge PDFs')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box className={styles.container}>
      {/* Component JSX */}
    </Box>
  )
}
```

**Key points**:
- Use TypeScript strict mode
- Define interfaces for all data structures
- Use functional components with hooks
- Keep components under 200 lines
- Use async/await over promises
- Handle all error cases

### CSS

Follow **BEM naming convention** (for non-module CSS):

```css
/* Good */
.upload-area {
  display: flex;
  flex-direction: column;
  padding: var(--spacing-2xl);
  border: 2px dashed var(--color-border-main);
  border-radius: var(--radius-lg);
}

.upload-area--active {
  border-color: var(--color-primary);
  background-color: var(--color-bg-hover);
}

.upload-area__icon {
  font-size: 48px;
  color: var(--color-primary);
}
```

**Key points**:
- Use CSS custom properties (variables)
- Follow existing component patterns
- Use CSS Modules for component styles
- Keep specificity low
- Mobile-first responsive design

---

## Testing

### Backend Testing (Python)

```bash
cd backend-python

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_pdf_merge.py

# Run specific test
pytest tests/test_pdf_merge.py::test_merge_two_pdfs
```

**Writing tests**:

```python
import pytest
from pathlib import Path
from services.pdf_merge import PdfMergeService

@pytest.fixture
def merge_service():
    """Fixture to create merge service instance"""
    from config import Settings
    settings = Settings()
    return PdfMergeService(settings)

def test_merge_two_pdfs(merge_service, tmp_path):
    """Test merging two PDF files"""
    # Arrange
    file1 = Path("tests/fixtures/sample1.pdf")
    file2 = Path("tests/fixtures/sample2.pdf")
    output_dir = tmp_path

    # Act
    result = await merge_service.merge_pdfs(
        [file1, file2],
        output_dir,
        "merged_test"
    )

    # Assert
    assert result["filename"] == "merged_test.pdf"
    assert result["pages"] == 2
    assert (output_dir / "merged_test.pdf").exists()
```

### Frontend Testing (JavaScript/TypeScript)

```bash
cd frontend

# Run tests (when configured)
npm test

# Run with coverage
npm test -- --coverage

# Run linter
npm run lint

# Fix linting issues
npm run lint -- --fix
```

**Writing component tests** (example with Vitest):

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { MergePanel } from './MergePanel'

describe('MergePanel', () => {
  it('should render upload area', () => {
    render(<MergePanel />)
    expect(screen.getByText(/drop pdf files here/i)).toBeInTheDocument()
  })

  it('should show error for single file', async () => {
    render(<MergePanel />)
    const mergeButton = screen.getByRole('button', { name: /merge pdfs/i })

    fireEvent.click(mergeButton)

    expect(await screen.findByText(/at least 2 pdf files/i)).toBeInTheDocument()
  })
})
```

---

## Submitting Changes

### Pull Request Process

1. **Update documentation** if you've changed APIs or added features
2. **Add tests** for new features or bug fixes
3. **Run all tests** and ensure they pass
4. **Update CHANGELOG.md** with your changes (if applicable)
5. **Submit Pull Request** with clear description

### Pull Request Template

```markdown
## Description
Brief description of changes

## Related Issue
Fixes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- List of changes
- Another change

## Testing Performed
- Describe testing done
- Include test results

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review performed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] No new warnings
```

### Code Review Process

1. Maintainer will review your PR
2. Address any feedback or requested changes
3. Once approved, maintainer will merge
4. Your contribution will be credited!

---

## Reporting Bugs

### Before Submitting

1. **Check existing issues** to avoid duplicates
2. **Try latest version** to see if bug is fixed
3. **Collect information**:
   - PDF Editor version
   - Operating system
   - Python/Node.js version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages or logs

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 13.0]
- Python: [e.g., 3.11.0]
- Node.js: [e.g., 18.0.0]
- Browser: [e.g., Chrome 119]

## Screenshots
If applicable

## Additional Context
Any other relevant information
```

---

## Feature Requests

We welcome feature requests! Please provide:

1. **Clear description** of the feature
2. **Use case** - Why is this needed?
3. **Proposed solution** - How should it work?
4. **Alternatives considered** - Other approaches?

### Feature Request Template

```markdown
## Feature Description
Clear description of proposed feature

## Problem to Solve
What problem does this feature solve?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other approaches you've thought about

## Additional Context
Any other relevant information

## Willingness to Contribute
- [ ] I'm willing to implement this feature
- [ ] I can help with testing
- [ ] I can help with documentation
```

---

## Development Tips

### Debugging Backend

```python
# Add logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")

# Use pdb for debugging
import pdb; pdb.set_trace()  # Breakpoint
```

### Debugging Frontend

```typescript
// Console logging
console.log('Variable value:', variable)
console.error('Error occurred:', error)

// React DevTools
// Install React DevTools browser extension
```

### Hot Reload

Both backend and frontend support hot reload during development:

```bash
# Backend auto-reloads on file changes
python main.py

# Frontend auto-reloads on file changes
npm run dev
```

---

## Questions?

If you have questions:

1. Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
2. Check [docs/API.md](docs/API.md) for API documentation
3. Open a [Discussion](https://github.com/Victor-EU/pdf-editor/discussions)
4. Ask in the issue tracker

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Recognition

All contributors will be recognized in the project! Significant contributions will be highlighted in the README.

Thank you for contributing to PDF Editor!
