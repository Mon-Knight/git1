# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['desktop_launcher.py'],
    pathex=[],
    binaries=[('C:/Users/17735/anaconda3/envs/aiworldengine/Library/bin/libssl-3-x64.dll', '.'), ('C:/Users/17735/anaconda3/envs/aiworldengine/Library/bin/libcrypto-3-x64.dll', '.'), ('C:/Users/17735/anaconda3/envs/aiworldengine/Library/bin/ffi.dll', '.'), ('C:/Users/17735/anaconda3/envs/aiworldengine/Library/bin/sqlite3.dll', '.')],
    datas=[('app/templates', 'app/templates'), ('app/static', 'app/static')],
    hiddenimports=['uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.asyncio', 'uvicorn.loops.auto', 'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.http.h11_impl', 'uvicorn.protocols.websockets', 'uvicorn.lifespan', 'uvicorn.lifespan.on', 'sqlalchemy.sql.default_comparator', 'jinja2', 'jinja2.ext', 'python_multipart', 'requests', 'h11', 'anyio', 'sniffio', 'starlette', 'fastapi', 'asyncio', 'app.constants', 'app.services.ai', 'app.services.ai.base', 'app.services.ai.errors', 'app.services.ai.mock_client', 'app.services.ai.openai_compatible_client', 'app.services.ai.model_router', 'app.services.ai.prompt_builder', 'app.services.ai.response_parser', 'app.services.settings_service', 'app.services.export_service', 'app.services.import_service', 'app.services.backup_service', 'app.routes.novel', 'app.routes.data'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AIWorldEngine',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AIWorldEngine',
)
