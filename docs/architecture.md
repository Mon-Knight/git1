# Architecture Document — AI World Engine

## 项目概述

AI World Engine 是一个 AI 小说世界观推演系统，帮助作者构建小说世界观并通过 AI 推演世界发展。

## 技术栈

- **后端**: Python 3.10+ / FastAPI
- **数据库**: SQLite (via SQLAlchemy)
- **模板**: Jinja2
- **前端**: HTML + CSS + JavaScript (原生)
- **测试**: pytest
- **AI**: OpenAI-compatible API + Mock 模式

## 目录结构（v0.1.0 实际）

```
f:\git\
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口（lifespan 事件）
│   ├── config.py            # 配置管理（读取 .env）
│   ├── database.py          # 数据库连接与初始化
│   ├── models.py            # SQLAlchemy 数据模型（8张表）
│   ├── routes/
│   │   ├── __init__.py
│   │   └── pages.py         # 页面路由（首页）
│   ├── services/
│   │   ├── __init__.py
│   │   └── ai_service.py    # AI 调用服务（Mock + 真实API）
│   ├── templates/
│   │   └── index.html       # 首页模板
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # 测试配置（内存数据库）
│   ├── test_main.py         # 应用与首页测试
│   ├── test_database.py     # 数据库表结构测试
│   └── test_ai_service.py   # AI 服务测试
├── docs/
├── .project_backups/        # 本地备份（不入Git）
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── CHANGELOG.md
```

## 数据库设计

### 表结构

#### 1. worlds（世界项目）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| name | VARCHAR(200) | 世界名称 |
| world_type | VARCHAR(100) | 世界类型（奇幻/科幻/武侠等） |
| description | TEXT | 简介 |
| current_era | VARCHAR(100) | 当前时代 |
| tone | VARCHAR(100) | 世界基调（黑暗/光明/中性） |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### 2. characters（角色）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| world_id | INTEGER FK | 所属世界 |
| name | VARCHAR(200) | 姓名 |
| role | VARCHAR(200) | 身份/职业 |
| faction_id | INTEGER FK | 所属势力（可空） |
| personality | TEXT | 性格描述 |
| goal | TEXT | 目标 |
| abilities | TEXT | 能力 |
| current_status | VARCHAR(100) | 当前状态（存活/死亡/失踪等） |
| notes | TEXT | 备注 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### 3. factions（势力）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| world_id | INTEGER FK | 所属世界 |
| name | VARCHAR(200) | 名称 |
| faction_type | VARCHAR(100) | 类型（国家/组织/家族等） |
| leader_id | INTEGER FK | 领袖角色ID（可空） |
| goal | TEXT | 目标 |
| resources | TEXT | 资源 |
| enemies | TEXT | 敌对势力（JSON数组存储势力ID） |
| allies | TEXT | 盟友（JSON数组存储势力ID） |
| notes | TEXT | 备注 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### 4. locations（地点）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| world_id | INTEGER FK | 所属世界 |
| name | VARCHAR(200) | 名称 |
| location_type | VARCHAR(100) | 类型（城市/国家/遗迹等） |
| region | VARCHAR(200) | 所属区域 |
| description | TEXT | 描述 |
| controlling_faction_id | INTEGER FK | 控制势力（可空） |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### 5. world_rules（世界规则）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| world_id | INTEGER FK | 所属世界 |
| name | VARCHAR(200) | 规则名称 |
| rule_type | VARCHAR(100) | 类型（物理/魔法/社会/经济等） |
| content | TEXT | 规则内容 |
| constraints | TEXT | 限制条件 |
| scope | TEXT | 影响范围 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### 6. historical_events（历史事件）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| world_id | INTEGER FK | 所属世界 |
| title | VARCHAR(300) | 事件标题 |
| event_time | VARCHAR(200) | 发生时间（世界内时间） |
| involved_characters | TEXT | 涉及角色（JSON数组） |
| involved_factions | TEXT | 涉及势力（JSON数组） |
| location_id | INTEGER FK | 地点（可空） |
| content | TEXT | 事件内容 |
| consequences | TEXT | 影响结果 |
| is_canon | BOOLEAN | 是否正史 |
| source_type | VARCHAR(50) | 来源类型（manual/simulation） |
| source_id | INTEGER | 来源记录ID |
| created_at | DATETIME | 创建时间 |

