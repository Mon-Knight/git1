# Changelog

## [v1.3.0] — 2026-05-11

### Added
- 新增 AI 设置页面(/settings/ai)：配置 AI 提供商、Base URL、API Key、模型、Temperature、Max Tokens、Timeout
- 新增 app_settings 配置表（数据库存储运行时配置，优先级：DB > .env > 默认值）
- 新增 OpenAI-compatible API 客户端，支持 DeepSeek、MiMo Token Plan、Ollama 等兼容接口
- 新增 Mock AI / 真实 AI 模式切换
- 新增模型路由(ModelRouter)：支持按任务类型（推演/检查/总结）选择不同模型
- 新增 PromptBuilder：集中构建推演和检查提示词
- 新增 ResponseParser：格式化 AI 输出为页面展示可用结构
- 新增 AI 连接测试功能（POST /settings/ai/test）
- 推演页面支持真实 AI + 显示当前 AI 模式和模型信息
- 检查中心支持规则式检查 + 可选 AI 补充分析
- 新增 AI 配置与错误处理测试（77 个新测试）
- 新增 app/services/ai/ 模块化 AI 服务层

### Changed
- 重构 AI 服务层(ai_service.py)，保留旧 Mock AI 兼容入口并委托新模块
- SimulationService 使用 ModelRouter 进行 AI 调用，失败时不创建空推演记录
- CheckService 使用 ModelRouter 进行 AI 调用，失败时优雅降级保留规则式检查结果
- 检查中心在 AI 不可用时显示回退提示
- PyInstaller 打包脚本新增 AI 服务模块 hidden imports

### Fixed
- AI 请求失败时不再导致页面 500
- API Key 页面显示脱敏（前 4 + **** + 后 4）
- Live AI 失败时不创建空推演记录
- 检查中心 AI 失败不影响规则式检查结果展示

### Notes
- 不新增多用户、权限系统、PostgreSQL、Alembic、云部署
- 推演记录不会自动写入正史，必须手动采纳或保存为分支
- 检查中心只读，不修改数据库

## [v1.2.2] — 2026-05-11

### Changed
- 文档整理：README.md 版本号从 v1.0.0 更新为 v1.2.2
- 代码中 VERSION 统一更新为 1.2.2（app/config.py）
- README 增加「Windows EXE 分发说明」：必须分发整个 dist/AIWorldEngine 文件夹
- README 增加「当前适用场景」：单人本地世界观推演、Windows 桌面端等
- README「已知限制」重命名为「已知限制 / 当前限制」，明确暂不支持多用户/权限/云端同步
- CHANGELOG.md v1.2.1 条目补充
- 版本记录表补充 v1.2.1、v1.2.2

### Notes
- 本次为发布整理版，不新增复杂业务功能
- 核心业务逻辑未改动

## [v1.2.1] — 2026-05-09

### Fixed
- PyInstaller 打包修复：添加 conda 环境缺失 DLL（libssl、libcrypto、ffi、sqlite3）
- desktop_launcher.py 修复：使用直接 import 替代字符串 uvicorn.run
- requirements.txt 新增 python-multipart 依赖
- build_exe.ps1 更新：包含所有必要 DLL
- EXE 打包验证通过：启动、首页、CSS、数据库、数据持久化

## [v1.2.0] — 2026-05-09

### Added
- desktop_launcher.py（pywebview 桌面窗口 + 后台 uvicorn）
- resource_path 工具函数（PyInstaller 兼容）
- 桌面模式数据库路径（AppData/Local/AIWorldEngine/）
- packaging/build_exe.ps1（PyInstaller onedir 打包脚本）
- docs/desktop-build.md（打包说明文档）
- 自动端口选择（8000-9000）
- 8个桌面/打包相关测试

### Notes
- PyInstaller 打包需要干净的 venv（conda base 环境包太多导致分析缓慢）
- 使用 --onedir 模式，输出为 dist/AIWorldEngine/

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
