import { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Divider,
  Snackbar,
} from '@mui/material';
import { useApi } from '../../src/hooks/useApi';

export default function Media() {
  const [tab, setTab] = useState(0);
  const [formats, setFormats] = useState({ video: [], audio: [], quality: [] });
  const [form, setForm] = useState({
    url: '',
    format_id: '',
    quality: '720p',
    customOptions: ''
  });
  const { loading, error, getFormats, processUrl, getVideoFormats } = useApi();
  const [videoFormats, setVideoFormats] = useState([]);
  const [videoTitle, setVideoTitle] = useState('');
  const [isLoadingFormats, setIsLoadingFormats] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '' });

  const resetForm = () => {
    setForm({
      url: '',
      format_id: '',
      quality: '720p',
      customOptions: ''
    });
    setVideoFormats([]);
    setVideoTitle('');
  };

  const loadFormats = async () => {
    try {
      const data = await getFormats();
      setFormats(data);
    } catch (error) {
      console.error('Erro ao carregar formatos:', error);
    }
  };

  const loadVideoFormats = async (url) => {
    setIsLoadingFormats(true);
    try {
      const data = await getVideoFormats(url);
      setVideoFormats(data.formats);
      setVideoTitle(data.title);
      
      // Seleciona automaticamente o melhor formato disponível
      if (data.formats.length > 0) {
        setForm(prev => ({
          ...prev,
          format_id: data.formats[0].format_id
        }));
      }
    } catch (error) {
      console.error('Erro ao carregar formatos:', error);
      setVideoFormats([]);
    } finally {
      setIsLoadingFormats(false);
    }
  };

  useEffect(() => {
    loadFormats();
  }, []); // Executar apenas na montagem

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (form.url) {
        loadVideoFormats(form.url);
      }
    }, 500); // Debounce para evitar múltiplas chamadas

    return () => clearTimeout(timeoutId);
  }, [form.url]); // Dependência apenas da URL

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.url) return;

    try {
      if (tab === 0) { // Download
        const formData = {
          url: form.url,
          format_id: form.format_id,
          // Removido quality pois não é necessário para download
        };
        await processUrl('/api/media/download', formData);
        setNotification({
          open: true,
          message: 'Item adicionado à fila de downloads'
        });
        resetForm();
      } else { // Convert
        await processUrl('/api/media/convert', form);
      }
    } catch (error) {
      console.error('Erro ao processar:', error);
      setNotification({
        open: true,
        message: `Erro: ${error.message}`
      });
    }
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Tabs value={tab} onChange={(e, v) => setTab(v)} sx={{ mb: 3 }}>
            <Tab label="Download" />
            <Tab label="Converter" />
          </Tabs>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="URL da Mídia"
                  value={form.url}
                  onChange={(e) => setForm(prev => ({ ...prev, url: e.target.value }))}
                  required
                  disabled={isLoadingFormats}
                />
              </Grid>

              {isLoadingFormats && (
                <Grid item xs={12}>
                  <Box display="flex" alignItems="center" gap={2}>
                    <CircularProgress size={20} />
                    <Typography>Carregando informações do vídeo...</Typography>
                  </Box>
                </Grid>
              )}

              {videoFormats.length > 0 && tab === 0 && (
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Formato e Qualidade</InputLabel>
                    <Select
                      value={form.format_id || ''}
                      onChange={(e) => setForm(prev => ({ ...prev, format_id: e.target.value }))}
                    >
                      {videoFormats.map((format) => (
                        <MenuItem key={format.format_id} value={format.format_id}>
                          {format.display}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              )}

              {tab === 1 && (
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Formato</InputLabel>
                    <Select
                      value={form.format}
                      onChange={(e) => setForm(prev => ({ ...prev, format: e.target.value }))}
                      required={tab === 1}
                    >
                      {formats.video.map(format => (
                        <MenuItem key={format} value={format}>{format.toUpperCase()}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              )}

              {tab === 1 && (
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Qualidade</InputLabel>
                    <Select
                      value={form.quality}
                      onChange={(e) => setForm(prev => ({ ...prev, quality: e.target.value }))}
                    >
                      {formats.quality.map(quality => (
                        <MenuItem key={quality} value={quality}>{quality}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              )}

              {tab === 1 && (
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Opções Personalizadas"
                    value={form.customOptions}
                    onChange={(e) => setForm(prev => ({ ...prev, customOptions: e.target.value }))}
                    helperText="Opções adicionais FFmpeg"
                    multiline
                  />
                </Grid>
              )}

              <Grid item xs={12}>
                <Button
                  type="submit"
                  variant="contained"
                  disabled={loading || isLoadingFormats || (tab === 0 && !videoFormats.length)}
                  startIcon={loading && <CircularProgress size={20} />}
                >
                  {tab === 0 ? 'Download' : 'Converter'}
                </Button>
              </Grid>
            </Grid>
          </Box>
        </Paper>
      </Grid>

      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
        message={notification.message}
      />
    </Grid>
  );
}
