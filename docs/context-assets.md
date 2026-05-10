# 创作上下文资产库设计文档

## 概述

创作上下文资产库（Creative Context Asset Library）是 AI World Engine v1.6.0 引入的功能模块，旨在解决小说生成时需要反复手动填写大量内容的问题。

## 核心概念

### 1. StyleProfile（写作风格方案）

**职责**: 保存用户确认的写作风格要求，作为 AI 生成的写作约束。

**字段概览**:
- `name`: 方案名称（必填）
- `world_id`: 关联世界（可为空，表示全局方案）
- `genre`: 题材类型
- `narrative_pov`: 叙事人称（第一人称/第三人称有限/第三人称全知/多视角）
- `pacing`: 叙事节奏
- `dialogue_style`: 对话风格
- `conflict_style`: 冲突推进风格
- `forbidden_patterns`: 禁用写法
- `extra_instructions`: 补充要求

**特点**:
- 可设为全局方案（world_id=NULL），在所有世界中可用
- 也可关联特定世界，仅在该世界中使用
- 只是写作约束，不得改变剧情事实

### 2. PlotAnchor（剧情时间点/剧情锚点）

**职责**: 记录当前故事推进到哪个阶段，作为后续生成的故事进度参考。

**字段概览**:
- `name`: 时间点名称（必填）
- `world_id`: 关联世界（必填，跨世界隔离）
- `stage`: 所属阶段
- `volume_name`: 所属卷名
- `protagonist_age`: 主角当前年龄
- `current_location`: 当前地点
- `occurred_events`: 已发生的关键事件
- `hidden_secrets`: 尚未公开的秘密
- `current_conflict`: 当前核心矛盾
- `character_states`: 主要角色当前状态
- `faction_states`: 各势力当前状态
- `current_goal`: 当前阶段目标
- `next_goal`: 下一步目标
- `forbidden_events`: 禁止在当前阶段发生的事件
- `is_locked`: 是否锁定（锁定后不可随意修改）

**特点**:
- 先做到"阶段级"，不要求精确章节级
- 不会自动改写历史事件
- 跨世界严格隔离

### 3. ContextPackage（创作上下文包）

**职责**: 将推演方案、风格方案、剧情时间点和生成配置组合成一个可复用的创作上下文包。

**字段概览**:
- `name`: 上下文包名称（必填）
- `world_id`: 关联世界（必填）
- `simulation_record_id`: 引用的推演记录（可选）
- `style_profile_id`: 引用的风格方案（可选）
- `plot_anchor_id`: 引用的剧情时间点（可选）
- `generation_type`: 生成类型
- `strict_canon`: 是否严格遵守正史
- `strict_style`: 是否严格遵守风格
- `include_branches`: 是否包含分支世界线
- `include_non_canon`: 是否包含非正史事件
- `target_words`: 目标字数
- `extra_requirements`: 补充要求
- `is_default`: 是否默认上下文包

**特点**:
- 只是引用组合，不复制重复内容
- 所有引用必须在同一个世界内
- 推演记录只能选 eligible 类型（novel_evolution/protagonist_route/world_reaction/world_simulation/general）
- 已废弃（discarded）的推演记录默认不展示

## 三者关系

```
ContextPackage（创作上下文包）
├── SimulationRecord（推演记录）  ← 引用
├── StyleProfile（风格方案）     ← 引用
└── PlotAnchor（剧情时间点）     ← 引用
```

用户在小说的创作流程中：
1. 先创建风格方案和剧情时间点
2. 运行 AI 推演获得推演记录
3. 将三者组合为创作上下文包
4. 在小说生成页面选择上下文包
5. AI 基于上下文包中的信息进行推演和生成

## 不会自动写入正史的内容

以下内容**不会**自动写入正史：
- AI 生成的所有内容
- 风格方案本身
- 剧情时间点本身
- 上下文包本身

用户必须手动审核后，选择「采纳为正史」或「保存为分支」。

## 安全规则

1. 跨世界数据隔离：世界 A 的剧情时间点不能出现在世界 B
2. 上下文包引用必须属于同一个世界
3. 全局风格方案可在所有世界使用
4. 删除被引用的资产时，提示先移除引用
5. 导入时自动 ID 重新映射

## 后续扩展方向

本版本（v1.6.0）只是创作上下文资产库基础版，后续可扩展：

- v1.7.0+: 全书演化推演增强版（基于上下文包生成更稳定的小说全书路线）
- 后续: 分卷大纲、章节大纲
- 后续: 正文生成完整流水线
- 后续: 参考小说导入和自动风格分析
- 后续: 风格一致性评分
- 后续: 多部小说项目管理
- 后续: 云同步

## 页面路径

| 页面 | 路径 |
|------|------|
| 创作上下文总览 | `/worlds/{id}/context` |
| 风格方案列表 | `/worlds/{id}/context/styles` |
| 新建/编辑风格方案 | `/worlds/{id}/context/styles/new` `/edit` |
| 剧情时间点列表 | `/worlds/{id}/context/anchors` |
| 新建/编辑剧情时间点 | `/worlds/{id}/context/anchors/new` `/edit` |
| 上下文包列表 | `/worlds/{id}/context/packages` |
| 新建/编辑上下文包 | `/worlds/{id}/context/packages/new` `/edit` |
| 上下文包详情 | `/worlds/{id}/context/packages/{id}` |

## 小说生成集成

在小说生成页面（`/worlds/{id}/novel`），用户可以选择已保存的创作上下文包。选中后：
- 推演记录内容被加载到 context_snapshot
- 风格方案被加载为写作约束
- 剧情时间点被加载为故事进度参考
- 生成配置被应用到 AI 调用选项
