import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from typing import Optional
import requests
import sys
import webbrowser
from ..controllers.app_controller import AppController

class MainWindow:
    def __init__(self):
        self.controller = AppController()
        self.root = tk.Tk()
        self.current_thread: Optional[threading.Thread] = None
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update_proxy_status()

    def setup_ui(self):
        self.root.title("M3UtoSTRM")
        self.create_input_fields()
        self.create_status_frame()
        self.create_buttons()

    def create_input_fields(self):
        # M3U Source Frame
        source_frame = tk.LabelFrame(self.root, text="Fonte M3U", padx=5, pady=5)
        source_frame.pack(fill=tk.X, padx=5, pady=5)

        # Source type selection
        self.source_var = tk.BooleanVar(value=not self.controller.config.get("use_file", False))
        
        tk.Radiobutton(
            source_frame, 
            text="URL", 
            variable=self.source_var, 
            value=True,
            command=self._toggle_source
        ).pack(anchor=tk.W)
        
        # URL input
        self.url_frame = tk.Frame(source_frame)
        self.url_frame.pack(fill=tk.X)
        self.url_entry = tk.Entry(self.url_frame, width=50)
        self.url_entry.insert(0, self.controller.config.get("m3u_url", ""))
        self.url_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # Botão de teste de conexão
        self.test_button = tk.Button(
            self.url_frame,
            text="Testar Conexão",
            command=self._test_connection
        )
        self.test_button.pack(side=tk.RIGHT, padx=5)
        
        # File selection
        tk.Radiobutton(
            source_frame, 
            text="Arquivo Local", 
            variable=self.source_var, 
            value=False,
            command=self._toggle_source
        ).pack(anchor=tk.W)
        
        self.file_frame = tk.Frame(source_frame)
        self.file_frame.pack(fill=tk.X)
        self.file_entry = tk.Entry(self.file_frame, width=50)
        self.file_entry.insert(0, self.controller.config.get("m3u_file", ""))
        self.file_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(
            self.file_frame, 
            text="Selecionar", 
            command=self._select_m3u_file
        ).pack(side=tk.RIGHT)

        self._toggle_source()  # Initialize states
        
        # Movies directory
        tk.Label(self.root, text="Pasta de Filmes:").pack()
        movies_frame = tk.Frame(self.root)
        movies_frame.pack(fill=tk.X, padx=5)
        
        self.movies_entry = tk.Entry(movies_frame, width=50)
        self.movies_entry.insert(0, self.controller.config.get("movies_dir", ""))
        self.movies_entry.pack(side=tk.LEFT, expand=True)
        
        tk.Button(movies_frame, text="Selecionar", 
                 command=lambda: self._select_directory(self.movies_entry)).pack(side=tk.RIGHT)

        # Series directory
        tk.Label(self.root, text="Pasta de Séries:").pack()
        series_frame = tk.Frame(self.root)
        series_frame.pack(fill=tk.X, padx=5)
        
        self.series_entry = tk.Entry(series_frame, width=50)
        self.series_entry.insert(0, self.controller.config.get("series_dir", ""))
        self.series_entry.pack(side=tk.LEFT, expand=True)
        
        tk.Button(series_frame, text="Selecionar", 
                 command=lambda: self._select_directory(self.series_entry)).pack(side=tk.RIGHT)

        # TMDB API Key
        tk.Label(self.root, text="Chave de API TheMovieDB:").pack()
        self.tmdb_entry = tk.Entry(self.root, width=50, show="*")
        self.tmdb_entry.insert(0, self.controller.config.get("tmdb_api_key", ""))
        self.tmdb_entry.pack()

        # OMDB API Key (Novo campo)
        tk.Label(self.root, text="Chave de API OMDB:").pack()
        self.omdb_entry = tk.Entry(self.root, width=50, show="*")
        self.omdb_entry.insert(0, self.controller.config.get("omdb_api_key", ""))
        self.omdb_entry.pack()

        # Checkboxes
        self.process_movies_var = tk.BooleanVar(value=self.controller.config.get("process_movies", True))
        self.process_series_var = tk.BooleanVar(value=self.controller.config.get("process_series", True))
        
        tk.Checkbutton(self.root, text="Processar Filmes", 
                      variable=self.process_movies_var).pack()
        tk.Checkbutton(self.root, text="Processar Séries", 
                      variable=self.process_series_var).pack()

    def create_status_frame(self):
        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Adicionar status do proxy
        self.proxy_status_label = tk.Label(self.status_frame, text="Status Proxy: Verificando...", fg="blue")
        self.proxy_status_label.pack()
        
        self.status_label = tk.Label(self.status_frame, text="Status: Aguardando")
        self.status_label.pack()
        
        self.action_label = tk.Label(self.status_frame, text="")
        self.action_label.pack()
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.status_frame, 
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X)

    def create_buttons(self):
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.process_button = tk.Button(
            self.button_frame, 
            text="Processar",
            command=self._start_processing
        )
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = tk.Button(
            self.button_frame,
            text="Cancelar",
            command=self._cancel_processing,
            state=tk.DISABLED
        )
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        self.open_web_button = tk.Button(
            self.button_frame,
            text="Abrir Interface Web",
            command=self._open_web_interface
        )
        self.open_web_button.pack(side=tk.LEFT, padx=5)

    def _select_directory(self, entry_widget):
        path = filedialog.askdirectory()
        if path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, path)

    def _select_m3u_file(self):
        filetypes = [("M3U Files", "*.m3u *.m3u8"), ("All Files", "*.*")]
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, path)

    def _toggle_source(self):
        is_url = self.source_var.get()
        self.url_entry.config(state=tk.NORMAL if is_url else tk.DISABLED)
        self.file_entry.config(state=tk.DISABLED if is_url else tk.NORMAL)
        
    def _start_processing(self):
        self.process_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        
        config = {
            "m3u_url": self.url_entry.get(),
            "m3u_file": self.file_entry.get(),
            "use_file": not self.source_var.get(),
            "movies_dir": self.movies_entry.get(),
            "series_dir": self.series_entry.get(),
            "tmdb_api_key": self.tmdb_entry.get(),
            "omdb_api_key": self.omdb_entry.get(),  # Adicionar OMDB API key
            "process_movies": self.process_movies_var.get(),
            "process_series": self.process_series_var.get()
        }
        
        self.controller.save_config(config)
        
        def process_callback(info, current, total):
            progress = int((current / total) * 100)
            self.progress_var.set(progress)
            self.action_label.config(text=f"Processando: {info.title}")
            self.root.update_idletasks()
        
        self.current_thread = threading.Thread(
            target=self.controller.process_playlist,
            args=(config, process_callback)
        )
        self.current_thread.daemon = True
        self.current_thread.start()
        
        self._check_thread_status()

    def _cancel_processing(self):
        if self.current_thread and self.current_thread.is_alive():
            self.controller.cancel_processing()
            self.status_label.config(text="Status: Cancelado")
            self.action_label.config(text="")

    def _check_thread_status(self):
        if self.current_thread and self.current_thread.is_alive():
            self.root.after(100, self._check_thread_status)
        else:
            self.process_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            if not self.controller.is_cancelled:
                self.status_label.config(text="Status: Concluído")
                messagebox.showinfo("Concluído", "Processamento finalizado com sucesso!")

    def _test_connection(self):
        """Testa a conexão com a playlist e mostra o resultado."""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Aviso", "Digite uma URL para testar")
            return
            
        self.test_button.config(state=tk.DISABLED)
        self.test_button.config(text="Testando...")
        self.root.update_idletasks()
        
        try:
            # Primeiro testa a conexão com a playlist
            success, message = self.controller.test_playlist_connection(url)
            
            if success:
                # Se a playlist está OK, testa a primeira mídia
                try:
                    response = requests.get(f"http://127.0.0.1:55950/test?url={url}", timeout=10)
                    if response.status_code == 200:
                        media_info = response.json()
                        info_text = self._format_media_info(media_info)
                        messagebox.showinfo("Informações da Mídia", info_text)
                    else:
                        messagebox.showwarning("Aviso", "Não foi possível testar a mídia")
                except:
                    messagebox.showinfo("Sucesso", "Playlist OK, mas não foi possível testar mídia")
            else:
                messagebox.showerror("Erro", message)
        finally:
            self.test_button.config(state=tk.NORMAL)
            self.test_button.config(text="Testar Conexão")

    def _format_media_info(self, info: dict) -> str:
        """Formata as informações da mídia para exibição"""
        text = f"Duração: {float(info['duration']):.2f}s\n"
        text += f"Tamanho: {int(info['size'])/1024/1024:.2f} MB\n"
        text += f"Bitrate: {int(info['bitrate'])/1024:.2f} Kbps\n\n"
        
        for stream in info['streams']:
            if stream['type'] == 'video':
                text += f"Vídeo: {stream['codec']} {stream['width']}x{stream['height']}\n"
                text += f"FPS: {stream['fps']}\n"
            elif stream['type'] == 'audio':
                text += f"Áudio: {stream['codec']} ({stream['language']})\n"
                
        return text

    def update_proxy_status(self):
        """Atualiza o status do proxy na interface"""
        try:
            response = requests.get("http://127.0.0.1:55950/status", timeout=1)
            if response.status_code == 200:
                self.proxy_status_label.config(text="Status Proxy: Ativo", fg="green")
            else:
                self.proxy_status_label.config(text="Status Proxy: Erro", fg="red")
        except requests.RequestException:
            self.proxy_status_label.config(text="Status Proxy: Inativo", fg="red")
        
        # Atualizar status a cada 5 segundos
        self.root.after(5000, self.update_proxy_status)

    def on_closing(self):
        """Chamado quando a janela é fechada"""
        response = messagebox.askyesnocancel(
            "M3UtoSTRM",
            "Escolha uma opção:\n"
            "Sim - Minimizar para a bandeja\n"
            "Não - Fechar completamente\n"
            "Cancelar - Voltar"
        )
        
        if response is True:  # Sim - Minimizar
            self.root.withdraw()
            messagebox.showinfo(
                "M3UtoSTRM",
                "O aplicativo continuará rodando na bandeja do sistema.\n"
                "O proxy permanecerá ativo para suas streams."
            )
        elif response is False:  # Não - Fechar
            self.root.quit()
            sys.exit(0)
        # Se Cancelar, não faz nada e mantém a janela aberta

    def show(self):
        """Mostra a janela novamente"""
        self.root.deiconify()
        self.update_proxy_status()

    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
        except Exception as e:
            logging.error(f"Erro na interface: {str(e)}")
            self.root.quit()
            sys.exit(1)
        
    def _open_web_interface(self):
        try:
            response = requests.get('http://localhost:8000/api/server-url')
            if response.status_code == 200:
                url = response.json()['url']
                webbrowser.open(url)
                self.status_label.config(text='Interface web aberta no navegador')
            else:
                self.status_label.config(text='Erro ao abrir interface web')
        except Exception as e:
            self.status_label.config(text=f'Erro ao abrir interface: {str(e)}')
