# Copilot Project Instructions

## Project Goal

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

必须为项目单独创建仓库。

默认：

```bash
gh repo create <repo-name> --private --source=. --remote=origin --push
```

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