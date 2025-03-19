import os
from typing import List, Dict
import m3u8
import re
from urllib.parse import urlparse

class PlaylistManager:
    def __init__(self, strm_folder: str = './strm'):
        self.STRM_FOLDER = os.path.abspath(strm_folder)
        os.makedirs(self.STRM_FOLDER, exist_ok=True)

    def analyze_url(self, url: str) -> Dict:
        """Analisa URL e retorna informações sobre o tipo de conteúdo"""
        if self._is_playlist(url):
            return {
                "type": "playlist",
                "items": self._extract_playlist_items(url)
            }
        return {
            "type": "single",
            "format": self._detect_format(url),
            "url": url
        }

    def _is_playlist(self, url: str) -> bool:
        return url.endswith('.m3u') or url.endswith('.m3u8')

    def _detect_format(self, url: str) -> str:
        # Detecta formato do arquivo pela extensão ou headers
        ext = os.path.splitext(urlparse(url).path)[1].lower()
        return ext[1:] if ext else 'unknown'

    def _extract_playlist_items(self, url: str) -> List[Dict]:
        playlist = m3u8.load(url)
        items = []
        
        for segment in playlist.segments:
            items.append({
                "url": segment.uri,
                "format": self._detect_format(segment.uri),
                "duration": segment.duration,
                "title": self._extract_title(segment.uri)
            })
        
        return items

    def _extract_title(self, url: str) -> str:
        # Extrai título do arquivo da URL
        filename = os.path.basename(urlparse(url).path)
        return os.path.splitext(filename)[0]

    def create_strm(self, url: str, title: str) -> str:
        """Cria arquivo STRM e retorna o caminho"""
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
        strm_path = os.path.join(self.STRM_FOLDER, f"{safe_title}.strm")
        
        with open(strm_path, 'w') as f:
            f.write(url)
            
        return strm_path

    def delete_strm(self, strm_path: str) -> bool:
        """Remove arquivo STRM após download bem sucedido"""
        try:
            if os.path.exists(strm_path):
                os.remove(strm_path)
            return True
        except:
            return False
