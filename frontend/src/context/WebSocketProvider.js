import { createContext, useEffect, useRef, useState, useCallback } from 'react';

let globalWs = null; // WebSocket singleton

export const WebSocketContext = createContext(null);

export function WebSocketProvider({ children }) {
  const [queueStatus, setQueueStatus] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const reconnectTimeout = useRef(null);
  const wsRef = useRef(null);
  const mountedRef = useRef(false);

  const connect = useCallback(() => {
    if (globalWs?.readyState === WebSocket.OPEN) {
      console.log('WebSocket já conectado');
      return () => {};
    }

    if (globalWs?.readyState === WebSocket.CONNECTING) {
      console.log('WebSocket conectando...');
      return () => {};
    }

    console.log('Iniciando nova conexão WebSocket');
    
    // Garantir que usamos ws:// em dev e wss:// em prod
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:8000/ws`;
    
    const ws = new WebSocket(wsUrl);
    globalWs = ws;
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket conectado');
      setIsConnected(true);
      ws.send(JSON.stringify({ type: 'get_status' }));
    };

    ws.onmessage = (event) => {
      if (!mountedRef.current) return;
      
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket mensagem recebida:', data);
        
        if (data.type === 'queue_status') {
          console.log('Atualizando status da fila:', data.data);
          setQueueStatus(data.data || []);
        } else if (data.type === 'progress') {
          console.log('Atualizando progresso:', data.data);
          setQueueStatus(prev => prev.map(item => 
            item.id === data.data.item_id
              ? { ...item, progress: data.data.progress, status: data.data.status }
              : item
          ));
        }
      } catch (error) {
        console.error('Erro ao processar mensagem:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket erro:', error);
      setIsConnected(false);
    };

    ws.onclose = (event) => {
      if (!mountedRef.current) return;
      
      console.log('WebSocket fechado:', event.code);
      setIsConnected(false);
      globalWs = null;

      if (event.code !== 1000 && mountedRef.current) {
        reconnectTimeout.current = setTimeout(connect, 5000);
      }
    };

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (ws.readyState === WebSocket.OPEN) {
        ws.close(1000);
      }
    };
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    
    // Conectar apenas se não houver conexão global ativa
    if (!globalWs || (globalWs.readyState !== WebSocket.OPEN && globalWs.readyState !== WebSocket.CONNECTING)) {
      connect();
    } else {
      // Se já existe conexão, apenas solicitar status atual
      if (globalWs.readyState === WebSocket.OPEN) {
        globalWs.send(JSON.stringify({ type: 'get_status' }));
      }
      setIsConnected(true);
    }

    return () => {
      mountedRef.current = false;
      clearTimeout(reconnectTimeout.current);
    };
  }, []);

  const cancelItem = useCallback((itemId) => {
    if (globalWs?.readyState === WebSocket.OPEN) {
      globalWs.send(JSON.stringify({
        type: 'cancel_item',
        item_id: itemId
      }));
    }
  }, []);

  return (
    <WebSocketContext.Provider value={{ queueStatus, cancelItem, isConnected }}>
      {children}
    </WebSocketContext.Provider>
  );
}
