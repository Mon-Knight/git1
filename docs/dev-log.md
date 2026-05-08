# Development Log — AI World Engine

## 2026-05-09 — v0.4.0: 历史事件和时间线管理

### 完成内容
- 历史事件 CRUD：service + routes + 5个模板
- 时间线查看：3种视图（canon/all/non_canon），query参数筛选
- 正史/非正史事件区分（is_canon 字段）
- 时间线按 event_time 文本排序（空值排最后）
- 世界详情页：历史事件和时间线入口已激活
- 19个新测试

### 修改文件
- `app/services/event_service.py` — 新建
- `app/services/timeline_service.py` — 新建
- `app/routes/events.py` — 新建
- `app/routes/timeline.py` — 新建
- `app/templates/events/` — 5个模板
- `app/templates/timeline/index.html` — 新建
- `app/templates/worlds/detail.html` — 激活事件+时间线入口
- `app/main.py` — 注册2个新路由
- `tests/test_events.py` — 新建（12个测试）
- `tests/test_timeline.py` — 新建（7个测试）
- `tests/test_worlds.py` — 更新占位测试
- `README.md` — 更新
- `CHANGELOG.md` — 更新
- `docs/dev-log.md` — 更新
- `docs/architecture.md` — 更新
- `docs/todo.md` — 更新

### 测试命令
```bash
pytest tests/ -v
```

### 测试结果
- 99 passed, 0 failed (v0.3.0: 80 + v0.4.0: 19)

### 备份路径
- `.project_backups/v0.4.0-20260509-0000.zip`

### commit 信息
- `feat: complete v0.4.0 event and timeline management`

### tag 信息
- `v0.4.0` — Version v0.4.0: event and timeline management

### push 结果
- main 分支推送成功
- v0.4.0 tag 推送成功

### 已知问题
- 无

### 下一步计划
- v0.5.0: AI 推演和推演记录

---

## 2026-05-09 — v0.3.0: 角色、势力、地点、世界规则管理 CRUD

### 完成内容
- 角色管理：service + routes + 5个模板（list/new/detail/edit/404）
- 势力管理：service + routes + 5个模板
- 地点管理：service + routes + 5个模板
- 世界规则管理：service + routes + 5个模板
- Location 模型新增 `important_events` 字段
- 世界详情页：角色/势力/地点/规则入口已激活
- 跨世界数据隔离（每个模块的列表仅显示当前世界数据）
- 表单校验（名称必填、长度限制）
- 44个新测试

### 修改文件
- `app/models.py` — Location 新增 important_events
- `app/main.py` — 注册 4 个新路由
- `app/services/character_service.py` — 新建
- `app/services/faction_service.py` — 新建
- `app/services/location_service.py` — 新建
- `app/services/rule_service.py` — 新建
- `app/routes/characters.py` — 新建
- `app/routes/factions.py` — 新建
- `app/routes/locations.py` — 新建
- `app/routes/rules.py` — 新建
- `app/templates/characters/` — 5个模板
- `app/templates/factions/` — 5个模板
- `app/templates/locations/` — 5个模板
- `app/templates/rules/` — 5个模板
- `app/templates/worlds/detail.html` — 激活模块入口
- `tests/test_characters.py` — 新建（11个测试）
- `tests/test_factions.py` — 新建（11个测试）
- `tests/test_locations.py` — 新建（11个测试）
- `tests/test_rules.py` — 新建（11个测试）
- `tests/test_worlds.py` — 更新占位测试
- `README.md` — 更新
- `CHANGELOG.md` — 更新
- `docs/dev-log.md` — 更新
- `docs/architecture.md` — 更新
- `docs/todo.md` — 更新

### 测试命令
```bash
pytest tests/ -v
```

### 测试结果
- 80 passed, 0 failed (v0.2.0: 36 + v0.3.0: 44)

### 备份路径
- `.project_backups/v0.3.0-20260509-0000.zip`

### commit 信息
- `feat: complete v0.3.0 core setting management`

### tag 信息
- `v0.3.0` — Version v0.3.0: character faction location rule CRUD

### push 结果
- main 分支推送成功
- v0.3.0 tag 推送成功

### 已知问题
- 无

### 下一步计划
- v0.4.0: 历史事件和时间线管理

---

## 2026-05-09 — v0.2.0: 世界项目管理 CRUD

### 完成内容
- 世界服务层 (`app/services/world_service.py`)：create_world, list_worlds, get_world, update_world, delete_world
- 世界路由 (`app/routes/worlds.py`)：7个端点，含表单校验
- 世界列表页 (`/worlds`)：卡片网格展示，含空状态提示
- 创建世界页 (`/worlds/new`)：表单含下拉选择器
- 世界详情页 (`/worlds/{id}`)：信息展示 + 6个模块占位入口
- 编辑世界页 (`/worlds/{id}/edit`)：预填表单
- 删除功能：硬删除 + JS确认弹窗
- 404 页面：世界不存在时友好提示
- 表单校验：名称必填、长度限制（name≤100, world_type≤50, current_era≤100, tone≤100）
- 新增 CSS 样式：导航、卡片、表单、空状态、模块网格
- 18个世界管理测试

