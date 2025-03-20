#!/usr/bin/env python3
from src.views.main_window import MainWindow
from src.services.system_tray import SystemTray
from src.api.app import app
import threading
import uvicorn
import logging
import signal
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

def signal_handler(signum, frame):
    """Manipulador de sinais para encerramento limpo"""
    sys.exit(0)

def run_api():
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logging.error(f"Erro ao iniciar API: {str(e)}")

class CORSHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self):
        # Normalizar o path para Windows
        self.path = self.path.replace('\\', '/')
        if self.path == '/' or not os.path.exists(os.path.join(self.directory, self.path.lstrip('/'))):
            self.path = '/index.html'
        return super().do_GET()

    def end_headers(self):
        # Headers CORS existentes
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:8000')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        SimpleHTTPRequestHandler.end_headers(self)

def run_frontend():
    try:
        httpd = HTTPServer(("0.0.0.0", 8001), CORSHTTPRequestHandler)
        httpd.serve_forever()
    except Exception as e:
        logging.error(f"Erro ao iniciar servidor frontend: {str(e)}")

def main():
    # Configurar manipulador de sinais
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Criar a interface principal
        app_window = MainWindow()
        
        # Iniciar system tray
        tray = SystemTray(app_window)
        tray_thread = threading.Thread(target=tray.run, daemon=True)
        tray_thread.start()

        # Iniciar API em uma thread separada
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()

        # Iniciar servidor frontend em uma thread separada
        frontend_thread = threading.Thread(target=run_frontend, daemon=True)
        frontend_thread.start()

        # Iniciar a interface
        app_window.run()
    except KeyboardInterrupt:
        logging.info("Encerrando aplicação...")
    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}")
    finally:
        sys.exit(0)

if __name__ == "__main__":
    main()
