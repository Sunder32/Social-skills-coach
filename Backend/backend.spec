# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Social Skills Coach Backend
"""

block_cipher = None

a = Analysis(
    ['run_backend.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('production.env', '.'),
        ('app', 'app'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        'sqlalchemy.dialects.postgresql',
        'sqlalchemy.dialects.sqlite',
        'asyncpg',
        'aiosqlite',
        'httpx',
        'argon2',
        'jose',
        'passlib',
        'pydantic',
        'pydantic_settings',
        'fastapi',
        'starlette',
        'anyio',
        'sniffio',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    name='backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False to hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
