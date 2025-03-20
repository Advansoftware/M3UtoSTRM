from fastapi import WebSocket, status
from typing import Set
import logging
from starlette.websockets import WebSocketState
import json

connected_clients: Set[WebSocket] = set()

async def safe_send(websocket: WebSocket, message: dict) -> bool:
    """Envia mensagem com tratamento de erro"""
    try:
        if websocket.client_state == WebSocketState.CONNECTED:
            logging.debug(f"Sending message: {message}")
            await websocket.send_text(json.dumps(message)) # Alterado para send_text
            return True
    except Exception as e:
        logging.error(f"Erro ao enviar mensagem: {str(e)}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except:
            pass
        return False

async def broadcast_message(message: dict):
    """Envia mensagem para todos os clientes conectados"""
    disconnected = set()
    
    for client in connected_clients:
        if not await safe_send(client, message):
            disconnected.add(client)
            
    # Remove clientes desconectados
    connected_clients.difference_update(disconnected)

async def broadcast_queue_status(queue_manager):
    """Envia status atual da fila para todos os clientes"""
    await broadcast_message({
        "type": "queue_status",
        "data": queue_manager.get_queue_status()
    })

async def broadcast_progress(item_id: str, progress: float, status: str):
    """Envia atualização de progresso para todos os clientes"""
    message = {
        "type": "progress",
        "data": {
            "item_id": item_id,
            "progress": round(progress, 2),  # Arredondar para 2 casas decimais
            "status": status
        }
    }
    logging.debug(f"Broadcasting progress: {message}")
    await broadcast_message(message)
