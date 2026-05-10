# 测试体系说明

## 测试框架

- **框架**: pytest
- **测试数量**: 706 个（v1.7.6）
- **数据库**: 内存 SQLite（每个测试独立）

## 运行测试

```bash
# 全部测试
pytest tests/ -v

# 语法检查
python -m compileall .

# 编码检查
python scripts/check_encoding.py

# 桌面构建验证
python scripts/verify_desktop_build.py --all
```

## 测试结构

| 目录/文件 | 覆盖范围 |
|-----------|----------|
| `tests/test_main.py` | 应用入口、首页 |
| `tests/test_worlds.py` | 世界 CRUD |
| `tests/test_characters.py` | 角色管理 |
| `tests/test_factions.py` | 势力管理 |
| `tests/test_locations.py` | 地点管理 |
| `tests/test_rules.py` | 规则管理 |
| `tests/test_events.py` | 历史事件 |
| `tests/test_timeline.py` | 时间线 |
| `tests/test_simulation.py` | AI 推演 |
| `tests/test_ai_*.py` | AI 服务、客户端、集成 |
| `tests/test_novel_*.py` | 小说工程 |
| `tests/test_context_*.py` | 创作上下文 |
| `tests/test_dashboard_*.py` | 工作台 |
| `tests/test_world_dashboard_*.py` | 世界控制台 |
| `tests/test_module_groups_*.py` | 模块分组 |
| `tests/test_desktop.py` | 桌面端 |
| `tests/test_project_docs.py` | 文档检查 |
| `tests/test_docs_structure.py` | 文档结构检查 |

## 测试原则

- 每个模块都有对应的测试文件
- 使用内存数据库隔离测试
- 测试覆盖正常路径和异常路径
- 旧测试不删除，只新增和修改
