import os
import sys
import logging
from typing import Optional

class StaticServer:
    def __init__(self):
        # Obter caminho do executável ou diretório atual
        if getattr(sys, 'frozen', False):
            # Executando como executável
            base_path = sys._MEIPASS
        else:
            # Executando como script
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        self.frontend_path = os.path.join(base_path, 'frontend', 'dist')
        self._ensure_frontend_directory()
        
    def _ensure_frontend_directory(self):
        """Garante que o diretório do front-end existe"""
        try:
            os.makedirs(self.frontend_path, exist_ok=True)
            index_path = os.path.join(self.frontend_path, 'index.html')
            
            # Criar index.html básico se não existir
            if not os.path.exists(index_path):
                with open(index_path, 'w') as f:
                    f.write('''
                    <!DOCTYPE html>
                    <html>
                      <head>
                        <title>M3UtoSTRM</title>
                      </head>
                      <body>
                        <h1>Servidor Funcionando!</h1>
                        <p>Configure seu frontend Nest.js na pasta frontend/dist</p>
                      </body>
                    </html>
                    ''')
        except Exception as e:
            logging.error(f"Erro ao configurar diretório frontend: {str(e)}")

    def get_frontend_path(self) -> str:
        """Retorna o caminho absoluto do diretório frontend"""
        return self.frontend_path
