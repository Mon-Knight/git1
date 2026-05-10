# Development Log — AI World Engine

## 2026-05-11 — v1.3.3: EXE 构建同步修复与推演系统整理

### 问题根因
- 打包后 EXE 的 `dist/AIWorldEngine/_internal/app/templates/index.html` 是旧版本（无 AI 设置卡片）
- `build_exe.ps1` 构建前虽清理了 dist，但之前用户运行的是未重新打包的旧 dist
- 缺少构建后验证步骤，无法自动检测打包模板是否正确

### 修复内容
1. build_exe.ps1 重写为 7 步流程：
   - 步骤 0：停止旧 AIWorldEngine 进程
   - 步骤 1：清理旧 build/dist
   - 步骤 2：源码模板预检（含 AI 设置关键字检查）
   - 步骤 3：PyInstaller 打包
   - 步骤 4：打包后模板验证（必须含 AI 设置卡片 + settings/ai.html）
   - 步骤 5：复制 README-Desktop.txt 到 dist
   - 步骤 6-7：构建摘要
2. 新增 scripts/verify_desktop_build.py：支持 --src / --dist / --all 模式验证
3. 新增 app/constants.py：simulation_type 常量集中管理（为 v1.4.0 准备）
4. 版本号更新为 v1.3.3

### 修改文件
- `packaging/build_exe.ps1` — 重写：7 步构建流程 + 预检 + 打包后验证
- `scripts/verify_desktop_build.py` — 新建：构建验证脚本
- `app/constants.py` — 新建：simulation_type 常量
- `app/config.py` — VERSION → 1.3.3
- `tests/test_desktop.py` — 版本断言更新
- `tests/test_main.py` — 版本断言更新
- `README.md` — 版本号、版本记录更新
- `CHANGELOG.md` — v1.3.3 条目
- `docs/dev-log.md` — 本条记录

### 测试命令 / 结果
- python -m compileall . ✅
- pytest tests/ -v ✅
- python scripts/check_encoding.py ✅
- python scripts/verify_desktop_build.py --src ✅

### EXE 打包验证
- powershell -ExecutionPolicy Bypass -File packaging/build_exe.ps1 ✅
- dist/AIWorldEngine/AIWorldEngine.exe 存在 ✅
- 打包后 index.html 包含「AI 模型设置」✅
- 打包后 index.html 包含「配置 AI」✅
- 打包后 settings/ai.html 存在 ✅

### 已知问题
- 无

---

## 2026-05-11 — v1.3.2: EXE 首页 AI 设置入口修复

### 完成内容
- 首页新增「AI 模型设置」卡片区域，含「⚙️ 配置 AI」主按钮
- Mock 模式下首页显示引导文案
- 已配置 AI 时显示当前模式、模型名、API Key 状态
- 配置不完整时显示警告提示
- SettingsService 新增 get_ai_summary() 方法（安全，不泄露完整 API Key）
- pages.py 首页路由传入 ai_summary 数据
- 新增 7 个首页 AI 入口测试
- 版本号更新为 v1.3.2

### 修改文件
- `app/templates/index.html` — 新增 AI 设置卡片和配置 AI 按钮
- `app/routes/pages.py` — 首页传入 ai_summary
- `app/services/settings_service.py` — 新增 get_ai_summary()
- `app/config.py` — VERSION → 1.3.2
- `tests/test_main.py` — 版本断言更新 + 7 个新测试
- `tests/test_desktop.py` — 版本断言更新
- `README.md` — 版本号、版本记录更新
- `CHANGELOG.md` — v1.3.2 条目
- `docs/dev-log.md` — 本条记录

### 测试命令 / 结果
- python -m compileall . ✅
- pytest tests/ -v ✅（357 passed）
- python scripts/check_encoding.py ✅

### 已知问题
- 无

---

## 2026-05-11 — v1.3.1: EXE 桌面端稳定化 + 日志系统 + 启动自检

### 完成内容
- desktop_launcher.py 全面重写：新增日志系统、启动自检、浏览器回退
- 桌面端日志目录：AppData/Local/AIWorldEngine/logs/（desktop.log、server.log、error.log）
- 启动自检项目：版本号、PyInstaller 模式、模板/静态文件定位、AI模块导入、数据库目录、端口
- 新增 packaging/README-Desktop.txt 分发说明文件
- 44 个新测试全部通过（日志/自检/AI配置持久化/构建配置）
- 版本号更新为 1.3.1

