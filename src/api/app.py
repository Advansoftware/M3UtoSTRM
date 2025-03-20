from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from .routers import media, queue, config, content, websocket, stats
from .core.settings import setup_cors, initialize_services
from .workers.queue_processor import QueueProcessor
import asyncio

# Inicializar serviços primeiro
services = initialize_services()
app_controller = services["app_controller"]
# Garantir que os diretórios existam
app_controller.ensure_directories()

# Então criar o queue_processor
queue_processor = QueueProcessor(services)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código que roda na inicialização
    processor_task = asyncio.create_task(queue_processor.start())
    
    yield  # A aplicação roda aqui
    
    # Código que roda no desligamento
    queue_processor.running = False
    await queue_processor.stop()
    try:
        await processor_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="M3UtoSTRM API",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(media.router, prefix="/api/media", tags=["media"])
app.include_router(queue.router, prefix="/api/queue", tags=["queue"])
app.include_router(config.router, prefix="/api/config", tags=["config"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
