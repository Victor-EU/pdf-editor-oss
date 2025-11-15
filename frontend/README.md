# PDF Editor Frontend

Modern React application for PDF editing operations with a clean, professional UI.

## Features

- **Merge PDFs**: Combine multiple PDF files into one
- **Split PDF**: Divide PDFs by pages or ranges
- **Compress PDF**: Reduce file size with optimization
- **Convert to Image**: Export PDF pages as PNG/JPEG/TIFF
- **Extract Text (OCR)**: Extract text from PDFs using Tesseract OCR
- **Extract Tables**: Intelligent table detection and extraction to Excel

## Technology Stack

- **React 18** with **TypeScript**
- **Vite** for fast development and building
- **Material-UI (MUI)** for UI components
- **Axios** for API communication
- **CSS Modules** for component-scoped styles

## Project Structure

```
frontend/
├── public/                   # Static assets
├── src/
│   ├── components/          # React components
│   │   ├── Operations/      # Merge, Split, Compress, Convert, OCR, Table Extract
│   │   ├── shared/          # Shared components (StatusAlerts, etc.)
│   ├── services/            # API service layer
│   │   └── api.ts           # Backend API calls
│   ├── hooks/               # Custom React hooks
│   │   ├── useFileDropzone.ts
│   │   └── usePDFOperation.ts
│   ├── theme/               # MUI theme configuration
│   │   └── theme.ts         # Clean blue theme
│   ├── types/               # TypeScript definitions
│   │   └── index.ts         # Shared types
│   ├── utils/               # Helper functions
│   ├── styles/              # Global CSS
│   │   ├── globals.css      # Global styles & resets
│   │   ├── typography.css   # Font and text styles
│   │   └── utilities.css    # Utility classes
│   ├── App.tsx              # Main application
│   ├── App.module.css       # App component local styles
│   └── main.tsx             # Entry point
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## CSS Architecture

### Global CSS (Scalability)

Located in `src/styles/`:

- **globals.css**: Base styles, resets, and global elements
- **typography.css**: Font imports and text styling
- **utilities.css**: Utility classes for rapid development

### Local CSS (Component Scoping)

Each component has its own `.module.css` file:

```
ComponentName/
├── ComponentName.tsx
└── ComponentName.module.css
```

**Example:**
```css
/* Component.module.css */
.container {
  padding: var(--spacing-lg);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
}

.title {
  color: var(--color-primary);
  font-size: var(--font-size-2xl);
}
```

**Usage in Component:**
```tsx
import styles from './Component.module.css'

export const Component = () => (
  <div className={styles.container}>
    <h2 className={styles.title}>Title</h2>
  </div>
)
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment Variables (Optional)

Create `.env` file:

```bash
# API Base URL (optional - defaults to /api via proxy)
VITE_API_BASE_URL=http://localhost:8080/api
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

## API Integration

All API calls are handled through `src/services/api.ts`:

```typescript
import { apiService } from '@/services/api'

// Merge
const response = await apiService.mergePdfs({ files, outputFileName })

// Split
const response = await apiService.splitPdf({
  file,
  splitMode: 'ranges',
  splitPoints: ['1-3', '4-6']
})

// Compress
const response = await apiService.compressPdf({
  file,
  compressionProfile: 'web'
})

// Convert
const response = await apiService.convertPdfToImage({
  file,
  imageFormat: 'png',
  dpi: 300
})

// OCR
const response = await apiService.extractText({
  file,
  language: 'eng'
})

// Extract Tables
const response = await apiService.extractTables({
  file,
  pages: 'all',
  includeHeaders: true
})
```

## Theme Customization

Edit `src/theme/theme.ts` to customize colors:

```typescript
export const theme = createTheme({
  palette: {
    primary: {
      main: '#4A9BD1',  // Light blue
      light: '#6BB6E8',
      dark: '#3A7FAF',
    },
    // ... other colors
  },
})
```

## Development Guidelines

### Code Style

- Use **TypeScript** for type safety
- Follow **React Hooks** best practices
- Use **functional components**
- Apply **OOP principles** where applicable (services, utilities)
- Add clear **JSDoc comments** to functions

### Component Pattern

```tsx
/**
 * Component description
 *
 * @param props - Component props
 * @returns JSX element
 */
export const MyComponent = ({ prop1, prop2 }: MyComponentProps) => {
  // Component logic
  return <div>...</div>
}
```

### CSS Modules Pattern

- Use kebab-case for CSS class names
- Keep styles scoped to the component
- Use MUI theme tokens when possible

## Next Steps

1. Install dependencies: `npm install`
2. Run development server: `npm run dev`
3. Test all PDF operations
4. Build for production: `npm run build`

## Resources

- [Material-UI Documentation](https://mui.com/)
- [Vite Documentation](https://vitejs.dev/)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)

## Author

PDF Editor Team - Built with modern best practices and clean code principles.
