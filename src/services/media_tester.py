import subprocess
import json
from typing import Dict, Optional, Tuple

class MediaTester:
    def __init__(self):
        self.ffprobe_path = "ffprobe"

    def test_media(self, url: str) -> Tuple[bool, Dict]:
        """Testa uma URL de mídia usando FFprobe.
        Returns:
            Tuple[bool, Dict]: (sucesso, informações da mídia)
        """
        try:
            command = [
                self.ffprobe_path,
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                url
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return False, {"error": "Erro ao analisar mídia"}
                
            media_info = json.loads(result.stdout)
            return True, self._parse_media_info(media_info)
            
        except subprocess.TimeoutExpired:
            return False, {"error": "Tempo limite excedido"}
        except Exception as e:
            return False, {"error": str(e)}

    def _parse_media_info(self, info: Dict) -> Dict:
        """Processa as informações da mídia para um formato mais amigável"""
        result = {
            "duration": info.get("format", {}).get("duration", "0"),
            "size": info.get("format", {}).get("size", "0"),
            "bitrate": info.get("format", {}).get("bit_rate", "0"),
            "streams": []
        }
        
        for stream in info.get("streams", []):
            stream_info = {
                "type": stream.get("codec_type", "unknown"),
                "codec": stream.get("codec_name", "unknown"),
                "language": stream.get("tags", {}).get("language", "unknown")
            }
            
            if stream.get("codec_type") == "video":
                stream_info.update({
                    "width": stream.get("width", 0),
                    "height": stream.get("height", 0),
                    "fps": stream.get("r_frame_rate", "0")
                })
            
            result["streams"].append(stream_info)
            
        return result
