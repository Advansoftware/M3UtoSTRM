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
  Tab
} from '@mui/material';
import { useApi } from '../../src/hooks/useApi';

export default function Media() {
  const [tab, setTab] = useState(0);
  const [formats, setFormats] = useState({ video: [], audio: [], quality: [] });
  const [form, setForm] = useState({
    url: '',
    format: '',
    quality: '720p',
    customOptions: ''
  });
  const { loading, error, getFormats, processUrl } = useApi();

  useEffect(() => {
    loadFormats();
  }, []);

  const loadFormats = async () => {
    try {
      const data = await getFormats();
      setFormats(data);
    } catch (error) {
      console.error('Erro ao carregar formatos:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.url) return;

    try {
      if (tab === 0) { // Download
        await processUrl('/api/media/download', form);
      } else { // Convert
        await processUrl('/api/media/convert', form);
      }
    } catch (error) {
      console.error(error);
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
                />
              </Grid>

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
                  disabled={loading}
                  startIcon={loading && <CircularProgress size={20} />}
                >
                  {tab === 0 ? 'Download' : 'Converter'}
                </Button>
              </Grid>
            </Grid>
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
}