#### 7. simulation_records（AI推演记录）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| world_id | INTEGER FK | 所属世界 |
| question | TEXT | 用户推演问题 |
| ai_response | TEXT | AI 推演结果 |
| status | VARCHAR(50) | 状态（pending/adopted/branched/discarded） |
| ai_model | VARCHAR(100) | 使用的AI模型 |
| is_mock | BOOLEAN | 是否mock模式 |
| created_at | DATETIME | 创建时间 |

#### 8. branches（分支记录）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| world_id | INTEGER FK | 所属世界 |
| simulation_id | INTEGER FK | 关联推演记录 |
| branch_name | VARCHAR(200) | 分支名称 |
| description | TEXT | 分支描述 |
| events_json | TEXT | 分支事件列表（JSON） |
| created_at | DATETIME | 创建时间 |

### ER 关系概要

```
worlds (1) ──< (N) characters
worlds (1) ──< (N) factions
worlds (1) ──< (N) locations
worlds (1) ──< (N) world_rules
worlds (1) ──< (N) historical_events
worlds (1) ──< (N) simulation_records
worlds (1) ──< (N) branches
factions (1) ──< (N) characters (可选)
simulation_records (1) ──< (N) branches
simulation_records (1) ──> (1) historical_events (采纳时)
```

## API 路由设计

### 基础路由 `/`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 首页 |

### 世界管理 `/worlds`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/worlds` | 世界列表页 |
| GET | `/worlds/create` | 创建世界表单页 |
| POST | `/worlds/create` | 创建世界 |
| GET | `/worlds/{id}` | 世界详情页 |
| GET | `/worlds/{id}/edit` | 编辑世界表单页 |
| POST | `/worlds/{id}/edit` | 更新世界 |
| POST | `/worlds/{id}/delete` | 删除世界 |

### 角色管理 `/worlds/{world_id}/characters`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/worlds/{world_id}/characters` | 角色列表 |
| GET | `/worlds/{world_id}/characters/create` | 创建角色表单 |
| POST | `/worlds/{world_id}/characters/create` | 创建角色 |
| GET | `/worlds/{world_id}/characters/{id}` | 角色详情 |
| GET | `/worlds/{world_id}/characters/{id}/edit` | 编辑角色表单 |
| POST | `/worlds/{world_id}/characters/{id}/edit` | 更新角色 |
| POST | `/worlds/{world_id}/characters/{id}/delete` | 删除角色 |

### 势力管理 `/worlds/{world_id}/factions`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/worlds/{world_id}/factions` | 势力列表 |
| GET/POST | `/worlds/{world_id}/factions/create` | 创建势力 |
| GET | `/worlds/{world_id}/factions/{id}` | 势力详情 |
| GET/POST | `/worlds/{world_id}/factions/{id}/edit` | 编辑势力 |
| POST | `/worlds/{world_id}/factions/{id}/delete` | 删除势力 |

### 地点管理 `/worlds/{world_id}/locations`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/worlds/{world_id}/locations` | 地点列表 |
| GET/POST | `/worlds/{world_id}/locations/create` | 创建地点 |
| GET | `/worlds/{world_id}/locations/{id}` | 地点详情 |
| GET/POST | `/worlds/{world_id}/locations/{id}/edit` | 编辑地点 |
| POST | `/worlds/{world_id}/locations/{id}/delete` | 删除地点 |

### 世界规则 `/worlds/{world_id}/rules`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/worlds/{world_id}/rules` | 规则列表 |
| GET/POST | `/worlds/{world_id}/rules/create` | 创建规则 |
| GET | `/worlds/{world_id}/rules/{id}` | 规则详情 |
| GET/POST | `/worlds/{world_id}/rules/{id}/edit` | 编辑规则 |
| POST | `/worlds/{world_id}/rules/{id}/delete` | 删除规则 |

