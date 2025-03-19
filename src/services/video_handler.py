import os
import re
import logging
import random
import string
import shutil
import subprocess
from unidecode import unidecode
from typing import Optional

class VideoHandler:
    def __init__(self, upload_folder: str = './uploads', 
                 processed_folder: str = './processed',
                 host_videos: str = './host_videos',
                 progress_callback=None):
        self.progress_callback = progress_callback
        self.UPLOAD_FOLDER = os.path.abspath(upload_folder)
        self.PROCESSED_FOLDER = os.path.abspath(processed_folder)
        self.HOST_VIDEOS = os.path.abspath(host_videos)
        
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(self.PROCESSED_FOLDER, exist_ok=True)
        os.makedirs(self.HOST_VIDEOS, exist_ok=True)

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

    def download_video(self, url: str, input_path: str, item_id: str = None) -> bool:
        download_command = f"yt-dlp --no-check-certificate --format best -o {input_path} {url}"
        
        try:
            process = subprocess.Popen(
                download_command, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            
            for line in process.stdout:
                if 'download' in line:
                    match = re.search(r'(\d+(\.\d+)?)%\s+of', line)
                    if match and self.progress_callback and item_id:
                        progress = float(match.group(1))
                        self.progress_callback(item_id, progress, "downloading")
                        
            process.wait()
            return process.returncode == 0
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Erro ao baixar o vídeo: {str(e)}")
            return False

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
                shutil.copy2(output_path, os.path.join(self.HOST_VIDEOS, os.path.basename(output_path)))
                os.remove(output_path)
                return True
                
            return False
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Erro ao processar vídeo: {str(e)}")
            return False
