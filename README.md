请先读取并严格遵守项目中的 .github/copilot-instructions.md。

注意：当前项目已经在 VS Code 中初始化 Git，并且已经连接到我的 GitHub 仓库 git1。  
本项目不要创建新的 GitHub 仓库。  
不要执行 gh repo create。  
不要修改 remote。  
不要重新 git init。  
不要删除 .git 目录。  
后续所有 commit、tag、push 都必须推送到当前已经绑定的 GitHub 仓库 git1。

请先执行并检查：

git status
git remote -v
git branch
gh auth status

我的 GitHub CLI 已经登录，GitHub 账号是 Mon-Knight，协议是 HTTPS。

如果当前 remote 已经指向 git1，请继续使用当前 remote。  
如果当前 remote 不是 git1，请停止操作，并向我汇报当前 remote 情况，不要擅自修改。  
如果当前分支不是 main，请使用当前分支名，不要擅自重命名分支。  
如果当前有未提交内容，请先列出变更，不要直接覆盖。

---

我要开发一个 AI 小说世界观推演系统，项目名为：

AI World Engine

注意：项目名可以是 AI World Engine，但 GitHub 仓库仍然使用当前已经绑定的 git1，不要创建 ai-world-engine 新仓库。

---

【项目目标】

系统用于帮助作者构建小说世界观，并通过 AI 不断推演世界发展。

系统需要支持创建世界项目、管理角色、势力、地点、世界规则、历史事件，并允许用户输入推演问题，由 AI 根据已有设定生成剧情或世界变化。

AI 生成结果不能直接写入正史，必须先保存为推演记录。用户可以选择采纳为正史，也可以保留为分支。

系统需要支持：

1. 时间线查看
2. 正史记录
3. 分支记录
4. 设定矛盾检查
5. 角色行为合理性检查

---

【第一版技术栈】

第一版使用：

- Python
- FastAPI
- SQLite
- HTML
- CSS
- JavaScript
- Jinja2
- pytest

第一版不要使用复杂前端框架，例如 Vue、React、Next.js。

代码结构需要清晰，方便后续扩展到：

- Flutter App
- 桌面端
- 本地 AI 模型
- 多用户系统
- 更复杂的世界观数据库

---

【环境配置要求】

必须提供：

.env.example

用于配置：

AI_API_KEY=
AI_BASE_URL=
AI_MODEL=
DATABASE_URL=

注意：

1. 不允许提交真实 .env。
2. 不允许硬编码 AI API Key。
3. 所有 AI 配置必须通过环境变量读取。
4. 如果没有真实 API Key，系统也必须支持 mock AI 推演模式，方便本地测试。

---

【页面要求】

第一版至少包括以下页面：

1. 首页
2. 世界列表
3. 世界详情
4. 角色管理
5. 势力管理
6. 地点管理
7. 世界规则管理
8. 时间线管理
9. AI 推演页面
10. 推演记录页面

---

【核心功能模块】

1. 首页

需要展示：

- 系统名称 AI World Engine
- 系统简介
- 进入世界列表的入口

2. 世界项目管理

需要支持：

- 创建世界项目
- 查看世界项目列表
- 查看单个世界详情
- 编辑世界基础信息

世界项目字段至少包括：

- 世界名称
- 世界类型
- 简介
- 当前时代
- 世界基调
- 创建时间

3. 角色管理

需要支持：

- 创建角色
- 查看角色列表
- 编辑角色信息

角色字段至少包括：

- 姓名
- 身份
- 所属势力
- 性格
- 目标
- 能力
- 当前状态
- 备注

4. 势力管理

需要支持：

- 创建势力
- 查看势力列表
- 编辑势力信息

势力字段至少包括：

- 名称
- 类型
- 领袖
- 目标
- 资源
- 敌对势力
- 盟友
- 备注

5. 地点管理

需要支持：

- 创建地点
- 查看地点列表
- 编辑地点信息

地点字段至少包括：

- 名称
- 类型
- 所属区域
- 描述
- 控制势力
- 重要事件

6. 世界规则管理

需要支持：

- 创建规则
- 查看规则列表
- 编辑规则

规则字段至少包括：

- 规则名称
- 规则类型
- 规则内容
- 限制条件
- 影响范围

7. 历史事件管理

需要支持：

- 创建历史事件
- 查看历史事件列表

事件字段至少包括：

- 事件标题
- 发生时间
- 涉及角色
- 涉及势力
- 地点
- 事件内容
- 影响结果
- 是否正史
- 来源记录

8. 时间线管理

需要支持：

- 按时间顺序查看正史事件
- 支持历史事件排序
- 区分正史事件和分支事件

9. AI 推演页面

需要支持：

- 用户输入推演问题
- 系统读取当前世界设定
- AI 根据角色、势力、地点、规则、历史事件生成推演结果
- 生成结果保存为推演记录
- AI 推演结果不允许直接写入正史

10. 推演记录页面

需要支持：

- 查看所有 AI 推演记录
- 查看单条推演详情
- 支持采纳为正史
- 支持保留为分支
- 支持标记为废弃

11. 正史记录

要求：

- 用户采纳 AI 推演结果后，才写入正史时间线
- 正史记录需要可追溯来源
- 不能让 AI 自动污染正史

12. 分支记录

要求：

- 未采纳但保留的推演结果作为分支
- 分支不能污染正史
- 分支记录需要和正史区分显示

13. 设定矛盾检查

第一版可以使用规则检查 + mock AI 分析。

需要检查：

- 新事件是否与已有世界规则冲突
- 角色状态是否前后矛盾
- 势力关系是否矛盾
- 历史事件是否时间顺序异常

14. 角色行为合理性检查

第一版可以使用规则检查 + mock AI 分析。

需要检查：

