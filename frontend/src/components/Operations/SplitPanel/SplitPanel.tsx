import { useState } from 'react'
import {
  Box, Button, Typography, TextField, RadioGroup,
  FormControlLabel, Radio, Chip, IconButton, Paper
} from '@mui/material'
import {
  Upload as UploadIcon,
  Delete as DeleteIcon,
  CallSplit as SplitIcon,
  Add as AddIcon
} from '@mui/icons-material'
import { apiService } from '../../../services/api'
import { usePDFOperation } from '../../../hooks/usePDFOperation'
import { useFileDropzone } from '../../../hooks/useFileDropzone'
import { StatusAlerts } from '../../shared/StatusAlerts'
import styles from './SplitPanel.module.css'

export const SplitPanel = () => {
  const [file, setFile] = useState<File | null>(null)
  const [splitMode, setSplitMode] = useState<'pages' | 'ranges'>('ranges')
  const [splitPoints, setSplitPoints] = useState<string[]>(['1-3'])
  const [outputNameBase, setOutputNameBase] = useState('split')

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

  const handleAddSplitPoint = () => {
    setSplitPoints([...splitPoints, splitMode === 'ranges' ? '4-6' : '5'])
  }

  const handleRemoveSplitPoint = (index: number) => {
    setSplitPoints(splitPoints.filter((_, i) => i !== index))
  }

  const handleSplitPointChange = (index: number, value: string) => {
    const newPoints = [...splitPoints]
    newPoints[index] = value
    setSplitPoints(newPoints)
  }

  const handleSplit = async () => {
    if (!file) {
      setError('Please select a PDF file to split')
      return
    }

    if (splitPoints.length === 0) {
      setError('Please add at least one split point')
      return
    }

    await executeOperation(async () => {
      const response = await apiService.splitPdf({
        file,
        splitMode,
        splitPoints,
        outputFileNameBase: outputNameBase
      })

      setSuccess(`PDF split successfully into ${response.data.length} files`)

      // Download all files
      for (const fileInfo of response.data) {
        const blob = await apiService.downloadFile(fileInfo.fileName)
        apiService.triggerDownload(blob, fileInfo.fileName)
        // Small delay between downloads
        await new Promise(resolve => setTimeout(resolve, 200))
      }

      // Reset
      setFile(null)
      setSplitPoints(['1-3'])
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
              Select a PDF file to split
            </Typography>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              id="split-upload"
            />
            <label htmlFor="split-upload">
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
          {/* Split Mode Selection */}
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              Split Mode
            </Typography>
            <RadioGroup
              value={splitMode}
              onChange={(e) => {
                setSplitMode(e.target.value as 'pages' | 'ranges')
                setSplitPoints(e.target.value === 'ranges' ? ['1-3'] : ['3'])
              }}
            >
              <FormControlLabel
                value="ranges"
                control={<Radio />}
                label="By Page Ranges (e.g., 1-5, 6-10)"
              />
              <FormControlLabel
                value="pages"
                control={<Radio />}
                label="At Specific Pages (e.g., split at page 5, 10)"
              />
            </RadioGroup>
          </Box>

          {/* Split Points */}
          <Box sx={{ mt: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="subtitle1">
                {splitMode === 'ranges' ? 'Page Ranges' : 'Split At Pages'}
              </Typography>
              <Button
                startIcon={<AddIcon />}
                onClick={handleAddSplitPoint}
                size="small"
              >
                Add
              </Button>
            </Box>

            {splitPoints.map((point, index) => (
              <Box key={index} display="flex" gap={1} mb={1}>
                <TextField
                  fullWidth
                  size="small"
                  value={point}
                  onChange={(e) => handleSplitPointChange(index, e.target.value)}
                  placeholder={splitMode === 'ranges' ? '1-5' : '5'}
                  helperText={
                    splitMode === 'ranges'
                      ? 'Format: start-end (e.g., 1-5)'
                      : 'Page number (e.g., 5)'
                  }
                />
                {splitPoints.length > 1 && (
                  <IconButton
                    onClick={() => handleRemoveSplitPoint(index)}
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                )}
              </Box>
            ))}
          </Box>

          {/* Output Name */}
          <TextField
            fullWidth
            label="Output Files Base Name"
            value={outputNameBase}
            onChange={(e) => setOutputNameBase(e.target.value)}
            sx={{ mt: 2 }}
            helperText="Each split file will be named: basename_part1_pages1-5.pdf"
          />

          {/* Split Button */}
          <Button
            variant="contained"
            size="large"
            startIcon={<SplitIcon />}
            onClick={handleSplit}
            disabled={loading}
            fullWidth
            sx={{ mt: 3 }}
          >
            {loading ? 'Splitting PDF...' : 'Split PDF'}
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
