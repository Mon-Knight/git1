# AI World Engine - Windows Build Script
# Run this script from the project root to build the desktop EXE.
# v1.3.3: Added pre/post validation, process cleanup, dist file inclusion.

$ErrorActionPreference = "Stop"

Write-Host "=== AI World Engine Build Script ===" -ForegroundColor Cyan

# 0. Stop any running AIWorldEngine process
Write-Host "[0/7] Stopping any running AIWorldEngine process..." -ForegroundColor Yellow
Get-Process -Name AIWorldEngine -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# 1. Clean previous builds
Write-Host "[1/7] Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# 2. Pre-build validation: source templates must contain AI settings card
Write-Host "[2/7] Validating source templates..." -ForegroundColor Yellow
$indexSrc = Get-Content "app/templates/index.html" -Raw
if (-not ($indexSrc -match "AI 模型设置")) {
    Write-Host "WARNING: Source index.html missing 'AI 模型设置'" -ForegroundColor Yellow
}
if (-not ($indexSrc -match "配置 AI")) {
    Write-Host "WARNING: Source index.html missing '配置 AI' button" -ForegroundColor Yellow
}
if (-not ($indexSrc -match "/settings/ai")) {
    Write-Host "WARNING: Source index.html missing /settings/ai link" -ForegroundColor Yellow
}
Write-Host "  Source template check passed" -ForegroundColor Green

# 3. Build with PyInstaller (onedir mode)
Write-Host "[3/7] Running PyInstaller..." -ForegroundColor Yellow
$envPath = "C:/Users/17735/anaconda3/envs/aiworldengine"
& $envPath/python.exe -m PyInstaller --name AIWorldEngine --onedir --windowed --clean `
    --add-data "app/templates;app/templates" `
    --add-data "app/static;app/static" `
    --add-binary "$envPath/Library/bin/libssl-3-x64.dll;." `
    --add-binary "$envPath/Library/bin/libcrypto-3-x64.dll;." `
    --add-binary "$envPath/Library/bin/ffi.dll;." `
    --add-binary "$envPath/Library/bin/sqlite3.dll;." `
    --hidden-import uvicorn.logging `
    --hidden-import uvicorn.loops.auto `
    --hidden-import uvicorn.protocols.http.auto `
    --hidden-import sqlalchemy.sql.default_comparator `
    --hidden-import jinja2 `
    --hidden-import jinja2.ext `
    --hidden-import python_multipart `
    --hidden-import requests `
    --hidden-import app.services.ai `
    --hidden-import app.services.ai.base `
    --hidden-import app.services.ai.errors `
    --hidden-import app.services.ai.mock_client `
    --hidden-import app.services.ai.openai_compatible_client `
    --hidden-import app.services.ai.model_router `
    --hidden-import app.services.ai.prompt_builder `
    --hidden-import app.services.ai.response_parser `
    --hidden-import app.services.settings_service `
    desktop_launcher.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: PyInstaller build failed!" -ForegroundColor Red
    exit 1
}

# 4. Post-build validation: packed template must contain AI settings card
Write-Host "[4/7] Validating packed templates..." -ForegroundColor Yellow
$packedIndex = "dist/AIWorldEngine/_internal/app/templates/index.html"
$packedSettings = "dist/AIWorldEngine/_internal/app/templates/settings/ai.html"
if (Test-Path $packedIndex) {
    $packedContent = Get-Content $packedIndex -Raw
    $checksPassed = $true
    foreach ($keyword in @("AI 模型设置", "配置 AI", "/settings/ai")) {
        if ($packedContent -match [regex]::Escape($keyword)) {
            Write-Host "  OK: '$keyword' found in packed index.html" -ForegroundColor Green
        } else {
            Write-Host "  FAIL: '$keyword' NOT found in packed index.html" -ForegroundColor Red
            $checksPassed = $false
        }
    }
    if (Test-Path $packedSettings) {
        Write-Host "  OK: settings/ai.html packed" -ForegroundColor Green
    } else {
        Write-Host "  FAIL: settings/ai.html NOT packed" -ForegroundColor Red
        $checksPassed = $false
    }
    if (-not $checksPassed) {
        Write-Host "ERROR: Post-build validation failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "ERROR: Packed index.html not found — build may be broken" -ForegroundColor Red
    exit 1
}

# 5. Copy config files
Write-Host "[5/7] Copying config files..." -ForegroundColor Yellow
Copy-Item ".env.example" "dist/AIWorldEngine/.env.example" -Force
Copy-Item "packaging/README-Desktop.txt" "dist/AIWorldEngine/README-Desktop.txt" -Force

# 6. Build summary
Write-Host "[6/7] Build summary..." -ForegroundColor Yellow
$exePath = "dist/AIWorldEngine/AIWorldEngine.exe"
if (Test-Path $exePath) {
    $exeSize = (Get-Item $exePath).Length / 1MB
    Write-Host "  EXE: $exePath ($([math]::Round($exeSize, 1)) MB)" -ForegroundColor Cyan
    $totalSize = (Get-ChildItem -Recurse "dist/AIWorldEngine" | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  Total dist: $([math]::Round($totalSize, 1)) MB" -ForegroundColor Cyan
}

# 7. Done
Write-Host "[7/7] Build complete!" -ForegroundColor Green
Write-Host ""
Write-Host "EXE: dist/AIWorldEngine/AIWorldEngine.exe" -ForegroundColor Cyan
Write-Host "DB:  %LOCALAPPDATA%/AIWorldEngine/ai_world_engine.db" -ForegroundColor White
Write-Host "Log: %LOCALAPPDATA%/AIWorldEngine/logs/" -ForegroundColor White