### 历史事件 `/worlds/{world_id}/events`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/worlds/{world_id}/events` | 事件列表 |
| GET/POST | `/worlds/{world_id}/events/create` | 创建事件 |
| GET | `/worlds/{world_id}/events/{id}` | 事件详情 |

### 时间线 `/worlds/{world_id}/timeline`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/worlds/{world_id}/timeline` | 时间线页面（正史） |

### AI 推演 `/worlds/{world_id}/simulation`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/worlds/{world_id}/simulation` | AI 推演页面 |
| POST | `/worlds/{world_id}/simulation/run` | 执行 AI 推演 |

### 推演记录 `/worlds/{world_id}/records`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/worlds/{world_id}/records` | 推演记录列表 |
| GET | `/worlds/{world_id}/records/{id}` | 推演记录详情 |
| POST | `/worlds/{world_id}/records/{id}/adopt` | 采纳为正史 |
| POST | `/worlds/{world_id}/records/{id}/branch` | 保留为分支 |
| POST | `/worlds/{world_id}/records/{id}/discard` | 标记为废弃 |

### 分支管理 `/worlds/{world_id}/branches`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/worlds/{world_id}/branches` | 分支列表 |
| GET | `/worlds/{world_id}/branches/{id}` | 分支详情 |

## AI 服务模块设计

### 模块结构

```
app/services/
├── __init__.py
├── ai_service.py       # AI 调用核心
├── world_service.py    # 世界设定聚合
├── check_service.py    # 矛盾检查
└── branch_service.py   # 分支管理
```

### AI 服务 (`ai_service.py`)

```
class AIService:
    - __init__(config): 初始化，读取环境变量
    - is_mock_mode(): 判断是否 mock 模式
    - generate_simulation(world_context, question): 生成推演结果
    - _call_real_api(prompt): 调用真实 AI API
    - _mock_simulation(world_context, question): Mock 生成
```

### 工作流程

1. 用户输入推演问题
2. 系统聚合世界设定（角色、势力、地点、规则、历史事件）
3. 构建 prompt 发送给 AI
4. AI 返回推演结果
5. 结果保存到 `simulation_records`，状态为 `pending`
6. 用户选择：采纳 / 分支 / 废弃
7. 采纳时：创建 `historical_events` 记录，`is_canon=True`
8. 分支时：创建 `branches` 记录

### Mock AI 模式

当 `AI_API_KEY` 为空时自动启用，生成基于规则的简单推演结果，用于测试和演示。

## 页面结构

```
首页 (/)
├── 系统名称 + 简介
└── 进入世界列表

世界列表 (/worlds)
├── 世界卡片列表
└── 创建世界按钮

世界详情 (/worlds/{id})
├── 世界基本信息
├── 导航：角色 | 势力 | 地点 | 规则 | 事件 | 时间线 | AI推演
└── 统计概览

角色管理 (/worlds/{id}/characters)
├── 角色列表（表格）
├── 创建/编辑表单
└── 详情页

势力管理 (/worlds/{id}/factions)
├── 势力列表
├── 创建/编辑表单
└── 详情页

地点管理 (/worlds/{id}/locations)
├── 地点列表
├── 创建/编辑表单
└── 详情页

规则管理 (/worlds/{id}/rules)
├── 规则列表
├── 创建/编辑表单
└── 详情页

历史事件 (/worlds/{id}/events)
├── 事件列表
└── 创建表单

时间线 (/worlds/{id}/timeline)
├── 正史事件按时间排序
└── 正史/分支切换

AI 推演 (/worlds/{id}/simulation)
├── 推演问题输入
├── 世界设定预览
└── 推演结果展示

推演记录 (/worlds/{id}/records)
├── 记录列表
├── 采纳/分支/废弃操作
└── 详情页

分支记录 (/worlds/{id}/branches)
├── 分支列表
└── 详情页
```
