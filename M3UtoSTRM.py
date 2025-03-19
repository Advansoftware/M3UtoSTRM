import os
import json
import requests
import tkinter as tk
from tkinter import filedialog, messagebox
from tqdm import tqdm

# Nome do arquivo de configuração
CONFIG_FILE = "config.json"

def load_config():
    """Carrega as configurações do arquivo JSON."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"m3u_url": "", "movies_dir": "iptv/filmes", "series_dir": "iptv/series"}

def save_config(config):
    """Salva as configurações no arquivo JSON."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def download_m3u(m3u_url):
    """Faz o download da playlist M3U."""
    try:
        response = requests.get(m3u_url, timeout=10)
        response.raise_for_status()
        return response.text.splitlines()
    except requests.RequestException as e:
        messagebox.showerror("Erro", f"Falha ao baixar M3U: {e}")
        return None

def classify_content(title):
    """Determina se um título é filme ou série usando uma API gratuita."""
    try:
        api_url = f"https://api.themoviedb.org/3/search/multi?query={title}&api_key=SUA_CHAVE_AQUI"
        response = requests.get(api_url).json()
        results = response.get("results", [])
        if results:
            media_type = results[0].get("media_type")
            if media_type == "movie":
                return "movie"
            elif media_type == "tv":
                return "series"
    except Exception:
        pass
    return "unknown"

def process_m3u(m3u_url, movies_dir, series_dir):
    """Processa a playlist M3U e gera arquivos .strm organizados."""
    lines = download_m3u(m3u_url)
    if not lines:
        return
    
    os.makedirs(movies_dir, exist_ok=True)
    os.makedirs(series_dir, exist_ok=True)
    
    with tqdm(total=len(lines), desc="Processando", unit=" linha") as pbar:
        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF"):
                info = lines[i]
                url = lines[i + 1] if i + 1 < len(lines) else ""
                title = info.split(",")[-1].strip()
                
                content_type = classify_content(title)
                
                if content_type == "movie":
                    filepath = os.path.join(movies_dir, f"{title}.strm")
                elif content_type == "series":
                    season_episode = "EP01S01"  # Supondo um padrão
                    series_folder = os.path.join(series_dir, title, "Season 01")
                    os.makedirs(series_folder, exist_ok=True)
                    filepath = os.path.join(series_folder, f"{season_episode}.strm")
                else:
                    continue  # Ignorar conteúdos desconhecidos
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(url)
                
                pbar.update(2)  # Atualiza a barra de progresso
    
    messagebox.showinfo("Concluído", "Processamento finalizado com sucesso!")

def run_gui():
    """Interface gráfica simples para configurar a URL e diretórios."""
    config = load_config()
    
    root = tk.Tk()
    root.title("M3UtoSTRM")
    
    tk.Label(root, text="URL da Playlist M3U:").pack()
    url_entry = tk.Entry(root, width=50)
    url_entry.insert(0, config["m3u_url"])
    url_entry.pack()
    
    def select_movies_dir():
        path = filedialog.askdirectory()
        if path:
            movies_entry.delete(0, tk.END)
            movies_entry.insert(0, path)
    
    tk.Label(root, text="Pasta de Filmes:").pack()
    movies_entry = tk.Entry(root, width=50)
    movies_entry.insert(0, config["movies_dir"])
    movies_entry.pack()
    tk.Button(root, text="Selecionar", command=select_movies_dir).pack()
    
    def select_series_dir():
        path = filedialog.askdirectory()
        if path:
            series_entry.delete(0, tk.END)
            series_entry.insert(0, path)
    
    tk.Label(root, text="Pasta de Séries:").pack()
    series_entry = tk.Entry(root, width=50)
    series_entry.insert(0, config["series_dir"])
    series_entry.pack()
    tk.Button(root, text="Selecionar", command=select_series_dir).pack()
    
    def process():
        config["m3u_url"] = url_entry.get()
        config["movies_dir"] = movies_entry.get()
        config["series_dir"] = series_entry.get()
        save_config(config)
        process_m3u(config["m3u_url"], config["movies_dir"], config["series_dir"])
    
    tk.Button(root, text="Processar", command=process).pack()
    
    root.mainloop()

if __name__ == "__main__":
    run_gui()