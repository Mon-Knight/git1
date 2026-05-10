# AI 模型配置指南

AI World Engine 支持两种 AI 模式。

## 模式说明

| 模式 | 条件 | 说明 |
|------|------|------|
| **Mock AI** | 未启用真实 AI | 使用规则式推演，适合本地测试和演示 |
| **OpenAI-compatible API** | 已在 /settings/ai 配置并启用 | 调用兼容 API 进行真实推演 |

> 自 v1.3.0 起，所有 AI 配置通过 **AI 设置页面** 管理（优先级：数据库 > .env）。

## 页面配置

启动项目后打开：`/settings/ai`

可配置：Base URL、Model、API Key、Temperature、Max Tokens、Timeout、以及推演/检查/总结各任务的专用模型。

## 示例配置

| 提供商 | Base URL | Model |
|--------|----------|-------|
| DeepSeek | `https://api.deepseek.com/v1` | 根据实际模型填写 |
| 小米 MiMo Token Plan | `https://token-plan-cn.xiaomimimo.com/v1` | 根据实际模型填写 |
| Ollama（本地） | `http://127.0.0.1:11434/v1` | 本地模型名 |

## 环境变量 (.env)

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `AI_API_KEY` | AI API 密钥（为空则使用 Mock AI） | (空) |
| `AI_BASE_URL` | AI API 地址 | `https://api.openai.com/v1` |
| `AI_MODEL` | AI 模型名称 | `gpt-4o` |

> **安全提醒**: 不要在 README、dev-log 或测试文件中写真实 API Key。API Key 已在页面上自动脱敏显示。
