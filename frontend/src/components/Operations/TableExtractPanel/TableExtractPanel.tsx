import { useState } from 'react'
import {
  Box, Button, Typography, TextField, Chip,
  FormControlLabel, Checkbox, Paper
} from '@mui/material'
import {
  Upload as UploadIcon,
  TableChart as TableIcon,
  Download as DownloadIcon,
  Description as PdfIcon
} from '@mui/icons-material'
import { usePDFOperation } from '../../../hooks/usePDFOperation'
import { useFileDropzone } from '../../../hooks/useFileDropzone'
import { StatusAlerts } from '../../shared/StatusAlerts'
import { apiService } from '../../../services/api'
import styles from './TableExtractPanel.module.css'

export const TableExtractPanel = () => {
  const [file, setFile] = useState<File | null>(null)
  const [outputName, setOutputName] = useState('tables')
  const [includeHeaders, setIncludeHeaders] = useState(true)
  const { loading, error, success, setError, setSuccess, executeOperation } = usePDFOperation()
  const { dragActive, handleDrag, handleDrop } = useFileDropzone({
    onFileDrop: (droppedFile) => {
      setFile(droppedFile)
      setError(null)
    }
  })

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0])
      setError(null)
    }
  }

  const handleExtract = async () => {
    if (!file) {
      setError('Please select a PDF file to extract tables from')
      return
    }

    await executeOperation(async () => {
      const response = await apiService.extractTablesFromPdf({
        file,
        outputFileName: outputName,
        includeHeaders
      })

      setSuccess(response.message)

      // Download the Excel file
      const blob = await apiService.downloadFile(response.data.fileName)
      apiService.triggerDownload(blob, response.data.fileName)

      // Reset
      setFile(null)
      setOutputName('tables')
    })
  }

  return (
    <Box>
      {/* File Upload */}
      <Paper
        className={`${styles.uploadBox} ${dragActive ? styles.uploadBoxActive : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => document.getElementById('table-extract-file-input')?.click()}
      >
        <input
          id="table-extract-file-input"
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          className={styles.fileInput}
        />
        <TableIcon className={styles.uploadIcon} />
        <Typography variant="h6" gutterBottom>
          Drop PDF file here or click to browse
        </Typography>
        <Typography variant="body2" color="text.secondary">
          PDF files with tables
        </Typography>
      </Paper>

      {/* Selected File Info */}
      {file && (
        <Box className={styles.fileInfo}>
          <PdfIcon className={styles.fileIcon} />
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle1" fontWeight="bold">
              {file.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </Typography>
          </Box>
          <Chip label="Ready" color="success" size="small" />
        </Box>
      )}

      {/* Extraction Settings */}
      <Box className={styles.settingsGrid}>
        {/* Output Name */}
        <Box className={styles.settingItem}>
          <Typography variant="subtitle2" fontWeight="bold">
            Output File Name
          </Typography>
          <TextField
            value={outputName}
            onChange={(e) => setOutputName(e.target.value)}
            placeholder="tables"
            size="small"
            fullWidth
            helperText="Excel file name (without extension)"
          />
        </Box>

        {/* Include Headers */}
        <Box className={styles.settingItem}>
          <Typography variant="subtitle2" fontWeight="bold">
            Table Headers
          </Typography>
          <FormControlLabel
            control={
              <Checkbox
                checked={includeHeaders}
                onChange={(e) => setIncludeHeaders(e.target.checked)}
                color="success"
              />
            }
            label={
              <Typography variant="body2">
                Use first row as headers
              </Typography>
            }
          />
        </Box>
      </Box>

      {/* Extract Button */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
        <Button
          variant="contained"
          size="large"
          onClick={handleExtract}
          disabled={!file || loading}
          className={styles.extractButton}
          startIcon={loading ? null : <DownloadIcon />}
        >
          {loading ? 'Extracting Tables...' : 'Extract Tables'}
        </Button>
      </Box>

      {/* Status Messages */}
      <StatusAlerts
        error={error}
        success={success}
        onClearError={() => setError(null)}
        onClearSuccess={() => setSuccess(null)}
      />

      {/* Info Box */}
      <Paper sx={{ p: 2, bgcolor: '#f1f8f4', border: '1px solid #81c784' }}>
        <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
          Automatic Table Detection:
        </Typography>
        <ul style={{ margin: 0, paddingLeft: 20 }}>
          <li>
            <Typography variant="body2">
              Automatically detects both <strong>bordered</strong> and <strong>non-bordered</strong> tables
            </Typography>
          </li>
          <li>
            <Typography variant="body2">
              Uses intelligent detection to find all tables in your PDF
            </Typography>
          </li>
          <li>
            <Typography variant="body2">
              All tables are exported to a <strong>single sheet</strong> with 3 empty rows between each table
            </Typography>
          </li>
          <li>
            <Typography variant="body2">
              Each table includes metadata (page number, method, accuracy) for easy reference
            </Typography>
          </li>
          <li>
            <Typography variant="body2">
              Headers will be bold and styled if "Use first row as headers" is enabled
            </Typography>
          </li>
        </ul>
      </Paper>
    </Box>
  )
}
