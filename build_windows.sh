#!/bin/bash

# Criar diretório de assets se não existir
mkdir -p src/assets

# Verificar se o ícone existe
if [ ! -f "src/assets/icon.ico" ]; then
    echo "Aviso: Arquivo de ícone não encontrado em src/assets/icon.ico"
    echo "O executável será gerado sem ícone personalizado"
fi

# Instalar dependências necessárias
sudo apt-get update
sudo apt-get install -y wine64 wget

# Baixar Python para Windows
wget https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe -O python_windows.exe

# Instalar Python via Wine
WINEARCH=win64 WINEPREFIX=~/.wine64 wine python_windows.exe /quiet InstallAllUsers=1 PrependPath=1

# Instalar dependências via pip
WINEARCH=win64 WINEPREFIX=~/.wine64 wine pip install -r requirements.txt

# Compilar com PyInstaller
WINEARCH=win64 WINEPREFIX=~/.wine64 wine python -m PyInstaller m3utostrm.spec --clean

echo "Build concluído! Verifique a pasta dist/"
