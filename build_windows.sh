#!/bin/bash

# Criar diretório de assets se não existir
mkdir -p src/assets

# Verificar se o ícone existe
if [ ! -f "src/assets/icon.ico" ]; then
    echo "Aviso: Arquivo de ícone não encontrado em src/assets/icon.ico"
    echo "O executável será gerado sem ícone personalizado"
fi

# Build do frontend Next.js
echo "Building Next.js frontend..."
cd frontend
npm install
npm run build
mkdir -p dist
if [ -d ".next/static" ]; then
    cp -r .next/static dist/
fi
cd ..

# Verificar se estamos no Windows
if [ "$(expr substr $(uname -s) 1 5)" == "MINGW" ] || [ "$(expr substr $(uname -s) 1 4)" == "MSYS" ]; then
    # Build no Windows
    echo "Executando build no Windows..."
    python -m pip install -r requirements.txt
    python -m PyInstaller m3utostrm.spec --clean
else
    # Build no Linux usando Wine
    echo "Executando build no Linux usando Wine..."
    # Instalar dependências
    sudo apt-get update
    sudo apt-get install -y wine64 wget nodejs npm

    # Baixar Python para Windows
    wget https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe -O python_windows.exe

    # Configurar ambiente Wine
    WINEARCH=win64 WINEPREFIX=~/.wine64

    # Instalar Python via Wine
    wine python_windows.exe /quiet InstallAllUsers=1 PrependPath=1

    # Instalar dependências Python
    wine pip install -r requirements.txt
    wine pip install pyinstaller

    # Compilar com PyInstaller
    wine python -m PyInstaller m3utostrm.spec --clean
fi

echo "Build concluído! Verifique a pasta dist/"
