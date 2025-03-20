import os
import re
import logging
import random
import string
import shutil
import subprocess
import asyncio
from unidecode import unidecode
from typing import Optional

class VideoHandler:
    def __init__(self, progress_callback=None, ffmpeg_options=None, download_options=None):
        self.progress_callback = progress_callback
        self.ffmpeg_options = ffmpeg_options or {
            "video_codec": "libx264",
            "audio_codec": "aac",
            "video_bitrate": "2000k",
            "audio_bitrate": "128k",
            "preset": "medium"
        }
        self.download_options = download_options or {
            "max_quality": "1080p",
            "preferred_format": "mp4",
            "max_retries": 3
        }
        self._directories = None  # Inicializar atributo privado
        
    @property
    def directories(self):
        if self._directories is None:
            raise ValueError("Directories not configured")
        return self._directories
        
    @directories.setter
    def directories(self, dirs: dict):
        if not dirs:
            raise ValueError("Directories cannot be empty")
        if not all(key in dirs for key in ['download_dir', 'processed_dir', 'temp_dir']):
            raise ValueError("Missing required directories")
            
        self._directories = dirs
        # Criar diretórios se não existirem
        for path in dirs.values():
            if path:  # Verificar se o caminho não está vazio
                os.makedirs(path, exist_ok=True)

    def sanitize_filename(self, filename: str) -> str:
        return unidecode(filename).replace(" ", "_")

    def generate_random_string(self, length: int = 6) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def get_video_duration(self, input_path: str) -> Optional[str]:
        command = f"ffmpeg -i {input_path} 2>&1 | grep 'Duration' | awk '{{print $2}}' | tr -d ','"
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        return None

    def convert_time_to_percent(self, current_time: str, total_duration: str) -> float:
        current_parts = current_time.split(':')
        total_parts = total_duration.split(':')

        current_sec = sum(x * float(t) if '.' in t else x * int(t) 
                         for x, t in zip([3600, 60, 1], current_parts[:3]))
        total_sec = sum(x * float(t) if '.' in t else x * int(t) 
                       for x, t in zip([3600, 60, 1], total_parts[:3]))

        if '.' in current_parts[-1]:
            current_sec += float(f"0.{current_parts[-1].split('.')[1]}")
        else:
            current_sec += int(current_parts[-1])

        if '.' in total_parts[-1]:
            total_sec += float(f"0.{total_parts[-1].split('.')[1]}")
        else:
            total_sec += int(total_parts[-1])

        return (current_sec / total_sec) * 100

    def get_default_command(self, input_path: str, output_path: str) -> str:
        return f"ffmpeg -i {input_path} -vf scale=1920:1080 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 192k -movflags +faststart {output_path}"

    async def get_video_formats(self, url: str) -> dict:
        """Obtém formatos disponíveis para download"""
        try:
            command = [
                "yt-dlp",
                "--no-check-certificate",
                "-J",  # Saída em JSON
                url
            ]
            
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await process.communicate()
            
            if process.returncode == 0:
                import json
                video_data = json.loads(stdout)
                
                if 'formats' in video_data:
                    # Filtrar e organizar formatos
                    formats = []
                    unique_formats = set()  # Para evitar duplicatas

                    for f in video_data['formats']:
                        if 'height' in f and f['height'] and f['ext']:
                            format_key = f"{f['height']}p-{f['ext']}"
                            if format_key not in unique_formats:
                                unique_formats.add(format_key)
                                format_info = {
                                    'format_id': f['format_id'],
                                    'ext': f['ext'],
                                    'height': f['height'],
                                    'filesize': f.get('filesize', 0),
                                    'vcodec': f.get('vcodec', ''),
                                    'acodec': f.get('acodec', ''),
                                    'display': f"{f['height']}p - {f['ext'].upper()}"
                                }
                                formats.append(format_info)
                    
                    return {
                        'title': video_data.get('title', ''),
                        'formats': sorted(formats, key=lambda x: (x['height'], x['ext']), reverse=True),
                        'is_youtube': 'youtube' in video_data.get('extractor', '').lower()
                    }
            
            # Formato padrão se não for YouTube
            return {
                'title': 'Unknown',
                'formats': [{'format_id': 'best', 'height': 1080, 'ext': 'mp4'}],
                'is_youtube': False
            }
            
        except Exception as e:
            logging.error(f"Erro ao obter formatos: {str(e)}")
            return None

    async def download_video(self, url: str, output_path: str, format_id: str = 'best', item_id: str = None):
        """Download de vídeo com formato específico"""
        if not self.directories:
            raise ValueError("Diretórios não configurados")

        try:
            if not output_path.startswith(self.directories['download_dir']):
                output_path = os.path.join(self.directories['download_dir'], os.path.basename(output_path))

            download_command = [
                "yt-dlp",
                "--no-check-certificate",
                "-f", format_id,
                "--newline",
                "--progress-template", "[download] %(progress.downloaded_bytes)s/%(progress.total_bytes)s",
                "-o", output_path,
                url
            ]
            
            process = await asyncio.create_subprocess_exec(
                *download_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                while True:
                    if process.returncode is not None:  # Processo terminou
                        break

                    line = await process.stdout.readline()
                    if not line:
                        break

                    line = line.decode().strip()
                    if line.startswith('[download]'):
                        try:
                            parts = line.split()[1].split('/')
                            # Melhor tratamento para valores inválidos
                            try:
                                downloaded = int(parts[0]) if parts[0] and parts[0] != 'NA' else 0
                                total = int(parts[1]) if parts[1] and parts[1] != 'NA' else 100
                                progress = (downloaded / total) * 100 if total > 0 else 0
                            except (ValueError, IndexError):
                                logging.debug(f"Ignorando linha de progresso inválida: {line}")
                                continue
                            
                            logging.debug(f"Download progress: {progress}% for item {item_id}")
                            
                            if self.progress_callback and item_id:
                                await self.progress_callback(item_id, progress, "downloading")
                        except Exception as e:
                            logging.error(f"Erro ao processar progresso: {str(e)}")
                            continue

                await process.wait()
                return process, process.returncode == 0

            except asyncio.CancelledError:
                # Se o processo for cancelado, mata o processo e limpa o arquivo
                try:
                    process.terminate()  # Tenta terminar graciosamente
                    await asyncio.sleep(1)
                    if process.returncode is None:
                        process.kill()  # Força o término se necessário
                finally:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    return process, False

        except Exception as e:
            logging.error(f"Erro ao baixar vídeo: {str(e)}")
            if os.path.exists(output_path):
                os.remove(output_path)
            return None, False

    def process_video(self, input_path: str, output_path: str, custom_command: str = None, item_id: str = None) -> bool:
        try:
            command = custom_command or self.get_default_command(input_path, output_path)
            command = command.replace("{input}", input_path).replace("{output}", output_path)
            
            total_duration = self.get_video_duration(input_path)
            
            process = subprocess.Popen(
                command, 
                shell=True, 
                stderr=subprocess.PIPE, 
                text=True
            )
            
            for line in process.stderr:
                if 'time=' in line and total_duration:
                    match = re.search(r'time=(\d+:\d+:\d+\.\d+)', line)
                    if match and self.progress_callback and item_id:
                        current_time = match.group(1)
                        progress = self.convert_time_to_percent(current_time, total_duration)
                        self.progress_callback(item_id, progress, "processing")
            
            process.wait()
            
            if process.returncode == 0 and os.path.exists(output_path):
                shutil.copy2(output_path, os.path.join(self.directories['host_videos'], os.path.basename(output_path)))
                os.remove(output_path)
                return True
                
            return False
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Erro ao processar vídeo: {str(e)}")
            return False
