import { Chip, Stack } from '@mui/material';
import { Download, Transform } from '@mui/icons-material';
import { useWebSocket } from '../hooks/useWebSocket';

export default function QueueStatus() {
  const { queueStatus } = useWebSocket();

  const downloadingCount = queueStatus.filter(item => 
    item.status === 'downloading' || item.status === 'pending'
  ).length;

  const convertingCount = queueStatus.filter(item => 
    item.status === 'converting'
  ).length;

  if (!downloadingCount && !convertingCount) return null;

  return (
    <Stack direction="row" spacing={1}>
      {downloadingCount > 0 && (
        <Chip
          icon={<Download />}
          label={`${downloadingCount} downloads ativos`}
          color="info"
        />
      )}
      {convertingCount > 0 && (
        <Chip
          icon={<Transform />}
          label={`${convertingCount} conversões ativas`}
          color="warning"
        />
      )}
    </Stack>
  );
}
