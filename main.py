#!/usr/bin/env python3
from src.views.main_window import MainWindow
from src.services.system_tray import SystemTray
from src.api.app import app
import threading
import uvicorn
import logging

def run_api():
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logging.error(f"Erro ao iniciar API: {str(e)}")

def main():
    # Criar a interface principal
    app_window = MainWindow()
    
    # Iniciar system tray
    tray = SystemTray(app_window)
    tray_thread = threading.Thread(target=tray.run, daemon=True)
    tray_thread.start()

    # Iniciar API em uma thread separada
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    # Iniciar a interface
    app_window.run()

if __name__ == "__main__":
    main()
