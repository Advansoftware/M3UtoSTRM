import { useState } from 'react';
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000', // Changed port to 8000
  timeout: 300000, // Aumentado para 30 segundos
  headers: {
    'Content-Type': 'application/json'
  },
  // Adicionar retry em caso de falha
  retry: 3,
  retryDelay: (retryCount) => {
    return retryCount * 1000; // tempo em ms (1s, 2s, 3s)
  }
});

// Interceptor para tratar erros de rede
api.interceptors.response.use(
  response => response,
  async error => {
    const { config } = error;
    
    // Se não é uma retry e tem configuração
    if (!config || !config.retry) {
      return Promise.reject(error);
    }

    if (error.code === 'ECONNABORTED' && config.retry > 0) {
      config.retry -= 1;
      const delayRetry = new Promise(resolve => {
        setTimeout(resolve, config.retryDelay(config.retry));
      });
      await delayRetry;
      return api(config);
    }
    
    return Promise.reject(error);
  }
);

export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Playlist Analysis
  const analyzeUrl = async (url) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('url', url);
      const { data } = await api.post('/api/analyze-url', formData);
      return data;
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao analisar URL');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // STRM File Management
  const createStrm = async (url, title) => {
    const formData = new FormData();
    formData.append('url', url);
    formData.append('title', title);
    const { data } = await api.post('/api/create-strm', formData);
    return data;
  };

  const deleteStrm = async (filename) => {
    const { data } = await api.delete(`/api/strm/${filename}`);
    return data;
  };

  // Video Processing
  const processUrl = async (endpoint, formData) => {
    setLoading(true);
    try {
      const form = new FormData();
      Object.entries(formData).forEach(([key, value]) => {
        if (value) form.append(key, value);
      });
      const { data } = await api.post(endpoint, form);
      return data;
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao processar URL');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const processFile = async (file, customCommand) => {
    const formData = new FormData();
    formData.append('file', file);
    if (customCommand) formData.append('custom_command', customCommand);
    const { data } = await api.post('/api/process-file', formData);
    return data;
  };

  // Queue Management
  const getQueue = async () => {
    const { data } = await api.get('/api/queue');
    return data;
  };

  // Configuration
  const getConfig = async () => {
    const { data } = await api.get('/api/config');
    return data;
  };

  const updateConfig = async (config) => {
    const formData = new FormData();
    if (config.omdb_api_key) formData.append('omdb_api_key', config.omdb_api_key);
    if (config.tmdb_api_key) formData.append('tmdb_api_key', config.tmdb_api_key);
    const { data } = await api.post('/api/config', formData);
    return data;
  };

  // Content Management
  const getContent = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/api/content', {
        retry: 2,
        timeout: 30000
      });
      
      if (!data || typeof data !== 'object') {
        throw new Error('Resposta inválida do servidor');
      }

      const result = {
        movies: data.movies?.map(movie => ({
          title: movie.title || '',
          file: movie.file || '',
          url: movie.url || ''
        })) || [],
        series: {}
      };

      if (data.series && typeof data.series === 'object') {
        Object.entries(data.series).forEach(([seriesName, seasons]) => {
          result.series[seriesName] = {};
          Object.entries(seasons).forEach(([seasonName, episodes]) => {
            result.series[seriesName][seasonName] = episodes?.map(episode => ({
              title: episode.title || '',
              file: episode.file || '',
              url: episode.url || ''
            })) || [];
          });
        });
      }
      
      setError(null);
      return result;
      
    } catch (err) {
      const errorMessage = err.code === 'ECONNABORTED'
        ? 'Tempo limite excedido. Tente novamente.'
        : err.response?.data?.error || 'Erro ao carregar conteúdo';
      
      setError(errorMessage);
      console.error('Erro ao carregar conteúdo:', err);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const deleteMovie = async (filename) => {
    try {
      const { data } = await api.delete(`/api/content/movies/${filename}`);
      return data;
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao deletar filme');
      throw err;
    }
  };

  const deleteEpisode = async (series, season, filename) => {
    try {
      const { data } = await api.delete(`/api/content/series/${series}/${season}/${filename}`);
      return data;
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao deletar episódio');
      throw err;
    }
  };

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const { data } = await api.get('/api/stats', {
        timeout: 5000 // timeout específico para esta chamada
      });
      
      // Validação dos dados retornados
      return {
        movies: parseInt(data.movies) || 0,
        series: parseInt(data.series) || 0,
        total: parseInt(data.total) || 0
      };
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Erro ao carregar estatísticas';
      setError(errorMessage);
      console.error('Erro ao buscar estatísticas:', errorMessage);
      
      // Retorna objeto com valores zerados em caso de erro
      return {
        movies: 0,
        series: 0,
        total: 0,
        error: errorMessage
      };
    } finally {
      setLoading(false);
    }
  };

  const getFormats = async () => {
    try {
      const { data } = await api.get('/api/media/formats');
      return data;
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao carregar formatos');
      throw err;
    }
  };

  return {
    loading,
    error,
    analyzeUrl,
    createStrm,
    deleteStrm,
    processUrl,
    processFile,
    getQueue,
    getConfig,
    updateConfig,
    getContent,
    deleteMovie,
    deleteEpisode,
    fetchStats,
    getFormats
  };
}
