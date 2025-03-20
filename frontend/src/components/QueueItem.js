import { Box, Typography, LinearProgress, IconButton, Chip, Card } from '@mui/material';
import { Cancel, Download, Transform } from '@mui/icons-material';
import { useApi } from '../hooks/useApi';

export default function QueueItem({ item }) {
  const { processUrl } = useApi();

  const handleCancel = async () => {
    try {
      await processUrl('/api/queue/cancel', { itemId: item.id });
    } catch (error) {
      console.error('Erro ao cancelar item:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'downloading':
        return 'info';
      case 'converting':
        return 'warning';
      case 'error':
        return 'error';
      case 'completed':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'downloading':
        return <Download fontSize="small" />;
      case 'converting':
        return <Transform fontSize="small" />;
      default:
        return null;
    }
  };

  return (
    <Card 
      sx={{ 
        p: 2, 
        mb: 1,
        position: 'relative',
        '&:hover .cancel-button': {
          opacity: 1
        }
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Typography variant="body2" sx={{ flex: 1 }} noWrap>
          {item.name}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Chip
            size="small"
            icon={getStatusIcon(item.status)}
            label={`${Math.round(item.progress)}%`}
            color={getStatusColor(item.status)}
          />
          {['downloading', 'converting'].includes(item.status) && (
            <IconButton 
              size="small"
              onClick={handleCancel}
              className="cancel-button"
              sx={{ 
                opacity: 0,
                transition: 'opacity 0.2s',
                '&:hover': { color: 'error.main' }
              }}
            >
              <Cancel fontSize="small" />
            </IconButton>
          )}
        </Box>
      </Box>
      <LinearProgress
        variant="determinate"
        value={item.progress}
        color={getStatusColor(item.status)}
        sx={{ 
          height: 6, 
          borderRadius: 1,
          backgroundColor: 'background.default'
        }}
      />
      {item.error && (
        <Typography 
          variant="caption" 
          color="error" 
          sx={{ display: 'block', mt: 1 }}
        >
          Erro: {item.error}
        </Typography>
      )}
    </Card>
  );
}
