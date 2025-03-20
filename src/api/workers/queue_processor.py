import asyncio
import logging
from typing import Optional, Dict

class QueueProcessor:
    def __init__(self, services: Dict):
        self.services = services
        self.queue_manager = services["queue_manager"]
        self.video_handler = services["video_handler"]
        self.app_controller = services["app_controller"]
        self.running = False
        self.current_task: Optional[asyncio.Task] = None
        
        # Configurar diretórios do VideoHandler
        media_paths = self.app_controller.get_media_paths()
        self.video_handler.directories = media_paths
        
    async def start(self):
        """Inicia o processador de fila"""
        if self.running:
            return
            
        self.running = True
        cleanup_counter = 0
        
        while self.running:
            try:
                # Processa itens pendentes
                await self.queue_manager.process_queue(self.video_handler)
                
                # Limpa itens antigos a cada 24 horas
                cleanup_counter += 1
                if cleanup_counter >= (24 * 60 * 12):  # 12 checks por minuto = 24h
                    self.queue_manager.cleanup_old_items()
                    cleanup_counter = 0
                
                # Aguarda 5 segundos antes de verificar novamente
                await asyncio.sleep(5)
            except Exception as e:
                logging.error(f"Erro no processador de fila: {str(e)}")
                await asyncio.sleep(10)  # Aguarda mais tempo em caso de erro
                
    async def stop(self):
        """Para o processador de fila"""
        self.running = False
        if self.current_task:
            self.current_task.cancel()
            try:
                await self.current_task
            except asyncio.CancelledError:
                pass
