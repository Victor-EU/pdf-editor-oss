import { useState } from 'react'
import { Box, Typography, Paper, Button, CircularProgress, Alert, IconButton } from '@mui/material'
import { Upload as UploadIcon, Description as PdfIcon, ZoomIn, ZoomOut, NavigateBefore, NavigateNext } from '@mui/icons-material'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/Page/AnnotationLayer.css'
import 'react-pdf/dist/Page/TextLayer.css'
import styles from './PDFViewer.module.css'

// Configure PDF.js worker - using local worker file
pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs'

/**
 * PDF Viewer Component using React-PDF (Open Source)
 * Based on Mozilla's PDF.js library
 */
export const PDFViewer = () => {
  const [file, setFile] = useState<File | null>(null)
  const [numPages, setNumPages] = useState<number>(0)
  const [pageNumber, setPageNumber] = useState<number>(1)
  const [scale, setScale] = useState<number>(1.0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0]
    if (!selectedFile) return

    if (selectedFile.type !== 'application/pdf') {
      setError('Please select a valid PDF file')
      return
    }

    setFile(selectedFile)
    setError(null)
    setPageNumber(1)
  }

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages)
    setIsLoading(false)
  }

  const onDocumentLoadError = (error: Error) => {
    console.error('Error loading PDF:', error)
    setError(`Failed to load PDF: ${error.message}`)
    setIsLoading(false)
  }

  const changePage = (offset: number) => {
    setPageNumber(prevPageNumber => {
      const newPage = prevPageNumber + offset
      return Math.min(Math.max(1, newPage), numPages)
    })
  }

  const previousPage = () => changePage(-1)
  const nextPage = () => changePage(1)
  const zoomIn = () => setScale(prev => Math.min(prev + 0.2, 2.0))
  const zoomOut = () => setScale(prev => Math.max(prev - 0.2, 0.5))

  return (
    <Box className={styles.container}>
      {!file && (
        <Paper className={styles.uploadArea}>
          <UploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Upload PDF to View
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Select a PDF file to view with the open source PDF.js viewer
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2, maxWidth: 500 }}>
              {error}
            </Alert>
          )}

          <input
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
            id="pdf-upload"
            disabled={isLoading}
          />
          <label htmlFor="pdf-upload">
            <Button
              variant="contained"
              component="span"
              disabled={isLoading}
              startIcon={isLoading ? <CircularProgress size={20} /> : <PdfIcon />}
            >
              {isLoading ? 'Loading...' : 'Select PDF File'}
            </Button>
          </label>
        </Paper>
      )}

      {file && (
        <Box sx={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
          {/* PDF Controls */}
          <Paper sx={{ p: 2, mb: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="body2">
                Page {pageNumber} of {numPages || '--'}
              </Typography>
              <Box>
                <IconButton onClick={previousPage} disabled={pageNumber <= 1} size="small">
                  <NavigateBefore />
                </IconButton>
                <IconButton onClick={nextPage} disabled={pageNumber >= numPages} size="small">
                  <NavigateNext />
                </IconButton>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <IconButton onClick={zoomOut} disabled={scale <= 0.5} size="small">
                <ZoomOut />
              </IconButton>
              <Typography variant="body2">{Math.round(scale * 100)}%</Typography>
              <IconButton onClick={zoomIn} disabled={scale >= 2.0} size="small">
                <ZoomIn />
              </IconButton>
            </Box>

            <Button
              variant="outlined"
              size="small"
              onClick={() => {
                setFile(null)
                setError(null)
              }}
            >
              Close
            </Button>
          </Paper>

          {/* PDF Document */}
          <Box
            sx={{
              flex: 1,
              overflow: 'auto',
              display: 'flex',
              justifyContent: 'center',
              bgcolor: '#525659',
              p: 2
            }}
          >
            <Document
              file={file}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={onDocumentLoadError}
              loading={
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <CircularProgress />
                  <Typography sx={{ mt: 2, color: 'white' }}>Loading PDF...</Typography>
                </Box>
              }
            >
              <Page
                pageNumber={pageNumber}
                scale={scale}
                renderTextLayer={true}
                renderAnnotationLayer={true}
              />
            </Document>
          </Box>
        </Box>
      )}
    </Box>
  )
}
