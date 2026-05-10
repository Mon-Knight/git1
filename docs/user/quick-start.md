# 快速开始

## 环境要求

- Python 3.10+
- Windows / macOS / Linux

## 安装

```bash
# 1. 克隆项目
git clone https://github.com/Mon-Knight/git1.git
cd git1

# 2. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量（可选，不配置则使用 Mock AI）
copy .env.example .env

# 5. 启动服务
python -m uvicorn app.main:app --reload

# 6. 打开浏览器
# http://127.0.0.1:8000
```

## 运行测试

```bash
python -m compileall .
pytest tests/ -v
```

## 编码检查

```bash
python scripts/check_encoding.py
```

## 桌面端打包

```bash
powershell -ExecutionPolicy Bypass -File packaging/build_exe.ps1
# 输出位置：dist/AIWorldEngine/AIWorldEngine.exe
```

## 下一步

- [AI 设置指南](ai-settings.md)
- [桌面端使用说明](desktop-usage.md)
- [创作流程指南](workflow-guide.md)
