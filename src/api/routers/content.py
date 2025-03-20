from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, List
import os
import asyncio
from datetime import datetime, timedelta
from ..core.settings import initialize_services
import aiofiles
from functools import lru_cache
import logging

router = APIRouter()
services = initialize_services()
app_controller = services["app_controller"]

# Cache para armazenar resultados
content_cache = {
    'data': None,
    'last_update': None,
    'updating': False
}

CACHE_DURATION = timedelta(minutes=5)
LOCK = asyncio.Lock()  # Adicionar lock para evitar atualizações simultâneas

async def read_file_content(filepath: str) -> str:
    """Lê conteúdo do arquivo de forma assíncrona"""
    try:
        async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
            return await f.read()
    except Exception as e:
        logging.error(f"Erro ao ler arquivo {filepath}: {str(e)}")
        return None

@lru_cache(maxsize=100)
def get_cached_url(filepath: str) -> str:
    """Cache para URLs já lidas"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        return None

async def scan_directory(base_path: str, is_movie: bool = True) -> List[Dict]:
    """Escaneia diretório de forma assíncrona"""
    results = []
    if not os.path.exists(base_path):
        return results

    tasks = []
    for file in os.listdir(base_path):
        if file.endswith('.strm'):
            filepath = os.path.join(base_path, file)
            if is_movie:
                results.append({
                    "title": os.path.splitext(file)[0],
                    "file": file,
                    "url": get_cached_url(filepath)
                })
            else:
                tasks.append(read_file_content(filepath))

    if not is_movie and tasks:
        urls = await asyncio.gather(*tasks)
        for file, url in zip(os.listdir(base_path), urls):
            if url:
                results.append({
                    "title": os.path.splitext(file)[0],
                    "file": file,
                    "url": url
                })

    return results

async def update_cache():
    """Atualiza cache de forma assíncrona"""
    if content_cache['updating']:
        return content_cache['data']
    
    async with LOCK:  # Usar lock para evitar múltiplas atualizações
        try:
            if (not content_cache['last_update'] or 
                datetime.now() - content_cache['last_update'] > CACHE_DURATION):
                
                content_cache['updating'] = True
                
                movies_dir = os.path.abspath(app_controller.get("movies_dir"))
                series_dir = os.path.abspath(app_controller.get("series_dir"))
                
                # Criar diretórios se não existirem
                os.makedirs(movies_dir, exist_ok=True)
                os.makedirs(series_dir, exist_ok=True)
                
                # Executa scan em paralelo
                movies = await scan_directory(movies_dir, True)
                series = {}
                
                if os.path.exists(series_dir):
                    series_tasks = []
                    for series_name in os.listdir(series_dir):
                        series_path = os.path.join(series_dir, series_name)
                        if os.path.isdir(series_path):
                            series[series_name] = {}
                            for season in os.listdir(series_path):
                                season_path = os.path.join(series_path, season)
                                if os.path.isdir(season_path):
                                    series_tasks.append((
                                        series_name,
                                        season,
                                        scan_directory(season_path, False)
                                    ))
                    
                    # Executa todas as tasks de séries em paralelo
                    if series_tasks:
                        results = await asyncio.gather(*(task[2] for task in series_tasks))
                        for (series_name, season, _), episodes in zip(series_tasks, results):
                            if episodes:
                                series[series_name][season] = episodes
                
                content_cache['data'] = {
                    'movies': movies,
                    'series': series
                }
                content_cache['last_update'] = datetime.now()
                
        finally:
            content_cache['updating'] = False
            
        return content_cache['data']

@router.get("")
async def get_content(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    force_refresh: bool = False
):
    """Lista conteúdo processado com paginação e cache"""
    try:
        # Se force_refresh, limpa o cache
        if force_refresh:
            content_cache['last_update'] = None
        
        # Obtém dados do cache ou atualiza
        data = await update_cache()
        
        if not data:
            return {
                'movies': [],
                'series': {},
                'pagination': {
                    'total': 0,
                    'page': page,
                    'limit': limit,
                    'pages': 0
                },
                'cache_age': 0
            }

        # Filtra por busca se necessário
        if search:
            search = search.lower()
            filtered_movies = [
                m for m in data['movies'] 
                if search in m['title'].lower()
            ]
            filtered_series = {
                name: seasons
                for name, seasons in data['series'].items()
                if search in name.lower()
            }
        else:
            filtered_movies = data['movies']
            filtered_series = data['series']

        # Calcula paginação
        total_movies = len(filtered_movies)
        total_pages = (total_movies + limit - 1) // limit
        page = min(max(1, page), total_pages) if total_pages > 0 else 1
        
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        return {
            'movies': filtered_movies[start_idx:end_idx],
            'series': filtered_series,
            'pagination': {
                'total': total_movies,
                'page': page,
                'limit': limit,
                'pages': total_pages
            },
            'cache_age': (datetime.now() - content_cache['last_update']).seconds if content_cache['last_update'] else None
        }

    except Exception as e:
        logging.error(f"Erro ao listar conteúdo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
