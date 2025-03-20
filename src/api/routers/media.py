from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import os
import asyncio
import logging
from ..core.settings import initialize_services

router = APIRouter()
services = initialize_services()
video_handler = services["video_handler"]
queue_manager = services["queue_manager"]

@router.post("/convert")
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

@router.post("/download")
async def download_media(
    url: str = Form(...),
    format_id: str = Form(...)
):
    """Download de mídia usando yt-dlp"""
    try:
        if not url or not format_id:
            raise HTTPException(
                status_code=400, 
                detail="URL e format_id são obrigatórios"
            )

        # Obtém informações do vídeo para determinar o formato correto
        video_info = await video_handler.get_video_formats(url)
        if not video_info:
            raise HTTPException(
                status_code=400, 
                detail="Não foi possível obter informações do vídeo"
            )

        # Encontra o formato correspondente
        selected_format = next(
            (f for f in video_info['formats'] if str(f['format_id']) == str(format_id)),
            None
        )
        if not selected_format:
            raise HTTPException(
                status_code=400, 
                detail=f"Formato {format_id} não disponível"
            )

        # Usa a extensão do formato selecionado
        output_format = selected_format['ext']
        
        # Usar versão assíncrona do add_item
        item_id = await queue_manager.add_item(
            filename=video_info.get('title', 'video'),
            url=url,
            format_id=format_id,
            output_format=output_format
        )
        
        # Inicia processamento da fila de forma assíncrona
        asyncio.create_task(queue_manager.process_queue(video_handler))
        
        return {
            "item_id": item_id,
            "filename": video_info.get('title', url),
            "status": "pending"
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Erro no download: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@router.get("/formats")
async def get_formats():
    """Lista formatos suportados"""
    return {
        "video": ["mp4", "mkv", "avi", "webm"],
        "audio": ["mp3", "aac", "wav", "ogg"],
        "quality": ["480p", "720p", "1080p", "2160p"]
    }

@router.get("/formats/{url:path}")
async def get_video_formats(url: str):
    """Obtém formatos disponíveis para uma URL"""
    try:
        formats = await video_handler.get_video_formats(url)
        if formats:
            return formats
        raise HTTPException(status_code=400, detail="Não foi possível obter os formatos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ... outras rotas relacionadas a media
