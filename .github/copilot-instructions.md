# Copilot Project Instructions

## Project Identity

- **项目名称**: AI World Engine
- **项目描述**: AI 小说世界观推演系统
- **GitHub 仓库**: Mon-Knight/git1（当前已绑定 remote `origin`）
- **技术栈**: Python / FastAPI / SQLite / Jinja2 / HTML / CSS / JS

## Project Goal

你现在是一个全流程软件开发 Agent。请从零开始为我完成一个完整程序，并在 VS Code 当前工作区中完成项目初始化、需求分析、架构设计、编码、测试、备份、Git 版本管理、GitHub 新仓库创建与推送。

【核心目标】
请根据我后续提供的项目主题，独立完成一个可运行、结构清晰、易维护、带文档、带测试、可提交 GitHub 的完整程序。如果我没有提供具体技术栈，请你根据项目类型自行选择最稳妥、最容易运行、依赖最少的技术方案，并在开始前写入 docs/decision-log.md。

【工作原则】
1. 不要一次性盲目生成大量代码。必须先完成需求拆解、目录规划、技术选型、风险分析，再开始编码。
2. 每完成一个稳定小版本，必须进行本地备份、Git 提交、打 Git tag，并推送到 GitHub。
3. 不允许在没有测试的情况下声称功能完成。
4. 每次修改代码前，先查看当前项目结构和已有文件，避免覆盖有效内容。
5. 遇到报错时，不要反复猜测。必须读取完整报错、定位根因、给出修复方案，再修改。
6. 禁止提交密钥、Token、密码、Cookie、个人隐私信息、数据库真实账号。
7. 所有敏感配置必须放入 .env，并提供 .env.example。
8. 所有重要步骤必须记录到 docs/dev-log.md。
9. 所有版本变化必须记录到 CHANGELOG.md。
10. 所有命令执行完成后，必须根据终端输出确认是否成功，不要假设成功。

【项目初始化要求】
请先执行以下步骤：
1. 检查当前目录是否为空。
2. 如果目录非空，列出文件并判断是否会冲突，不要随意删除。
3. 创建标准项目结构。
4. 创建 .gitignore，必须排除：
   - node_modules/
   - venv/
   - .venv/
   - __pycache__/
   - dist/
   - build/
   - .env
   - *.log
   - .DS_Store
   - .project_backups/
5. 创建 README.md，说明项目简介、功能、运行方式、目录结构、开发进度。
6. 创建 CHANGELOG.md。
7. 创建 docs/dev-log.md。
8. 创建 docs/decision-log.md。
9. 创建 docs/security-review.md。
10. 创建 .env.example。
11. 创建 .github/copilot-instructions.md，用于记录本项目后续开发规范。



本项目要求 Copilot Agent 能够独立完成：
- 需求分析
- 架构设计
- 编码
- 调试
- 测试
- Git 版本管理
- GitHub 仓库推送
- 文档维护

禁止只生成代码而不验证运行结果。

---

# Development Workflow

## 每次开发必须遵循：

1. 先阅读项目结构
2. 分析已有代码
3. 不允许覆盖有效代码
4. 每次只实现一个模块
5. 每次修改后运行测试
6. 测试通过后才能提交 Git
7. 每个稳定版本必须备份
8. 每个稳定版本必须 push GitHub

---

# Git Rules

## 初始化

如果未初始化 Git：

```bash
git init
```

## 提交规范

提交信息格式：

```text
feat:
fix:
docs:
refactor:
test:
security:
chore:
```

示例：

```bash
git commit -m "feat: add login module"
```

---

# Version Backup Rules

## 每个稳定版本必须：

1. 本地压缩备份
2. Git commit
3. Git tag
4. Push GitHub

## Tag 示例

```bash
git tag -a v0.1.0 -m "stable version"
git push origin v0.1.0
```

---

# GitHub Rules
本项目已经完成 Git 初始化，并已连接到 GitHub 远程仓库 `git1`。

Copilot Agent 必须遵守：

1. 不要重新创建 GitHub 仓库。
2. 不要执行 `gh repo create`。
3. 不要修改已有 remote。
4. 不要推送到其他仓库。
5. 不要删除 `.git` 目录。
6. 不要重新执行 `git init`，除非确认当前目录不是 Git 仓库。
7. 每次开发前必须先检查：

