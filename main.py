#!/usr/bin/env python3
from src.views.main_window import MainWindow
from src.services.system_tray import SystemTray
import threading

def main():
    # Criar a interface principal primeiro
    app = MainWindow()
    
    # Iniciar system tray passando a referência da janela
    tray = SystemTray(app)
    tray_thread = threading.Thread(target=tray.run, daemon=True)
    tray_thread.start()

    # Iniciar a interface
    app.run()

if __name__ == "__main__":
    main()
