import os
import re
import requests
from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass
class M3UItem:
    title: str
    url: str
    logo: str = ""
    group: str = ""
    is_series: bool = False
    series_name: str = ""
    season: str = ""
    episode: str = ""

class M3UProcessor:
    def __init__(self, tmdb_api_key: str = ""):
        self.tmdb_api_key = tmdb_api_key

    def load_m3u(self, source: str, is_url: bool = True) -> Optional[List[str]]:
        if is_url:
            return self.download_m3u(source)
        return self.read_m3u_file(source)

    def read_m3u_file(self, filepath: str) -> Optional[List[str]]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().splitlines()
        except Exception:
            return None

    def download_m3u(self, url: str) -> Optional[List[str]]:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text.splitlines()
        except requests.RequestException:
            return None

    def extract_info(self, info_line: str, url: str = "") -> M3UItem:
        info: Dict[str, str] = {
            'url': url  # Adicionando url como parâmetro opcional
        }
        
        tvg_name_match = re.search(r'tvg-name="([^"]+)"', info_line)
        info['title'] = tvg_name_match.group(1) if tvg_name_match else ""
        
        tvg_logo_match = re.search(r'tvg-logo="([^"]+)"', info_line)
        info['logo'] = tvg_logo_match.group(1) if tvg_logo_match else ""
        
        group_match = re.search(r'group-title="([^"]+)"', info_line)
        info['group'] = group_match.group(1) if group_match else ""
        
        series_info = self._extract_series_info(info['title'])
        return M3UItem(**info, **series_info)

    def _extract_series_info(self, title: str) -> Dict[str, str]:
        if "S" in title and "E" in title:
            series_match = re.search(r'(.*?)\s*(S(\d+)E(\d+))', title)
            if series_match:
                return {
                    'series_name': series_match.group(1).strip(),
                    'season': series_match.group(3),
                    'episode': series_match.group(4),
                    'is_series': True
                }
        return {'is_series': False}

    def create_strm(self, item: M3UItem, base_dir: str) -> None:
        if item.is_series:
            self._create_series_strm(item, base_dir)
        else:
            self._create_movie_strm(item, base_dir)

    def _create_series_strm(self, item: M3UItem, base_dir: str) -> None:
        series_dir = os.path.join(base_dir, item.series_name)
        season_dir = os.path.join(series_dir, f"Season {item.season.zfill(2)}")
        os.makedirs(season_dir, exist_ok=True)
        
        filename = f"S{item.season.zfill(2)}E{item.episode.zfill(2)}.strm"
        filepath = os.path.join(season_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(item.url)

    def _create_movie_strm(self, item: M3UItem, base_dir: str) -> None:
        # Criar o diretório base se não existir
        os.makedirs(base_dir, exist_ok=True)
        
        safe_title = "".join(c for c in item.title if c.isalnum() or c in (' ', '-', '_'))
        filepath = os.path.join(base_dir, f"{safe_title}.strm")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(item.url)

    def test_connection(self, url: str) -> tuple[bool, str]:
        """Testa a conexão com a URL da playlist.
        Returns:
            tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            if not response.text.strip().startswith("#EXTM3U"):
                return False, "URL não retorna uma playlist M3U válida"
            return True, "Conexão estabelecida com sucesso"
        except requests.Timeout:
            return False, "Tempo limite de conexão excedido"
        except requests.ConnectionError:
            return False, "Erro de conexão com o servidor"
        except requests.RequestException as e:
            return False, f"Erro ao acessar a URL: {str(e)}"
