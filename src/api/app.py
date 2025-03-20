from fastapi import FastAPI, UploadFile, File, Form, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import os
import sys
from ..services.queue_manager import QueueManager
from ..services.video_handler import VideoHandler
from ..services.playlist_manager import PlaylistManager
from ..services.media_info import MediaInfo
from ..services.config_manager import ConfigManager
from ..controllers.app_controller import AppController
import asyncio
from typing import Dict, Set, Optional, List
from math import ceil
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app_controller = AppController()

# Usar caminhos absolutos dos diretórios
MOVIES_DIR = os.path.abspath(app_controller.get("movies_dir"))
SERIES_DIR = os.path.abspath(app_controller.get("series_dir"))
DOWNLOAD_DIR = app_controller.get_path("download_dir")
PROCESSED_DIR = app_controller.get_path("processed_dir")
TEMP_DIR = app_controller.get_path("temp_dir")

# Configurar serviços com APIs do config.json
media_info = MediaInfo(
    omdb_api_key=app_controller.get("omdb_api_key"),
    tmdb_api_key=app_controller.get("tmdb_api_key")
)

# Inicializar VideoHandler com as configurações
video_handler = VideoHandler(
    progress_callback=lambda item_id, progress, status: 
        asyncio.create_task(broadcast_progress(item_id, progress, status)),
    ffmpeg_options=app_controller.get("ffmpeg", {}),
    download_options=app_controller.get("download", {})
)

app = FastAPI(title="M3UtoSTRM API")
queue_manager = QueueManager()
connected_clients: Set[WebSocket] = set()

# Determinar o caminho do frontend
if getattr(sys, 'frozen', False):
    # Executando como executável
    frontend_path = os.path.join(sys._MEIPASS, 'frontend', 'dist')
else:
    # Executando como script
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frontend', 'dist')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar CORS permitindo o Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

playlist_manager = PlaylistManager()

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
    """Retorna as configurações do arquivo config.json"""
    return app_controller.config

@app.get("/api/server-url")
async def get_server_url():
    """Retorna a URL do servidor"""
    port = os.getenv("PORT", "8000")
    return {"url": f"http://localhost:{port}"}

@app.get("/api/content")
async def get_content(page: int = 1, limit: int = 20, search: Optional[str] = None):
    """Lista arquivos STRM processados com paginação"""
    try:
        logger.info(f"Buscando conteúdo: page={page}, limit={limit}, search={search}")
        
        content = {
            "movies": [],
            "series": {},
            "pagination": {
                "total": 0,
                "pages": 0,
                "current": page,
                "limit": limit
            }
        }
        
        all_movies = []
        
        # Lista filmes
        if os.path.exists(MOVIES_DIR):
            logger.info(f"Buscando filmes em: {MOVIES_DIR}")
            try:
                for file in os.listdir(MOVIES_DIR):
                    if file.endswith('.strm'):
                        file_path = os.path.join(MOVIES_DIR, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                url = f.read().strip()
                            movie = {
                                "title": os.path.splitext(file)[0],
                                "file": file,
                                "url": url
                            }
                            if not search or search.lower() in movie["title"].lower():
                                all_movies.append(movie)
                        except Exception as e:
                            logger.error(f"Erro ao ler arquivo {file_path}: {str(e)}")
            except Exception as e:
                logger.error(f"Erro ao listar diretório {MOVIES_DIR}: {str(e)}")
                raise

        # Lista séries
        if os.path.exists(SERIES_DIR):
            content["series"] = {}
            for series in os.listdir(SERIES_DIR):
                if not search or search.lower() in series.lower():
                    series_path = os.path.join(SERIES_DIR, series)
                    if os.path.isdir(series_path):
                        content["series"][series] = {}
                        for season in os.listdir(series_path):
                            season_path = os.path.join(series_path, season)
                            if os.path.isdir(season_path):
                                content["series"][series][season] = []
                                for episode in os.listdir(season_path):
                                    if episode.endswith('.strm'):
                                        try:
                                            with open(os.path.join(season_path, episode), 'r', encoding='utf-8') as f:
                                                url = f.read().strip()
                                            content["series"][series][season].append({
                                                "title": os.path.splitext(episode)[0],
                                                "file": episode,
                                                "url": url
                                            })
                                        except Exception as e:
                                            logger.error(f"Erro ao ler episódio {episode}: {str(e)}")

        # Calcular paginação para filmes
        total_movies = len(all_movies)
        total_pages = ceil(total_movies / limit)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        content["movies"] = all_movies[start_idx:end_idx]
        content["pagination"].update({
            "total": total_movies,
            "pages": total_pages
        })

        logger.info(f"Conteúdo encontrado: {len(content['movies'])} filmes")
        return content

    except Exception as e:
        logger.error(f"Erro ao buscar conteúdo: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Erro ao buscar conteúdo: {str(e)}"}
        )

