# Prompt Learning 重构迁移计划

## 当前状态

本迁移计划已经执行完成。

当前 `prompt-learning` 已经：

- 完成平台化重构
- 完成模块拆分
- 完成 workspace 与状态模型落地
- 完成 `SKILL.md` contract 化
- 完成 legacy 接口移除

这份文档保留的主要价值，是记录当时的迁移路径和实施顺序。

## 目标

在不一次性推翻现有实现的前提下，将 `prompt-learning` 平滑迁移到新的“学习平台型”结构。

迁移目标：

- 先建立产品骨架
- 再逐步拆旧逻辑
- 过渡期允许短期兼容
- 降低一次性重构风险

## 迁移原则

### 1. 文档先行

先明确产品、状态、持久化和模块边界，再动 `SKILL.md` 和脚本。

### 2. 分阶段收敛

过渡期允许兼容层存在，但最终产品应只保留新平台接口。

### 3. 先平台骨架，后模块细拆

先让首页、workspace 和状态成立，再迁学习、练习、考试、Prompt Lab。

### 4. 先迁最独立模块

Prompt Lab 和 workspace 最容易抽离，应优先实施。

## 当前资产盘点

当前已存在：

- `SKILL.md`
- `scripts/__main__.py`
- `scripts/state.py`
- `scripts/exam.py`
- `scripts/course_catalog.py`
- `courses/`
- `reference/`

这些资产说明：

- 课程内容和考试蓝图已有基础
- Script-First 思路已经存在
- 但模块边界尚未产品化

## 迁移阶段

## 阶段 0：架构定稿

目标：

- 完成产品化重构文档
- 确定 workspace、状态、CLI 和模块边界

产物：

- `overview.md`
- `skill-contract.md`
- `workspace-and-persistence.md`
- `cli-and-modules.md`
- `state-model.md`
- 各模块专项文档

状态：

- 已完成

## 阶段 1：基础设施迁移

目标：

- 引入 workspace
- 引入新的状态模型
- 建立平台首页能力

建议实现项：

1. 新增 `scripts/workspace.py`
2. 重构或扩展 `scripts/state.py`
3. 新增 `scripts/home.py`
4. 在 `__main__.py` 中增加：
   - `workspace`
   - `home`

阶段验收标准：

- 能成功初始化 `prompt-learning-workspace/<username>/`
- 能返回首页 dashboard
- 能返回 resume 和 recommendation

## 阶段 2：Prompt Lab 迁移

目标：

- 将旧 `generate` 迁移为 `lab`
- 先迁入平台模块，再在后续阶段移除旧入口

建议实现项：

1. 新增 `scripts/prompt_lab.py`
2. 将现有 generate 相关逻辑逐步迁入
3. 增加模板保存与模板列表
4. CLI 增加：
   - `lab --workflow`
   - `lab --interview-blueprint`
   - `lab --validate-slots`
   - `lab --review-checklist`
   - `lab --validate-draft`
   - `lab --save-template`
   - `lab --list-templates`

阶段验收标准：

- Prompt Lab 可独立运行
- 已保存模板可进入 workspace
- 后续可顺利切换到平台型 Prompt Lab 入口

## 阶段 3：学习中心拆分

目标：

- 从 `engine.py` 中拆出学习中心逻辑
- 建立产品化学习闭环

建议实现项：

1. 新增 `scripts/learning.py`
2. 将课程目录、课程元数据、课后面板、代码讲解 outline 迁入
3. 将首页的继续学习与推荐课程接到 `learning`

阶段验收标准：

- `learning --catalog` 可返回结构化课程目录
- `learning --lesson-meta` 可作为课程讲解入口
- `learning --lesson-panel` 可承接课后分流

## 阶段 4：练习中心拆分

目标：

- 将课后一题升级为独立练习中心
- 建立错题回练与掌握度摘要

建议实现项：

1. 新增 `scripts/practice.py`
2. 实现三种练习入口
3. 实现蓝图生成
4. 实现结果摘要写入和错题记录
5. 将状态更新接回 `mastery.json`

阶段验收标准：

- 练习中心可独立进入
- 错题可被记录并回练
- 首页推荐可感知练习结果

## 阶段 5：考试中心产品化

目标：

- 将现有考试逻辑纳入考试中心模块
- 打通考试结果回流

建议实现项：

1. 保留并重构 `scripts/exam.py`
2. 增加考试入口与考试类型
3. 将结果写入考试历史和报告目录
4. 将薄弱点建议回流首页和练习中心

阶段验收标准：

- 诊断考试和综合考试可运行
- 考试记录可进入学习档案
- 首页可基于考试结果推荐下一步

## 阶段 6：`SKILL.md` 切换

目标：

- 将现有 `SKILL.md` 改写为 agent contract
- 用户侧心智全面切换到平台模块

建议实现项：

1. 按 `skill-contract.md` 重写 `SKILL.md`
2. 删除流程性细节
3. 强调平台入口与脚本调用边界

阶段验收标准：

- `SKILL.md` 明显变薄
- 角色、行为、约束边界清晰
- 流程定义主要由脚本和架构文档承接

## 阶段 7：兼容清理

目标：

- 清理内部重复逻辑
- 最终移除旧命令

建议实现项：

1. 让旧 `learn / exam / generate` 先转调新模块
2. 在确认无行为回归后，移除旧命令
3. 删除 `engine.py`

阶段验收标准：

- 只剩新平台入口
- 核心逻辑集中到新模块
- 不再保留 legacy 兼容层

## 优先级建议

若按最小可行重构推进，建议顺序如下：

1. workspace
2. state
3. home
4. prompt_lab
5. learning
6. practice
7. exam
8. `SKILL.md`

## 风险与应对

### 风险 1：一次性改动过大

应对：

- 分阶段迁移
- 分阶段实施后再删除兼容层

### 风险 2：`SKILL.md` 与脚本边界继续混乱

应对：

- 先写 contract 文档
- 改 `SKILL.md` 时严格对照 `skill-contract.md`

### 风险 3：状态模型过重

应对：

- 只存必要摘要
- 历史事件分散到 JSONL 文件

### 风险 4：练习系统过早复杂化

应对：

- V1 只做三种入口
- 不做难度自适应和复杂题库系统

## 成功标准

迁移完成后，应满足：

- 用户首先感知到的是学习平台，而不是旧命令集合
- `SKILL.md` 只承担 contract 职责
- workspace 成为统一持久化入口
- 首页成为统一导航入口
- 学习、练习、考试、Prompt Lab 逐步模块化
- 旧逻辑不再继续膨胀，而是逐步被新结构吸收
