from fastapi import APIRouter, Form
from typing import Optional
from ..core.settings import initialize_services

router = APIRouter()
services = initialize_services()
app_controller = services["app_controller"]

@router.get("/")
async def get_config():
    """Retorna as configurações atuais"""
    return app_controller.config

@router.post("/")
async def update_config(
    omdb_api_key: Optional[str] = Form(None),
    tmdb_api_key: Optional[str] = Form(None)
):
    """Atualiza as configurações"""
    if omdb_api_key:
        app_controller.set("omdb_api_key", omdb_api_key)
    if tmdb_api_key:
        app_controller.set("tmdb_api_key", tmdb_api_key)
    return {"status": "success"}
