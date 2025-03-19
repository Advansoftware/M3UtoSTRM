from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class QueueItem:
    id: str
    filename: str
    status: str
    progress: float
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

class QueueManager:
    def __init__(self):
        self.queue: Dict[str, QueueItem] = {}
        
    def add_item(self, filename: str) -> str:
        item_id = str(uuid.uuid4())
        self.queue[item_id] = QueueItem(
            id=item_id,
            filename=filename,
            status="pending",
            progress=0.0,
            created_at=datetime.now()
        )
        return item_id
        
    def update_progress(self, item_id: str, progress: float, status: str = None):
        if item_id in self.queue:
            self.queue[item_id].progress = progress
            if status:
                self.queue[item_id].status = status
                
    def complete_item(self, item_id: str, error: str = None):
        if item_id in self.queue:
            self.queue[item_id].completed_at = datetime.now()
            self.queue[item_id].status = "error" if error else "completed"
            if error:
                self.queue[item_id].error = error
                
    def get_queue_status(self) -> List[Dict]:
        return [
            {
                "id": item.id,
                "filename": item.filename,
                "status": item.status,
                "progress": item.progress,
                "created_at": item.created_at.isoformat(),
                "completed_at": item.completed_at.isoformat() if item.completed_at else None,
                "error": item.error
            }
            for item in self.queue.values()
        ]