### 修改文件
- `desktop_launcher.py` — 新增日志系统、启动自检、Health检查输出、浏览器回退
- `packaging/README-Desktop.txt` — 新建
- `app/config.py` — VERSION → 1.3.1
- `tests/test_desktop.py` — 版本号断言更新
- `tests/test_main.py` — 版本号断言更新
- `tests/test_desktop_logging.py` — 新建
- `tests/test_desktop_self_check.py` — 新建
- `tests/test_desktop_ai_settings.py` — 新建
- `tests/test_build_config.py` — 新建
- `README.md` — 版本号、测试数更新
- `CHANGELOG.md` — v1.3.1 条目
- `docs/dev-log.md` — 本条记录

### 测试命令 / 结果
- python -m compileall . ✅
- pytest tests/ -v ✅ (347 passed)
- python scripts/check_encoding.py ✅

### 已知问题
- 无

---

## 2026-05-11 — v1.3.0: 正式 AI API 接入 + AI 设置页面 + 模型路由

### 完成内容
- 新增 app_settings 配置表（数据库优先级高于 .env）
- 新增 app/services/settings_service.py 配置管理
- 新增 app/services/ai/ 模块化 AI 服务层
  - base.py（统一 AIClient 接口）
  - errors.py（HTTP/异常错误映射）
  - mock_client.py（Mock AI 实现）
  - openai_compatible_client.py（OpenAI-compatible API 客户端）
  - model_router.py（任务类型路由 + 模型选择）
  - prompt_builder.py（推演/检查提示词构建）
  - response_parser.py（AI 输出解析与格式化）
- 新增 AI 设置页面 /settings/ai（配置 AI 提供商、连接测试、API Key 脱敏）
- 推演页面显示当前 AI 模式，改造为使用 ModelRouter
- 检查中心显示 AI 可用性提示，改造为使用 ModelRouter
- 重构 ai_service.py 为兼容入口，委托新 AI 模块
- desktop_launcher.py 补充新模块 PyInstaller 导入
- packaging/AIWorldEngine.spec、build_exe.ps1 补充 hidden imports
- 77 个新测试全部通过
- 版本号统一更新为 1.3.0
- README.md 新增 AI API 配置章节

### 修改文件
- `app/models.py` — 新增 AppSetting 模型
- `app/database.py` — 注册 AppSetting
- `app/config.py` — VERSION → 1.3.0
- `app/main.py` — 注册 settings_router、启动时初始化默认配置
- `app/services/settings_service.py` — 新建
- `app/services/ai/__init__.py` — 新建
- `app/services/ai/base.py` — 新建
- `app/services/ai/errors.py` — 新建
- `app/services/ai/mock_client.py` — 新建
- `app/services/ai/openai_compatible_client.py` — 新建
- `app/services/ai/model_router.py` — 新建
- `app/services/ai/prompt_builder.py` — 新建
- `app/services/ai/response_parser.py` — 新建
- `app/services/ai_service.py` — 重构为兼容入口
- `app/services/simulation_service.py` — 使用 ModelRouter
- `app/services/check_service.py` — 使用 ModelRouter
- `app/routes/settings.py` — 新建
- `app/routes/simulation.py` — 显示 AI 模式、使用 ModelRouter
- `app/routes/checks.py` — 显示 AI 提示
- `app/templates/settings/ai.html` — 新建
- `app/templates/simulation/index.html` — AI 模式显示
- `app/templates/index.html` — AI 设置入口链接
- `desktop_launcher.py` — 新增模块 imports
- `packaging/AIWorldEngine.spec` — hidden imports
- `packaging/build_exe.ps1` — hidden imports
- `tests/test_desktop.py` — 版本号断言更新
- `tests/test_main.py` — 版本号断言更新
- `tests/test_settings_service.py` — 新建（22 个测试）
- `tests/test_ai_client.py` — 新建（17 个测试）
- `tests/test_model_router.py` — 新建（22 个测试）
- `tests/test_ai_settings_routes.py` — 新建（10 个测试）
- `tests/test_ai_integration.py` — 新建（10 个测试）
- `README.md` — 版本号、AI 配置章节
- `CHANGELOG.md` — v1.3.0 条目
- `docs/dev-log.md` — 本条记录

