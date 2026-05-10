# API 路由参考

## 核心路由

### 首页与系统
| 路径 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页工作台 |
| `/health` | GET | 健康检查 |

### 世界管理 (`/worlds`)
| 路径 | 方法 | 说明 |
|------|------|------|
| `/worlds` | GET | 世界列表 |
| `/worlds/new` | GET | 新建世界表单 |
| `/worlds` | POST | 创建世界 |
| `/worlds/{id}` | GET | 世界控制台 |
| `/worlds/{id}/edit` | GET/POST | 编辑世界 |
| `/worlds/{id}/export` | GET | 导出世界 JSON |

### 设定库 (`/worlds/{id}`)
| 子路径 | 说明 |
|--------|------|
| `/characters` | 角色管理 |
| `/factions` | 势力管理 |
| `/locations` | 地点管理 |
| `/rules` | 规则管理 |

### 剧情历史
| 路径 | 说明 |
|------|------|
| `/worlds/{id}/events` | 历史事件 |
| `/worlds/{id}/timeline` | 时间线 |

### AI 推演
| 路径 | 说明 |
|------|------|
| `/worlds/{id}/simulation` | AI 推演 |
| `/worlds/{id}/records` | 推演记录 |
| `/worlds/{id}/branches` | 分支记录 |

### 小说工程
| 路径 | 说明 |
|------|------|
| `/worlds/{id}/novel/evolution` | 全书演化推演 |
| `/worlds/{id}/novel/evolutions` | 演化方案列表 |

### 创作资产 (`/worlds/{id}/context`)
| 路径 | 说明 |
|------|------|
| `/context` | 创作上下文总览 |
| `/context/styles` | 风格方案 |
| `/context/anchors` | 剧情时间点 |
| `/context/packages` | 上下文包 |

### 检查中心
| 路径 | 说明 |
|------|------|
| `/worlds/{id}/checks` | 检查中心 |
| `/worlds/{id}/checks/conflicts` | 设定矛盾检查 |
| `/worlds/{id}/checks/behavior` | 角色行为检查 |

### 数据与设置
| 路径 | 说明 |
|------|------|
| `/data` | 数据管理 |
| `/settings/ai` | AI 设置 |
