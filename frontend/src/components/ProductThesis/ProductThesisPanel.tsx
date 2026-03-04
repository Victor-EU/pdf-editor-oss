import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material'
import styles from './ProductThesisPanel.module.css'

const modules = [
  { name: 'pikepdf (QPDF)', purpose: 'PDF merge, split, compress', feature: 'Merge / Split / Compress', license: 'MPL-2.0' },
  { name: 'PyMuPDF (MuPDF/fitz)', purpose: 'Text extraction from PDF pages', feature: 'Extract Text', license: 'AGPL-3.0' },
  { name: 'pdf2image + Poppler', purpose: 'Render PDF pages to raster images', feature: 'Convert to Image', license: 'MIT + GPL' },
  { name: 'pytesseract + Tesseract', purpose: 'Optical character recognition on scanned pages', feature: 'OCR Text', license: 'Apache 2.0' },
  { name: 'camelot-py', purpose: 'Detect and extract tables from PDFs', feature: 'Extract Tables', license: 'MIT' },
  { name: 'openpyxl', purpose: 'Write extracted tables to Excel files', feature: 'Extract Tables', license: 'MIT' },
  { name: 'react-pdf + PDF.js', purpose: 'Render PDFs in the browser', feature: 'View PDF', license: 'Apache 2.0' },
  { name: 'pdf-lib', purpose: 'Client-side PDF manipulation', feature: 'View PDF', license: 'MIT' },
  { name: 'FastAPI', purpose: 'Python backend framework', feature: 'All operations', license: 'MIT' },
  { name: 'React + MUI', purpose: 'Frontend UI framework', feature: 'All operations', license: 'MIT' },
]

const licenseColor = (license: string): 'default' | 'success' | 'warning' | 'info' => {
  if (license.includes('AGPL')) return 'warning'
  if (license.includes('GPL')) return 'info'
  if (license.includes('MPL')) return 'info'
  return 'success'
}

export function ProductThesisPanel() {
  return (
    <div className={styles.container}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom fontWeight="bold">
          Why This Exists
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2, maxWidth: 680 }}>
          Built with every open-source PDF module we could find, to see what's
          actually possible in browser-based PDF editing — without paying for
          proprietary SDKs.
        </Typography>
      </Box>

      <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          The Problem
        </Typography>
        <Typography variant="body2" color="text.secondary">
          PDF is a notoriously difficult format. It's a binary container with no
          standard editing API — text isn't stored as paragraphs, layout isn't
          CSS, and even "simple" operations like merging two files require
          understanding cross-reference tables and object streams. Most PDF tools
          are proprietary, expensive, or both.
        </Typography>
      </Paper>

      <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          The Approach
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Instead of building one monolithic library, we assembled the best
          open-source tool for each operation: one library for merging, another
          for OCR, another for table extraction, and so on. Each module is
          battle-tested in its own domain. Together they cover the full spectrum
          of what you'd need from a PDF editor.
        </Typography>
      </Paper>

      <Paper elevation={1} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Open-Source Modules Used
        </Typography>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell><strong>Module</strong></TableCell>
                <TableCell><strong>What It Does</strong></TableCell>
                <TableCell><strong>Feature</strong></TableCell>
                <TableCell><strong>License</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {modules.map((m) => (
                <TableRow key={m.name}>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {m.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {m.purpose}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">{m.feature}</Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={m.license}
                      size="small"
                      color={licenseColor(m.license)}
                      variant="outlined"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </div>
  )
}