### 修改文件
- `app/services/world_service.py` — 新建
- `app/routes/worlds.py` — 新建
- `app/templates/worlds/list.html` — 新建
- `app/templates/worlds/new.html` — 新建
- `app/templates/worlds/detail.html` — 新建
- `app/templates/worlds/edit.html` — 新建
- `app/templates/worlds/404.html` — 新建
- `app/static/css/style.css` — 新增样式
- `app/main.py` — 注册 worlds 路由
- `tests/test_worlds.py` — 新建
- `README.md` — 更新
- `CHANGELOG.md` — 更新
- `docs/dev-log.md` — 更新
- `docs/architecture.md` — 更新
- `docs/todo.md` — 更新

### 测试命令
```bash
pytest tests/ -v
```

### 测试结果
- 36 passed, 0 failed (v0.1.0: 18 + v0.2.0: 18)
- 世界测试覆盖：列表、创建、详情、编辑、删除、404、表单校验

### 备份路径
- `.project_backups/v0.2.0-20260509-0000.zip`

### commit 信息
- `feat: complete v0.2.0 world management`

### tag 信息
- `v0.2.0` — Version v0.2.0: world management CRUD

### push 结果
- main 分支推送成功
- v0.2.0 tag 推送成功

### 已知问题
- 无

### 下一步计划
- v0.3.0: 角色、势力、地点、规则管理 CRUD

---

## 2026-05-09 — v0.1.0: 项目骨架完成

### 完成内容
- FastAPI 应用入口 (`app/main.py`)，使用 lifespan 事件初始化数据库
- 配置管理 (`app/config.py`)，读取 .env 环境变量
- SQLite 数据库初始化 (`app/database.py`)
- 8张数据模型表 (`app/models.py`)
- 首页路由 (`app/routes/pages.py`)
- 首页模板 (`app/templates/index.html`)，展示系统名称、简介、功能卡片、版本号
- 基础 CSS (`app/static/css/style.css`)，暗色主题
- AI 服务模块 (`app/services/ai_service.py`)，Mock 模式 + 真实 API 模式
- 测试套件：18个测试，覆盖应用导入、首页响应、数据库表结构、Mock AI
- requirements.txt

### 修改文件
- `app/__init__.py` — 新建
- `app/main.py` — 新建
- `app/config.py` — 新建
- `app/database.py` — 新建
- `app/models.py` — 新建
- `app/routes/__init__.py` — 新建
- `app/routes/pages.py` — 新建
- `app/services/__init__.py` — 新建
- `app/services/ai_service.py` — 新建
- `app/templates/index.html` — 新建
- `app/static/css/style.css` — 新建
- `app/static/js/main.js` — 新建
- `tests/__init__.py` — 新建
- `tests/conftest.py` — 新建
- `tests/test_main.py` — 新建
- `tests/test_database.py` — 新建
- `tests/test_ai_service.py` — 新建
- `requirements.txt` — 新建
- `README.md` — 更新
- `CHANGELOG.md` — 更新
- `docs/dev-log.md` — 更新
- `docs/architecture.md` — 更新
- `docs/todo.md` — 更新

### 测试命令
```bash
python -m compileall app tests
pytest tests/ -v
```

### 测试结果
- 18 passed, 0 failed, 0 warnings
- 测试覆盖：应用导入、首页200、首页内容、版本号、健康检查、静态文件、数据库表结构（5个）、AI服务（7个）

### 备份路径
- `.project_backups/v0.1.0-20260509-0000.zip`

### commit 信息
- `feat: complete v0.1.0 project skeleton`

### tag 信息
- `v0.1.0` — Version v0.1.0: project skeleton

### push 结果
- main 分支推送成功
- v0.1.0 tag 推送成功

### 已知问题
- 无

### 下一步计划
- v0.2.0: 世界项目管理 CRUD

---

## 2026-05-09 — 第一阶段：需求分析与架构设计

### 完成内容
- Git 环境检查（main 分支，remote 指向 git1）
- GitHub CLI 认证确认（Mon-Knight，HTTPS）
- 技术选型确定
- 项目目录结构设计
- 数据库表设计（8张表）
- API 路由设计（10个路由模块）
- AI 服务模块设计
- 页面结构设计
- 风险分析

### 创建/修改文件
- `.gitignore` — 新建
- `.env.example` — 新建
- `docs/decision-log.md` — 新建
- `docs/architecture.md` — 新建
- `docs/todo.md` — 新建
- `docs/dev-log.md` — 新建
- `docs/security-review.md` — 新建
- `CHANGELOG.md` — 更新

### 已知问题
- 无（尚未开始编码）

### 下一步
- 等待用户确认第一阶段结果
- 开始 v0.1.0 编码（项目骨架、首页、数据库初始化）