```bash
git status
git remote -v
git branch

禁止推送到错误仓库。

推送前必须检查：

```bash
git remote -v
```

---

# Security Rules

禁止：

- 硬编码 Token
- 提交 .env
- 使用危险 eval
- SQL 字符串拼接
- 未校验输入
- 路径穿越
- 上传无限制文件

所有敏感信息必须使用：

```text
.env
```

并提供：

```text
.env.example
```

---

# Required Files

项目必须包含：

```text
README.md
CHANGELOG.md
docs/dev-log.md
docs/security-review.md
.env.example
.gitignore
```

---

# Testing Rules

## Python 项目：

```bash
pytest
python -m compileall .
```

## Node.js 项目：

```bash
npm run build
npm test
npm run lint
```

## Flutter 项目：

```bash
flutter analyze
flutter test
```

禁止未测试直接声称完成。

---

# Failure Handling

如果出现错误：

1. 阅读完整报错
2. 分析根因
3. 最小化修改
4. 重新测试
5. 连续失败两次必须回滚

禁止删除整个项目重写。

---

# Documentation Rules

每次开发后必须更新：

- CHANGELOG.md
- docs/dev-log.md

记录：
- 修改内容
- 测试结果
- 已知问题
- 下一步计划

---

# Important

禁止：

- 虚假测试通过
- 虚假 GitHub 推送成功
- 未运行代码就声称完成
- 跳过版本备份
- 提交 node_modules
- 提交 venv
- 提交备份压缩包



【版本备份机制】
每一个可运行版本都必须完成以下动作：

1. 本地备份：
   - 创建 .project_backups/ 目录。
   - 每个版本创建一个备份压缩包。
   - 命名格式：
     .project_backups/v0.1.0-YYYYMMDD-HHMM.zip
   - 备份时排除：
     .git/
     node_modules/
     venv/
     .venv/
     __pycache__/
     dist/
     build/
     .env
     .project_backups/

2. Git 提交：
   - 每完成一个稳定版本，执行：
     git status
     git add .
     git commit -m "feat: complete v0.1.0 <简短说明>"

3. Git Tag：
   - 每个稳定版本必须创建 tag：
     git tag -a v0.1.0 -m "Version v0.1.0: <说明>"

4. 推送 GitHub：
   - 推送主分支：
     git push -u origin main
   - 推送 tag：
     git push origin v0.1.0

5. 版本记录：
   - 更新 CHANGELOG.md。
   - 更新 docs/dev-log.md。
   - 在 docs/dev-log.md 中记录：
     - 当前版本号
     - 完成功能
     - 修改文件
     - 测试命令
     - 测试结果
     - 已知问题
     - 下一步计划

【版本号规则】
请使用语义化版本：
- v0.1.0：项目骨架完成，可启动。
- v0.2.0：核心功能初版完成。
- v0.3.0：界面或交互完善。
- v0.4.0：错误处理、边界情况、数据校验完善。
- v0.5.0：测试、文档、安全检查完善。
- v1.0.0：完整稳定版。

不要把不可运行的状态标记为稳定版本。不可运行的中间状态只能使用普通 commit，不能打正式 tag。

【开发流程】
请严格按照下面流程执行：

阶段 1：需求分析
- 根据项目目标写出功能清单。
- 区分核心功能、增强功能、暂不实现功能。
- 写入 docs/decision-log.md。

阶段 2：架构设计
- 设计目录结构。
- 说明前端、后端、数据存储、配置文件、测试文件的职责。
- 写入 README.md 和 docs/decision-log.md。

阶段 3：最小可运行版本
- 先完成最小可运行版本，不要一开始堆复杂功能。
- 运行启动命令。
- 发现错误必须修复。
- 启动成功后提交为 v0.1.0。

阶段 4：核心功能开发
- 每次只实现一个功能模块。
- 每个功能完成后运行测试。
- 测试通过后提交。
- 达到稳定阶段后打 tag 并推送。

阶段 5：异常处理与安全检查
- 检查输入校验。
- 检查路径穿越风险。
- 检查命令注入风险。
- 检查 XSS、SQL 注入、敏感信息泄露风险。
- 检查依赖漏洞。
- 检查 .gitignore 是否生效。
- 结果写入 docs/security-review.md。

阶段 6：最终整理
- 完善 README.md。
- 完善 CHANGELOG.md。
- 完善运行说明。
- 补充常见问题。
- 清理无用代码。
- 执行最终测试。
- 提交并打 v1.0.0 tag。
- 推送到 GitHub。

【测试要求】
根据项目技术栈自动选择测试方式：

如果是 Python 项目：
- 创建 requirements.txt
- 推荐使用 pytest
- 至少执行：
  python -m compileall .
  pytest

如果是 Node.js / 前端项目：
- 创建 package.json
- 至少执行：
  npm install
  npm run build
  npm test
  npm run lint

如果是 Flutter 项目：
- 至少执行：
  flutter pub get
  flutter analyze
  flutter test
  flutter build apk 或适合当前平台的构建命令

如果是 Web 项目：
- 检查页面是否能启动
- 检查路由是否正常
- 检查控制台是否有明显错误
- 检查表单输入是否合法

如果没有测试框架，也必须创建最基本的 smoke test，并说明如何验证程序可运行。

【安全要求】
必须避免以下问题：
1. 硬编码密钥。
2. 把 .env 提交到 GitHub。
3. 使用 eval、exec 或危险 shell 拼接。
4. 没有校验用户输入。
5. 文件上传不限制类型和大小。
6. 路径拼接导致路径穿越。
7. 数据库查询直接拼接字符串。
8. 前端直接渲染未经处理的 HTML。
9. 日志输出密码、Token、Cookie。
10. 把备份压缩包提交进 Git 仓库。

【失败处理规则】
如果某一步失败：
1. 停止继续扩展新功能。
2. 读取并总结错误。
3. 判断是环境问题、依赖问题、代码问题还是权限问题。
4. 优先做最小修改。
5. 修改后重新运行测试。
6. 如果连续两次失败，必须回退到上一个稳定 Git commit，并记录原因。
7. 不要删除整个项目重来，除非我明确允许。

【Git 分支策略】
默认使用 main 分支。
开发复杂功能时可以创建 feature 分支：
git checkout -b feature/<功能名>

功能完成并测试通过后合并回 main：
git checkout main
git merge feature/<功能名>

合并前必须运行测试。
合并后必须提交并推送。

【提交信息规范】
提交信息必须使用以下格式：
- feat: 新功能
- fix: 修复问题
- docs: 文档修改
- test: 测试相关
- refactor: 重构
- chore: 配置或杂项
- security: 安全修复
- backup: 版本备份说明

示例：
git commit -m "feat: add user login module"
git commit -m "fix: handle empty input validation"
git commit -m "docs: update installation guide"

【最终交付要求】
完成后请给我输出：
1. 项目名称。
2. GitHub 仓库地址。
3. 当前最终版本号。
4. 已完成功能列表。
5. 项目目录结构。
6. 本地运行命令。
7. 测试命令和测试结果。
8. 已创建的 Git tags。
9. 已知问题。
10. 后续可扩展方向。
11. 安全检查结果摘要。

【重要限制】
- 不要伪造 GitHub 推送成功。
- 不要伪造测试通过。
- 不要在没有实际运行命令的情况下说“已验证”。
- 不要把未完成版本标记为完成。
- 不要为了省事跳过备份、提交、tag、推送。
- 不要把备份压缩包提交到 GitHub，GitHub 上通过 commit、tag 和 release 记录版本即可。
- 如果 GitHub CLI 没有登录，请明确告诉我需要先执行 gh auth login。
- 如果缺少必要环境，请先说明缺少什么，并给出安装命令。
- 如果存在多个解决方案，请选择最稳定、最容易运行、最适合初学者维护的方案。

---

# AI World Engine — 项目特有规则

## 项目核心约束

1. **项目名**: AI World Engine
2. **当前仓库**: Mon-Knight/git1（remote `origin`）
3. **不允许创建新 GitHub 仓库**
4. **不允许执行 `gh repo create`**
5. **不允许修改 remote**
6. **不允许删除 `.git` 目录**
7. **不允许重新执行 `git init`**
8. 所有 commit、tag、push 必须推送到当前已绑定的 `git1` 仓库

## AI 推演核心规则

1. **AI 生成结果必须先保存到 `simulation_records` 表**
2. **AI 生成结果不允许直接写入 `historical_events`（正史）表**
3. 用户必须手动审核推演结果后选择：采纳为正史 / 保留为分支 / 标记为废弃
4. 采纳时：从 `simulation_records` 创建一条 `historical_events` 记录，`is_canon=True`
5. 分支时：创建 `branches` 记录，不污染正史

## 版本开发规则

1. 每个稳定版本必须：本地备份 → 测试通过 → commit → tag → push
2. 未通过测试的代码不允许打 tag
3. 不可运行的中间状态只能普通 commit，不能打正式 tag
4. 版本号遵循语义化版本：v0.1.0 → v0.2.0 → ... → v1.0.0

## 禁止提交的文件

- `.env`
- `venv/` / `.venv/`
- `node_modules/`
- `.project_backups/`
- `__pycache__/`
- `*.pyc`
- `*.log`
- `.DS_Store`

## Mock AI 模式

- 如果 `.env` 中 `AI_API_KEY` 为空或未设置，系统必须自动使用 Mock AI 模式
- Mock AI 模式生成基于规则的简单推演结果，用于本地测试和演示