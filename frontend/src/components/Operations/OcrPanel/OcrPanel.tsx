import { useState } from 'react'
import {
  Box, Button, Typography, TextField, Chip,
  FormControlLabel, Checkbox, Paper, MenuItem, Select,
  FormControl, InputLabel, Slider
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
import styles from './OcrPanel.module.css'

export const OcrPanel = () => {
  const [file, setFile] = useState<File | null>(null)
  const [outputName, setOutputName] = useState('ocr_text')
  const [language, setLanguage] = useState('eng')
  const [dpi, setDpi] = useState(300)
  const [includePageNumbers, setIncludePageNumbers] = useState(true)
  const { loading, error, success, setError, setSuccess, executeOperation } = usePDFOperation()
  const { dragActive, handleDrag, handleDrop } = useFileDropzone({
    onFileDrop: (droppedFile) => {
      setFile(droppedFile)
      setError(null)
    }
  })

  const languages = [
    { code: 'eng', name: 'English' },
    { code: 'spa', name: 'Spanish' },
    { code: 'fra', name: 'French' },
    { code: 'deu', name: 'German' },
    { code: 'ita', name: 'Italian' },
    { code: 'por', name: 'Portuguese' },
    { code: 'rus', name: 'Russian' },
    { code: 'chi_sim', name: 'Chinese (Simplified)' },
    { code: 'chi_tra', name: 'Chinese (Traditional)' },
    { code: 'jpn', name: 'Japanese' },
    { code: 'kor', name: 'Korean' },
  ]

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0])
      setError(null)
    }
  }

  const handleOcr = async () => {
    if (!file) {
      setError('Please select a PDF file to extract text using OCR')
      return
    }

    await executeOperation(async () => {
      const response = await apiService.ocrPdfText({
        file,
        outputFileName: outputName,
        language,
        dpi,
        includePageNumbers
      })

      setSuccess(response.message)

      // Download the text file
      const blob = await apiService.downloadFile(response.data.fileName)
      apiService.triggerDownload(blob, response.data.fileName)

      // Reset
      setFile(null)
      setOutputName('ocr_text')
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
              Select a scanned PDF file for OCR text extraction
            </Typography>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              id="ocr-upload"
            />
            <label htmlFor="ocr-upload">
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

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>OCR Language</InputLabel>
              <Select
                value={language}
                label="OCR Language"
                onChange={(e) => setLanguage(e.target.value)}
              >
                {languages.map((lang) => (
                  <MenuItem key={lang.code} value={lang.code}>
                    {lang.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Typography gutterBottom>
              Image Quality (DPI): {dpi}
            </Typography>
            <Slider
              value={dpi}
              onChange={(_, value) => setDpi(value as number)}
              min={150}
              max={600}
              step={50}
              marks={[
                { value: 150, label: '150' },
                { value: 300, label: '300' },
                { value: 450, label: '450' },
                { value: 600, label: '600' },
              ]}
              valueLabelDisplay="auto"
              sx={{ mb: 2 }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
              Higher DPI = Better quality but slower processing. 300 DPI is recommended.
            </Typography>

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

          {/* OCR Button */}
          <Button
            variant="contained"
            size="large"
            startIcon={loading ? <TextIcon /> : <DownloadIcon />}
            onClick={handleOcr}
            disabled={loading}
            fullWidth
            sx={{ mt: 3 }}
          >
            {loading ? 'Extracting Text with OCR...' : 'Extract Text with OCR'}
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
