import { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Tabs,
  Tab,
  IconButton,
  Alert,
  LinearProgress,
  Stack,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
  Button
} from '@mui/material';
import { Cancel, Delete, Download, Transform, CheckCircle, Error, HourglassEmpty } from '@mui/icons-material';
import { useContext } from 'react';
import { WebSocketContext } from '../../src/context/WebSocketProvider';

export default function Queue() {
  const [tab, setTab] = useState(0);
  const { queueStatus, cancelItem } = useContext(WebSocketContext);
  const [cancelDialog, setCancelDialog] = useState({ open: false, itemId: null });

  // Filtrar itens por status
  const activeItems = queueStatus.filter(item => 
    ['downloading', 'converting'].includes(item.status)
  );
  
  const pendingItems = queueStatus.filter(item => 
    item.status === 'pending'
  );
  
  const cancelledItems = queueStatus.filter(item => 
    item.status === 'cancelled'
  );

  const completedItems = queueStatus.filter(item => 
    item.status === 'completed'
  );
  
  const failedItems = queueStatus.filter(item => 
    item.status === 'error'
  );

  const handleCancelClick = (itemId) => {
    setCancelDialog({ open: true, itemId });
  };

  const handleConfirmCancel = () => {
    if (cancelDialog.itemId) {
      cancelItem(cancelDialog.itemId);
      // Item será atualizado automaticamente via WebSocket
    }
    setCancelDialog({ open: false, itemId: null });
  };

  const renderQueueItem = (item) => (
    <Paper key={item.id} sx={{ p: 2, mb: 2 }}>
      <Stack spacing={2}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="subtitle1">
            {item.filename}
          </Typography>
          <Stack direction="row" spacing={1}>
            <Chip
              size="small"
              icon={
                item.status === 'downloading' ? <Download /> :
                item.status === 'converting' ? <Transform /> :
                item.status === 'completed' ? <CheckCircle /> :
                item.status === 'error' ? <Error /> : null
              }
              label={item.status}
              color={
                item.status === 'downloading' ? 'info' :
                item.status === 'converting' ? 'warning' :
                item.status === 'completed' ? 'success' :
                item.status === 'error' ? 'error' : 'default'
              }
            />
            {['pending', 'downloading', 'converting'].includes(item.status) && (
              <IconButton size="small" onClick={() => handleCancelClick(item.id)}>
                <Cancel />
              </IconButton>
            )}
          </Stack>
        </Box>

        {['pending', 'downloading', 'converting'].includes(item.status) && (
          <>
            <LinearProgress 
              variant="determinate" 
              value={item.progress} 
              sx={{ height: 8, borderRadius: 1 }}
            />
            <Typography variant="caption" align="right">
              {Math.round(item.progress)}%
            </Typography>
          </>
        )}

        {item.error && (
          <Alert severity="error" sx={{ mt: 1 }}>
            {item.error}
          </Alert>
        )}
      </Stack>
    </Paper>
  );

  return (
    <>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Gerenciador de Fila
            </Typography>

            <Tabs 
              value={tab} 
              onChange={(e, newValue) => setTab(newValue)}
              sx={{ mb: 3 }}
              variant="scrollable"
              scrollButtons="auto"
            >
              <Tab 
                label={`Ativos (${activeItems.length})`}
                icon={<Transform sx={{ mr: 1 }} />}
              />
              <Tab 
                label={`Pendentes (${pendingItems.length})`}
                icon={<HourglassEmpty sx={{ mr: 1 }} />}
              />
              <Tab 
                label={`Concluídos (${completedItems.length})`}
                icon={<CheckCircle sx={{ mr: 1 }} />}
              />
              <Tab 
                label={`Cancelados (${cancelledItems.length})`}
                icon={<Cancel sx={{ mr: 1 }} />}
              />
              <Tab 
                label={`Falhas (${failedItems.length})`}
                icon={<Error sx={{ mr: 1 }} />}
              />
            </Tabs>

            <Box>
              {tab === 0 && activeItems.map(renderQueueItem)}
              {tab === 1 && pendingItems.map(renderQueueItem)}
              {tab === 2 && completedItems.map(renderQueueItem)}
              {tab === 3 && cancelledItems.map(renderQueueItem)}
              {tab === 4 && failedItems.map(renderQueueItem)}

              {tab === 0 && !activeItems.length && (
                <Typography color="text.secondary">
                  Nenhum item em processamento
                </Typography>
              )}
              {tab === 1 && !pendingItems.length && (
                <Typography color="text.secondary">
                  Nenhum item pendente
                </Typography>
              )}
              {tab === 2 && !completedItems.length && (
                <Typography color="text.secondary">
                  Nenhum item concluído
                </Typography>
              )}
              {tab === 3 && !cancelledItems.length && (
                <Typography color="text.secondary">
                  Nenhum item cancelado
                </Typography>
              )}
              {tab === 4 && !failedItems.length && (
                <Typography color="text.secondary">
                  Nenhuma falha
                </Typography>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>

      <Dialog
        open={cancelDialog.open}
        onClose={() => setCancelDialog({ open: false, itemId: null })}
      >
        <DialogTitle>Confirmar Cancelamento</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Tem certeza que deseja cancelar este item da fila?
            Esta ação não pode ser desfeita.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setCancelDialog({ open: false, itemId: null })}
          >
            Não
          </Button>
          <Button 
            onClick={handleConfirmCancel} 
            color="error" 
            variant="contained"
            autoFocus
          >
            Sim, Cancelar
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
