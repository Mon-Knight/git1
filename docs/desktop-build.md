# Desktop Build Guide — AI World Engine

## 概述

AI World Engine 支持打包为 Windows 桌面端 EXE，使用户可以双击启动，无需手动打开终端。

## 技术方案

- **窗口框架**: pywebview（轻量级 WebView 桌面窗口）
- **后端**: FastAPI + uvicorn（后台线程运行）
- **打包工具**: PyInstaller（onedir 模式）
- **数据库**: SQLite（保存到 `%LOCALAPPDATA%\AIWorldEngine\ai_world_engine.db`）

## 环境要求

- Windows 10/11
- Python 3.10+
- 已安装项目依赖：`pip install -r requirements.txt`
- 需要 WebView2 运行时（Windows 10/11 通常已内置）

## 打包步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行打包脚本

在项目根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File packaging/build_exe.ps1
```

### 3. 输出位置

打包完成后，EXE 位于：

```
dist/AIWorldEngine/AIWorldEngine.exe
```

### 4. 启动

双击 `AIWorldEngine.exe` 即可启动桌面端。

## 数据库位置

桌面端数据库默认保存到：

```
C:\Users\<用户名>\AppData\Local\AIWorldEngine\ai_world_engine.db
```

如果设置了 `DATABASE_URL` 环境变量，则优先使用环境变量指定的路径。

## .env 配置

桌面端同样支持 `.env` 配置。将 `.env.example` 复制为 `.env` 并编辑：

```
AI_API_KEY=your_key_here
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o
```

`.env` 文件放在 EXE 所在目录即可。

## 常见错误

### WebView2 未安装

如果启动时报错找不到 WebView2，请下载安装：

https://developer.microsoft.com/microsoft-edge/webview2/

Windows 11 通常已内置，Windows 10 可能需要手动安装。

### 端口被占用

桌面启动器会自动寻找可用端口（8000-9000）。如果该范围所有端口都被占用，启动会失败。

### 数据库文件损坏

如果数据库文件损坏，删除以下目录后重新启动：

```
C:\Users\<用户名>\AppData\Local\AIWorldEngine\
```

### 打包后资源文件找不到

确保打包脚本中包含 `--add-data` 参数，将 `app/templates` 和 `app/static` 打包进 EXE。

## 重新打包

修改代码后重新打包：

```powershell
powershell -ExecutionPolicy Bypass -File packaging/build_exe.ps1
```

## 开发者运行

开发时可以直接用 Python 运行：

```bash
# 桌面模式（pywebview 窗口）
python desktop_launcher.py

# 服务器模式（浏览器访问）
python -m uvicorn app.main:app --reload
```
