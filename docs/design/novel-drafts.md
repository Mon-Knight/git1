# Novel Drafts — 正文草稿设计文档

## 概述

正文草稿模块是 AI World Engine 小说工程闭环的最后一步：全书演化 → 分卷大纲 → 章节大纲 → **正文草稿**。

用户从主线章节方案中选择具体章节，AI 基于世界设定、已采纳角色/势力/地点/规则、正史事件和创作资产，生成单章正文初稿候选。用户审核后可标记为采用稿或废弃。

## 数据模型

### NovelDraft

表名：`novel_drafts`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| world_id | Integer (FK→worlds) | 所属世界 |
| chapter_outline_id | Integer (FK→novel_chapter_outlines) | 来源主线章节方案 |
| volume_index | Integer | 所属卷序号 |
| volume_title | String(300) | 所属卷标题 |
| chapter_index | Integer | 所属章节序号 |
| chapter_title | String(300) | 所属章节标题 |
| title | String(300) | 正文草稿标题 |
| style_profile_id | Integer (FK→style_profiles, nullable) | 写作风格方案 |
| context_package_id | Integer (FK→context_packages, nullable) | 创作上下文包 |
| plot_anchor_id | Integer (FK→plot_anchors, nullable) | 剧情时间点 |
| generation_requirement | Text | 用户补充要求 |
| prompt | Text | 本次生成使用的 Prompt |
| content | Text | 正文草稿内容 |
| raw_text | Text | AI 原始返回 |
| notes | Text | 用户编辑备注 |
| word_count | Integer | 正文字数 |
| status | String(20) | candidate / accepted / discarded |
| is_accepted | Boolean | 是否该章节采用稿 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |
| accepted_at | DateTime (nullable) | 标记为采用稿时间 |

### 约束

1. 正文草稿按 world_id 隔离
2. 同一世界、同一 chapter_outline_id、同一 chapter_index 最多只能有一个 is_accepted=True
3. 设置新的 accepted 时，旧 accepted 自动取消（status→candidate, is_accepted→False）

## 状态流转

```
candidate → accepted    （标记为采用稿）
candidate → discarded   （废弃）
candidate → candidate   （编辑保存仍为候选）
accepted → candidate    （同章节被新采用稿替代时自动降级）
accepted → discarded    （允许但需确认）
discarded → (不可设为 accepted / 不可编辑)
```

## 路由

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | /worlds/{id}/novel/drafts | 正文草稿列表 |
| GET | /worlds/{id}/novel/drafts/new | 新建正文草稿 |
| POST | /worlds/{id}/novel/drafts | 生成正文草稿 |
| GET | /worlds/{id}/novel/drafts/{draft_id} | 查看详情 |
| GET | /worlds/{id}/novel/drafts/{draft_id}/edit | 编辑页 |
| POST | /worlds/{id}/novel/drafts/{draft_id}/edit | 保存编辑 |
| POST | /worlds/{id}/novel/drafts/{draft_id}/set-accepted | 标记为采用稿 |
| POST | /worlds/{id}/novel/drafts/{draft_id}/discard | 废弃草稿 |

## 服务层

`app/services/novel_draft_service.py` 包含：

- `build_novel_draft_prompt()` — 构建包含世界信息、角色、势力、地点、规则、正史、章节方案、风格方案、上下文包等的 Prompt
- `generate_novel_draft()` — 调用 AI 或 Mock 生成正文草稿
- `save_novel_draft()` — 保存正文草稿到数据库
- `list_novel_drafts()` — 列出当前世界所有正文草稿
- `get_novel_draft()` — 读取详情（校验 world_id）
- `set_accepted_novel_draft()` — 标记为采用稿（同章节唯一）
- `discard_novel_draft()` — 废弃正文草稿
- `update_novel_draft()` — 编辑正文草稿
- `extract_draft_content()` — 从 AI 返回中提取正文主体

## Prompt 规则

- 只生成单章正文初稿
- 不生成下一章 / 整卷 / 整书
- 不修改章节大纲 / 分卷大纲 / 世界设定 / 正史
- 输出仅为候选草稿，用户确认后才成为采用稿
- 必须遵守主线章节方案与已确认正史
- 必须体现本章主要冲突、人物动机与情绪变化
- 必须安排信息释放与章末钩子
- 输出中文正文，不得抄袭

## 模板

| 模板 | 说明 |
|------|------|
| novel_drafts/index.html | 列表页：标题、状态标签、来源章节、字数、操作按钮 |
| novel_drafts/new.html | 新建页：章节选择、风格方案、字数目标、补充要求 |
| novel_drafts/detail.html | 详情页：标题、内容、Prompt 摘要、采用/编辑/废弃按钮 |
| novel_drafts/edit.html | 编辑页：标题、正文内容、备注 |

## 版本历史

- v2.0.0：正文草稿生成基础闭环（本版本）
- v2.1.0：正文润色、正文质量检查（计划）
