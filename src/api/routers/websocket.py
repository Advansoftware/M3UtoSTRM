from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from ..core.websocket import connected_clients, broadcast_queue_status
from ..core.settings import initialize_services
import logging
import json
from starlette.websockets import WebSocketState

router = APIRouter()
services = initialize_services()
queue_manager = services["queue_manager"]

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket principal"""
    try:
        # Aceitar conexão
        await websocket.accept()
        connected_clients.add(websocket)
        logging.info("Nova conexão WebSocket estabelecida")

        try:
            # Enviar status inicial
            await websocket.send_json({
                "type": "queue_status",
                "data": queue_manager.get_queue_status()
            })

            # Loop de mensagens
            while True:
                try:
                    # Aguardar mensagem
                    message = await websocket.receive_json()

                    if message.get("type") == "get_status":
                        await websocket.send_json({
                            "type": "queue_status",
                            "data": queue_manager.get_queue_status()
                        })
                    elif message.get("type") == "cancel_item":
                        item_id = message.get("item_id")
                        if item_id:
                            # Corrigido para aguardar a coroutine
                            await queue_manager.cancel_item(item_id)
                            await broadcast_queue_status(queue_manager)

                except WebSocketDisconnect:
                    logging.info("Cliente WebSocket desconectado")
                    break
                except json.JSONDecodeError:
                    logging.warning("Mensagem WebSocket inválida recebida")
                    continue
                except Exception as e:
                    logging.error(f"Erro no processamento de mensagem: {str(e)}")
                    break

        except Exception as e:
            logging.error(f"Erro no loop de mensagens: {str(e)}")

    except Exception as e:
        logging.error(f"Erro na inicialização do WebSocket: {str(e)}")

    finally:
        # Limpeza ao desconectar
        if websocket in connected_clients:
            connected_clients.remove(websocket)
            logging.info("Cliente removido da lista de conexões")
