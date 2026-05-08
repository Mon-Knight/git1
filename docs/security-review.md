# Security Review — AI World Engine

## 审查日期
2026-05-09（v0.5.0 更新）

## 安全设计原则

### 1. 密钥管理
- [x] 所有敏感配置使用 `.env` 文件
- [x] 提供 `.env.example` 模板
- [x] `.gitignore` 已排除 `.env`
- [x] 代码中无硬编码密钥
- [x] AI_API_KEY 通过环境变量读取，日志不输出

### 2. 输入校验
- [x] 所有用户输入有校验（名称必填、长度限制）
- [x] 使用 SQLAlchemy ORM，避免 SQL 注入
- [x] Jinja2 默认转义，防止 XSS
- [x] 路径参数校验（world_id、resource_id 不存在返回 404）

### 3. 数据库安全
- [x] 使用 SQLAlchemy ORM，避免 SQL 字符串拼接
- [x] 数据库文件通过 .gitignore 排除

### 4. AI 调用安全
- [x] AI_API_KEY 通过环境变量读取
- [x] AI 请求日志不记录 API Key
- [x] AI 返回内容通过 Jinja2 渲染，防 XSS
- [x] AI 推演结果不直接写入正史（核心规则）
- [x] 跨世界数据隔离（上下文聚合仅包含当前世界数据）

### 5. 文件上传
- 第一版无文件上传功能，暂不评估

### 6. 依赖安全
- [x] 依赖版本已固定（requirements.txt）
- [ ] 定期检查依赖漏洞

### 7. 错误处理
- [x] 生产环境不暴露详细错误（.env 控制 APP_DEBUG）
- [x] 自定义 404 错误页面
- [x] AI 调用失败有友好错误提示，不泄露配置

### 8. CSRF 保护
- 第一版为单用户本地应用
- 后续多用户版本需要添加 CSRF 保护

## v0.5.0 新增安全确认
- [x] AI 推演结果不自动写入 historical_events
- [x] 世界上下文聚合不跨世界泄露数据
- [x] simulation_records 状态默认为 pending，需用户手动操作
- [x] Mock AI 模式不会调用外部 API

## 风险等级
当前：**低风险**

