import json
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str = './config.json'):
        self.config_path = os.path.abspath(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {
            "m3u_url": "",
            "m3u_file": "",
            "use_file": False,
            "movies_dir": "iptv/filmes",
            "series_dir": "iptv/series",
            "tmdb_api_key": "",
            "omdb_api_key": "",
            "process_movies": False,
            "process_series": True
        }

    def save_config(self) -> None:
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.config[key] = value
        self.save_config()
