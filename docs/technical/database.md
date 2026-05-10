# 数据库说明

## 技术概述

| 项目 | 说明 |
|------|------|
| 数据库 | SQLite |
| ORM | SQLAlchemy |
| 默认文件 | `ai_world_engine.db`（项目根目录） |
| Git 提交 | 不提交（已加入 `.gitignore`） |

## 数据模型

当前版本包含以下核心表：
- `worlds` — 世界项目
- `characters` — 角色
- `factions` — 势力
- `locations` — 地点
- `world_rules` — 世界规则
- `historical_events` — 历史事件
- `simulation_records` — AI 推演记录
- `branches` — 分支记录
- `context_packages` — 创作上下文包
- `style_profiles` — 风格方案
- `plot_anchors` — 剧情时间点

## 迁移

| 阶段 | 说明 |
|------|------|
| 开发阶段 | 模型字段变更后可删除 `.db` 文件，重启项目自动重建 |
| 生产建议 | 后续版本建议加入 Alembic 数据库迁移工具 |

## 桌面端数据库位置

```
C:\Users\<用户名>\AppData\Local\AIWorldEngine\ai_world_engine.db
```
