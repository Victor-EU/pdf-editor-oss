import { useState, useRef, useEffect } from 'react'
import { Box, Typography, Paper, Button, CircularProgress, Alert, IconButton, Divider } from '@mui/material'
import {
  Upload as UploadIcon,
  Description as PdfIcon,
  ZoomIn,
  ZoomOut,
  ViewSidebar,
  Close as CloseIcon,
  Fullscreen,
  FullscreenExit
} from '@mui/icons-material'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/Page/AnnotationLayer.css'
import 'react-pdf/dist/Page/TextLayer.css'
import styles from './PDFViewer.module.css'

// Configure PDF.js worker - using local worker file
pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs'

/**
 * PDF Viewer Component using React-PDF (Open Source)
 * Continuous scroll style with thumbnail sidebar
 * Based on Mozilla's PDF.js library
 */
export const PDFViewer = () => {
  const [file, setFile] = useState<File | null>(null)
  const [numPages, setNumPages] = useState<number>(0)
  const [currentPage, setCurrentPage] = useState<number>(1)
  const [scale, setScale] = useState<number>(1.0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showThumbnails, setShowThumbnails] = useState(true)
  const [isFullscreen, setIsFullscreen] = useState(false)

  const pageRefs = useRef<{ [key: number]: HTMLDivElement | null }>({})
  const scrollContainerRef = useRef<HTMLDivElement | null>(null)
  const thumbnailRefs = useRef<{ [key: number]: HTMLDivElement | null }>({})
  const thumbnailContainerRef = useRef<HTMLDivElement | null>(null)
  const viewerContainerRef = useRef<HTMLDivElement | null>(null)

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0]
    if (!selectedFile) return

    if (selectedFile.type !== 'application/pdf') {
      setError('Please select a valid PDF file')
      return
    }

    setFile(selectedFile)
    setError(null)
    setCurrentPage(1)
    setShowThumbnails(true) // Always show thumbnails when uploading new file
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

  const zoomIn = () => setScale(prev => Math.min(prev + 0.2, 3.0))
  const zoomOut = () => setScale(prev => Math.max(prev - 0.2, 0.5))

  const toggleFullscreen = async () => {
    if (!viewerContainerRef.current) return

    try {
      if (!isFullscreen) {
        // Enter fullscreen
        await viewerContainerRef.current.requestFullscreen()
        setIsFullscreen(true)
      } else {
        // Exit fullscreen
        await document.exitFullscreen()
        setIsFullscreen(false)
      }
    } catch (error) {
      console.error('Fullscreen error:', error)
    }
  }

  // Listen for fullscreen changes (e.g., when user presses ESC)
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement)
    }

    document.addEventListener('fullscreenchange', handleFullscreenChange)
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange)
  }, [])

  // Scroll to specific page
  const scrollToPage = (pageNum: number) => {
    const pageElement = pageRefs.current[pageNum]

    if (pageElement) {
      // Use scrollIntoView which works better for elements in scrollable containers
      pageElement.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
        inline: 'nearest'
      })
    }
  }

  // Track which page is currently visible
  useEffect(() => {
    if (!scrollContainerRef.current || numPages === 0) return

    const handleScroll = () => {
      const container = scrollContainerRef.current
      if (!container) return

      // Find which page is most visible
      let maxVisiblePage = 1
      let maxVisibleArea = 0

      Object.keys(pageRefs.current).forEach(pageNumStr => {
        const pageNum = parseInt(pageNumStr)
        const pageElement = pageRefs.current[pageNum]
        if (!pageElement) return

        const rect = pageElement.getBoundingClientRect()
        const containerRect = container.getBoundingClientRect()

        // Calculate visible area
        const visibleTop = Math.max(rect.top, containerRect.top)
        const visibleBottom = Math.min(rect.bottom, containerRect.bottom)
        const visibleHeight = Math.max(0, visibleBottom - visibleTop)
        const visibleArea = visibleHeight * rect.width

        if (visibleArea > maxVisibleArea) {
          maxVisibleArea = visibleArea
          maxVisiblePage = pageNum
        }
      })

      setCurrentPage(maxVisiblePage)
    }

    const container = scrollContainerRef.current
    container.addEventListener('scroll', handleScroll)

    // Call handleScroll initially to set the correct page
    // Use setTimeout to ensure pages are rendered first
    const timeoutId = setTimeout(handleScroll, 100)

    return () => {
      container.removeEventListener('scroll', handleScroll)
      clearTimeout(timeoutId)
    }
  }, [numPages])

  // Auto-scroll thumbnail sidebar to keep current page thumbnail visible
  useEffect(() => {
    const thumbnailElement = thumbnailRefs.current[currentPage]
    const thumbnailContainer = thumbnailContainerRef.current

    if (thumbnailElement && thumbnailContainer && showThumbnails) {
      // Scroll the thumbnail into view within the sidebar
      thumbnailElement.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest'
      })
    }
  }, [currentPage, showThumbnails])

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
        <Box ref={viewerContainerRef} sx={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          {/* PDF Controls */}
          <Paper sx={{ p: 2, mb: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <IconButton
                onClick={() => setShowThumbnails(!showThumbnails)}
                size="small"
                color={showThumbnails ? 'primary' : 'default'}
              >
                <ViewSidebar />
              </IconButton>
              <Typography variant="body2">
                Page {currentPage} of {numPages || '--'}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <IconButton onClick={zoomOut} disabled={scale <= 0.5} size="small">
                <ZoomOut />
              </IconButton>
              <Typography variant="body2">{Math.round(scale * 100)}%</Typography>
              <IconButton onClick={zoomIn} disabled={scale >= 3.0} size="small">
                <ZoomIn />
              </IconButton>
              <IconButton onClick={toggleFullscreen} size="small" title={isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'}>
                {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
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

          {/* Main Content Area */}
          <Box sx={{ flex: 1, display: 'flex', minHeight: 0 }}>
            {/* Thumbnail Sidebar - Always visible on left */}
            {showThumbnails && (
              <Box
                ref={thumbnailContainerRef}
                sx={{
                  width: 200,
                  bgcolor: '#2b2b2b',
                  overflowY: 'auto',
                  overflowX: 'hidden',
                  p: 2,
                  borderRight: '1px solid rgba(255, 255, 255, 0.12)',
                  flexShrink: 0
                }}
              >
                <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="subtitle2" sx={{ color: 'white' }}>
                    Thumbnails
                  </Typography>
                  <IconButton size="small" onClick={() => setShowThumbnails(false)} sx={{ color: 'white' }}>
                    <CloseIcon fontSize="small" />
                  </IconButton>
                </Box>
                <Divider sx={{ bgcolor: 'rgba(255, 255, 255, 0.12)', mb: 2 }} />
                {Array.from(new Array(numPages), (_el, index) => (
                  <Box
                    key={`thumb_${index + 1}`}
                    ref={(ref) => {
                      if (ref) thumbnailRefs.current[index + 1] = ref as HTMLDivElement
                    }}
                    onClick={() => scrollToPage(index + 1)}
                    sx={{
                      mb: 2,
                      cursor: 'pointer',
                      border: currentPage === index + 1 ? '2px solid #1976d2' : '2px solid transparent',
                      borderRadius: 1,
                      overflow: 'hidden',
                      bgcolor: 'white',
                      '&:hover': {
                        borderColor: '#1976d2'
                      }
                    }}
                  >
                    <Document file={file}>
                      <Page
                        pageNumber={index + 1}
                        width={160}
                        renderTextLayer={false}
                        renderAnnotationLayer={false}
                      />
                    </Document>
                    <Typography
                      variant="caption"
                      sx={{
                        display: 'block',
                        textAlign: 'center',
                        py: 0.5,
                        bgcolor: currentPage === index + 1 ? '#1976d2' : '#424242',
                        color: 'white'
                      }}
                    >
                      {index + 1}
                    </Typography>
                  </Box>
                ))}
              </Box>
            )}

            {/* PDF Document - Continuous Scroll */}
            <Box
              ref={scrollContainerRef}
              sx={{
                flex: 1,
                overflowY: 'auto',
                overflowX: 'auto',
                display: 'flex',
                justifyContent: 'center',
                bgcolor: '#525659',
                p: 2,
                minHeight: 0
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
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {Array.from(new Array(numPages), (_el, index) => (
                    <Box
                      key={`page_${index + 1}`}
                      ref={(ref) => {
                        if (ref) pageRefs.current[index + 1] = ref as HTMLDivElement
                      }}
                      sx={{
                        bgcolor: 'white',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
                      }}
                    >
                      <Page
                        pageNumber={index + 1}
                        scale={scale}
                        renderTextLayer={true}
                        renderAnnotationLayer={true}
                      />
                    </Box>
                  ))}
                </Box>
              </Document>
            </Box>
          </Box>
        </Box>
      )}
    </Box>
  )
}
