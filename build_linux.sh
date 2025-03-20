#!/bin/bash

# Criar diretório de assets se não existir
mkdir -p src/assets

# Build do frontend Next.js
echo "Building Next.js frontend..."
cd frontend

# Adicionar variável de ambiente para o endereço do servidor
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "PORT=8001" >> .env.local

# Instalar dependências e fazer build
npm install
npm run build

# Limpar pasta dist anterior
rm -rf dist
mkdir -p dist/_next
mkdir -p dist/static

# Copiar os arquivos do Next.js build - estrutura correta
cp -r dist/_next/* dist/_next/ 2>/dev/null || true
cp -r dist/static/* dist/static/ 2>/dev/null || true
cp -r dist/* dist/ 2>/dev/null || true

cd ..

# Build para Linux
echo "Executando build para Linux..."
python -m pip install -r requirements.txt
python -m PyInstaller linux.spec --clean

echo "Build concluído! Verifique a pasta dist/"
