import { Box, Typography, Paper, Divider } from '@mui/material';
import QueueItem from './QueueItem';
import { useContext } from 'react';
import { WebSocketContext } from '../context/WebSocketProvider';

export default function QueuePanel() {
  const { queueStatus } = useContext(WebSocketContext);

  const downloadQueue = queueStatus.filter(item => 
    ['downloading', 'pending'].includes(item.status)
  );

  const convertQueue = queueStatus.filter(item => 
    item.status === 'converting'
  );

  if (!downloadQueue.length && !convertQueue.length) {
    return null;
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Fila de Processamento
      </Typography>
      
      {/* Downloads */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          Downloads ({downloadQueue.length})
        </Typography>
        {downloadQueue.length > 0 ? (
          downloadQueue.map(item => (
            <QueueItem key={item.id} item={item} />
          ))
        ) : (
          <Typography variant="body2" color="text.secondary">
            Nenhum download ativo
          </Typography>
        )}
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Conversões */}
      <Box>
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          Conversões ({convertQueue.length})
        </Typography>
        {convertQueue.length > 0 ? (
          convertQueue.map(item => (
            <QueueItem key={item.id} item={item} />
          ))
        ) : (
          <Typography variant="body2" color="text.secondary">
            Nenhuma conversão ativa
          </Typography>
        )}
      </Box>
    </Paper>
  );
}
