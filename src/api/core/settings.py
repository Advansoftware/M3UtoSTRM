from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
from dotenv import load_dotenv
from .websocket import broadcast_progress, broadcast_queue_status

# Usar importações relativas
from ...services.video_handler import VideoHandler
from ...services.queue_manager import QueueManager
from ...services.media_info import MediaInfo
from ...controllers.app_controller import AppController

load_dotenv()

def setup_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def initialize_services():
    app_controller = AppController()
    
    # Garantir que os diretórios existam primeiro
    app_controller.ensure_directories()
    
    # Configurar VideoHandler com diretórios
    video_handler = VideoHandler(
        progress_callback=broadcast_progress,
        ffmpeg_options=app_controller.get("ffmpeg", {}),
        download_options=app_controller.get("download", {})
    )
    
    # Configurar diretórios do VideoHandler
    video_handler.directories = app_controller.get_media_paths()
    
    queue_manager = QueueManager(
        broadcast_handlers={
            'queue_status': lambda manager: broadcast_queue_status(manager),
            'progress': lambda data: broadcast_progress(
                data['item_id'], 
                data['progress'], 
                data['status']
            )
        }
    )
    
    media_info = MediaInfo(
        omdb_api_key=app_controller.get("omdb_api_key"),
        tmdb_api_key=app_controller.get("tmdb_api_key")
    )
    
    return {
        "app_controller": app_controller,
        "video_handler": video_handler,
        "queue_manager": queue_manager,
        "media_info": media_info
    }
