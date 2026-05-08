# Changelog

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
