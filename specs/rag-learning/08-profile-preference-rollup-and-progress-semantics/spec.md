# Spec Change: Profile Preference Rollup And Progress Semantics

## Objective

把 `rag-learning` 的学习档案从“当前状态 + 最近历史”收敛为“当前状态 + 真实进度 + 稳定偏好”的产品模块，使 `profile` 真正承担长期沉淀职责。

本次 change 主要解决：

1. `workspace-and-persistence.md` 已定义 `profile/preferences.json`，但当前实现几乎没有消费或更新它
2. `overview.md` 与 `profile.md` 都承诺了“选型偏好”，`profile --summary` 目前尚未暴露
3. `active_project_count` 当前按项目总数统计，容易把 completed project 继续算成 active
4. 实验和评审已经产生了结构化证据，但还没有被聚合成稳定的用户级偏好视图

## Assumptions

1. `profile` 仍是平台的长期状态聚合模块，不承担新的教学或执行职责
2. 偏好沉淀只记录稳定 summary，不保存完整推理过程
3. 偏好来源以实验结果和评审推荐栈为主，必要时可补充 build 选择痕迹
4. 本次 change 不引入复杂打分系统或趋势分析仪表盘

## Background

当前 `profile --summary` 已经能展示：

- 当前模块
- 课程 / 项目 / 实验 / 评审数量
- 最近实验与最近评审
- 状态层 recommendation

但仍缺少“长期沉淀”这一层：

- 用户已经多次选择 `qdrant`、`bge-m3` 或“不引入 rerank”，平台没有形成稳定偏好摘要
- `preferences.json` 只是目录骨架的一部分，还不是产品真相
- 项目进度计数仍偏粗，无法稳定支持首页或档案解释

结果是 learning profile 更像“最近发生了什么”，而不是“这个用户已经形成了哪些判断”。

## Scope

### 1. 定义稳定偏好的聚合来源

偏好不应自由生成，应来自已存在的结构化证据，例如：

- `lab` 中的 `recommended_choice`
- `review` 中的 `recommended_stack`
- 必要时来自 build 的已确认组件选择

至少应覆盖：

- embedding 偏好
- vector db 偏好
- retrieval / rerank 偏好
- deployment 或方案倾向

### 2. 让 `preferences.json` 成为可解释的稳定摘要

`preferences.json` 不应只是空壳或手写占位，而应能表达：

- 当前稳定偏好
- 最近证据来源
- 最近更新时间

它可以是写时更新，也可以是聚合时回写，但必须只有一套真相。

### 3. 扩展 `profile --summary` 的长期沉淀视图

`profile --summary` 至少应新增：

- `stable_preferences`
- 偏好证据摘要或来源计数
- 更准确的 active/completed progress 计数

这样用户才能从档案里看到“我已经形成了哪些工程判断”。

### 4. 对齐首页、档案和持久化边界

需要确保：

- 首页可以消费档案层的真实进度，而不是被粗糙统计误导
- 偏好只保存稳定 summary，不保存冗余对话
- 文档中的 `preferences.json` 与真实实现一致

## Boundaries

- Always:
  - 偏好必须来自结构化证据，而不是自由生成
  - `preferences.json` 必须可解释、可追溯
  - active / completed progress 统计必须和真实 project 状态一致
- Ask first:
  - 引入复杂画像系统或多维打分仪表盘
  - 保存完整评审正文或实验草稿
  - 把偏好扩展成跨用户全局推荐系统
- Never:
  - 把单次偶然选择直接包装成稳定偏好而不标注来源
  - 让 `profile` 只显示 history，却不形成长期沉淀
  - 让 `preferences.json` 与 `profile --summary` 出现双真相

## Success Criteria

- [x] `preferences.json` 有明确、可解释的稳定偏好结构
- [x] `profile --summary` 暴露 `stable_preferences` 与相应证据摘要
- [x] active/completed project 计数与真实状态一致
- [x] 偏好来源在实验与评审证据层可追溯
- [x] 文档、持久化结构和 `profile` 输出语义一致
- [x] 相关平台、状态流与内容测试覆盖上述行为

## Non-Goals

- 不做复杂用户画像
- 不新增趋势分析图表
- 不重做实验和评审的完整 history schema
- 不把偏好变成强制推荐策略

## Open Questions

1. 冲突偏好应优先按“最近证据”还是“累计证据”聚合？
2. `preferences.json` 应主要在写入实验/评审时更新，还是由 `profile` 聚合并回写？
