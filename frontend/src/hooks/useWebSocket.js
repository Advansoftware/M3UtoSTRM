import { useEffect, useRef, useState, useCallback } from 'react';

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [queueStatus, setQueueStatus] = useState([]);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const connect = useCallback(() => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${process.env.NEXT_PUBLIC_API_URL.replace('http://', '')}/ws`;
      
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        console.log('WebSocket conectado');
        setIsConnected(true);
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
      };

      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'queue_status') {
          setQueueStatus(data.data);
        } else if (data.type === 'progress') {
          setQueueStatus(prev => prev.map(item => 
            item.id === data.data.item_id 
              ? { ...item, progress: data.data.progress, status: data.data.status }
              : item
          ));
        }
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket desconectado, tentando reconectar...');
        setIsConnected(false);
        reconnectTimeoutRef.current = setTimeout(connect, 3000);
      };

    } catch (error) {
      console.error('Erro ao conectar WebSocket:', error);
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  return { isConnected, queueStatus };
}
