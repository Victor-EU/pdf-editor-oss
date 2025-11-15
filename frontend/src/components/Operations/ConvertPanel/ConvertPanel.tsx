import { useState } from 'react'
import {
  Box, Button, Typography, TextField, RadioGroup,
  FormControlLabel, Radio, Chip, Paper, Select, MenuItem,
  FormControl, InputLabel, LinearProgress
} from '@mui/material'
import {
  Upload as UploadIcon,
  Image as ImageIcon
} from '@mui/icons-material'
import { usePDFOperation } from '../../../hooks/usePDFOperation'
import { useFileDropzone } from '../../../hooks/useFileDropzone'
import { StatusAlerts } from '../../shared/StatusAlerts'
import { apiService } from '../../../services/api'
import styles from './ConvertPanel.module.css'

export const ConvertPanel = () => {
  const [file, setFile] = useState<File | null>(null)
  const [imageFormat, setImageFormat] = useState<'png' | 'jpeg' | 'tiff'>('png')
  const [dpi, setDpi] = useState(150)
  const [pages, setPages] = useState('')
  const [outputNameBase, setOutputNameBase] = useState('converted')
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

  const handleConvert = async () => {
    if (!file) {
      setError('Please select a PDF file to convert')
      return
    }

    await executeOperation(async () => {
      const response = await apiService.convertPdfToImage({
        file,
        imageFormat,
        dpi,
        pages: pages || undefined,
        outputFileNameBase: outputNameBase
      })

      setSuccess(`PDF converted successfully to ${response.data.length} image(s)`)

      // Download all images
      for (const fileInfo of response.data) {
        const blob = await apiService.downloadFile(fileInfo.fileName)
        apiService.triggerDownload(blob, fileInfo.fileName)
        // Small delay between downloads
        await new Promise(resolve => setTimeout(resolve, 200))
      }

      // Reset
      setFile(null)
      setPages('')
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
              Select a PDF file to convert to images
            </Typography>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              id="convert-upload"
            />
            <label htmlFor="convert-upload">
              <Button variant="outlined" component="span">
                Select PDF File
              </Button>
            </label>
          </>
        ) : (
          <Box textAlign="center">
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
          {/* Image Format Selection */}
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              Output Format
            </Typography>
            <RadioGroup
              value={imageFormat}
              onChange={(e) => setImageFormat(e.target.value as any)}
              row
            >
              <FormControlLabel
                value="png"
                control={<Radio />}
                label={
                  <Box>
                    <Typography variant="body1">PNG</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Lossless, supports transparency
                    </Typography>
                  </Box>
                }
              />
              <FormControlLabel
                value="jpeg"
                control={<Radio />}
                label={
                  <Box>
                    <Typography variant="body1">JPEG</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Smaller file size
                    </Typography>
                  </Box>
                }
              />
              <FormControlLabel
                value="tiff"
                control={<Radio />}
                label={
                  <Box>
                    <Typography variant="body1">TIFF</Typography>
                    <Typography variant="caption" color="text.secondary">
                      High quality, large files
                    </Typography>
                  </Box>
                }
              />
            </RadioGroup>
          </Box>

          {/* DPI Selection */}
          <FormControl fullWidth sx={{ mt: 3 }}>
            <InputLabel>Resolution (DPI)</InputLabel>
            <Select
              value={dpi}
              label="Resolution (DPI)"
              onChange={(e) => setDpi(e.target.value as number)}
            >
              <MenuItem value={72}>
                <Box>
                  <Typography>72 DPI - Screen</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Low quality, smallest file size
                  </Typography>
                </Box>
              </MenuItem>
              <MenuItem value={150}>
                <Box>
                  <Typography>150 DPI - Standard</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Good balance of quality and size
                  </Typography>
                </Box>
              </MenuItem>
              <MenuItem value={300}>
                <Box>
                  <Typography>300 DPI - High Quality</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Print quality, larger file size
                  </Typography>
                </Box>
              </MenuItem>
              <MenuItem value={600}>
                <Box>
                  <Typography>600 DPI - Very High Quality</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Maximum quality, very large files
                  </Typography>
                </Box>
              </MenuItem>
            </Select>
          </FormControl>

          {/* Page Selection */}
          <TextField
            fullWidth
            label="Pages to Convert (optional)"
            value={pages}
            onChange={(e) => setPages(e.target.value)}
            placeholder="e.g., 1,3,5 or 1-5"
            helperText="Leave empty to convert all pages. Format: 1,3,5 or 1-5"
            sx={{ mt: 3 }}
          />

          {/* Output Name */}
          <TextField
            fullWidth
            label="Output Files Base Name"
            value={outputNameBase}
            onChange={(e) => setOutputNameBase(e.target.value)}
            sx={{ mt: 2 }}
            helperText="Each image will be named: basename_page_01.png"
          />

          {/* Convert Button */}
          <Button
            variant="contained"
            size="large"
            startIcon={<ImageIcon />}
            onClick={handleConvert}
            disabled={loading}
            fullWidth
            sx={{ mt: 3 }}
          >
            {loading ? 'Converting PDF...' : 'Convert to Images'}
          </Button>

          {/* Progress */}
          {loading && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                Converting pages to images... This may take a moment
              </Typography>
            </Box>
          )}
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
