# Changelog

## [v0.3.0] — 2026-05-09

### Added
- 角色管理 CRUD（列表/创建/详情/编辑/删除）
- 势力管理 CRUD（列表/创建/详情/编辑/删除）
- 地点管理 CRUD（列表/创建/详情/编辑/删除）
- 世界规则管理 CRUD（列表/创建/详情/编辑/删除）
- 世界详情页模块入口激活（角色/势力/地点/规则）
- 跨世界数据隔离
- 44个新测试（角色11 + 势力11 + 地点11 + 规则11）

### Changed
- Location 模型新增 `important_events` 字段
- 世界详情页模块卡片：4个已激活 + 2个占位

## [v0.2.0] — 2026-05-09

### Added
- 世界管理 CRUD（创建/查看/编辑/删除）
- 世界列表页面 (`/worlds`)
- 创建世界页面 (`/worlds/new`)
- 世界详情页面 (`/worlds/{id}`)，含后续模块占位入口
- 编辑世界页面 (`/worlds/{id}/edit`)
- 世界服务层 (`app/services/world_service.py`)
- 世界路由 (`app/routes/worlds.py`)
- 表单校验（名称必填、长度限制）
- 404 错误页面
- 18个世界管理测试

### Notes
- 删除采用硬删除
- 详情页模块入口为占位，后续版本实现

## [v0.1.0] — 2026-05-09

### Added
- FastAPI 应用骨架 (`app/main.py`)
- 配置管理模块 (`app/config.py`)，支持 .env 环境变量
- SQLite 数据库初始化 (`app/database.py`)
- 8张数据模型表 (`app/models.py`): worlds, characters, factions, locations, world_rules, historical_events, simulation_records, branches
- 首页模板 (`app/templates/index.html`)
- 基础 CSS 样式 (`app/static/css/style.css`)
- AI 服务模块 (`app/services/ai_service.py`)，支持 Mock 和真实 API 双模式
- 18个基础测试，全部通过
- requirements.txt

### Notes
- 无 API Key 时自动使用 Mock AI 模式
- AI 推演结果不直接写入正史表

## [Unreleased]

### 2026-05-09 — 第一阶段：需求分析与架构设计
- 完成技术选型（Python/FastAPI/SQLite/Jinja2）
- 完成项目目录结构设计
- 完成数据库表设计（8张表：worlds, characters, factions, locations, world_rules, historical_events, simulation_records, branches）
- 完成 API 路由设计（10个路由模块）
- 完成 AI 服务模块设计（支持真实 API 和 Mock 模式）
- 完成页面结构设计（10个页面）
- 完成风险分析
- 创建项目文档体系
