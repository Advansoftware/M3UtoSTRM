from fastapi import FastAPI, UploadFile, File, Form, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from ..services.queue_manager import QueueManager
from ..services.video_handler import VideoHandler
from ..services.playlist_manager import PlaylistManager
from ..services.media_info import MediaInfo
from ..services.config_manager import ConfigManager
import asyncio
from typing import Dict, Set, Optional
import os
from dotenv import load_dotenv

load_dotenv()

config_manager = ConfigManager()
app = FastAPI(title="M3UtoSTRM API")
queue_manager = QueueManager()
connected_clients: Set[WebSocket] = set()

# Configurar CORS permitindo o Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

playlist_manager = PlaylistManager()
media_info = MediaInfo(
    omdb_api_key=config_manager.get('omdb_api_key'),
    tmdb_api_key=config_manager.get('tmdb_api_key')
)

async def broadcast_progress(item_id: str, progress: float, status: str):
    queue_manager.update_progress(item_id, progress, status)
    message = {
        "type": "progress",
        "data": {
            "item_id": item_id,
            "progress": progress,
            "status": status
        }
    }
    for client in connected_clients:
        try:
            await client.send_json(message)
        except:
            connected_clients.remove(client)

video_handler = VideoHandler(
    progress_callback=lambda item_id, progress, status: asyncio.create_task(broadcast_progress(item_id, progress, status))
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        # Envia status inicial da fila
        await websocket.send_json({
            "type": "queue_status",
            "data": queue_manager.get_queue_status()
        })
        
        while True:
            await websocket.receive_text()  # Mantém conexão ativa
    except:
        connected_clients.remove(websocket)

@app.get("/api/health")
async def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return {"status": "online"}

@app.get("/api/queue")
async def get_queue():
    return queue_manager.get_queue_status()

# Atualizar rotas existentes para usar a fila
@app.post("/api/process-url")
async def process_url(
    url: str = Form(...),
    custom_command: Optional[str] = Form(None)
):
    try:
        unique_id = video_handler.generate_random_string()
        input_path = os.path.join(video_handler.UPLOAD_FOLDER, f"downloaded_{unique_id}.mp4")
        output_path = os.path.join(video_handler.PROCESSED_FOLDER, f"processed_{unique_id}.mp4")

        item_id = queue_manager.add_item(f"URL: {url}")

        # Download e processamento em background
        async def process():
            if not video_handler.download_video(url, input_path, item_id):
                queue_manager.complete_item(item_id, error="Falha ao baixar o vídeo")
                return

            if not video_handler.process_video(input_path, output_path, custom_command, item_id):
                queue_manager.complete_item(item_id, error="Falha ao processar o vídeo")
                return

            queue_manager.complete_item(item_id)

        asyncio.create_task(process())

        return {"item_id": item_id}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/api/process-file")
async def process_file(
    file: UploadFile = File(...),
    custom_command: Optional[str] = Form(None)
):
    try:
        unique_id = video_handler.generate_random_string()
        sanitized_filename = video_handler.sanitize_filename(file.filename)
        input_path = os.path.join(video_handler.UPLOAD_FOLDER, f"{unique_id}_{sanitized_filename}")
        output_path = os.path.join(video_handler.PROCESSED_FOLDER, f"processed_{unique_id}_{sanitized_filename}")

        item_id = queue_manager.add_item(f"File: {sanitized_filename}")

        # Salvar arquivo e processamento em background
        async def process():
            with open(input_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            if not video_handler.process_video(input_path, output_path, custom_command, item_id):
                queue_manager.complete_item(item_id, error="Falha ao processar o vídeo")
                return

            queue_manager.complete_item(item_id)

        asyncio.create_task(process())

        return {"item_id": item_id}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/api/video-info/{video_id}")
async def get_video_info(video_id: str):
    try:
        video_path = os.path.join(video_handler.HOST_VIDEOS, video_id)
        if not os.path.exists(video_path):
            return JSONResponse(
                status_code=404,
                content={"error": "Vídeo não encontrado"}
            )

        duration = video_handler.get_video_duration(video_path)
        return {
            "duration": duration,
            "path": f"/host_videos/{video_id}"
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/api/analyze-url")
async def analyze_url(url: str = Form(...)):
    """Analisa URL e retorna informações sobre o conteúdo"""
    try:
        result = playlist_manager.analyze_url(url)
        
        # Adicionar metadata para cada item
        if result['type'] == 'playlist':
            for item in result['items']:
                metadata = await media_info.search_title(item['title'])
                if metadata:
                    item['metadata'] = metadata
        
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/api/create-strm")
async def create_strm(url: str = Form(...), title: str = Form(...)):
    """Cria arquivo STRM para URL"""
    try:
        strm_path = playlist_manager.create_strm(url, title)
        return {"path": strm_path}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.delete("/api/strm/{filename}")
async def delete_strm(filename: str):
    """Remove arquivo STRM após download"""
    path = os.path.join(playlist_manager.STRM_FOLDER, filename)
    if playlist_manager.delete_strm(path):
        return {"status": "success"}
    return JSONResponse(
        status_code=404,
        content={"error": "Arquivo não encontrado"}
    )

@app.post("/api/config")
async def update_config(
    omdb_api_key: Optional[str] = Form(None),
    tmdb_api_key: Optional[str] = Form(None)
):
    """Atualiza as configurações da API"""
    if omdb_api_key:
        config_manager.set('omdb_api_key', omdb_api_key)
    if tmdb_api_key:
        config_manager.set('tmdb_api_key', tmdb_api_key)
    
    # Recriar o serviço de media info com as novas chaves
    global media_info
    media_info = MediaInfo(
        omdb_api_key=config_manager.get('omdb_api_key'),
        tmdb_api_key=config_manager.get('tmdb_api_key')
    )
    
    return {"status": "success"}

@app.get("/api/config")
async def get_config():
    """Retorna as configurações atuais"""
    return {
        "omdb_api_key": config_manager.get('omdb_api_key'),
        "tmdb_api_key": config_manager.get('tmdb_api_key')
    }
