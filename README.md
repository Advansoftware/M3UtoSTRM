# M3UtoSTRM

M3UtoSTRM é um utilitário em Python que converte playlists M3U em arquivos STRM organizados para filmes e séries, ignorando canais de TV. Ideal para organizar conteúdo em servidores de mídia como **Jellyfin**, **Kodi** e outros.

## 🛠️ Funcionalidades
- Processa playlists M3U via URL ou arquivo local
- Separa **filmes** e **séries** automaticamente
- Ignora canais de TV e streams ao vivo
- Interface gráfica intuitiva com progresso em tempo real
- Suporte a URLs protegidas e arquivos locais
- Estrutura organizada para mídias
- Configurações persistentes em JSON

## 📝 Estrutura do Projeto

```
M3UtoSTRM/
├── src/
│   ├── controllers/
│   │   └── app_controller.py
│   ├── models/
│   │   └── m3u_processor.py
│   └── views/
│       └── main_window.py
├── main.py
├── requirements.txt
└── config.json
```

## 📁 Estrutura dos Arquivos Gerados

- **Filmes**: `iptv/filmes/Nome do Filme.strm`
- **Séries**: `iptv/series/Nome da Serie/Season 01/S01E01.strm`

## ⚡ Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seuusuario/M3UtoSTRM.git
   cd M3UtoSTRM
   ```

2. Crie e ative o ambiente virtual:
   ```bash
   python -m venv .venv
   
   # Windows:
   .venv\Scripts\activate
   
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Instale o tkinter se necessário:
   ```bash
   # Debian/Ubuntu:
   sudo apt-get install python3-tk
   
   # Fedora:
   sudo dnf install python3-tkinter
   
   # Arch Linux:
   sudo pacman -S tk
   ```

## 🚀 Uso

1. Execute o programa:
   ```bash
   python main.py
   ```

2. Na interface:
   - Escolha entre URL ou arquivo local
   - Configure os diretórios de saída
   - Selecione os tipos de mídia a processar
   - Clique em "Processar"

## ⚙️ Configuração

O arquivo `config.json` é gerado automaticamente e armazena:
- URL da playlist ou caminho do arquivo
- Diretórios de saída
- Preferências de processamento

## 🛠️ Compilando

### Windows
Para criar um executável no Windows:

```bash
# Instale as dependências
pip install -r requirements.txt

# Compile o programa
pyinstaller m3utostrm.spec --clean
```

### Linux (Compilação Cruzada para Windows)
Para compilar no Linux gerando executável para Windows:

1. Dê permissão ao script de build:
   ```bash
   chmod +x build_windows.sh
   ```

2. Execute o script:
   ```bash
   ./build_windows.sh
   ```

O executável será gerado em `dist/M3UtoSTRM.exe`

### Requisitos para Compilação Cruzada
- Linux com Wine 64-bit instalado
- Conexão com internet para baixar Python para Windows
- Pelo menos 2GB de espaço livre

### Resolvendo Problemas de Compilação
- Se o Wine não estiver instalado: `sudo apt-get install wine64`
- Se falhar ao baixar Python: Verifique sua conexão de internet
- Se ocorrer erro de permissão: Execute com sudo
- Para limpar builds anteriores: `rm -rf build dist`

### Requisitos para execução no Windows
- Windows 7/8/10/11 (32-bit e 64-bit)
- Compatível com todas as versões do Windows 10
- Otimizado para sistemas 64 bits
- Não é necessário Python instalado
- Execute como administrador na primeira vez
- Se o Windows Defender bloquear, clique em "Mais informações" e "Executar assim mesmo"

### Executando no Windows
1. Ao executar pela primeira vez:
   - Clique com botão direito > Executar como administrador
   - Se aparecer "Windows protegeu seu PC":
     1. Clique em "Mais informações"
     2. Depois em "Executar assim mesmo"
   - Se aparecer UAC (Controle de Conta de Usuário), aceite

2. Na próxima execução, o Windows já reconhecerá o programa

### Resolvendo Problemas
- Se o antivírus bloquear, adicione o programa às exceções
- Certifique-se de ter permissões de administrador
- Execute sempre a partir de um diretório com permissões de escrita

## 📝 Notas
- Certifique-se de ter permissões de escrita nos diretórios de saída
- URLs de playlist devem ser válidas e acessíveis
- Canais de TV e streams ao vivo são automaticamente ignorados

## 🤝 Contribuição
Contribuições são bem-vindas! Por favor, sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Enviar pull requests

## 📄 Licença
Este projeto está licenciado sob a **MIT License**.

---
Desenvolvido com ❤️