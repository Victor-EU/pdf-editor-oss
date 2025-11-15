/**
 * Material-UI Theme Configuration
 * Pleasant light green theme for open source PDF editor
 */

import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#7FD68D',       // Light green
      light: '#9FE6AC',      // Lighter green
      dark: '#5FB86F',       // Darker green
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#5A7D6C',
      light: '#95B8A5',
      dark: '#2C503E',
      contrastText: '#FFFFFF',
    },
    success: {
      main: '#5CB85C',
      light: '#D4EDDA',
      dark: '#4A9B4A',
    },
    error: {
      main: '#D9534F',
      light: '#F8D7DA',
      dark: '#C9302C',
    },
    warning: {
      main: '#F0AD4E',
      light: '#FFF3CD',
      dark: '#EC971F',
    },
    info: {
      main: '#5BC0DE',
      light: '#D1ECF1',
      dark: '#31B0D5',
    },
    background: {
      default: '#F5FFF7',    // Very light green tint
      paper: '#FFFFFF',
    },
    text: {
      primary: '#2C3E50',
      secondary: '#5A6C7D',
      disabled: '#95A5B8',
    },
    divider: '#E1F1EA',
  },
  typography: {
    fontFamily: '"Source Sans Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      lineHeight: 1.25,
      color: '#2C3E50',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      lineHeight: 1.25,
      color: '#2C3E50',
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.25,
      color: '#2C3E50',
    },
    h4: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.25,
      color: '#2C3E50',
    },
    h5: {
      fontSize: '1.125rem',
      fontWeight: 600,
      lineHeight: 1.25,
      color: '#2C3E50',
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
      lineHeight: 1.25,
      color: '#2C3E50',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
      color: '#5A6C7D',
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
      color: '#5A6C7D',
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 8,
  },
  shadows: [
    'none',
    '0 1px 2px rgba(127, 214, 141, 0.08)',
    '0 1px 3px rgba(127, 214, 141, 0.1)',
    '0 4px 6px rgba(127, 214, 141, 0.15)',
    '0 10px 25px rgba(127, 214, 141, 0.2)',
    '0 20px 40px rgba(127, 214, 141, 0.25)',
    '0 1px 3px rgba(127, 214, 141, 0.1)',
    '0 4px 6px rgba(127, 214, 141, 0.15)',
    '0 10px 25px rgba(127, 214, 141, 0.2)',
    '0 1px 3px rgba(127, 214, 141, 0.1)',
    '0 4px 6px rgba(127, 214, 141, 0.15)',
    '0 10px 25px rgba(127, 214, 141, 0.2)',
    '0 1px 3px rgba(127, 214, 141, 0.1)',
    '0 4px 6px rgba(127, 214, 141, 0.15)',
    '0 10px 25px rgba(127, 214, 141, 0.2)',
    '0 1px 3px rgba(127, 214, 141, 0.1)',
    '0 4px 6px rgba(127, 214, 141, 0.15)',
    '0 10px 25px rgba(127, 214, 141, 0.2)',
    '0 1px 3px rgba(127, 214, 141, 0.1)',
    '0 4px 6px rgba(127, 214, 141, 0.15)',
    '0 10px 25px rgba(127, 214, 141, 0.2)',
    '0 1px 3px rgba(127, 214, 141, 0.1)',
    '0 4px 6px rgba(127, 214, 141, 0.15)',
    '0 10px 25px rgba(127, 214, 141, 0.2)',
    '0 20px 40px rgba(127, 214, 141, 0.25)',
  ],
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '8px 24px',
          fontSize: '1rem',
          fontWeight: 600,
          transition: 'all 250ms ease',
          '&:hover': {
            transform: 'translateY(-1px)',
            boxShadow: '0 4px 6px rgba(127, 214, 141, 0.15)',
          },
        },
        contained: {
          boxShadow: '0 1px 3px rgba(127, 214, 141, 0.1)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 1px 3px rgba(127, 214, 141, 0.1)',
          transition: 'all 250ms ease',
          '&:hover': {
            boxShadow: '0 4px 6px rgba(127, 214, 141, 0.15)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
        elevation1: {
          boxShadow: '0 1px 3px rgba(127, 214, 141, 0.1)',
        },
        elevation2: {
          boxShadow: '0 4px 6px rgba(127, 214, 141, 0.15)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: '#7FD68D',
            },
          },
        },
      },
    },
  },
});
