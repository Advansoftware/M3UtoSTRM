import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#007FFF',
      light: '#66B2FF',
      dark: '#0059B2',
      contrastText: '#fff'
    },
    secondary: {
      main: '#9c27b0',
      light: '#ba68c8',
      dark: '#7b1fa2',
      contrastText: '#fff'
    },
    background: {
      default: '#0A1929',
      paper: '#001E3C'
    },
    divider: 'rgba(194, 224, 255, 0.08)',
    text: {
      primary: '#fff',
      secondary: '#B2BAC2'
    }
  },
  shape: {
    borderRadius: 10
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: '#001E3C',
          boxShadow: '0px 2px 4px -1px rgba(0,0,0,0.2)'
        }
      }
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#001E3C',
          borderRight: '1px solid rgba(194, 224, 255, 0.08)'
        }
      }
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none'
        }
      }
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          '&.Mui-selected': {
            backgroundColor: 'rgba(19, 47, 76, 0.4)'
          },
          '&:hover': {
            backgroundColor: 'rgba(19, 47, 76, 0.6)'
          }
        }
      }
    },
    MuiListItemIcon: {
      styleOverrides: {
        root: {
          color: '#66B2FF'
        }
      }
    }
  },
  typography: {
    fontFamily: '"IBM Plex Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol"',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600
    }
  }
});

export default theme;
