/**
 * Shared StatusAlerts component
 * Displays error and success alerts consistently across all operation panels
 */

import { Alert } from '@mui/material'

interface StatusAlertsProps {
  error: string | null
  success: string | null
  onClearError?: () => void
  onClearSuccess?: () => void
}

export const StatusAlerts = ({
  error,
  success,
  onClearError,
  onClearSuccess
}: StatusAlertsProps) => {
  return (
    <>
      {error && (
        <Alert
          severity="error"
          sx={{ mb: 2 }}
          onClose={onClearError}
        >
          {error}
        </Alert>
      )}

      {success && (
        <Alert
          severity="success"
          sx={{ mb: 2 }}
          onClose={onClearSuccess}
        >
          {success}
        </Alert>
      )}
    </>
  )
}
