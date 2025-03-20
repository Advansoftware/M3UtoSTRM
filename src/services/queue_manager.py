from typing import Dict, List, Optional, Deque
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid
import logging
from collections import deque
import asyncio
import os
import json

@dataclass
class QueueItem:
    id: str
    filename: str
    url: str  # Adicionando campo url
    format_id: str  # Adicionando campo format_id
    output_format: str  # Adicionando campo output_format
    status: str
    progress: float
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

class QueueManager:
    def __init__(self, broadcast_handlers=None):
        self.queue: Dict[str, QueueItem] = {}
        self.processing_queue: Deque[str] = deque()  # FIFO queue
        self.is_processing = False
        self.current_item = None
        self.processing_lock = asyncio.Lock()
        self.broadcast_handlers = broadcast_handlers or {}
        self.current_process = None  # Adicionar referência ao processo atual
        self.queue_file = os.path.join(os.path.dirname(__file__), "../data/queue.json")
        self.load_queue()
        
    async def _broadcast(self, event_type, data):
        """Modificar para ser async"""
        handler = self.broadcast_handlers.get(event_type)
        if handler and asyncio.iscoroutinefunction(handler):
            return handler(data)
        elif handler:
            return asyncio.create_task(handler(data))

    def load_queue(self):
        """Carrega fila do arquivo JSON"""
        try:
            if os.path.exists(self.queue_file):
                with open(self.queue_file, 'r') as f:
                    data = json.load(f)
                    for item_data in data.get('items', []):
                        # Converter strings de data para objetos datetime
                        if isinstance(item_data['created_at'], str):
                            item_data['created_at'] = datetime.fromisoformat(item_data['created_at'])
                        if item_data.get('completed_at') and isinstance(item_data['completed_at'], str):
                            item_data['completed_at'] = datetime.fromisoformat(item_data['completed_at'])
                            
                        # Atualizar status de itens interrompidos
                        if item_data['status'] in ['downloading', 'converting', 'pending']:
                            item_data['status'] = 'error'
                            item_data['error'] = 'Processo interrompido'
                            item_data['completed_at'] = datetime.now()
                            
                        self.queue[item_data['id']] = QueueItem(**item_data)
                        if item_data['status'] == 'pending':
                            self.processing_queue.append(item_data['id'])
                            
                logging.info(f"Fila carregada com {len(self.queue)} itens")
        except Exception as e:
            logging.error(f"Erro ao carregar fila: {str(e)}")
            self.queue = {}
            self.processing_queue = deque()

    def save_queue(self):
        """Salva fila no arquivo JSON"""
        try:
            # Criar diretório data se não existir
            os.makedirs(os.path.dirname(self.queue_file), exist_ok=True)
            
            # Cria estrutura de dados inicial se arquivo não existir
            if not os.path.exists(self.queue_file):
                initial_data = {
                    'items': [],
                    'lastUpdate': datetime.now().isoformat()
                }
                with open(self.queue_file, 'w') as f:
                    json.dump(initial_data, f, indent=2)
                logging.info(f"Arquivo de fila criado: {self.queue_file}")

            # Salva dados atuais
            data = {
                'items': [
                    {
                        'id': item.id,
                        'filename': item.filename,
                        'url': item.url,
                        'format_id': item.format_id,
                        'output_format': item.output_format,
                        'status': item.status,
                        'progress': item.progress,
                        'created_at': item.created_at.isoformat(),
                        'completed_at': item.completed_at.isoformat() if item.completed_at else None,
                        'error': item.error
                    }
                    for item in self.queue.values()
                ],
                'lastUpdate': datetime.now().isoformat()
            }
            
            with open(self.queue_file, 'w') as f:
                json.dump(data, f, indent=2)
            logging.debug("Fila salva com sucesso")
            
        except Exception as e:
            logging.error(f"Erro ao salvar fila: {str(e)}")

    async def add_item(self, filename: str, url: str, format_id: str, output_format: str) -> str:
        """Versão assíncrona do add_item"""
        item_id = str(uuid.uuid4())
        self.queue[item_id] = QueueItem(
            id=item_id,
            filename=filename,
            url=url,
            format_id=format_id,
            output_format=output_format,
            status="pending",
            progress=0.0,
            created_at=datetime.now()
        )
        self.processing_queue.append(item_id)
        logging.info(f"Item adicionado à fila: {filename} (ID: {item_id})")
        
        await self._broadcast('queue_status', self)
        self.save_queue()
        return item_id
        
    async def update_progress(self, item_id: str, progress: float, status: str = None):
        """Atualiza progresso de forma assíncrona"""
        if item_id in self.queue:
            self.queue[item_id].progress = progress
            if status:
                self.queue[item_id].status = status
            logging.debug(f"Progresso atualizado: {item_id} - {progress}% ({status})")
            
            # Garantir que o broadcast é assíncrono
            await self._broadcast('progress', {
                'item_id': item_id,
                'progress': progress,
                'status': status
            })
                
    async def complete_item(self, item_id: str, error: str = None):
        """Versão assíncrona do complete_item"""
        if item_id in self.queue:
            self.queue[item_id].completed_at = datetime.now()
            self.queue[item_id].status = "error" if error else "completed"
            if error:
                self.queue[item_id].error = error
            logging.info(f"Item completado: {item_id} {'com erro: ' + error if error else 'com sucesso'}")
            
            await self._broadcast('queue_status', self)
            self.save_queue()

    async def process_queue(self, video_handler):
        """Processa itens da fila em ordem FIFO"""
        async with self.processing_lock:
            if self.is_processing or not self.processing_queue:
                return

            self.is_processing = True
            try:
                item_id = self.processing_queue[0]
                item = self.queue[item_id]
                self.current_item = item_id

                try:
                    await self.update_progress(item_id, 0, "downloading")
                    output_path = os.path.join(
                        video_handler.directories['download_dir'],
                        f"{item.filename}.{item.output_format}"
                    )
                    
                    self.current_process, download_success = await video_handler.download_video(
                        url=item.url,
                        output_path=output_path,
                        format_id=item.format_id,
                        item_id=item_id
                    )
                    
                    if download_success:
                        await self.complete_item(item_id)
                    else:
                        await self.complete_item(item_id, error="Falha no download")
                        
                except Exception as e:
                    logging.error(f"Erro processando item {item_id}: {str(e)}")
                    await self.complete_item(item_id, error=str(e))
                finally:
                    self.processing_queue.popleft()
                    
            finally:
                self.is_processing = False
                self.current_item = None
                self.current_process = None

    async def cancel_item(self, item_id: str):
        """Cancela um item da fila e limpa arquivos"""
        if item_id in self.queue:
            item = self.queue[item_id]
            
            # Se for o item atual, mata o processo
            if item_id == self.current_item and self.current_process:
                try:
                    logging.info(f"Cancelando download do item {item_id}")
                    self.current_process.terminate()
                    await asyncio.sleep(0.5)
                    if self.current_process.returncode is None:
                        self.current_process.kill()
                    await self.current_process.wait()
                except Exception as e:
                    logging.error(f"Erro ao matar processo: {str(e)}")
                
            # Remove arquivos parciais
            try:
                output_path = os.path.join(
                    self.video_handler.directories['download_dir'],
                    f"{item.filename}.{item.output_format}"
                )
                if os.path.exists(output_path):
                    os.remove(output_path)
                    logging.info(f"Arquivo parcial removido: {output_path}")
            except Exception as e:
                logging.error(f"Erro ao remover arquivo: {str(e)}")

            # Atualiza status imediatamente
            item.status = "cancelled"
            item.progress = 0
            item.completed_at = datetime.now()
            
            # Remove da fila de processamento
            if item_id in self.processing_queue:
                self.processing_queue.remove(item_id)
            
            # Notifica clientes sobre o cancelamento
            await self._broadcast('progress', {
                'item_id': item_id,
                'progress': 0,
                'status': 'cancelled'
            })
            
            await self._broadcast('queue_status', self)
            self.save_queue()

    def cleanup_old_items(self, days: int = 7):
        """Remove itens antigos da fila"""
        cutoff = datetime.now() - timedelta(days=days)
        removed = []
        
        for item_id, item in list(self.queue.items()):
            if item.completed_at and datetime.fromisoformat(item.completed_at) < cutoff:
                del self.queue[item_id]
                removed.append(item_id)
        
        if removed:
            self.save_queue()
            logging.info(f"Removidos {len(removed)} itens antigos da fila")

    def get_queue_status(self) -> List[Dict]:
        return [
            {
                "id": item.id,
                "filename": item.filename,
                "url": item.url,
                "format_id": item.format_id,
                "output_format": item.output_format,
                "status": item.status,
                "progress": item.progress,
                "created_at": item.created_at.isoformat(),
                "completed_at": item.completed_at.isoformat() if item.completed_at else None,
                "error": item.error
            }
            for item in self.queue.values()
        ]
