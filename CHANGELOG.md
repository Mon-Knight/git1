# Changelog

## [v1.7.1] — 2026-05-11

### Added
- 新增 development-rules.md（开发规范与不可破坏规则）
- 新增 version-roadmap.md（v1.7.1～v2.4.0+ 完整版本路线）
- 新增 ui-information-architecture.md（9 模块应用信息架构）
- 新增 agent-task-rules.md（Agent 开发前/中/后必须遵守的规则）
- 新增 module-boundaries.md（7 大模块边界与依赖关系）

### Changed
- README 增加应用化路线说明、当前小说工程能力说明
- 明确 v1.7.x 为应用化补课阶段
- 明确 v1.8.0 之后再进入分卷大纲

### Notes
- 本版本不新增业务功能
- 本版本不修改数据库结构
- 本版本不开发分卷、章节、正文
- 本版本用于防止后续 Agent 开发混乱

## [v1.7.0] — 2026-05-11

### Added
- 新增基于创作上下文包的全书演化推演（`/novel/evolution`）
- 新增 NovelEvolutionService（结构化 Prompt 构建、context_snapshot、方案管理）
- 新增全书演化方案列表页（`/novel/evolutions`）和详情页
- 新增方案状态操作：设为主线方案 / 设为备选方案 / 废弃方案
- 状态映射：adopted→主线方案 / branched→备选方案 / discarded→已废弃
- 世界详情页新增「全书演化推演」和「演化方案列表」入口
- 上下文包详情页新增「用于全书演化推演」区域和快捷入口
- Mock AI 输出升级为 12 章节结构化全书演化方案
- 新增 3 个模板（evolution_form/evolutions/evolution_detail）
- 新增 19 个服务层测试 + 28 个路由测试 + 5 个导出导入测试
- build 系统同步更新（spec/build_exe.ps1/verify）

### Design
- 方案 B：复用 simulation_records.status，不新增字段
- 允许多个主线方案（不做唯一约束）
- AI 生成结果不自动写入正史
- 方案状态操作不创建 historical_events

### Notes
- v1.7.0 不做正文生成、分卷大纲、章节大纲
- v1.7.0 不做参考小说导入和自动风格分析
- v1.7.0 只是全书演化推演增强版

## [v1.6.0] — 2026-05-11

### Added
- 新增创作上下文资产库基础版
- 新增 StyleProfile 写作风格方案管理（创建/编辑/删除/全局风格）
- 新增 PlotAnchor 剧情时间点管理（创建/编辑/删除/跨世界隔离）
- 新增 ContextPackage 创作上下文包（组合推演方案/风格/时间点）
- 新增小说生成页面上下文包下拉选择
- 上下文包选中后自动加载推演方案/风格/剧情时间点到生成 Prompt
- simulation_records 新增 context_snapshot 包含上下文包信息
- 新增 3 个服务文件：style_profile_service / plot_anchor_service / context_package_service
- 新增 context 路由（14 个端点）
- 新增 8 个 context 模板页面
- 世界详情页新增「创作上下文」入口卡片
- 导出/导入兼容 StyleProfile / PlotAnchor / ContextPackage
- 导入自动 ID 映射（sim_record / style / anchor / context_package）
- 导出自动包含被引用的全局风格方案
- 备份服务 metadata 新增 context 表计数
- 新增 29 个服务测试 + 26 个路由测试 + 5 个导出/导入测试
- build_exe.ps1 / AIWorldEngine.spec 新增 context 路由和模板
- verify_desktop_build.py 新增 context 模板检查

### Design Principles
- AI 生成内容不自动成为正史
- 风格方案只是写作约束，不改变剧情事实
- 剧情时间点只是进度记录，不自动改写历史
- 上下文包只是引用组合，不复制重复内容
- 跨世界数据完全隔离
- 删除被引用资产时有安全保护（提示先移除引用）

### Notes
- v1.6.0 不做正文生成完整流水线
- v1.6.0 不做分卷大纲/章节大纲
- v1.6.0 不做参考小说导入和自动风格分析
- v1.6.0 不做风格一致性评分和复杂小说项目管理
- 本版本只是创作上下文资产库基础版

## [v1.5.0] — 2026-05-11

### Added
- 新增数据管理页面 /data（导入/导出/备份/恢复）
- 新增单世界 JSON 导出功能（含角色/势力/地点/规则/事件/推演记录/分支）
- 新增世界 JSON 导入功能（自动创建新世界，重名自动重命名，事务保护）
- 新增数据库一键备份（含 metadata JSON + SHA256 校验）
- 新增数据库备份恢复（恢复前自动备份，确认机制）
- 新增 EXE 模式 AppData backups/ 目录
- 新增 export_service / import_service / backup_service
- 新增 22 个数据服务测试 + 12 个路由测试
- 世界详情页新增「导出世界」按钮
- 首页新增「数据管理」入口
- .gitignore 新增 backups/

### Security
- 导出文件不包含 app_settings
- 导出文件不包含 AI API Key
- 导出文件不包含 .env 和日志
- 恢复数据库前自动备份当前数据库

### Notes
- v1.5.0 不包含云同步、多用户、PostgreSQL、Alembic
- v1.5.0 不包含正文生成和章节大纲

## [v1.4.0] — 2026-05-11

