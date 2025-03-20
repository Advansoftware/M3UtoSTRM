from fastapi import APIRouter, Form
from ..core.settings import initialize_services

router = APIRouter()
services = initialize_services()
queue_manager = services["queue_manager"]

@router.get("/")
async def get_queue():
    """Retorna o status atual da fila"""
    return queue_manager.get_queue_status()

@router.post("/cancel")
async def cancel_queue_item(item_id: str = Form(...)):
    """Cancela um item da fila"""
    try:
        queue_manager.complete_item(item_id, error="Cancelled by user")
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
