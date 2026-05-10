============================================================
  AI World Engine — 桌面版使用说明
  Version: v1.3.1
============================================================

【启动方式】
  双击 AIWorldEngine.exe 即可启动。

【重要提醒】
  ⚠️ 不能只复制 AIWorldEngine.exe！
  必须保留整个 AIWorldEngine 文件夹（包括 _internal 目录），
  否则程序将无法启动。

【数据位置】
  数据库文件：
    C:\Users\<用户名>\AppData\Local\AIWorldEngine\ai_world_engine.db
  日志文件夹：
    C:\Users\<用户名>\AppData\Local\AIWorldEngine\logs\
  日志文件：
    desktop.log  — 桌面端运行日志（所有级别）
    server.log   — 服务端日志
    error.log    — 错误日志（仅警告和错误）

【AI 设置】
  启动后在首页点击「AI 设置」，或直接访问：
    http://127.0.0.1:<port>/settings/ai

  支持两种模式：
  1. Mock AI — 无需 API Key，适合本地测试和演示
  2. OpenAI-compatible API — 需要配置 Base URL、Model、API Key
     支持：DeepSeek、小米 MiMo Token Plan、Ollama、本地模型等

  API Key 在页面上显示为脱敏形式（如 sk-1****abcd），
  不会显示完整内容，也不会写入任何配置文件。

【常见配置示例】
  DeepSeek:
    Base URL: https://api.deepseek.com/v1
    Model: 根据实际可用模型填写

  小米 MiMo Token Plan:
    Base URL: https://token-plan-cn.xiaomimimo.com/v1
    Model: 根据实际可用模型填写

  Ollama（本地）:
    Base URL: http://127.0.0.1:11434/v1
    Model: 本地模型名（如 qwen2）

【启动失败排查】
  1. 检查 logs/error.log 是否有错误信息。
  2. 确认 AIWorldEngine 文件夹完整（不要单独移动 .exe）。
  3. 确认 8000-9000 端口未被其他程序占用（程序会自动选择可用端口）。
  4. 如遇到 Windows Defender 拦截，允许程序运行即可。
  5. 日志位置：C:\Users\<用户名>\AppData\Local\AIWorldEngine\logs\

【功能说明】
  - 创建和管理小说世界观项目
  - 管理角色、势力、地点、规则
  - 管理历史事件和时间线
  - AI 推演（Mock 或真实 AI）
  - 推演记录可采纳为正史或保存为分支
  - 设定矛盾检查（规则式 + 可选 AI 补充）
  - 角色行为合理性检查

【GitHub 项目】
  https://github.com/Mon-Knight/git1

============================================================