### 测试命令 / 结果
- python -m compileall . ✅
- pytest tests/ -v ✅ (303 passed, 0 failed)
- python scripts/check_encoding.py ✅

### 备份 / commit / tag / push
- 待定（feature 分支合并后）

### 已知问题
- 无

---

## 2026-05-11 — v1.2.2: 发布整理版（文档统一 + 版本号统一）

### 完成内容
- README.md 版本号从 v1.0.0 更新为 v1.2.2
- app/config.py VERSION 统一更新为 1.2.2
- README 增加「Windows EXE 分发说明」
- README 增加「当前适用场景」
- README「已知限制」重命名为「已知限制 / 当前限制」，增加多用户/权限/云端限制
- CHANGELOG.md 新增 v1.2.2 条目
- docs/dev-log.md 新增本条记录

### 修改文件
- `README.md` — 版本号、EXE 分发说明、适用场景、限制说明
- `app/config.py` — VERSION → 1.2.2
- `CHANGELOG.md` — 新增 v1.2.2 条目
- `docs/dev-log.md` — 新增本条记录

### 测试命令 / 结果
- python -m compileall . ✅
- pytest tests/ -v ✅ (226 passed)
- python scripts/check_encoding.py ✅

### 备份 / commit / tag / push
- `fa209f4` — `docs: v1.2.2 release - unify version, add EXE distribution guide, usage scenarios and limits`
- `v1.2.2` — main + tag 已推送

### 已知问题
- 无

---

## 2026-05-09 — v1.2.1: EXE 打包验证与修复

### 完成内容
- 修复 PyInstaller 打包：conda 环境 DLL 缺失（libssl、libcrypto、ffi、sqlite3）
- 修复 desktop_launcher.py：使用直接 import 替代字符串 uvicorn.run
- requirements.txt 新增 python-multipart
- build_exe.ps1 更新：包含所有必要 DLL
- EXE 打包验证通过：启动、首页、CSS、数据库、数据持久化

### 修改文件
- `desktop_launcher.py` — 修复 uvicorn import 方式
- `packaging/build_exe.ps1` — 添加 DLL 路径
- `requirements.txt` — 新增 python-multipart
- `CHANGELOG.md` — 更新
- `docs/dev-log.md` — 更新
- `docs/desktop-build.md` — 更新
- `README.md` — 更新

### 测试命令 / 结果
- 226 passed, 0 failed

### 打包状态
- PyInstaller 打包成功
- EXE 路径：dist/AIWorldEngine/AIWorldEngine.exe
- EXE 启动成功，首页正常，CSS 正常
- 数据库路径：%LOCALAPPDATA%\AIWorldEngine\ai_world_engine.db
- 数据持久化验证通过

### 备份 / commit / tag / push
- `.project_backups/v1.2.1-20260509-0000.zip`
- `fix: verify v1.2.1 desktop exe packaging`
- `v1.2.1` — main + tag 已推送

### 已知问题
- 无

---

## 2026-05-09 — v1.2.0: Windows 桌面端 EXE 打包

### 完成内容
- desktop_launcher.py（pywebview + 后台 uvicorn）
- resource_path 工具函数
- 桌面数据库路径（AppData）
- PyInstaller 打包脚本
- 桌面打包文档
- 8个新测试

### 修改文件
- `desktop_launcher.py` — 新建
- `app/config.py` — 新增 resource_path、get_desktop_db_path、VERSION→1.2.0
- `app/main.py` — 使用 resource_path 挂载静态文件
- `packaging/build_exe.ps1` — 新建
- `docs/desktop-build.md` — 新建
- `tests/test_desktop.py` — 新建（8个测试）
- `tests/test_main.py` — 更新版本号断言
- `requirements.txt` — 新增 pywebview、pyinstaller
- `README.md` — 更新
- `CHANGELOG.md` — 更新
- `docs/dev-log.md` — 更新
- `docs/architecture.md` — 更新
- `docs/todo.md` — 更新

### 测试命令 / 结果
- 226 passed, 0 failed (v1.0.0: 218 + v1.2.0: 8)

### 打包状态
- PyInstaller 打包脚本已就绪（packaging/build_exe.ps1）
- 建议使用干净 venv 执行打包

### 备份 / commit / tag / push
- `.project_backups/v1.2.0-20260509-0000.zip`
- `feat: complete v1.2.0 desktop exe packaging`
- `v1.2.0` — main + tag 已推送

