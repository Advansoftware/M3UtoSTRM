import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import requests
from urllib.parse import unquote
import threading
from .media_tester import MediaTester

class ProxyServer:
    def __init__(self, host="127.0.0.1", port=55950):
        self.host = host
        self.port = port
        self.app = FastAPI()
        self.server = None
        self.media_tester = MediaTester()
        self.setup_routes()

    def setup_routes(self):
        @self.app.get("/status")
        async def status():
            return JSONResponse({"status": "active"})

        @self.app.get("/proxy")
        async def proxy(url: str):
            try:
                decoded_url = unquote(url)
                response = requests.get(decoded_url, stream=True, allow_redirects=True)
                response.raise_for_status()
                
                return StreamingResponse(
                    response.iter_content(chunk_size=8192),
                    media_type=response.headers.get('content-type'),
                    headers=dict(response.headers)
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/test")
        async def test_media(url: str):
            try:
                success, info = self.media_tester.test_media(url)
                if success:
                    return JSONResponse(info)
                else:
                    raise HTTPException(status_code=400, detail=info["error"])
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    def start(self):
        def run_server():
            uvicorn.run(self.app, host=self.host, port=self.port)

        self.server = threading.Thread(target=run_server, daemon=True)
        self.server.start()

    def stop(self):
        # O servidor será encerrado quando o programa principal terminar
        # pois é um daemon thread
        pass

    def get_proxy_url(self, original_url: str) -> str:
        return f"http://{self.host}:{self.port}/proxy?url={original_url}"
