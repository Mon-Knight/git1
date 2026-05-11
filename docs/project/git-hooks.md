# Git Hooks — AI World Engine

## 目的

Git Hooks 用于在提交和推送前自动执行质量检查，防止：
- 修改代码但忘记更新 CHANGELOG/dev-log 等文档
- 修改 VERSION 但忘记同步 README/CHANGELOG/version-roadmap
- 提交存在语法错误的代码
- 推送未通过测试的代码

## 安装

```bash
python scripts/install_git_hooks.py
```

安装脚本会：
1. 将 `scripts/git-hooks/pre-commit` 复制到 `.git/hooks/pre-commit`
2. 将 `scripts/git-hooks/pre-push` 复制到 `.git/hooks/pre-push`
3. 如有已有 hook，自动备份为 `.bak` 文件

安装后可重复执行，不会丢失已有 hook。

## pre-commit 检查内容

每次 `git commit` 时自动执行（轻量）：

| 检查项 | 命令 | 说明 |
|--------|------|------|
| 编码检查 | `python scripts/check_encoding.py` | 确保 Markdown 文件编码正确 |
| 版本一致性 | `python scripts/check_version_sync.py` | 确保 VERSION 与文档一致 |
| 文档同步 | `python scripts/check_docs_sync.py --staged` | 检查 staged 文件是否需要同步更新文档 |
| 语法检查 | `python -m compileall app scripts desktop_launcher.py` | 确保 Python 代码无语法错误 |

## pre-push 检查内容

每次 `git push` 时自动执行（完整质量门禁）：

| 检查项 | 命令 | 说明 |
|--------|------|------|
| 全量语法 | `python -m compileall .` | 检查所有 Python 文件 |
| 编码检查 | `python scripts/check_encoding.py` | 同上 |
| 版本一致性 | `python scripts/check_version_sync.py` | 同上 |
| 文档同步 | `python scripts/check_docs_sync.py --all` | 检查所有文件 |
| 构建验证 | `python scripts/verify_desktop_build.py --all` | 验证桌面构建 |
| 测试套件 | `pytest tests/ -q --tb=short` | 运行所有测试 |

## 文档同步规则

当修改以下类型文件时，必须同步更新文档：

| 修改内容 | 必须更新的文档 |
|----------|---------------|
| app/、templates、static、routes、services、models | CHANGELOG.md 或 dev-log.md |
| app/config.py (VERSION) | CHANGELOG.md + dev-log.md + README.md + version-roadmap.md |
| templates/、static/css/、static/js/ | CHANGELOG.md + dev-log.md + ui-information-architecture.md |
| tests/ | dev-log.md 或 test-debt.md |
| packaging/、desktop_launcher.py | CHANGELOG.md + dev-log.md + desktop-build.md |
| 导出功能 | CHANGELOG.md + dev-log.md + data-import-export.md |
| 设置中心 | CHANGELOG.md + dev-log.md + ui-information-architecture.md + ai-settings.md |

仅修改错别字、注释、格式化时，允许只更新 dev-log.md。

## 版本一致性规则

`app/config.py` 中的 VERSION 必须在以下文件中出现：
- README.md
- CHANGELOG.md（作为 `## [vX.Y.Z]` 标题）
- docs/dev-log.md（作为版本记录标题）
- docs/project/version-roadmap.md（作为版本条目）

## 测试债务规则

- 不允许存在未记录的失败测试
- 所有非通过测试必须标记为 `@pytest.mark.xfail` 并附带原因
- 所有 xfail 测试必须在 `docs/project/test-debt.md` 中记录
- 记录内容：测试文件、测试名称、失败原因、目标修复版本
- pre-push 时 `check_test_debt.py` 会检查债务记录是否存在

## 常见失败处理

### "Code files modified but CHANGELOG.md not updated"
修改了代码但未更新 CHANGELOG.md 或 dev-log.md。
**解决**：在 CHANGELOG.md 或 docs/dev-log.md 中添加本次修改说明。

### "VERSION changed but README.md not updated"
修改了版本号但未同步 README。
**解决**：在 README.md 中更新版本号引用。

### "Version 'vX.Y.Z' not found in CHANGELOG.md"
版本号与文档不一致。
**解决**：在对应文档中添加版本号。

## 临时跳过 Hook

**仅在紧急修复或 Hook 自身故障时使用：**

```bash
# 跳过 pre-commit
git commit --no-verify

# 跳过 pre-push
git push --no-verify
```

**Agent 执行正式版本提交时不允许跳过 Hook。**
