# M3UtoSTRM

M3UtoSTRM é um utilitário em Python que converte playlists M3U em arquivos STRM organizados para facilitar a gestão de conteúdo em servidores de mídia como **Jellyfin**, **Kodi** e outros. Ele categoriza filmes e séries automaticamente, criando uma estrutura de diretórios organizada.

## 🛠️ Funcionalidades
- Processa playlists M3U diretamente de uma URL.
- Separa **filmes** e **séries**, criando uma estrutura correta.
- Utiliza API gratuita para validar metadados quando necessário.
- Atualização inteligente para evitar duplicidades.
- Interface simples para configuração e monitoramento do progresso.
- Armazena configurações em um arquivo JSON.
- Compilável para Windows e Linux.

## 📝 Estrutura dos Arquivos

- **Filmes**: `iptv/filmes/Nome do Filme.strm`
- **Séries**: `iptv/series/Nome da Serie/Season 01/EP01S01.strm`

## ⚡ Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seuusuario/M3UtoSTRM.git
   cd M3UtoSTRM
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute a aplicação:
   ```bash
   python m3utoStrm.py
   ```

## 🌐 Interface
A interface permite:
- Inserir a URL da playlist M3U.
- Definir diretórios padrões para filmes e séries.
- Monitorar a porcentagem de progresso.
- Atualizar a playlist com um clique.

## 🛠️ Compilando para Windows e Linux

**Para Windows:**
```bash
pyinstaller --onefile --windowed m3utoStrm.py
```

**Para Linux:**
```bash
pyinstaller --onefile --console m3utoStrm.py
```

O executável será gerado na pasta `dist/`.

## 🏆 Contribuição
Se você deseja contribuir com melhorias, faça um fork do repositório, crie uma branch, faça suas modificações e envie um pull request!

## 💎 Licença
Este projeto está licenciado sob a **MIT License**. Sinta-se livre para usá-lo e modificá-lo!

---
Feito com ❤️ por [Seu Nome]