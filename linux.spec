# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Atualizar caminhos do frontend
added_files = [
    ('frontend/dist', 'frontend/dist'),      # Next.js files
    ('config.json', '.'),                    # Config file
]

# Garantir que todos os arquivos estáticos do Next.js sejam incluídos
datas = added_files + [
    ('frontend/dist/static', 'frontend/dist/static'),  # Next.js static files
    ('frontend/dist/_next', 'frontend/dist/_next'),    # Next.js assets
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'tkinter',
        'requests',
        'urllib3',
        'json',
        're',
        '_decimal',
        'decimal',
        'asyncio',
        'pkg_resources.py2_warn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
        'websockets',
    ] + collect_submodules('fastapi'),
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='M3UtoSTRM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
)
