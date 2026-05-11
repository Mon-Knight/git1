# AI World Engine

AI 小说世界观推演系统 — 帮助作者构建小说世界观，通过 AI 推演世界发展。

> **当前版本**: v1.7.8 | **GitHub**: [Mon-Knight/git1](https://github.com/Mon-Knight/git1)
>
> **当前阶段**: 应用化阶段整理完成，进入桌面端窗口优化、响应式 UI 与 2K 适配（v1.7.7），后续为导出体验优化和设定库 AI 推演（v1.7.8–v1.7.10），以及分卷大纲（v1.8.0）。

---

## 当前核心能力

| 模块 | 说明 |
|------|------|
| 首页工作台 | 数据概览、最近世界、待处理事项、快捷操作 |
| 世界控制台 | 数据概览、创作进度、推荐下一步、功能分组导航 |
| 设定库 | 角色、势力、地点、规则的结构化管理 |
| 剧情历史 | 正史/非正史事件、时间线管理 |
| AI 推演 | 基于世界设定的推演，Mock AI + 真实 API 双模式 |
| 推演审核 | 推演记录 → 采纳为正史 / 保存为分支 |
| 小说工程 | 全书演化推演、演化方案管理 |
| 创作资产 | 风格方案、剧情时间点、创作上下文包 |
| 检查中心 | 设定矛盾检查、角色行为合理性检查 |
| 数据管理 | 世界 JSON 导出/导入、数据库备份/恢复 |
| Windows EXE | 双击启动，无需命令行 |

> 详细文档索引：[docs/README.md](docs/README.md)

---

## 快速开始

``bash
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

# 6. 打开浏览器 http://127.0.0.1:8000
``

> 详细安装指引：[docs/user/quick-start.md](docs/user/quick-start.md)

---

## Windows EXE 使用

AI World Engine 可打包为 Windows 桌面 EXE，双击即可启动。

``bash
# 打包
powershell -ExecutionPolicy Bypass -File packaging/build_exe.ps1

# 启动：双击 dist/AIWorldEngine/AIWorldEngine.exe
``

> 注意：必须分发整个 dist/AIWorldEngine/ 文件夹，不能只复制 EXE。
>
> 详细说明：[docs/user/desktop-usage.md](docs/user/desktop-usage.md) | 打包详情：[docs/technical/desktop-build.md](docs/technical/desktop-build.md)

---

## 页面入口

| 路径 | 说明 |
|------|------|
| / | 首页工作台 |
| /worlds | 世界列表 |
| /worlds/{id} | 世界控制台（含功能分组导航） |
| /worlds/{id}/characters | 角色管理 |
| /worlds/{id}/factions | 势力管理 |
| /worlds/{id}/locations | 地点管理 |
| /worlds/{id}/rules | 规则管理 |
| /worlds/{id}/events | 历史事件 |
| /worlds/{id}/timeline | 时间线 |
| /worlds/{id}/simulation | AI 推演 |
| /worlds/{id}/records | 推演记录 |
| /worlds/{id}/branches | 分支记录 |
| /worlds/{id}/checks | 检查中心 |
| /worlds/{id}/context | 创作上下文 |
| /worlds/{id}/novel/evolution | 全书演化推演 |
| /data | 数据管理 |
| /settings/ai | AI 设置 |

> 完整路由：[docs/technical/api-routes.md](docs/technical/api-routes.md)

---

## AI 模式与配置

| 模式 | 条件 | 说明 |
|------|------|------|
| **Mock AI** | 未配置 API Key | 规则式推演，适合测试演示 |
| **真实 API** | 已配置 API Key | 调用 OpenAI-compatible API（支持 DeepSeek / Ollama 等） |

AI 配置页面：/settings/ai（优先级：数据库 > .env）

> 详细配置指南：[docs/user/ai-settings.md](docs/user/ai-settings.md)

---

## 核心规则

- **AI 推演结果不会自动写入正史**，必须先保存为推演记录
- 用户需手动审核后选择「采纳为正史」或「保存为分支」
- 分支记录不影响正史时间线

---

## 当前版本路线

| 版本 | 目标 | 状态 |
|------|------|------|
| v1.7.5 | 模块分组与二级导航 | ✅ |
| v1.7.6 | 阶段性整理、文档体系重整与 EXE 验证 | ✅ |
| **v1.7.8** | **导出文件位置选择与导出体验优化** | **✅ 当前** |
| v1.7.7.1 | 左侧边栏可用性更新 | ✅ |
| v1.7.8 | 导出文件位置选择与导出体验优化 | 待开始 |
| v1.7.9 | 设定库 AI 推演基础版 | 待开始 |
| v1.7.10 | 候选设定采纳与测试补齐 | 待开始 |
| v1.8.0 | 基于主线方案的分卷大纲生成 | 待开始 |
| v1.9.0 | 章节大纲生成 | 待开始 |
| v2.0.0 | 正文初稿生成基础闭环 | 待开始 |

> 完整路线：[docs/project/version-roadmap.md](docs/project/version-roadmap.md)
> 版本历史：[CHANGELOG.md](CHANGELOG.md)

---

## 项目结构

``
app/                    # 应用代码
  main.py               # FastAPI 入口
  config.py             # 配置管理
  database.py           # 数据库连接
  models.py             # 数据模型
  routes/               # 16 个路由模块
  services/             # 18 个服务模块
  templates/            # HTML 模板
  static/               # CSS / JS
tests/                  # 测试（706 个）
scripts/                # 工具脚本
docs/                   # 文档
  user/                 # 用户文档
  project/              # 项目文档
  technical/            # 技术文档
  design/               # 设计文档
packaging/              # 打包脚本
``

---

## 技术栈

| 层面 | 技术 |
|------|------|
| 后端框架 | Python / FastAPI |
| 数据库 | SQLite (SQLAlchemy ORM) |
| 模板引擎 | Jinja2 |
| 前端 | HTML / CSS / JavaScript (原生) |
| AI 调用 | OpenAI-compatible API + Mock 模式 |
| 测试 | pytest (816 个测试) |

---

## 测试与构建

``bash
python -m compileall .               # 语法检查
pytest tests/ -v                     # 运行测试（816 个）
python scripts/check_encoding.py     # 编码检查
python scripts/verify_desktop_build.py --all  # 桌面构建验证
powershell -ExecutionPolicy Bypass -File packaging/build_exe.ps1  # 打包 EXE
``

> 测试体系说明：[docs/technical/testing.md](docs/technical/testing.md)

---

## 当前限制

- 暂不支持多用户和权限系统（单人本地应用）
- 暂不支持云端同步（本地 SQLite 存储）
- 无数据库迁移工具，模型变更需手动重建数据库
- AI 推演默认使用 Mock 模式，需配置 API Key 接入真实 AI
- 检查功能使用规则式关键词匹配，非 NLP 深度分析
- Windows EXE 仅支持 Windows 平台

---

## 文档索引

| 分类 | 入口 |
|------|------|
| 📖 用户文档 | [docs/user/](docs/user/) — 快速开始、桌面使用、AI 配置、数据导入导出、创作流程 |
| 📋 项目文档 | [docs/project/](docs/project/) — 版本路线、模块边界、UI 架构、开发规范 |
| ⚙️ 技术文档 | [docs/technical/](docs/technical/) — 架构、构建、部署、数据库、测试、API |
| 🎨 设计文档 | [docs/design/](docs/design/) — 小说工程、上下文资产、设定建议、交互式故事 |
| 📝 文档索引 | [docs/README.md](docs/README.md) |