### 已知问题
- conda base 环境 PyInstaller 打包缓慢，需用干净 venv

---

## 2026-05-09 — v1.0.0: 稳定展示版

### 完成内容
- README 最终整理（功能总览、页面路径、安装说明、演示流程、AI配置、数据库说明、目录结构、已知限制、后续规划）
- 架构文档最终整理
- 安全审查最终总结
- TODO 更新后续计划

### 修改文件
- `README.md` — 最终整理
- `CHANGELOG.md` — 更新
- `docs/dev-log.md` — 更新
- `docs/architecture.md` — 更新
- `docs/todo.md` — 更新
- `docs/security-review.md` — 更新

### 测试命令
```bash
pytest tests/ -v
```

### 测试结果
- 210 passed, 0 failed

### 备份路径
- `.project_backups/v1.0.0-20260509-0000.zip`

### commit 信息
- `release: complete v1.0.0 stable demo`

### tag 信息
- `v1.0.0` — Version v1.0.0: stable demo release

### push 结果
- main 分支推送成功
- v1.0.0 tag 推送成功

### 已知问题
- 无

### 项目总结
- 从零到完整系统，8个版本迭代
- 210个测试，覆盖所有核心功能
- 15个功能模块，17个页面路径
- 代码结构清晰，易于后续扩展

---

## 2026-05-09 — v0.8.0: 页面优化、错误处理和测试完善

### 完成内容
- 统一错误页面模板（errors/404, 400, 500）
- 页面导航一致性确认（所有模块返回链接正确）
- 空状态友好提示确认
- 表单错误提示确认
- README 补充数据库开发说明和已知限制
- 44个润色测试

### 修改文件
- `app/templates/errors/404.html` — 新建
- `app/templates/errors/400.html` — 新建
- `app/templates/errors/500.html` — 新建
- `tests/test_polish.py` — 新建（44个测试）
- `README.md` — 补充数据库说明、已知限制、v1.0.0计划
- `CHANGELOG.md` — 更新
- `docs/dev-log.md` — 更新
- `docs/architecture.md` — 更新
- `docs/todo.md` — 更新
- `docs/security-review.md` — 更新

### 测试命令
```bash
pytest tests/ -v
```

### 测试结果
- 210 passed, 0 failed (v0.7.0: 166 + v0.8.0: 44)

### 备份路径
- `.project_backups/v0.8.0-20260509-0000.zip`

### commit 信息
- `chore: complete v0.8.0 polish and error handling`

### tag 信息
- `v0.8.0` — Version v0.8.0: polish error handling and tests

### push 结果
- main 分支推送成功
- v0.8.0 tag 推送成功

### 已知问题
- 无

### 下一步计划
- v1.0.0: 最终整理、完整测试、文档完善、稳定发布

---

## 2026-05-09 — v0.7.0: 设定矛盾检查和角色行为合理性检查

### 完成内容
- 检查中心页面（设定矛盾 + 角色行为两个入口）
- 设定矛盾检查：规则冲突、事件冲突、角色状态冲突、势力关系冲突、时间线异常
- 角色行为合理性检查：性格匹配、目标匹配、能力匹配、状态匹配、势力立场
- 规则式关键词检查 + Mock AI 辅助分析
- 检查功能只读数据库，不修改任何设定
- 25个新测试

### 修改文件
- `app/services/consistency_service.py` — 新建（设定矛盾检查）
- `app/services/behavior_service.py` — 新建（角色行为检查）
- `app/services/check_service.py` — 新建（检查编排）
- `app/routes/checks.py` — 新建（5个端点）
- `app/templates/checks/index.html` — 新建
- `app/templates/checks/conflicts.html` — 新建
- `app/templates/checks/behavior.html` — 新建
- `app/templates/worlds/detail.html` — 激活检查中心入口
- `app/main.py` — 注册 checks 路由
- `tests/test_checks.py` — 新建（25个测试）
- `README.md` — 更新
- `CHANGELOG.md` — 更新
- `docs/dev-log.md` — 更新
- `docs/architecture.md` — 更新
- `docs/todo.md` — 更新
- `docs/security-review.md` — 更新

### 测试命令
```bash
pytest tests/ -v
```

### 测试结果
- 166 passed, 0 failed (v0.6.0: 141 + v0.7.0: 25)

### 备份路径
- `.project_backups/v0.7.0-20260509-0000.zip`

