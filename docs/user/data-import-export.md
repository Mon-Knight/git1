# 数据导入导出

## 世界 JSON 导出

在世界详情页（`/worlds/{id}`）点击"导出世界"按钮，可导出当前世界所有数据为 JSON 文件。

## 数据管理

访问 `/data` 页面，可以进行：
- 数据库备份
- 数据库恢复
- 单世界 JSON 导出/导入

## 备份位置

使用 Web 端时，数据库文件位于项目根目录：
```
ai_world_engine.db
```

使用桌面 EXE 时，数据库文件位于：
```
C:\Users\<用户名>\AppData\Local\AIWorldEngine\ai_world_engine.db
```

## 注意事项

- JSON 导出仅包含当前世界的数据
- 数据库备份为完整的 SQLite 文件副本
- 恢复操作会覆盖当前数据库，请谨慎操作
