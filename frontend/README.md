# PDF Editor Frontend

Modern React application for PDF editing operations with a light blue theme inspired by pdftools.com.

## Features

- **View & Annotate**: View PDFs and add annotations using PDF Tools Viewer SDK
- **Merge PDFs**: Combine multiple PDF files
- **Split PDF**: Divide PDFs by pages or ranges
- **Compress PDF**: Reduce file size with optimization
- **Convert to Image**: Export PDF pages as PNG/JPEG/TIFF

## Technology Stack

- **React 18** with **TypeScript**
- **Vite** for fast development and building
- **Material-UI (MUI)** for UI components
- **PDF Tools Four Heights Viewer** for PDF viewing/annotation
- **Axios** for API communication
- **CSS Modules** for component-scoped styles

## Project Structure

```
frontend/
├── public/                   # Static assets
├── src/
│   ├── components/          # React components
│   │   ├── PDFViewer/      # PDF viewer with annotation
│   │   ├── Operations/     # Merge, Split, Compress, Convert
│   │   ├── Layout/         # Header, Sidebar components
│   │   └── common/         # Reusable components (Button, Modal, etc.)
│   ├── services/           # API service layer
│   │   └── api.ts          # Backend API calls
│   ├── hooks/              # Custom React hooks
│   ├── theme/              # MUI theme configuration
│   │   └── theme.ts        # Light blue theme
│   ├── types/              # TypeScript definitions
│   │   └── index.ts        # Shared types
│   ├── utils/              # Helper functions
│   ├── styles/             # Global CSS
│   │   ├── variables.css   # CSS custom properties
│   │   ├── globals.css     # Global styles & resets
│   │   ├── typography.css  # Font and text styles
│   │   └── utilities.css   # Utility classes
│   ├── App.tsx             # Main application
│   ├── App.module.css      # App component local styles
│   └── main.tsx            # Entry point
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## CSS Architecture

### Global CSS (Scalability)

Located in `src/styles/`:

- **variables.css**: CSS custom properties for theme (colors, spacing, typography)
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

### 2. Configure PDF Tools Viewer SDK License

Edit `src/main.tsx` or create a viewer configuration file:

```typescript
const viewerConfig = {
  licenseKey: '<4H,V6,VIEWWEB,CUA6C7MBS6L2SJXS87K50CVQC21SL2SJ40APNVS>',
  // other viewer options
}
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

## Implementing the Components

### 1. PDF Viewer Component (with Four Heights SDK)

Create `src/components/PDFViewer/PDFViewer.tsx`:

```tsx
import { useEffect, useRef } from 'react'
import { Box } from '@mui/material'
import styles from './PDFViewer.module.css'

export const PDFViewer = ({ file }: { file: File }) => {
  const viewerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Initialize PDF Tools Viewer SDK
    // Documentation: https://docs.pdf-tools.com/viewer/
    // Configure with license key and viewer options
  }, [file])

  return (
    <Box className={styles.viewerContainer}>
      <div ref={viewerRef} className={styles.viewer} />
    </Box>
  )
}
```

### 2. Merge Component

Create `src/components/Operations/MergePanel/MergePanel.tsx`:

```tsx
import { useState } from 'react'
import { Button, Box, List, ListItem } from '@mui/material'
import { apiService } from '@/services/api'
import styles from './MergePanel.module.css'

export const MergePanel = () => {
  const [files, setFiles] = useState<File[]>([])
  const [loading, setLoading] = useState(false)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files))
    }
  }

  const handleMerge = async () => {
    setLoading(true)
    try {
      const response = await apiService.mergePdfs({
        files,
        outputFileName: 'merged.pdf'
      })
      // Handle success, download file
      const blob = await apiService.downloadFile(response.data.fileName)
      apiService.triggerDownload(blob, response.data.fileName)
    } catch (error) {
      console.error('Merge failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box className={styles.container}>
      <input
        type="file"
        multiple
        accept=".pdf"
        onChange={handleFileSelect}
      />
      <List>
        {files.map((file, index) => (
          <ListItem key={index}>{file.name}</ListItem>
        ))}
      </List>
      <Button
        variant="contained"
        onClick={handleMerge}
        disabled={files.length < 2 || loading}
      >
        {loading ? 'Merging...' : 'Merge PDFs'}
      </Button>
    </Box>
  )
}
```

### 3. Split, Compress, Convert Components

Follow the same pattern as MergePanel, using the respective API methods:
- `apiService.splitPdf()`
- `apiService.compressPdf()`
- `apiService.convertPdfToImage()`

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
- Reference CSS variables for consistency
- Keep styles scoped to the component

## License Keys

- **Viewer SDK**: `<4H,V6,VIEWWEB,CUA6C7MBS6L2SJXS87K50CVQC21SL2SJ40APNVS>`
- Configure in the PDF viewer initialization

## Next Steps

1. Install dependencies: `npm install`
2. Implement PDF Viewer with Four Heights SDK
3. Complete operation components (Merge, Split, Compress, Convert)
4. Add error handling and loading states
5. Implement file upload UI with drag-and-drop
6. Add progress indicators for long operations
7. Test with various PDF files
8. Build for production

## Resources

- [PDF Tools Viewer Documentation](https://docs.pdf-tools.com/viewer/)
- [Material-UI Documentation](https://mui.com/)
- [Vite Documentation](https://vitejs.dev/)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)

## Author

PDF Editor Team - Built with modern best practices and clean code principles.
