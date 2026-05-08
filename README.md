# AI World Engine

AI 小说世界观推演系统 — 帮助作者构建小说世界观，通过 AI 推演世界发展。

> **当前版本**: v1.0.0 | **GitHub**: [Mon-Knight/git1](https://github.com/Mon-Knight/git1)

---

## 技术栈

| 层面 | 技术 |
|------|------|
| 后端框架 | Python / FastAPI |
| 数据库 | SQLite (SQLAlchemy ORM) |
| 模板引擎 | Jinja2 |
| 前端 | HTML / CSS / JavaScript (原生) |
| AI 调用 | OpenAI-compatible API + Mock 模式 |
| 测试 | pytest (210 个测试) |

---

## 功能总览

| 模块 | 说明 |
|------|------|
| 首页 | 系统介绍、世界列表入口 |
| 世界管理 | 创建/查看/编辑/删除世界项目 |
| 角色管理 | 管理角色（姓名、身份、性格、目标、能力、状态） |
| 势力管理 | 管理势力（类型、领袖、目标、资源、敌对/盟友） |
| 地点管理 | 管理地点（类型、区域、描述、控制势力） |
| 规则管理 | 管理世界规则（类型、内容、限制条件、影响范围） |
| 历史事件 | 管理历史事件（正史/非正史、涉及角色/势力/地点） |
| 时间线 | 按时间查看正史/全部/非正史事件，支持筛选 |
| AI 推演 | 基于世界设定推演发展，Mock AI + 真实 API 双模式 |
| 推演记录 | 查看推演历史，采纳为正史 / 保存为分支 |
| 分支记录 | 查看独立分支世界线，不影响正史 |
| 检查中心 | 设定矛盾检查 + 角色行为合理性检查 |

---

## 页面路径总览

| 路径 | 说明 |
|------|------|
| `/` | 首页 |
| `/worlds` | 世界列表 |
| `/worlds/new` | 创建世界 |
| `/worlds/{id}` | 世界详情（10 个模块入口） |
| `/worlds/{id}/edit` | 编辑世界 |
| `/worlds/{id}/characters` | 角色管理 |
| `/worlds/{id}/factions` | 势力管理 |
| `/worlds/{id}/locations` | 地点管理 |
| `/worlds/{id}/rules` | 规则管理 |
| `/worlds/{id}/events` | 历史事件 |
| `/worlds/{id}/timeline` | 时间线（?view=canon/all/non_canon） |
| `/worlds/{id}/simulation` | AI 推演 |
| `/worlds/{id}/records` | 推演记录 |
| `/worlds/{id}/branches` | 分支记录 |
| `/worlds/{id}/checks` | 检查中心 |
| `/worlds/{id}/checks/conflicts` | 设定矛盾检查 |
| `/worlds/{id}/checks/behavior` | 角色行为合理性检查 |
| `/health` | 健康检查 |

---

## 项目目录结构

```
app/
  main.py                  # FastAPI 入口
  config.py                # 配置管理
  database.py              # 数据库连接
  models.py                # 数据模型（8 张表）
  routes/                  # 10 个路由模块
  services/                # 11 个服务模块
  templates/               # 30+ 模板文件
  static/                  # CSS / JS
tests/                     # 11 个测试文件，210 个测试
scripts/                   # 工具脚本
docs/                      # 设计文档
.project_backups/          # 本地备份（不入 Git）
requirements.txt
.env.example
.gitignore
```

---

## 安装与运行

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

### 运行测试

```bash
python -m compileall .
pytest tests/ -v
```

### 编码检查

```bash
python scripts/check_encoding.py
```

---

## 环境变量配置 (.env)

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `AI_API_KEY` | AI API 密钥（为空则使用 Mock AI） | (空) |
| `AI_BASE_URL` | AI API 地址 | `https://api.openai.com/v1` |
| `AI_MODEL` | AI 模型名称 | `gpt-4o` |
| `DATABASE_URL` | 数据库连接字符串 | `sqlite:///./ai_world_engine.db` |
| `APP_HOST` | 服务监听地址 | `127.0.0.1` |
| `APP_PORT` | 服务端口 | `8000` |
| `APP_DEBUG` | 调试模式 | `false` |

> **安全提醒**: `.env` 文件包含敏感信息，已加入 `.gitignore`，不会被提交到 Git。

---

## AI 模式说明

| 模式 | 条件 | 说明 |
|------|------|------|
| **Mock AI** | `AI_API_KEY` 为空 | 使用规则式推演，适合本地测试和演示 |
| **Live API** | 已配置 `AI_API_KEY` | 调用 OpenAI-compatible API 进行真实推演 |

### 核心规则

- **AI 推演结果不会自动写入正史**，必须先保存为推演记录（`simulation_records`）
- 用户需手动审核后选择「采纳为正史」或「保存为分支」
- 采纳后创建 `historical_events` 记录（`is_canon=True`, `source_type=simulation`）
- 分支记录不影响正史时间线

### 推演记录状态

| 状态 | 说明 | 可操作 |
|------|------|--------|
| `pending` | 待处理 | 采纳为正史 / 保存为分支 |
| `adopted` | 已采纳 | 已写入时间线 |
| `branched` | 已分支 | 已保存为独立分支 |
| `discarded` | 已废弃 | 预留状态 |

---

## 数据库说明

| 项目 | 说明 |
|------|------|
| 数据库 | SQLite |
| 默认文件 | `ai_world_engine.db`（项目根目录） |
| Git 提交 | 不提交（已加入 `.gitignore`） |
| 迁移工具 | 当前版本暂未引入 Alembic |
| 开发阶段 | 模型字段变更后可删除 `.db` 文件，重启项目自动重建 |
| 生产建议 | 后续版本建议加入数据库迁移工具 |

### 数据备份

每个稳定版本在 `.project_backups/` 目录下有对应的 ZIP 备份包：

```
.project_backups/
  v0.1.0-20260509-0000.zip
  v0.2.0-20260509-0000.zip
  ...
  v1.0.0-20260509-0000.zip
```

> `.project_backups/` 已加入 `.gitignore`，不会被提交到 Git。

---

## Docker / 正式使用准备

当前版本为本地开发版。如需部署到生产环境：

1. 使用 Gunicorn + Uvicorn workers 替代 `uvicorn --reload`
2. 配置反向代理（Nginx / Caddy）
3. 迁移到 PostgreSQL（修改 `DATABASE_URL`）
4. 引入 Alembic 管理数据库迁移
5. 添加用户认证和权限系统
6. 配置真实的 AI API Key

---

## 已完成版本记录

| 版本 | 内容 | 测试数 |
|------|------|--------|
| v0.1.0 | 项目骨架、首页、数据库初始化 | 18 |
| v0.2.0 | 世界管理 CRUD | 36 |
| v0.3.0 | 角色、势力、地点、规则 CRUD | 80 |
| v0.4.0 | 历史事件、时间线管理 | 99 |
| v0.5.0 | AI 推演、推演记录 | 116 |
| v0.6.0 | 采纳为正史、分支记录 | 141 |
| v0.7.0 | 设定矛盾检查、角色行为检查 | 166 |
| v0.8.0 | 页面优化、错误处理、测试完善 | 210 |
| v1.0.0 | 稳定展示版 | 210 |

---

## 演示流程

1. 启动项目 → 打开 `http://127.0.0.1:8000`
2. 首页展示系统简介 → 点击「进入世界列表」
3. 创建世界项目（如「艾泽拉斯」奇幻世界）
4. 进入世界详情 → 创建角色、势力、地点、规则
5. 创建历史事件 → 标记为正史
6. 查看时间线 → 正史事件按时间排列
7. 进入 AI 推演 → 输入推演问题
8. 查看推演结果 → 推演记录列表
9. 将推演记录「采纳为正史」→ 时间线新增事件
10. 将另一条推演记录「保存为分支」→ 分支独立保存
11. 进入检查中心 → 运行设定矛盾检查
12. 运行角色行为合理性检查

---

## 已知限制

- 单用户本地应用，无多用户和权限系统
- 无数据库迁移工具，模型变更需手动重建数据库
- AI 推演默认使用 Mock 模式，需配置 API Key 才能接入真实 AI
- 检查功能使用规则式关键词匹配，非 NLP 深度分析

---

## 后续规划

1. 多用户登录与权限管理
2. Alembic 数据库迁移
3. 正式 AI API 深度接入
4. 分支对比和分支合并
5. 角色关系图谱
6. 时间线可视化
7. Flutter App / 桌面端
8. 本地大模型接入
9. 数据导出功能
