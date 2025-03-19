#!/bin/bash

# Criar diretório de assets se não existir
mkdir -p src/assets

# Build do frontend Next.js
echo "Building Next.js frontend..."
cd frontend
# Adicionar variável de ambiente para o endereço do servidor
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm install
npm run build

# Garantir que todos os arquivos necessários sejam copiados
mkdir -p dist
cp -r .next/static dist/
cp -r .next/standalone/* dist/ 2>/dev/null || true
cp -r public/* dist/ 2>/dev/null || true
cd ..

# Build para Linux
echo "Executando build para Linux..."
python -m pip install -r requirements.txt
python -m PyInstaller linux.spec --clean

echo "Build concluído! Verifique a pasta dist/"