- 角色行动是否符合性格
- 角色行动是否符合目标
- 角色行动是否符合当前状态
- 角色行动是否超出能力范围

---

【数据库要求】

使用 SQLite。

请先设计数据库表，不要直接开始写业务代码。

至少需要考虑以下表：

1. worlds
2. characters
3. factions
4. locations
5. world_rules
6. historical_events
7. simulation_records
8. branches

数据库设计需要写入：

docs/architecture.md

---

【AI 调用要求】

第一版需要有 AI 服务模块，但必须支持两种模式：

1. 真实 AI API 模式
2. mock AI 模式

如果 .env 中没有 AI_API_KEY，则默认使用 mock AI 模式。

AI 模块不要和路由代码混在一起，应该单独放在 services 目录中。

AI 生成结果必须先保存到 simulation_records，不允许直接写入 historical_events 正史表。

---

## 开发进度

### v0.2.0 ✅ 已完成
- 世界管理 CRUD（创建/查看/编辑/删除）
- 世界列表页、详情页、创建/编辑表单
- 表单校验（名称必填、长度限制）
- 详情页含后续模块占位入口

### v0.1.0 ✅ 已完成
- FastAPI 应用骨架
- SQLite 数据库初始化（8张表）
- 首页模板
- Mock AI 服务模块
- 基础测试（36个测试全部通过）

### 运行方式

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python -m uvicorn app.main:app --reload

# 运行测试
pytest tests/ -v
```

### 页面路径

| 路径 | 说明 |
|------|------|
| `/` | 首页 |
| `/worlds` | 世界列表 |
| `/worlds/new` | 创建世界 |
| `/worlds/{id}` | 世界详情 |
| `/worlds/{id}/edit` | 编辑世界 |
| `/health` | 健康检查 |

### 项目目录结构

```
app/
  main.py          # FastAPI 入口
  config.py        # 配置管理
  database.py      # 数据库连接
  models.py        # 数据模型（8张表）
  routes/
    pages.py       # 页面路由
  services/
    ai_service.py  # AI 服务（Mock + 真实API）
  templates/
    index.html     # 首页模板
  static/
    css/style.css
    js/main.js
tests/
  conftest.py
  test_main.py
  test_database.py
  test_ai_service.py
docs/
  architecture.md
  decision-log.md
  dev-log.md
  todo.md
  security-review.md
requirements.txt
.env.example
.gitignore
```

### 下一阶段 v0.3.0
- 角色、势力、地点、规则管理 CRUD

【项目结构要求】

请设计清晰结构，例如：

app/
  main.py
  database.py
  models.py
  schemas.py
  routes/
  services/
  templates/
  static/
tests/
docs/
README.md
CHANGELOG.md
.env.example
.gitignore

具体结构可以根据 FastAPI 项目最佳实践调整，但必须保持简单、清晰、适合后续扩展。

---

【版本管理要求】

本项目已经连接到 GitHub 仓库 git1。

每完成一个稳定版本，必须：

1. 本地备份
2. git status
3. git add .
4. git commit
5. git tag
6. git push 到当前 git1 仓库
7. git push tag 到当前 git1 仓库
8. 更新 README.md
9. 更新 CHANGELOG.md
10. 更新 docs/dev-log.md

禁止：

1. 创建新 GitHub 仓库
2. 执行 gh repo create
3. 修改 remote
4. 推送到 git1 以外的仓库
5. 提交 .env
6. 提交 venv
7. 提交 node_modules
8. 提交 .project_backups

---

【推荐版本规划】

请按阶段开发：

v0.1.0：项目骨架完成，可启动首页  
v0.2.0：世界项目管理完成  
v0.3.0：角色、势力、地点、规则管理完成  
v0.4.0：历史事件和时间线管理完成  
v0.5.0：AI 推演和推演记录完成  
v0.6.0：采纳为正史、分支记录功能完成  
v0.7.0：设定矛盾检查和角色行为合理性检查完成  
v0.8.0：页面优化、错误处理、基础测试完善  
v1.0.0：稳定展示版完成

---

【测试要求】

必须使用 pytest。

至少需要测试：

1. FastAPI 应用是否能启动
2. 首页是否能访问
3. 数据库初始化是否正常
4. 世界项目创建是否正常
5. AI mock 推演是否正常
6. 推演结果是否不会直接写入正史
7. 采纳推演结果后是否会写入正史
8. 分支记录是否不会污染正史

每次稳定版本提交前必须运行：

python -m compileall .
pytest

如果测试失败，不允许 commit、tag、push 稳定版本。

---

【第一阶段任务】

现在只完成第一阶段，不要直接写完整业务代码。

请完成：

1. 读取 .github/copilot-instructions.md。
2. 检查 Git 状态。
3. 检查 remote 是否指向 git1。
4. 检查当前分支。
5. 检查当前目录结构。
6. 根据本需求写出功能清单。
7. 设计技术选型。
8. 设计项目目录结构。
9. 设计数据库表初稿。
10. 设计页面结构。
11. 设计 API 路由初稿。
12. 设计 AI 服务模块结构。
13. 分析可能风险。
14. 修改或创建以下文件：

- README.md
- CHANGELOG.md
- docs/dev-log.md
- docs/decision-log.md
- docs/architecture.md
- docs/todo.md
- docs/security-review.md
- .env.example
- .gitignore

第一阶段完成后，请运行：

git status

然后向我汇报：

1. 当前 Git 分支
2. 当前 remote 地址
3. 是否确认指向 git1
4. 已创建或修改的文件
5. 项目目录规划
6. 数据库表设计摘要
7. API 路由设计摘要
8. 第一阶段是否完成
9. 下一阶段准备实现什么

第一阶段结束后不要继续写核心业务代码，等待我下一步指令。