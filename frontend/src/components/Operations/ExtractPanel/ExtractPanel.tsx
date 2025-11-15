import { useState } from 'react'
import {
  Box, Button, Typography, TextField, Chip,
  FormControlLabel, Checkbox, Paper
} from '@mui/material'
import {
  Upload as UploadIcon,
  TextFields as TextIcon,
  Download as DownloadIcon
} from '@mui/icons-material'
import { usePDFOperation } from '../../../hooks/usePDFOperation'
import { useFileDropzone } from '../../../hooks/useFileDropzone'
import { StatusAlerts } from '../../shared/StatusAlerts'
import { apiService } from '../../../services/api'
import styles from './ExtractPanel.module.css'

export const ExtractPanel = () => {
  const [file, setFile] = useState<File | null>(null)
  const [outputName, setOutputName] = useState('extracted_text')
  const [includePageNumbers, setIncludePageNumbers] = useState(true)
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
      setError('Please select a PDF file to extract text from')
      return
    }

    await executeOperation(async () => {
      const response = await apiService.extractTextFromPdf({
        file,
        outputFileName: outputName,
        includePageNumbers
      })

      setSuccess(response.message)

      // Download the text file
      const blob = await apiService.downloadFile(response.data.fileName)
      apiService.triggerDownload(blob, response.data.fileName)

      // Reset
      setFile(null)
      setOutputName('extracted_text')
    })
  }

  return (
    <Box className={styles.container}>
      {/* File Upload Area */}
      <Paper
        className={`${styles.uploadArea} ${dragActive ? styles.dragActive : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {!file ? (
          <>
            <UploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Drop PDF here or click to select
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Select a PDF file to extract text
            </Typography>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              id="extract-upload"
            />
            <label htmlFor="extract-upload">
              <Button variant="outlined" component="span">
                Select PDF File
              </Button>
            </label>
          </>
        ) : (
          <Box>
            <Typography variant="h6" gutterBottom>
              Selected File
            </Typography>
            <Chip
              label={`${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`}
              onDelete={() => setFile(null)}
              color="primary"
              sx={{ maxWidth: '100%' }}
            />
          </Box>
        )}
      </Paper>

      {file && (
        <>
          {/* Options */}
          <Box sx={{ mt: 3 }}>
            <TextField
              fullWidth
              label="Output File Name"
              value={outputName}
              onChange={(e) => setOutputName(e.target.value)}
              helperText="The text file will be saved as: filename.txt"
              sx={{ mb: 2 }}
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={includePageNumbers}
                  onChange={(e) => setIncludePageNumbers(e.target.checked)}
                  color="primary"
                />
              }
              label="Include page numbers in extracted text"
            />
          </Box>

          {/* Extract Button */}
          <Button
            variant="contained"
            size="large"
            startIcon={loading ? <TextIcon /> : <DownloadIcon />}
            onClick={handleExtract}
            disabled={loading}
            fullWidth
            sx={{ mt: 3 }}
          >
            {loading ? 'Extracting Text...' : 'Extract Text to TXT'}
          </Button>
        </>
      )}

      {/* Messages */}
      <StatusAlerts
        error={error}
        success={success}
        onClearError={() => setError(null)}
        onClearSuccess={() => setSuccess(null)}
      />
    </Box>
  )
}
