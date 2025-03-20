import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import AdminLayout from '../src/components/layout/AdminLayout';
import theme from '../src/theme';
import { WebSocketProvider } from '../src/context/WebSocketProvider';

export default function App({ Component, pageProps }) {
  return (
    <WebSocketProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AdminLayout>
          <Component {...pageProps} />
        </AdminLayout>
      </ThemeProvider>
    </WebSocketProvider>
  );
}
