# M3UtoSTRM

M3UtoSTRM é uma aplicação completa que converte e gerencia playlists M3U/M3U8 em arquivos STRM, com suporte a streaming e proxy integrado. Ideal para organizar e reproduzir conteúdo em servidores de mídia como **Jellyfin**, **Emby**, **Plex** e **Kodi**.

## 🌟 Principais Recursos

### Sistema Core
- Processamento de playlists M3U/M3U8 (URL ou arquivo local)
- Proxy integrado para streaming direto
- Separação automática de filmes e séries
- Sistema de filas para processamento em lote
- Cache inteligente de streams
- APIs TMDB e OMDB para metadados

### Interface Desktop
- GUI moderna com Tkinter
- System tray com controles rápidos
- Monitoramento em tempo real
- Testes de conexão e mídia
- Minimização para bandeja do sistema
- Indicadores de status do proxy

### Interface Web
- Dashboard responsivo em Next.js
- Gerenciamento remoto via browser
- Sistema de filas visual
- Análise de playlists em tempo real
- Preview de mídia integrado
- APIs RESTful e WebSocket

## 💻 Tecnologias

- **Backend**: Python 3.12+, FastAPI, WebSocket
- **Frontend**: Next.js, React, TailwindCSS
- **GUI**: Tkinter, Pystray
- **Proxy**: Servidor proxy personalizado
- **APIs**: TMDB, OMDB
- **Streaming**: FFmpeg, yt-dlp

## 📦 Instalação

### Via Executável
1. Baixe o último release para seu sistema
2. Execute o instalador
3. Siga as instruções na tela

### Via Código Fonte
```bash
# Clone o repositório
git clone https://github.com/seuusuario/M3UtoSTRM.git
cd M3UtoSTRM

# Ambiente virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# Dependências
pip install -r requirements.txt

# Inicie a aplicação
python main.py
```

### Dependências do Sistema

#### Windows
- Windows 7+ (64-bit)
- Microsoft Visual C++ 2019+

#### Linux
```bash
# Debian/Ubuntu
sudo apt-get install python3-tk ffmpeg

# Fedora
sudo dnf install python3-tkinter ffmpeg

# Arch
sudo pacman -S tk ffmpeg
```

## 🚀 Uso

### Interface Desktop

1. Execute o programa
2. Configure:
   - Fonte M3U (URL/arquivo)
   - Diretórios de saída
   - Chaves API (TMDB/OMDB)
3. Use o botão "Testar" para validar a fonte
4. Clique em "Processar"

### Interface Web

1. Acesse http://localhost:8000
2. Use as seguintes funcionalidades:
   - Upload de playlists
   - Análise de conteúdo
   - Gerenciamento de filas
   - Monitoramento de progresso
   - Configuração remota

### System Tray

- Clique direito no ícone para:
  - Abrir interface principal
  - Abrir interface web
  - Controlar proxy
  - Gerenciar aplicação

## ⚙️ Configuração

### config.json
```json
{
  "m3u_url": "",
  "m3u_file": "",
  "movies_dir": "iptv/filmes",
  "series_dir": "iptv/series",
  "tmdb_api_key": "",
  "omdb_api_key": "",
  "proxy_port": 55950,
  "web_port": 8000
}
```

### Variáveis de Ambiente
```bash
PORT=8000                    # Porta da interface web
PROXY_PORT=55950            # Porta do proxy
TMDB_API_KEY=sua_chave      # Chave TMDB
OMDB_API_KEY=sua_chave      # Chave OMDB
```

## 📁 Estrutura

### Arquivos STRM
iptv/
├── filmes/
│   └── Nome do Filme.strm
└── series/
    └── Nome da Serie/
        └── Season 01/
            └── S01E01.strm

### Código Fonte
M3UtoSTRM/
├── src/
│   ├── api/          # FastAPI endpoints
│   ├── controllers/  # Lógica de negócio
│   ├── models/       # Modelos de dados
│   ├── services/     # Serviços core
│   └── views/        # Interfaces
├── frontend/         # Next.js frontend
├── main.py          # Entrada principal
└── config.json      # Configurações

## 🤝 Contribuição
###  Fork o projeto
- Crie sua branch (git checkout -b feature/AmazingFeature)
- Commit suas mudanças (git commit -m 'Add: nova funcionalidade')
- Push para a branch (git push origin feature/AmazingFeature)
- Abra um Pull Request
- Áreas para Contribuição
- Melhorias no proxy
- Otimizações de cache
- Novos formatos de playlist
- Melhorias na interface web
- Documentação
- Traduções

## 🙏 Agradecimentos
### Comunidade IPTV
- Contribuidores do FFmpeg
- Equipe do yt-dlp
- Desenvolvedores do Next.js

Feito com ❤️ pela comunidade