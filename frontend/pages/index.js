import { useEffect, useState } from 'react';
import { Typography, Paper, Grid, Box, Alert, CircularProgress } from '@mui/material';
import QueuePanel from '../src/components/QueuePanel';
import { useApi } from '../src/hooks/useApi';
import { Movie, Tv, PlaylistPlay } from '@mui/icons-material';

export default function Home() {
  const [stats, setStats] = useState({
    movies: 0,
    series: 0,
    total: 0
  });
  const { loading, error, fetchStats } = useApi();

  
  const loadStats = async () => {
    try {
      const data = await fetchStats();
      if (!data.error) {
        setStats(data);
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };
  
  useEffect(() => {
    loadStats();
  }, []);

  const renderStatCard = (icon, title, value) => (
    <Grid item xs={12} md={6} lg={4}>
      <Paper sx={{ p: 3, position: 'relative', minHeight: '140px' }}>
        {loading && (
          <Box sx={{ 
            position: 'absolute', 
            top: 0, 
            left: 0, 
            right: 0, 
            bottom: 0, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            bgcolor: 'rgba(255, 255, 255, 0.8)'
          }}>
            <CircularProgress />
          </Box>
        )}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
          {icon}
          <Typography variant="h6" gutterBottom>
            {title}
          </Typography>
        </Box>
        <Typography variant="h3" color="primary.light">
          {value}
        </Typography>
      </Paper>
    </Grid>
  );

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper 
          elevation={0}
          sx={{ 
            p: 3,
            background: 'linear-gradient(to right bottom, #001E3C, #003362)'
          }}
        >
          <Typography 
            variant="h4" 
            component="h1" 
            gutterBottom
            sx={{ 
              color: 'primary.light',
              fontWeight: 'bold'
            }}
          >
            Dashboard
          </Typography>
          <Typography 
            variant="body1"
            sx={{ color: 'text.secondary' }}
          >
            Gerenciamento de mídia M3UtoSTRM
          </Typography>
        </Paper>
      </Grid>

      {error && (
        <Grid item xs={12}>
          <Alert severity="error">{error}</Alert>
        </Grid>
      )}

      <Grid item xs={12}>
        <QueuePanel />
      </Grid>

      {renderStatCard(
        <PlaylistPlay color="primary" fontSize="large" />,
        "Total de Itens",
        stats.total
      )}
      
      {renderStatCard(
        <Movie color="primary" fontSize="large" />,
        "Filmes",
        stats.movies
      )}
      
      {renderStatCard(
        <Tv color="primary" fontSize="large" />,
        "Séries",
        stats.series
      )}
    </Grid>
  );
}
