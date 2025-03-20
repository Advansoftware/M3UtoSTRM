import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import AdminLayout from '../src/components/layout/AdminLayout';
import theme from '../src/theme';

export default function App({ Component, pageProps }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AdminLayout>
        <Component {...pageProps} />
      </AdminLayout>
    </ThemeProvider>
  );
}
