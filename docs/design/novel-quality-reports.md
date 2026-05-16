# 正文质量检查报告 — 设计文档

> **版本**: v2.1.0  
> **定位**: 正文质量控制阶段，只生成检查报告，不自动润色正文

## 设计目标

v2.0.0 已完成正文草稿生成闭环。v2.1.0 为正文质量提供系统化检查机制：
- 基于正文草稿、章节大纲、世界设定、创作资产生成结构化质量检查报告
- 提供综合评分和各维度评分
- 提供具体问题列表和可执行修改建议
- 支持标记当前参考报告和废弃报告
- 为 v2.2.0 正文润色候选生成提供基础

## 数据模型

### NovelDraftQualityReport

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| world_id | FK(World) | 所属世界 |
| draft_id | FK(NovelDraft) | 关联正文草稿 |
| chapter_outline_id | FK(NovelChapterOutline) | 来源章节大纲 |
| volume_index | Integer | 卷索引 |
| chapter_index | Integer | 章索引 |
| title | String(300) | 报告标题 |
| prompt | Text | 生成 Prompt |
| result_json | Text | 结构化结果 JSON |
| raw_text | Text | 原始返回文本 |
| overall_score | Integer | 综合评分 (0-100) |
| outline_alignment_score | Integer | 章节匹配度 |
| world_consistency_score | Integer | 世界一致性 |
| character_consistency_score | Integer | 人物一致性 |
| plot_coherence_score | Integer | 剧情连贯性 |
| pacing_score | Integer | 节奏控制 |
| prose_score | Integer | 文风一致性 |
| hook_score | Integer | 章末钩子 |
| status | String(20) | candidate / current / discarded |
| is_current | Boolean | 是否为当前参考报告 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |
| confirmed_at | DateTime | 确认时间 |

### 状态流转

```
candidate ──→ current (标记为当前参考)
candidate ──→ discarded (废弃)
current ────→ discarded (废弃，同时取消 current 标记)
```

- 同一草稿最多一个 `is_current=True`
- 设置新 current 时自动取消旧 current
- discarded 不能设为 current

## 服务层

### NovelQualityService

| 方法 | 说明 |
|------|------|
| build_quality_report_prompt | 构建质量检查 Prompt |
| generate_quality_report | 调用 AI/Mock 生成报告 |
| save_quality_report | 保存报告到数据库 |
| list_quality_reports | 列表查询（world_id + 可选 draft_id） |
| get_quality_report | 单条查询（世界隔离） |
| set_current_quality_report | 设置当前参考报告 |
| discard_quality_report | 废弃报告 |
| parse_quality_report_response | JSON 解析兜底 |

## Mock 模式

Mock 模式返回固定分值：
- overall_score: 82
- outline_alignment: 85
- world_consistency: 80
- character_consistency: 78
- plot_coherence: 84
- pacing: 76
- prose: 82
- ending_hook: 88

## 路由

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /worlds/{id}/novel/quality-reports | 世界全部报告列表 |
| GET | /worlds/{id}/novel/drafts/{did}/quality-reports | 草稿报告列表 |
| GET | /worlds/{id}/novel/drafts/{did}/quality-reports/new | 新建报告页 |
| POST | /worlds/{id}/novel/drafts/{did}/quality-reports | 生成报告 |
| GET | /worlds/{id}/novel/quality-reports/{rid} | 报告详情 |
| POST | /worlds/{id}/novel/quality-reports/{rid}/set-current | 标记当前参考 |
| POST | /worlds/{id}/novel/quality-reports/{rid}/discard | 废弃报告 |

## JSON 输出格式

```json
{
  "title": "正文质量检查报告",
  "overall_score": 82,
  "summary": "整体评价",
  "scores": {
    "outline_alignment": 85,
    "world_consistency": 80,
    "character_consistency": 78,
    "plot_coherence": 84,
    "pacing": 76,
    "prose": 82,
    "ending_hook": 88
  },
  "strengths": ["优点1", "优点2"],
  "issues": [
    {
      "category": "章节目标偏离",
      "severity": "medium",
      "description": "问题说明",
      "evidence": "对应文本",
      "suggestion": "修改建议"
    }
  ],
  "revision_suggestions": [
    {
      "priority": "high",
      "target": "中段",
      "suggestion": "具体修改方向"
    }
  ],
  "risk_flags": ["风险提示"],
  "next_step": "下一步建议"
}
```

## 集成点

1. **正文草稿详情页**：新增质量检查区域，显示报告数量、当前参考报告、最新报告
2. **侧边栏小说工程分组**：正文质量检查从"后续开放"变为可用链接
3. **世界控制台**：小说工程分组包含正文质量检查入口

## 边界处理

| 场景 | 处理方式 |
|------|----------|
| 正文草稿为空 | 阻止生成，页面提示 |
| 缺少来源章节方案 | 允许生成但提示不完整 |
| 缺少风格方案 | 按通用标准检查 |
| AI 返回非 JSON | 保存原始文本，显示兜底报告 |
| 废弃报告设为 current | 返回错误提示 |
| 跨世界访问 | 返回 404 |
