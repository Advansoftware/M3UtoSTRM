import { useEffect, useState } from 'react';
import { Grid, Paper, Typography, TextField, Button, Alert } from '@mui/material';
import { useApi } from '../../src/hooks/useApi';

export default function Settings() {
  const [config, setConfig] = useState({
    omdb_api_key: '',
    tmdb_api_key: ''
  });
  const [saveSuccess, setSaveSuccess] = useState(false);
  const { getConfig, updateConfig } = useApi();

  useEffect(() => {
    const loadConfig = async () => {
      const data = await getConfig();
      setConfig(data);
    };
    loadConfig();
  }, []);

  const handleSave = async () => {
    try {
      await updateConfig(config);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>Configurações da API</Typography>
          
          {saveSuccess && (
            <Alert severity="success" sx={{ mb: 2 }}>
              Configurações salvas com sucesso!
            </Alert>
          )}

          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="OMDB API Key"
                value={config.omdb_api_key}
                onChange={(e) => setConfig(prev => ({ ...prev, omdb_api_key: e.target.value }))}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="TMDB API Key"
                value={config.tmdb_api_key}
                onChange={(e) => setConfig(prev => ({ ...prev, tmdb_api_key: e.target.value }))}
              />
            </Grid>

            <Grid item xs={12}>
              <Button
                variant="contained"
                onClick={handleSave}
                sx={{ mt: 2 }}
              >
                Salvar Configurações
              </Button>
            </Grid>
          </Grid>
        </Paper>
      </Grid>
    </Grid>
  );
}
