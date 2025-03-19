import json
import os
from typing import Dict, Any
from ..models.m3u_processor import M3UProcessor

class AppController:
    def __init__(self):
        self.config_file = "config.json"
        self.processor = M3UProcessor()
        self.config = self.load_config()
        self.is_cancelled = False

    def load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "m3u_url": "",
            "m3u_file": "",  # Novo campo para arquivo local
            "use_file": False,  # Flag para escolher entre URL e arquivo
            "movies_dir": "iptv/filmes",
            "series_dir": "iptv/series",
            "tmdb_api_key": "",
            "process_movies": True,
            "process_series": True
        }

    def save_config(self, config: Dict[str, Any]) -> None:
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

    def process_playlist(self, config: Dict[str, Any], callback=None) -> None:
        self.is_cancelled = False
        self.processor.tmdb_api_key = config["tmdb_api_key"]
        
        source = config["m3u_file"] if config["use_file"] else config["m3u_url"]
        lines = self.processor.load_m3u(source, not config["use_file"])
        
        if not lines:
            return

        def is_valid_item(line: str) -> bool:
            # Ignora linhas que contêm indicadores de canais de TV
            invalid_patterns = [
                "Canais |", 
                "HD", 
                "FHD", 
                "SD",
                "4K",
                "CHANNELS",
                "CHANNEL"
            ]
            return not any(pattern in line for pattern in invalid_patterns)

        total_valid_items = sum(1 for i in range(len(lines)) 
                              if lines[i].startswith("#EXTINF") and is_valid_item(lines[i]))

        processed = 0
        i = 0
        while i < len(lines) and not self.is_cancelled:
            if lines[i].startswith("#EXTINF"):
                if is_valid_item(lines[i]):  # Usa a mesma função para verificar
                    url = lines[i + 1] if i + 1 < len(lines) else ""
                    info = self.processor.extract_info(lines[i], url)
                    
                    if callback:
                        callback(info, processed, total_valid_items)
                        processed += 1

                    if info.is_series and config["process_series"]:
                        self.processor.create_strm(info, config["series_dir"])
                    elif not info.is_series and config["process_movies"]:
                        self.processor.create_strm(info, config["movies_dir"])
                i += 2
            else:
                i += 1

    def cancel_processing(self) -> None:
        self.is_cancelled = True

    def test_playlist_connection(self, url: str) -> tuple[bool, str]:
        """Testa a conexão com a playlist.
        Returns:
            tuple[bool, str]: (sucesso, mensagem)
        """
        return self.processor.test_connection(url)
