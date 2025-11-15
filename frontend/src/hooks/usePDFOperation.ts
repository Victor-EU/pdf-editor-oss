/**
 * Custom hook for managing PDF operations
 * Centralizes loading, error, and success state management
 */

import { useState } from 'react'

interface UsePDFOperationReturn {
  loading: boolean
  error: string | null
  success: string | null
  setError: (error: string | null) => void
  setSuccess: (success: string | null) => void
  executeOperation: <T>(operation: () => Promise<T>) => Promise<T | null>
  resetState: () => void
}

export const usePDFOperation = (): UsePDFOperationReturn => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const resetState = () => {
    setError(null)
    setSuccess(null)
  }

  const executeOperation = async <T,>(
    operation: () => Promise<T>
  ): Promise<T | null> => {
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const result = await operation()
      return result
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'Operation failed'
      setError(errorMessage)
      return null
    } finally {
      setLoading(false)
    }
  }

  return {
    loading,
    error,
    success,
    setError,
    setSuccess,
    executeOperation,
    resetState
  }
}
