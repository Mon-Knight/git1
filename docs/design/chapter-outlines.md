# 章节大纲 — 设计文档

## 功能定位

章节大纲是小说工程中的第三个核心模块，位于分卷大纲之后、正文生成之前。它基于主线分卷方案中的某一卷，生成该卷下所有章节的详细规划。

## 数据来源

### 必选
- 主线分卷方案（volume_outline_id）：提供该卷的核心冲突、主角目标、主要事件
- 目标分卷（volume_index）：确定要为哪一卷生成章节大纲

### 可选
- 写作风格方案（style_profile_id）
- 剧情时间点（plot_anchor_id）
- 创作上下文包（context_package_id）

### 自动读取
- 世界信息（名称、类型、时代、基调）
- 已采纳角色（最多 15 个）
- 已采纳势力（最多 10 个）
- 已采纳地点（最多 10 个）
- 已采纳规则（最多 10 条）
- 正史事件（最多 10 条）

## 生成流程

```
1. 用户进入世界控制台
2. 进入小说工程 → 章节大纲
3. 点击"新建章节大纲"
4. 系统自动读取主线分卷方案
5. 用户选择目标分卷
6. 用户选择风格方案（可选）
7. 用户选择剧情时间点（可选）
8. 用户选择创作上下文包（可选）
9. 用户设置章节数量
10. 用户填写补充要求
11. AI 生成章节大纲候选
12. 系统保存候选章节方案
13. 用户查看详情
14. 用户选择：设为主线 / 编辑 / 废弃
```

## 数据模型

### NovelChapterOutline

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| world_id | Integer FK | 所属世界 |
| volume_outline_id | Integer FK | 来源分卷方案 |
| volume_index | Integer | 所属卷序号 |
| volume_title | String(300) | 所属卷标题 |
| title | String(300) | 章节大纲标题 |
| style_profile_id | Integer FK | 写作风格方案（可选） |
| plot_anchor_id | Integer FK | 剧情时间点（可选） |
| context_package_id | Integer FK | 创作上下文包（可选） |
| generation_requirement | Text | 用户补充要求 |
| prompt | Text | 生成使用的 Prompt |
| result_json | Text | AI 生成的 JSON |
| raw_text | Text | AI 原始输出 |
| chapter_count | Integer | 章节数量 |
| status | String(20) | candidate / main / discarded |
| is_main | Boolean | 是否为主线章节方案 |
| confirmed_at | DateTime | 设为主线时间 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

## 状态流转

```
candidate ──→ main
candidate ──→ discarded
candidate ──编辑→ candidate
main ──(被替换)──→ candidate
main ──→ discarded（需确认）
discarded ──✗→ main（不可）
discarded ──✗→ 编辑（不可）
```

## Prompt 原则

1. 只生成章节大纲候选，不生成正文
2. 必须遵守主线分卷方案中该卷的核心冲突、主角目标和主要事件
3. 必须遵守已确认正史
4. 必须尊重已采纳设定
5. 每章剧情目标服务于本卷核心冲突
6. 必须保持角色动机合理
7. 必须安排冲突推进、信息释放和章末钩子
8. 输出结构化 JSON
9. 不复制现成作品专有名词
10. 输出仅为候选，用户确认后设为主线

## 输出 JSON 结构

```json
{
  "title": "第X卷章节大纲方案",
  "volume_index": X,
  "volume_title": "卷标题",
  "summary": "本卷章节安排总览",
  "chapter_count": N,
  "chapters": [
    {
      "chapter_index": 1,
      "title": "章节标题",
      "chapter_goal": "本章剧情目标",
      "main_conflict": "本章主要冲突",
      "pov_character": "视角角色",
      "key_characters": ["角色A", "角色B"],
      "key_locations": ["地点A"],
      "plot_events": ["事件1", "事件2"],
      "emotional_beat": "情绪推进",
      "foreshadowing": "伏笔或信息释放",
      "ending_hook": "章末钩子",
      "estimated_words": 3000,
      "notes": "补充说明"
    }
  ]
}
```

## 主线章节方案规则

- 同一世界、同一 volume_index 最多只有一个 is_main=True
- 设置新主线时，同卷旧主线自动降级为 candidate
- 不同卷可以各自拥有主线章节方案
- 废弃方案不可设为主线

## 与分卷大纲的关系

- 章节大纲必须基于主线分卷方案
- 章节大纲选择某一卷生成
- 没有主线分卷方案时，页面提示前往分卷大纲
- 章节大纲详情显示来源分卷方案链接

## 与正文生成的边界

- 章节大纲：规划每章的剧情目标、冲突、事件、钩子
- 正文生成（v2.0.0）：基于章节大纲生成每章正文初稿
- 章节大纲不包含正文内容
- 正文生成将在下一版本开发
