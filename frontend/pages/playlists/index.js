import { useEffect, useState } from 'react';
import { 
  Box, 
  Grid, 
  Paper, 
  Typography, 
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Divider,
  CircularProgress,
  Button,
  Stack,
  Pagination,
  Alert
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import MediaActionModal from '../../src/components/MediaActionModal';
import { useApi } from '../../src/hooks/useApi';

export default function Playlists() {
  const [content, setContent] = useState({
    movies: [],
    series: {},
    pagination: {
      total: 0,
      pages: 0,
      current: 1,
      limit: 20
    }
  });
  const [localLoading, setLocalLoading] = useState(true);
  const [page, setPage] = useState(1);
  const { getContent, deleteMovie, deleteEpisode } = useApi();
  const [selectedMedia, setSelectedMedia] = useState(null);

  useEffect(() => {
    let mounted = true;

    const fetchContent = async () => {
      try {
        setLocalLoading(true);
        const data = await getContent(page);
        
        if (!mounted) return;
        setContent(data);
      } catch (error) {
        if (!mounted) return;
        console.error('Erro ao carregar conteúdo:', error);
        setContent(prev => ({
          ...prev,
          error: error.message
        }));
      } finally {
        if (mounted) {
          setLocalLoading(false);
        }
      }
    };

    fetchContent();

    return () => {
      mounted = false;
    };
  }, [page]);

  const handleRetry = () => {
    setPage(1); // Reset para primeira página em caso de retry
  };

  const handleDeleteMovie = async (filename) => {
    try {
      await deleteMovie(filename);
      setPage(1); // Reset para primeira página em caso de delete
    } catch (error) {
      console.error(error);
    }
  };

  const handleDeleteEpisode = async (series, season, filename) => {
    try {
      await deleteEpisode(series, season, filename);
      setPage(1); // Reset para primeira página em caso de delete
    } catch (error) {
      console.error(error);
    }
  };

  const handleMediaAction = (media) => {
    setSelectedMedia(media);
  };

  if (localLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (content.error) {
    return (
      <Box sx={{ mt: 2 }}>
        <Alert 
          severity="error" 
          action={
            <Button color="inherit" size="small" onClick={handleRetry}>
              Tentar novamente
            </Button>
          }
        >
          {content.error}
        </Alert>
      </Box>
    );
  }

  return (
    <Grid container spacing={3}>
      <MediaActionModal 
        open={Boolean(selectedMedia)}
        onClose={() => setSelectedMedia(null)}
        mediaUrl={selectedMedia?.url}
        mediaTitle={selectedMedia?.title}
      />

      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>Filmes</Typography>
          {Array.isArray(content.movies) && content.movies.length > 0 ? (
            <>
              <List>
                {content.movies.map((movie) => (
                  <ListItem key={movie.file}>
                    <ListItemText 
                      primary={movie.title}
                      secondary={movie.url}
                    />
                    <Stack direction="row" spacing={1}>
                      <IconButton
                        onClick={() => handleMediaAction(movie)}
                        color="primary"
                      >
                        <MoreVertIcon />
                      </IconButton>
                      <IconButton 
                        edge="end" 
                        onClick={() => handleDeleteMovie(movie.file)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Stack>
                  </ListItem>
                ))}
              </List>
              
              {content.pagination.pages > 1 && (
                <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
                  <Pagination 
                    count={content.pagination.pages}
                    page={page}
                    onChange={(e, value) => setPage(value)}
                    color="primary"
                  />
                </Box>
              )}
            </>
          ) : (
            <Typography color="text.secondary">
              Nenhum filme encontrado
            </Typography>
          )}
        </Paper>
      </Grid>

      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>Séries</Typography>
          {Object.keys(content.series || {}).length > 0 ? (
            Object.entries(content.series).map(([series, seasons]) => (
              <Accordion key={series}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>{series}</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {Object.entries(seasons).map(([season, episodes]) => (
                    <Box key={season}>
                      <Typography variant="h6" gutterBottom>{season}</Typography>
                      <List>
                        {Array.isArray(episodes) && episodes.map((episode) => (
                          <ListItem key={episode.file}>
                            <ListItemText 
                              primary={episode.title}
                              secondary={episode.url}
                            />
                            <Stack direction="row" spacing={1}>
                              <IconButton
                                onClick={() => handleMediaAction(episode)}
                                color="primary"
                              >
                                <MoreVertIcon />
                              </IconButton>
                              <IconButton 
                                edge="end" 
                                onClick={() => handleDeleteEpisode(series, season, episode.file)}
                                color="error"
                              >
                                <DeleteIcon />
                              </IconButton>
                            </Stack>
                          </ListItem>
                        ))}
                      </List>
                      <Divider sx={{ my: 2 }} />
                    </Box>
                  ))}
                </AccordionDetails>
              </Accordion>
            ))
          ) : (
            <Typography color="text.secondary">
              Nenhuma série encontrada
            </Typography>
          )}
        </Paper>
      </Grid>
    </Grid>
  );
}
