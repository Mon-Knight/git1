# Windows 桌面端使用说明

AI World Engine 支持打包为 Windows 桌面 EXE，双击即可启动。

## 启动方式

### 方式一：直接运行 EXE

1. 获取 `dist/AIWorldEngine/` 文件夹（整个文件夹，不是单个 EXE）
2. 双击 `AIWorldEngine.exe`
3. 浏览器将自动打开 `http://127.0.0.1:8000`

### 方式二：源码桌面模式

```bash
python desktop_launcher.py
```

## 数据存储

- **数据库位置**: `C:\Users\<用户名>\AppData\Local\AIWorldEngine\ai_world_engine.db`
- 用户数据、推演记录、分支记录均保存在此 SQLite 数据库中
- 卸载 EXE 不会自动删除数据库（如需清理可手动删除该目录）

## 分发说明

> ⚠️ **重要**：不能只复制 `AIWorldEngine.exe`！必须分发整个 `dist/AIWorldEngine/` 文件夹。

分发方式：将整个 `dist/AIWorldEngine/` 文件夹压缩为 ZIP，分发给使用者。

EXE 结构：`dist/AIWorldEngine/` 目录包含 EXE、DLL、Python 运行时、模板、静态资源等，缺少任何文件都可能导致启动失败。

## 技术细节

详见 [桌面端打包说明](../technical/desktop-build.md)。
