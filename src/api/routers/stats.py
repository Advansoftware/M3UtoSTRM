from fastapi import APIRouter
from ..core.settings import initialize_services
import os
import logging

router = APIRouter()
services = initialize_services()
app_controller = services["app_controller"]

@router.get("")
async def get_stats():
    """Retorna estatísticas dos arquivos processados"""
    try:
        movies_dir = app_controller.get("movies_dir")
        series_dir = app_controller.get("series_dir")
        stats = {
            "movies": 0,
            "series": 0,
            "episodes": 0,
            "total_files": 0
        }
        
        # Contagem de filmes
        if os.path.exists(movies_dir):
            stats["movies"] = len([f for f in os.listdir(movies_dir) if f.endswith('.strm')])
        
        # Contagem de séries e episódios
        if os.path.exists(series_dir):
            series_count = 0
            episodes_count = 0
            
            for series in os.listdir(series_dir):
                series_path = os.path.join(series_dir, series)
                if os.path.isdir(series_path):
                    series_count += 1
                    for season in os.listdir(series_path):
                        season_path = os.path.join(series_path, season)
                        if os.path.isdir(season_path):
                            episodes_count += len([f for f in os.listdir(season_path) if f.endswith('.strm')])
            
            stats["series"] = series_count
            stats["episodes"] = episodes_count
        
        stats["total_files"] = stats["movies"] + stats["episodes"]
        
        return stats
        
    except Exception as e:
        logging.error(f"Erro ao buscar estatísticas: {str(e)}")
        return {"error": str(e)}