# Novos endpoints para conversão e download
@app.post("/api/media/convert")
async def convert_media(
    input_url: str = Form(...),
    format: str = Form(...),
    quality: str = Form("720p"),
    custom_options: Optional[str] = Form(None)
):
    """Converte mídia para o formato especificado"""
    try:
        item_id = queue_manager.add_item(f"Converting: {input_url}")
        
        async def process():
            try:
                output_path = os.path.join(
                    video_handler.PROCESSED_FOLDER, 
                    f"{video_handler.generate_random_string()}.{format}"
                )
                
                command = video_handler.build_convert_command(
                    input_url, 
                    output_path, 
                    format, 
                    quality, 
                    custom_options
                )
                
                success = await video_handler.run_conversion(command, item_id)
                if success:
                    queue_manager.complete_item(item_id)
                else:
                    queue_manager.complete_item(item_id, error="Falha na conversão")
            except Exception as e:
                queue_manager.complete_item(item_id, error=str(e))
        
        asyncio.create_task(process())
        return {"item_id": item_id}
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/api/media/download")
async def download_media(
    url: str = Form(...),
    format: Optional[str] = Form(None)
):
    """Download de mídia com formato opcional"""
    try:
        item_id = queue_manager.add_item(f"Downloading: {url}")
        
        async def process():
            try:
                output_path = os.path.join(
                    video_handler.DOWNLOAD_FOLDER,
                    f"{video_handler.generate_random_string()}"
                )
                if format:
                    output_path += f".{format}"
                
                success = await video_handler.download_with_progress(url, output_path, item_id)
                if success:
                    queue_manager.complete_item(item_id)
                else:
                    queue_manager.complete_item(item_id, error="Falha no download")
            except Exception as e:
                queue_manager.complete_item(item_id, error=str(e))
        
        asyncio.create_task(process())
        return {"item_id": item_id}
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/api/media/formats")
async def get_formats():
    """Lista formatos suportados"""
    return {
        "video": ["mp4", "mkv", "avi", "webm"],
        "audio": ["mp3", "aac", "wav", "ogg"],
        "quality": ["480p", "720p", "1080p", "2160p"]
    }

@app.delete("/api/content/movies/{filename}")
async def delete_movie(filename: str):
    """Remove um arquivo STRM de filme"""
    filepath = os.path.join(config_manager["movies_dir"], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return {"status": "success"}
    return {"status": "error", "message": "Arquivo não encontrado"}

@app.delete("/api/content/series/{series}/{season}/{filename}")
async def delete_episode(series: str, season: str, filename: str):
    """Remove um arquivo STRM de episódio"""
    filepath = os.path.join(config_manager["series_dir"], series, season, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return {"status": "success"}
    return {"status": "error", "message": "Arquivo não encontrado"}

@app.post("/api/queue/cancel")
async def cancel_queue_item(itemId: str = Form(...)):
    """Cancela um item da fila de processamento"""
    try:
        queue_manager.cancel_item(itemId)
        # Broadcast cancelamento para todos os clientes
        message = {
            "type": "item_cancelled",
            "data": {
                "item_id": itemId
            }
        }
        for client in connected_clients:
            try:
                await client.send_json(message)
            except:
                connected_clients.remove(client)
        return {"status": "success"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/api/stats")
async def get_stats():
    """Retorna estatísticas dos arquivos processados"""
    try:
        stats = {
            "movies": 0,
            "series": 0,
            "total": 0
        }
        
        logger.info(f"Buscando estatísticas em: {MOVIES_DIR} e {SERIES_DIR}")
        
        # Contagem de filmes
        if os.path.exists(MOVIES_DIR):
            movies_count = len([f for f in os.listdir(MOVIES_DIR) if f.endswith('.strm')])
            logger.info(f"Encontrados {movies_count} filmes")
            stats["movies"] = movies_count
        
        # Contagem de séries
        if os.path.exists(SERIES_DIR):
            series_count = len([d for d in os.listdir(SERIES_DIR) if os.path.isdir(os.path.join(SERIES_DIR, d))])
            logger.info(f"Encontradas {series_count} séries")
            stats["series"] = series_count
        
        stats["total"] = stats["movies"] + stats["series"]
        logger.info(f"Total: {stats['total']}")
        
        return stats
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Erro ao buscar estatísticas: {str(e)}"}
        )
