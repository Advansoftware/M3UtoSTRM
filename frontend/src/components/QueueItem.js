import { Box, Typography, LinearProgress, IconButton, Chip, Card } from '@mui/material';
import { Cancel, Download, Transform, HourglassEmpty, Error, CheckCircle } from '@mui/icons-material';
import { useApi } from '../hooks/useApi';

export default function QueueItem({ item }) {
  const { processUrl } = useApi();

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'secondary';
      case 'downloading':
        return 'info';
      case 'converting':
        return 'warning';
      case 'error':
        return 'error';
      case 'completed':
        return 'success';
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'pending':
        return 'Aguardando';
      case 'downloading':
        return 'Baixando';
      case 'converting':
        return 'Convertendo';
      case 'completed':
        return 'Concluído';
      case 'error':
        return 'Erro';
      case 'cancelled':
        return 'Cancelado';
      default:
        return status;
    }
  };

  const getProgressText = (status, progress) => {
    if (status === 'downloading') {
      return `Baixando: ${progress.toFixed(1)}%`;
    } else if (status === 'converting') {
      return `Convertendo: ${progress.toFixed(1)}%`;
    }
    return getStatusLabel(status);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <HourglassEmpty />;
      case 'downloading':
        return <Download />;
      case 'converting':
        return <Transform />;
      case 'cancelled':
        return <Cancel />;
      case 'error':
        return <Error />;
      case 'completed':
        return <CheckCircle />;
      default:
        return null;
    }
  };

  const handleCancel = async () => {
    try {
      await processUrl('/api/queue/cancel', { item_id: item.id });
    } catch (error) {
      console.error('Erro ao cancelar item:', error);
    }
  };

  return (
    <Card sx={{ p: 2, mb: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
        <Box>
          <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
            {item.filename}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {getProgressText(item.status, item.progress)}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Chip
            size="small"
            label={getStatusLabel(item.status)}
            color={getStatusColor(item.status)}
            icon={getStatusIcon(item.status)}
          />
          {['pending', 'downloading', 'converting'].includes(item.status) && (
            <IconButton size="small" onClick={handleCancel}>
              <Cancel />
            </IconButton>
          )}
        </Box>
      </Box>

      <Box sx={{ width: '100%', mt: 1 }}>
        <LinearProgress 
          variant="determinate" 
          value={item.progress} 
          sx={{ 
            height: 6, 
            borderRadius: 1,
            '& .MuiLinearProgress-bar': {
              transition: 'transform 0.1s linear' // Transição mais suave
            }
          }}
        />
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'flex-end', 
          mt: 0.5,
          minHeight: '20px' // Evita "pulo" do layout
        }}>
          <Typography variant="caption" color="text.secondary">
            {Math.round(item.progress)}%
          </Typography>
        </Box>
      </Box>
    </Card>
  );
}
