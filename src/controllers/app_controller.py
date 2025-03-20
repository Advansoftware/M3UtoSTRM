import json
import os
import logging
from typing import Dict, Any
from ..models.m3u_processor import M3UProcessor

class AppController:
    def __init__(self):
        self.config_file = "config.json"
        self.processor = M3UProcessor()
        self.config = self.load_config()
        self.is_cancelled = False

    def load_config(self) -> Dict[str, Any]:
        """Carrega configuração do arquivo config.json ou cria uma nova"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                # Merge com configurações padrão
                return {**self.get_default_config(), **user_config}
        return self.get_default_config()

    def get_default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão"""
        return {
            # Configurações da GUI
            "m3u_url": "",
            "m3u_file": "",
            "use_file": False,
            "process_movies": True,
            "process_series": True,

            # APIs
            "tmdb_api_key": "",
            "omdb_api_key": "",

            # Diretórios
            "movies_dir": "iptv/filmes",
            "series_dir": "iptv/series",
            "download_dir": "downloads",
            "processed_dir": "processed",
            "temp_dir": "temp",

            # FFmpeg
            "ffmpeg": {
                "video_codec": "libx264",
                "audio_codec": "aac",
                "video_bitrate": "2000k",
                "audio_bitrate": "128k",
                "preset": "medium",
            },

            # Opções de Download
            "download": {
                "max_quality": "1080p",
                "preferred_format": "mp4",
                "max_retries": 3
            }
        }

    def save_config(self) -> None:
        """Salva configuração atual no arquivo"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Define valor de configuração e salva"""
        self.config[key] = value
        self.save_config()

    def update(self, updates: Dict[str, Any]) -> None:
        """Atualiza múltiplas configurações"""
        self.config.update(updates)
        self.save_config()

    def get_path(self, key: str) -> str:
        """Retorna caminho absoluto para diretório"""
        path = self.get(key, "")
        if not os.path.isabs(path):
            # Usar o diretório atual como base
            return os.path.abspath(path)
        return path

    def ensure_directories(self) -> None:
        """Cria diretórios necessários"""
        for dir_key in ["movies_dir", "series_dir", "download_dir", "processed_dir", "temp_dir"]:
            path = self.get_path(dir_key)
            try:
                os.makedirs(path, exist_ok=True)
                logging.info(f"Diretório criado/verificado: {path}")
            except Exception as e:
                logging.error(f"Erro ao criar diretório {path}: {str(e)}")

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

    def cleanup_temp_files(self) -> None:
        """Limpa arquivos temporários"""
        if os.path.exists(self.config["temp_dir"]):
            for file in os.listdir(self.config["temp_dir"]):
                try:
                    os.remove(os.path.join(self.config["temp_dir"], file))
                except:
                    pass
