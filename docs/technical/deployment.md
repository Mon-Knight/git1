# 生产部署指南

当前版本为本地开发版。如需部署到生产环境：

## 推荐部署方案

1. **使用 Gunicorn + Uvicorn workers** 替代 `uvicorn --reload`
2. **配置反向代理**（Nginx / Caddy）
3. **迁移到 PostgreSQL**（修改 `DATABASE_URL`）
4. **引入 Alembic** 管理数据库迁移
5. **添加用户认证和权限系统**
6. **配置真实的 AI API Key**

## Docker 部署（未来）

Docker 支持将在后续版本中添加。

## 安全注意事项

- 生产环境务必设置 `AI_API_KEY`
- 不要将 `.env` 文件提交到版本控制
- 使用 HTTPS 保护 API 通信
- 定期备份数据库