### commit 信息
- `feat: complete v0.7.0 consistency and behavior checks`

### tag 信息
- `v0.7.0` — Version v0.7.0: consistency and behavior checks

### push 结果
- main 分支推送成功
- v0.7.0 tag 推送成功

### 已知问题
- 无

### 下一步计划
- v0.8.0: 页面优化、错误处理、基础测试完善

---

## 2026-05-09 — v0.6.0: 采纳为正史和分支记录

### 完成内容
- 推演记录采纳为正史：创建 historical_events（is_canon=True, source_type=simulation）
- 推演记录保存为分支：创建 branches，不写入 historical_events
- 记录状态流转：pending → adopted / branched
- 防止重复操作、跨世界操作
- 分支列表和详情页
- Branch 模型新增 updated_at
- 25个新测试

### 修改文件
- `app/models.py` — Branch 新增 updated_at
- `app/services/record_action_service.py` — 新建
- `app/services/branch_service.py` — 新建
- `app/routes/records.py` — 新增 adopt/branch 端点 + 跨世界校验
- `app/routes/branches.py` — 新建
- `app/templates/records/detail.html` — 新增操作按钮（按状态显示）
- `app/templates/branches/` — 3个模板
- `app/templates/worlds/detail.html` — 激活分支记录入口
- `app/main.py` — 注册 branches 路由
- `tests/test_adopt_branch.py` — 新建（25个测试）
- `README.md` — 更新
- `CHANGELOG.md` — 更新
- `docs/dev-log.md` — 更新
- `docs/architecture.md` — 更新
- `docs/todo.md` — 更新
- `docs/security-review.md` — 更新

### 测试命令
```bash
pytest tests/ -v
```

### 测试结果
- 141 passed, 0 failed (v0.5.0: 116 + v0.6.0: 25)

### 备份路径
- `.project_backups/v0.6.0-20260509-0000.zip`

### commit 信息
- `feat: complete v0.6.0 canon adoption and branches`

### tag 信息
- `v0.6.0` — Version v0.6.0: canon adoption and branches

### push 结果
- main 分支推送成功
- v0.6.0 tag 推送成功

### 已知问题
- 数据库迁移：v0.5.0 和 v0.6.0 均修改了模型。开发阶段删除旧 `ai_world_engine.db` 后重新启动即可。

### 下一步计划
- v0.7.0: 设定矛盾检查和角色行为合理性检查

---

## 2026-05-09 — v0.5.0: AI 推演和推演记录

### 完成内容
- AI 推演页面：问题输入、类型选择、世界设定预览、结果展示
- 世界上下文聚合服务：聚合角色/势力/地点/规则/正史事件
- 推演记录：列表 + 详情页
- SimulationRecord 模型新增 simulation_type、context_snapshot、updated_at
- 核心规则：AI 推演结果不直接写入 historical_events
- 17个新测试（含跨世界隔离、不污染正史验证）

### 修改文件
- `app/models.py` — SimulationRecord 新增3个字段
- `app/services/world_context_service.py` — 新建
- `app/services/simulation_service.py` — 新建
- `app/routes/simulation.py` — 新建
- `app/routes/records.py` — 新建
- `app/templates/simulation/index.html` — 新建
- `app/templates/records/list.html` — 新建
- `app/templates/records/detail.html` — 新建
- `app/templates/records/404.html` — 新建
- `app/templates/worlds/detail.html` — 激活AI推演+推演记录入口
- `app/main.py` — 注册2个新路由
- `tests/test_simulation.py` — 新建（17个测试）
- `tests/test_worlds.py` — 更新占位测试
- `README.md` — 更新
- `CHANGELOG.md` — 更新
- `docs/dev-log.md` — 更新
- `docs/architecture.md` — 更新
- `docs/todo.md` — 更新
- `docs/security-review.md` — 更新

### 测试命令
```bash
pytest tests/ -v
```

### 测试结果
- 116 passed, 0 failed (v0.4.0: 99 + v0.5.0: 17)

### 备份路径
- `.project_backups/v0.5.0-20260509-0000.zip`

### commit 信息
- `feat: complete v0.5.0 AI simulation records`

### tag 信息
- `v0.5.0` — Version v0.5.0: AI simulation and records

### push 结果
- main 分支推送成功
- v0.5.0 tag 推送成功

### 已知问题
- 无

### 下一步计划
- v0.6.0: 采纳为正史、分支记录

---

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
