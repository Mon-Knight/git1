# AI World Engine - Windows Build Script
# Run this script from the project root to build the desktop EXE.

$ErrorActionPreference = "Stop"

Write-Host "=== AI World Engine Build Script ===" -ForegroundColor Cyan

# 1. Clean previous builds
Write-Host "[1/4] Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# 2. Build with PyInstaller (onedir mode)
Write-Host "[2/4] Running PyInstaller..." -ForegroundColor Yellow
C:/Users/17735/anaconda3/Scripts/conda.exe run -p C:\Users\17735\anaconda3 --no-capture-output python -m PyInstaller --name AIWorldEngine --onedir --windowed --clean --add-data "app/templates;app/templates" --add-data "app/static;app/static" --hidden-import uvicorn.logging --hidden-import uvicorn.loops.auto --hidden-import uvicorn.protocols.http.auto --hidden-import sqlalchemy.sql.default_comparator --hidden-import jinja2 --hidden-import jinja2.ext desktop_launcher.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: PyInstaller build failed!" -ForegroundColor Red
    exit 1
}

# 3. Copy .env.example (if not exists, create it)
Write-Host "[3/4] Copying config files..." -ForegroundColor Yellow
Copy-Item ".env.example" "dist/AIWorldEngine/.env.example" -Force

# 4. Done
Write-Host "[4/4] Build complete!" -ForegroundColor Green
Write-Host ""
Write-Host "EXE location: dist/AIWorldEngine/AIWorldEngine.exe" -ForegroundColor Cyan
Write-Host ""
Write-Host "To run: double-click dist/AIWorldEngine/AIWorldEngine.exe" -ForegroundColor White
Write-Host "Database will be saved to: %LOCALAPPDATA%/AIWorldEngine/ai_world_engine.db" -ForegroundColor White
