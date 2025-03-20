import { useState } from 'react';
import {
  Modal,
  Box,
  Typography,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Stack,
  TextField,
  Alert,
  CircularProgress
} from '@mui/material';
import { Download, Transform } from '@mui/icons-material';

export default function MediaActionModal({ open, onClose, mediaUrl, mediaTitle }) {
  const [action, setAction] = useState('download');
  const [format, setFormat] = useState('mp4');
  const [quality, setQuality] = useState('720p');
  const [customOptions, setCustomOptions] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const endpoint = action === 'download' ? '/api/media/download' : '/api/media/convert';
      const formData = {
        url: mediaUrl,
        format,
        ...(action === 'convert' && { quality, customOptions })
      };
      
      // Use o hook useApi para processar
      // await processUrl(endpoint, formData);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      aria-labelledby="media-action-modal"
    >
      <Box sx={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: { xs: '90%', sm: 500 },
        bgcolor: 'background.paper',
        borderRadius: 1,
        p: 4,
      }}>
        <Typography variant="h6" gutterBottom>
          {mediaTitle}
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Stack spacing={3}>
          <FormControl fullWidth>
            <InputLabel>Ação</InputLabel>
            <Select
              value={action}
              onChange={(e) => setAction(e.target.value)}
              disabled={loading}
            >
              <MenuItem value="download">
                <Stack direction="row" alignItems="center" spacing={1}>
                  <Download fontSize="small" />
                  <span>Download</span>
                </Stack>
              </MenuItem>
              <MenuItem value="convert">
                <Stack direction="row" alignItems="center" spacing={1}>
                  <Transform fontSize="small" />
                  <span>Converter</span>
                </Stack>
              </MenuItem>
            </Select>
          </FormControl>

          <FormControl fullWidth>
            <InputLabel>Formato</InputLabel>
            <Select
              value={format}
              onChange={(e) => setFormat(e.target.value)}
              disabled={loading}
            >
              <MenuItem value="mp4">MP4</MenuItem>
              <MenuItem value="mkv">MKV</MenuItem>
              <MenuItem value="avi">AVI</MenuItem>
              <MenuItem value="webm">WEBM</MenuItem>
            </Select>
          </FormControl>

          {action === 'convert' && (
            <>
              <FormControl fullWidth>
                <InputLabel>Qualidade</InputLabel>
                <Select
                  value={quality}
                  onChange={(e) => setQuality(e.target.value)}
                  disabled={loading}
                >
                  <MenuItem value="480p">480p</MenuItem>
                  <MenuItem value="720p">720p</MenuItem>
                  <MenuItem value="1080p">1080p</MenuItem>
                  <MenuItem value="2160p">2160p</MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                multiline
                rows={2}
                label="Opções FFmpeg Personalizadas"
                value={customOptions}
                onChange={(e) => setCustomOptions(e.target.value)}
                disabled={loading}
                helperText="Opções adicionais para FFmpeg"
              />
            </>
          )}

          <Stack direction="row" spacing={2} justifyContent="flex-end">
            <Button
              variant="outlined"
              onClick={onClose}
              disabled={loading}
            >
              Cancelar
            </Button>
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              {loading ? 'Processando...' : 'Confirmar'}
            </Button>
          </Stack>
        </Stack>
      </Box>
    </Modal>
  );
}
