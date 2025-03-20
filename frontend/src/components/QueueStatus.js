import { Box, Paper, Typography, LinearProgress, Chip, Stack } from '@mui/material';
import { Download, Transform } from '@mui/icons-material';
import { useWebSocket } from '../hooks/useWebSocket';

export default function QueueStatus() {
  const { queueStatus } = useWebSocket();

  // Filtrar itens ativos
  const downloadingItems = queueStatus.filter(item => 
    item.status === 'downloading' || item.status === 'pending'
  );
  const convertingItems = queueStatus.filter(item => 
    item.status === 'converting'
  );

  if (!downloadingItems.length && !convertingItems.length) {
    return null;
  }

  const renderItems = (items, title, icon) => (
    <Box sx={{ mb: items.length ? 2 : 0 }}>
      {items.length > 0 && (
        <>
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
            {icon}
            <Typography variant="subtitle1">
              {title} ({items.length})
            </Typography>
          </Stack>
          {items.map((item) => (
            <Box key={item.id} sx={{ mb: 1 }}>
              <Typography variant="body2" sx={{ mb: 0.5 }}>
                {item.filename}
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={item.progress} 
                sx={{ height: 8, borderRadius: 1 }}
              />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                <Typography variant="caption" color="text.secondary">
                  {item.status}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {Math.round(item.progress)}%
                </Typography>
              </Box>
            </Box>
          ))}
        </>
      )}
    </Box>
  );

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Status do Processamento
      </Typography>
      
      {renderItems(downloadingItems, "Downloads", <Download color="info" />)}
      {renderItems(convertingItems, "Conversões", <Transform color="warning" />)}
    </Paper>
  );
}
