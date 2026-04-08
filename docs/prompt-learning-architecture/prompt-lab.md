# Prompt Lab 设计

## 目标

将旧的“提示词生成模式”重构为学习平台中的 `Prompt Lab` 模块，使其承担“学以致用”的实战角色，而不是一个脱离平台的并列模式。

Prompt Lab 的核心目标不是代写，而是：

- 让用户把真实任务带进来
- 用稳定结构收敛 prompt 需求
- 解释 prompt 为什么这样设计
- 在用户确认后沉淀可复用模板

## 产品定位

Prompt Lab 是 `prompt-learning` 的应用实验室。

它适合：

- 已学过课程后做真实任务实战
- 对已有 prompt 进行结构化改写
- 快速生成可复用的 prompt 模板
- 在生成过程中顺带学习 prompt 设计原则

它不等同于普通问答，也不等同于简单 prompt 代写。

## 与旧 `generate` 模式的关系

旧 `generate` 模式中的核心资产可以保留：

- 固定 workflow
- 固定槽位
- 槽位校验
- 审查清单
- 草稿校验

但用户心智要改成：

- 从“进入一种模式”
- 变成“进入 Prompt Lab 做一次实战任务”

## 核心流程

Prompt Lab 建议采用以下固定流程：

1. 明确任务主题
2. 获取 workflow
3. 获取 interview blueprint
4. 补齐关键槽位
5. 校验槽位完整性
6. 生成 prompt 草稿
7. 获取审查清单
8. 只修改未通过项
9. 校验最终草稿
10. 用户确认是否保存模板

## 关键槽位

V1 保持五个固定槽位，不扩展更多：

- `task`
- `input`
- `output_format`
- `constraints`
- `quality_bar`

设计原则：

- 槽位少而稳定
- 便于解释
- 能覆盖大多数任务

## 交互原则

### 一次补最缺的 1 到 2 个槽位

不要一次扔给用户五连问问卷。

### 追问要贴近用户原话

优先根据上下文归纳，再请用户确认。

### 解释要嵌入过程

在提问和修订时解释“为什么这个槽位重要”，而不是只做数据采集。

### 先校验，再生成

当槽位不完整时，不要直接跳到最终 prompt。

## 脚本与 LLM 分工

### 脚本负责

- workflow
- interview blueprint
- 槽位校验
- 审查清单
- 草稿校验
- 模板保存
- 模板列表读取

### LLM 负责

- 追问与归纳
- prompt 草稿内容生成
- 审查失败项的修订
- 设计理由说明

## 数据结构

### workflow

用于定义稳定流程：

```json
{
  "topic": "会议纪要总结",
  "workflow": [
    "先收集任务目标、输入、输出、限制",
    "脚本检查是否缺少关键槽位",
    "LLM 生成初稿提示词",
    "脚本按审查清单逐项复核",
    "LLM 只修改未通过项"
  ],
  "required_slots": [
    "task",
    "input",
    "output_format",
    "constraints",
    "quality_bar"
  ]
}
```

### interview blueprint

用于定义槽位提问结构：

```json
{
  "topic": "会议纪要总结",
  "goal": "先补齐稳定槽位，再生成提示词初稿",
  "slots": [
    {
      "name": "task",
      "required": true,
      "question": "你希望 AI 最终完成什么任务？"
    }
  ]
}
```

### review checklist

用于审查 prompt 草稿：

```json
{
  "topic": "会议纪要总结",
  "checklist": [
    "任务目标是否单一明确",
    "输入信息是否定义清楚",
    "输出格式是否可直接判定",
    "约束条件是否可执行",
    "是否明确了失败或边界处理方式",
    "是否避免了重复或冲突指令"
  ]
}
```

## 草稿保存策略

Prompt Lab 只区分两种状态：

- 临时草稿
- 已保存模板

### 临时草稿

- 只存在于当前交互
- 不写入 workspace
- 允许多轮修改

### 已保存模板

- 仅在用户明确确认后写入 workspace
- 保存到 `prompt-learning-workspace/<username>/prompt-lab/templates/`
- 同步更新 `template-index.json`

## 模板保存内容

单个模板应保存：

- 模板 ID
- 模板名称
- topic
- 五个槽位
- 最终 prompt
- 简短备注
- 创建时间与更新时间

不保存：

- 临时追问历史
- 审查中间版本
- 多轮未确认草稿

## 首页与学习档案中的作用

Prompt Lab 的持久化结果应回流到：

### 首页

用于展示：

- 最近是否保存过模板
- 是否推荐继续使用 Prompt Lab

### 学习档案

用于展示：

- 已保存模板数量
- 最近保存模板
- 模板主题分布

## 与课程学习的关系

Prompt Lab 不应被设计成完全独立于课程体系。

建议支持以下联动：

- 学完某门课后，引导用户把该课技术迁移到真实任务
- 在 Prompt Lab 反馈中引用已学课程概念
- 在生成 prompt 时提示相关课程，例如：
  - 零样本提示
  - 少样本提示
  - 思维链提示
  - 链式提示

这样 Prompt Lab 才能真正承担“学习迁移”的作用。

## CLI 建议

Prompt Lab 对应 `lab` 模块，建议支持：

- `lab --workflow --topic "<topic>"`
- `lab --interview-blueprint --topic "<topic>"`
- `lab --validate-slots --topic "<topic>"`
- `lab --review-checklist --topic "<topic>"`
- `lab --validate-draft --topic "<topic>"`
- `lab --save-template`
- `lab --list-templates`

## V1 范围

V1 先做这些：

- 固定 workflow
- 固定五槽位
- 槽位校验
- 审查清单
- 草稿校验
- 模板保存与列表

暂不做：

- 草稿版本管理
- 多模板分组
- 模板评分体系
- 模板协作与共享

## 成功标准

Prompt Lab 重构成功后，应满足：

- 用户把真实任务带进来时有稳定流程可走
- 槽位缺失时系统会继续澄清而不是直接生成
- 生成结果不仅可用，还能解释为什么这样写
- 只有确认后的成果才会进入 workspace
- Prompt Lab 能自然融入整个学习平台，而不是悬空存在