### Added
- 新增小说工程模式 /worlds/{id}/novel
- 新增世界详情页"小说工程模式"入口卡片
- 新增 novel_evolution 推演类型（app/constants.py）
- 新增 PromptBuilder.build_novel_evolution_prompt 方法
- 新增小说工程表单页面（app/templates/novel/form.html）
- 新增小说工程路由（app/routes/novel.py）
- Mock AI 支持小说工程推演（结构化 14 板块输出）
- 推演记录列表显示"小说工程推演"类型标签
- 推演记录 detail 页显示类型中文名称
- 新增 3 个小说工程路由测试、14 个 PromptBuilder 测试、10 个集成测试
- build_exe.ps1 和 AIWorldEngine.spec 同步更新 hidden imports（app.routes.novel）
- desktop_launcher.py 同步更新 PyInstaller imports

### Changed
- ModelRouter TASK_MODEL_KEYS 新增 novel_evolution（使用 ai_simulation_model）
- records 列表和详情页使用 Jinja2 全局函数 get_type_label 显示类型
- 复用现有 AI 推演、推演记录、采纳正史和保存分支流程

### Notes
- v1.4.0 只实现"全书演化方向推演"
- 不做正文生成、章节大纲、参考小说分析、复杂小说项目管理
- 小说工程推演结果保存为 simulation_records，simulation_type=novel_evolution
- 用户仍通过原有记录页面手动采纳或保存分支

## [v1.3.5] — 2026-05-11

### Fixed
- 修复 PyInstaller EXE 无控制台环境下 uvicorn logging DefaultFormatter 调用 isatty() 崩溃
- 修复 EXE 后端启动后 health check 一直 timeout 的问题（根因：uvicorn 在 log_config 配置阶段崩溃）
- 修复桌面端日志中 Unicode 特殊符号在 Windows PowerShell 下显示乱码的问题

### Changed
- uvicorn log_config 改用纯 Python logging.Formatter（移除 DefaultFormatter/AccessFormatter/use_colors）
- 启动 uvicorn 前调用 ensure_stdio_available() 补齐可能为 None 的 sys.stdout/stderr
- 桌面端自检日志统一改为 ASCII 标记：[OK]、[WARN]、[ERROR]

## [v1.3.4] — 2026-05-11

### Fixed
- 修复 EXE 启动后内置后端服务（uvicorn/FastAPI）无法启动的问题
- 修复 server.log 始终为空的问题（增加 uvicorn log_config + 文件 handler）
- 修复 SQLite URL 在 Windows 使用反斜杠的问题（改为 Path.as_posix()）
- 修复后端线程异常无法追踪（start_server 包裹 BaseException + traceback 写入 server.log）
- 修复 wait_for_server 超时无诊断信息的问题（每次失败记录异常类型）

### Added
- 桌面端 headless 模式（AIWORLDENGINE_HEADLESS=1），方便自动验证
- 启动失败时弹出 Windows 错误提示框（含日志路径）
- 打包脚本新增 uvicorn/h11/anyio/starlette/fastapi/asyncio 等 hidden imports
- spec 文件同步新增所有 uvicorn 内部模块 hidden imports

### Changed
- desktop_launcher.py v1.3.4 全面重写后端启动逻辑
  - uvicorn 使用 loop="asyncio", http="h11"（避免二进制依赖）
  - 所有后端异常写入 server.log + error.log
  - Health check 轮询记录每次失败原因

## [v1.3.3] — 2026-05-11

### Fixed
- 修复 EXE 打包后首页没有 AI 配置按钮的问题（根因：旧 dist 未清理重新打包）
- 构建脚本现在构建前自动停止旧进程、清理旧 build/dist
- 构建脚本现在构建后自动验证打包模板内容正确性

### Added
- 新增 scripts/verify_desktop_build.py 构建验证脚本（支持 --src / --dist / --all）
- 新增 app/constants.py 集中定义 simulation_type 常量（为 v1.4.0 小说工程模式准备）
- 构建后自动校验：打包后的 index.html 必须包含「AI 模型设置」「配置 AI」「/settings/ai」
- 构建后自动校验 settings/ai.html 是否被打包
- 打包脚本自动将 README-Desktop.txt 复制到 dist/

### Changed
- packaging/build_exe.ps1 重写：7 步构建流程，含进程清理、模板预检、打包后验证、构建摘要
- packaging/AIWorldEngine.spec 和 build_exe.ps1 保持一致的 hidden imports

## [v1.3.2] — 2026-05-11

### Fixed
- 修复 EXE 端首页缺少 AI 设置入口的问题
- 首页新增"AI 模型设置"卡片，含显著"⚙️ 配置 AI"按钮指向 /settings/ai
- 首页 AI 状态显示不泄露完整 API Key

### Added
- 首页显示当前 AI 模式（Mock AI / OpenAI-compatible / 配置不完整）
- 首页显示当前模型名称和 API Key 已设置/未设置状态
- SettingsService.get_ai_summary() 安全摘要方法（不返回完整 API Key）
- 新增 10 个首页 AI 入口和 get_ai_summary 测试

### Changed
- 首页路由传入 ai_summary，提供安全的 AI 配置摘要
- 完善首页 AI 配置引导文案

## [v1.3.1] — 2026-05-11

### Added
- 新增桌面端启动自检（模板、静态文件、AI模块、数据库目录、端口、app_settings表）
- 新增桌面端日志系统（desktop.log、server.log、error.log）
- 新增 EXE 分发说明文件（packaging/README-Desktop.txt）
- 新增浏览器回退模式（WebView不可用时自动用系统浏览器）
- 新增 44 个桌面端测试（日志/自检/AI配置持久化/构建配置验证）

### Fixed
- 修复 EXE 启动失败时缺少日志的问题
- 修复桌面端启动异常无日志记录的问题
- 修复 WebView 启动失败时直接退出的问题（改为浏览器回退）
- 修复 self-check 中数据库目录写入权限检测不够健壮的问题

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
