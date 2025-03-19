import pystray
from PIL import Image
from .proxy_server import ProxyServer
import sys
import logging

class SystemTray:
    def __init__(self, main_window=None):
        self.proxy_server = ProxyServer()
        self.icon = None
        self.main_window = main_window
        self.create_icon()

    def create_icon(self):
        # Criar um ícone básico 16x16 pixels
        image = Image.new('RGB', (16, 16), 'blue')
        self.icon = pystray.Icon(
            "M3UtoSTRM",
            image,
            "M3UtoSTRM Proxy",
            menu=self.create_menu()
        )

    def create_menu(self):
        return pystray.Menu(
            pystray.MenuItem(
                "Abrir Interface",
                self.show_window,
                default=True  # Faz este ser o item padrão ao clicar com botão esquerdo
            ),
            pystray.MenuItem(
                "Status do Proxy",
                pystray.Menu(
                    pystray.MenuItem(
                        "Iniciar",
                        self.start_proxy,
                        checked=lambda item: self.proxy_server.server is not None
                    ),
                    pystray.MenuItem(
                        "Parar",
                        self.stop_proxy,
                        checked=lambda item: self.proxy_server.server is None
                    )
                )
            ),
            pystray.MenuItem(
                "Sair",
                self.exit_application
            )
        )

    def show_window(self):
        """Mostra a janela principal"""
        if self.main_window:
            self.main_window.show()

    def start_proxy(self):
        if not self.proxy_server.server:
            self.proxy_server.start()

    def stop_proxy(self):
        if self.proxy_server.server:
            self.proxy_server.stop()

    def quit_application(self):
        try:
            self.stop_proxy()
            if self.icon:
                self.icon.stop()
        except Exception as e:
            logging.error(f"Erro ao encerrar system tray: {str(e)}")
        finally:
            if self.main_window:
                try:
                    self.main_window.root.quit()
                except:
                    pass

    def exit_application(self):
        """Fecha completamente o aplicativo e o proxy"""
        if self.main_window:
            self.main_window.root.quit()
        self.stop_proxy()
        self.icon.stop()
        sys.exit(0)

    def run(self):
        try:
            self.start_proxy()
            self.icon.run()
        except KeyboardInterrupt:
            self.quit_application()
        except Exception as e:
            logging.error(f"Erro no system tray: {str(e)}")
            self.quit_application()
