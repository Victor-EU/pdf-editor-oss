import { useState } from 'react'
import { Box, Container, Paper, Tabs, Tab, Typography } from '@mui/material'
import { Description as PdfIcon } from '@mui/icons-material'
import { PDFViewer } from './components/PDFViewer/PDFViewer'
import { MergePanel } from './components/Operations/MergePanel/MergePanel'
import { SplitPanel } from './components/Operations/SplitPanel/SplitPanel'
import { CompressPanel } from './components/Operations/CompressPanel/CompressPanel'
import { ConvertPanel } from './components/Operations/ConvertPanel/ConvertPanel'
import { ExtractPanel } from './components/Operations/ExtractPanel/ExtractPanel'
import { OcrPanel } from './components/Operations/OcrPanel/OcrPanel'

function App() {
  const [selectedTab, setSelectedTab] = useState(0)

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue)
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* Header */}
      <Box
        component="header"
        sx={{
          bgcolor: 'primary.main',
          color: 'white',
          py: 3,
          boxShadow: 2,
        }}
      >
        <Container maxWidth="xl">
          <Box display="flex" alignItems="center" gap={2}>
            <PdfIcon sx={{ fontSize: 40 }} />
            <Box>
              <Typography variant="h4" fontWeight="bold">
                PDF editor - free with Open Source
              </Typography>
              <Typography variant="body2" sx={{ color: 'white' }}>
                View, Edit, Merge, Split, Compress, Convert, Extract & OCR Text from PDFs
              </Typography>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* Main Content */}
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Tabs */}
        <Paper elevation={2} sx={{ mb: 3 }}>
          <Tabs
            value={selectedTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab label="View PDF" />
            <Tab label="Merge PDFs" />
            <Tab label="Split PDF" />
            <Tab label="Compress PDF" />
            <Tab label="Convert to Image" />
            <Tab label="Extract Text" />
            <Tab label="OCR Text" />
          </Tabs>
        </Paper>

        {/* Tab Content */}
        <Paper elevation={2} sx={{ p: 4, minHeight: '60vh' }}>
          {selectedTab === 0 && (
            <Box>
              <Typography variant="h5" gutterBottom>
                View PDF
              </Typography>
              <Typography color="text.secondary" sx={{ mb: 3 }}>
                Upload and view PDF documents with page navigation and zoom controls
              </Typography>
              <PDFViewer />
            </Box>
          )}

          {selectedTab === 1 && (
            <Box>
              <Typography variant="h5" gutterBottom>
                Merge Multiple PDFs
              </Typography>
              <Typography color="text.secondary" sx={{ mb: 3 }}>
                Combine multiple PDF files into a single document
              </Typography>
              <MergePanel />
            </Box>
          )}

          {selectedTab === 2 && (
            <Box>
              <Typography variant="h5" gutterBottom>
                Split PDF File
              </Typography>
              <Typography color="text.secondary" sx={{ mb: 3 }}>
                Divide a PDF into multiple files by pages or ranges
              </Typography>
              <SplitPanel />
            </Box>
          )}

          {selectedTab === 3 && (
            <Box>
              <Typography variant="h5" gutterBottom>
                Compress PDF File
              </Typography>
              <Typography color="text.secondary" sx={{ mb: 3 }}>
                Reduce PDF file size with optimized compression
              </Typography>
              <CompressPanel />
            </Box>
          )}

          {selectedTab === 4 && (
            <Box>
              <Typography variant="h5" gutterBottom>
                Convert PDF to Image
              </Typography>
              <Typography color="text.secondary" sx={{ mb: 3 }}>
                Convert PDF pages to PNG, JPEG, or TIFF images
              </Typography>
              <ConvertPanel />
            </Box>
          )}

          {selectedTab === 5 && (
            <Box>
              <Typography variant="h5" gutterBottom>
                Extract Text from PDF
              </Typography>
              <Typography color="text.secondary" sx={{ mb: 3 }}>
                Extract all text content from PDF and save as TXT file
              </Typography>
              <ExtractPanel />
            </Box>
          )}

          {selectedTab === 6 && (
            <Box>
              <Typography variant="h5" gutterBottom>
                OCR Text Extraction
              </Typography>
              <Typography color="text.secondary" sx={{ mb: 3 }}>
                Extract text from scanned PDFs using Optical Character Recognition
              </Typography>
              <OcrPanel />
            </Box>
          )}
        </Paper>

        {/* Footer */}
        <Box sx={{ mt: 4, textAlign: 'center', color: 'text.secondary' }}>
          <Typography variant="body2">
            Built with Open Source Solutions
          </Typography>
        </Box>
      </Container>
    </Box>
  )
}

export default App
