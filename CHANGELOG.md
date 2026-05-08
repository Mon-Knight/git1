# Changelog

## [v1.0.0] — 2026-05-09

### Stable Demo Release
- README 最终整理（功能总览、页面路径、安装说明、演示流程、AI配置、数据库说明、目录结构、已知限制、后续规划）
- 架构文档最终整理
- 安全审查最终总结
- TODO 更新后续计划
- 210 个测试全部通过

## [v0.8.0] — 2026-05-09

### Added
- 统一错误页面模板（errors/404.html, 400.html, 500.html）
- 44个润色测试（导航/错误页/空状态/表单错误/跨世界隔离/Git安全）

### Changed
- README 补充数据库开发说明和已知限制
- 页面导航一致性确认

## [v0.7.0] — 2026-05-09

### Added
- 设定矛盾检查（规则/事件/角色状态/势力关系/时间线）
- 角色行为合理性检查（性格/目标/能力/状态/势力立场）
- 检查中心页面
- 规则式检查 + Mock AI 辅助分析
- 检查结果不修改数据库（只读）
- 25个新测试

## [v0.6.0] — 2026-05-09

### Added
- 推演记录采纳为正史（创建 historical_events，is_canon=True）
- 推演记录保存为分支（创建 branches，不影响正史）
- 分支记录列表和详情页
- 记录状态流转：pending → adopted / branched
- 防止重复采纳、防止跨世界操作
- Branch 模型新增 updated_at 字段
- 25个新测试

## [v0.5.0] — 2026-05-09

### Added
- AI 推演页面（提交问题、查看结果）
- 世界上下文聚合服务（角色/势力/地点/规则/正史事件）
- 推演记录列表和详情页
- SimulationRecord 新增 simulation_type、context_snapshot、updated_at 字段
- 推演结果不直接写入正史（核心规则）
- 17个新测试（模拟10 + 记录7）

## [v0.4.0] — 2026-05-09

### Added
- 历史事件管理 CRUD（列表/创建/详情/编辑/删除）
- 时间线查看页面（正史/全部/非正史 三种视图）
- 正史与非正史事件区分
- 时间线按 event_time 排序
- 世界详情页新增历史事件和时间线入口
- 19个新测试（事件12 + 时间线7）

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
