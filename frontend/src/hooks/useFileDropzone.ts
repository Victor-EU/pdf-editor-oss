/**
 * Custom hook for file dropzone functionality
 * Centralizes drag & drop handlers for PDF file uploads
 */

import { useState } from 'react'

interface UseFileDropzoneOptions {
  onFileDrop: (file: File) => void
  acceptedType?: string
  errorMessage?: string
}

interface UseFileDropzoneReturn {
  dragActive: boolean
  handleDrag: (e: React.DragEvent) => void
  handleDrop: (e: React.DragEvent) => void
}

export const useFileDropzone = ({
  onFileDrop,
  acceptedType = 'application/pdf',
  errorMessage = 'Please drop a PDF file'
}: UseFileDropzoneOptions): UseFileDropzoneReturn => {
  const [dragActive, setDragActive] = useState(false)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()

    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0]

      if (droppedFile.type === acceptedType) {
        onFileDrop(droppedFile)
      } else {
        // You might want to handle error through a callback
        console.error(errorMessage)
      }
    }
  }

  return {
    dragActive,
    handleDrag,
    handleDrop
  }
}
