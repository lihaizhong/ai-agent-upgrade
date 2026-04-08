# Spec: Prompt Learning Interaction Mode Declaration

## 前置依赖

1. `03-selector-first-interaction` 已完成，定义了选择器优先的产品规则和文档对齐
2. 03 号规格验证时发现：当前脚本只在部分交互点返回 `question` 字段，其他交互点完全由 LLM 自行决定如何呈现
3. 这种"部分有声明、部分没有"的状态是 LLM 不稳定使用选择器的根本原因

## 问题陈述

当前 `prompt-learning` 脚本对所有用户交互点的交互模式声明不一致：

- 首页、选课、练习入口、考试入口等**有** `question` 字段 → LLM 能识别出需要用选择器
- 课程推荐、练习蓝图、Prompt Lab 槽位等**没有**任何交互模式声明 → LLM 必须自行推断如何与用户交互
- 当 LLM 需要自行推断时，它有时会退化为纯文本编号列表，而不是使用原生选择器或合适的交互方式

这种不一致导致：

- 选择器渲染不稳定：同一个 skill 在不同对话中可能使用选择器，也可能退化成纯文本
- 03 号规格的"选择器优先"规则只约束了有 `question` 字段的场景，对没有声明的场景没有约束力
- LLM 无法区分"脚本期望这里用选择器"和"脚本期望这里开放式追问"

## 目标

为脚本的所有用户交互输出添加 `interaction` 字段，显式声明每个交互点的交互模式：

1. **`selector`**：必须使用 AI 执行器的原生选择器渲染，脚本提供 `question` 对象
2. **`open_ended`**：由 LLM 自主决定如何与用户交互（追问、确认等），脚本可能提供 `prompt_hint` 作为引导
3. **`inform`**：纯信息展示，没有用户交互

使得：

- LLM 不再需要推断交互模式——脚本明确告诉它每个输出点应该怎么呈现
- 选择器渲染从"LLM 认出 `question` 字段"升级为"脚本声明 `interaction.mode == 'selector'`"
- 退化行为变得可解释、可审计

## 非目标

本规格不包括：

- 改变 CLI 命令结构或新增命令
- 改变 `question` 对象的字段结构
- 改变练习/考试/Prompt Lab 的业务逻辑
- 引入新的交互模式（只有 `selector`、`open_ended`、`inform` 三种）
- 自动化测试 LLM 的工具调用行为（这无法程序化验证）

## 范围

### 必须覆盖的脚本输出点

以下表格列出所有需要添加 `interaction` 字段的脚本输出：

| 模块 | 命令 | 当前输出 | interaction.mode | 备注 |
|------|------|---------|-----------------|------|
| home | `home --dashboard` | 有 `question` | `selector` | ✅ 已有 question |
| home | `home --resume` | dict（路由目标） | `open_ended` | 路由推荐，需要 LLM 组织语言 |
| home | `home --recommend` | dict（推荐动作） | `open_ended` | 推荐说明，需要 LLM 组织语言 |
| learning | `learning --catalog` | 有 `question`（顶层 + 分类级） | `selector` | ✅ 已有 question |
| learning | `learning --category <name>` | 有 `question` | `selector` | ✅ 已有 question |
| learning | `learning --recommend-course` | dict（推荐课程） | `open_ended` | 推荐课程，需要 LLM 组织语言 |
| learning | `learning --lesson-meta` | dict（课程路径） | `inform` | 纯信息输出 |
| learning | `learning --lesson-panel` | 有 `question` | `selector` | ✅ 已有 question |
| learning | `learning --code-meta` | dict（代码路径） | `inform` | 纯信息输出 |
| learning | `learning --code-outline` | dict（讲解结构） | `inform` | 纯信息输出 |
| learning | `learning --complete` | dict（完成确认） | `inform` | 纯信息输出 |
| practice | `practice --entry-points` | 有 `question` | `selector` | ✅ 已有 question |
| practice | `practice --resume` | dict（路由目标） | `open_ended` | 练习路由推荐 |
| practice | `practice --blueprint` | dict（蓝图） | `open_ended` | LLM 需要按蓝图生成题目 |
| practice | `practice --record-result` | dict（记录确认） | `inform` | 纯信息输出 |
| practice | `practice --review-mistakes` | dict（错题列表） | `inform` | 纯信息输出 |
| practice | `practice --summary` | dict（练习摘要） | `inform` | 纯信息输出 |
| exam | `exam --entry-points` | 有 `question` | `selector` | ✅ 已有 question |
| exam | `exam --structure` | dict（考试结构） | `inform` | 纯信息输出 |
| exam | `exam --blueprint` | dict（蓝图） | `inform` | 蓝图供 LLM 参考 |
| lab | `lab --workflow` | dict（固定流程） | `inform` | 流程供 LLM 参考 |
| lab | `lab --interview-blueprint` | dict（槽位定义） | 每个 slot 为 `open_ended`，整体为 `inform` | 槽位逐个追问由 LLM 自主决定 |
| lab | `lab --review-checklist` | dict（审查清单） | `inform` | 清单供 LLM 参考 |
| lab | `lab --validate-slots` | dict（校验结果） | `inform` | 纯信息输出 |
| lab | `lab --validate-draft` | dict（校验结果） | `inform` | 纯信息输出 |
| lab | `lab --save-template` | dict（保存确认） | `inform` | 纯信息输出 |
| lab | `lab --list-templates` | dict（模板列表） | `inform` | 纯信息输出 |
| profile | `profile --summary` | dict（档案摘要） | `inform` | 纯信息输出 |
| profile | `profile --progress` | dict（进度详情） | `inform` | 纯信息输出 |
| profile | `profile --mistakes` | dict（错题详情） | `inform` | 纯信息输出 |
| profile | `profile --exam-history` | dict（考试历史） | `inform` | 纯信息输出 |
| profile | `profile --templates` | dict（模板列表） | `inform` | 纯信息输出 |

### `interaction` 字段格式

```json
{
  "interaction": {
    "mode": "selector" | "open_ended" | "inform",
    "prompt_hint": "可选，当 mode 为 open_ended 时，给 LLM 的交互提示"
  }
}
```

规则：

- `mode` 为必填字段
- `prompt_hint` 为可选字段，只在 `open_ended` 模式下使用，为 LLM 提供交互引导但不强制措辞
- `selector` 模式下，脚本必须同时提供 `question` 对象（保持现有结构不变）
- `inform` 模式下，LLM 只需展示信息，无需设计互动

### Prompt Lab 槽位的特殊处理

`lab --interview-blueprint` 返回的每个 slot 本身是 `open_ended` 交互，但整体输出标记为 `inform`：

```json
{
  "interaction": {
    "mode": "inform",
    "note": "每个 slot 是开放式追问，由 LLM 逐个引导用户填写，不要把 slot 做成选择器"
  },
  "slots": [
    {
      "name": "task",
      "interaction": {
        "mode": "open_ended",
        "prompt_hint": "用自然语言追问用户任务目标"
      },
      ...
    }
  ]
}
```

### SKILL.md 新增：选择器渲染协议

在 SKILL.md 的"选择器优先"小节后新增"选择器渲染协议"子节：

```markdown
### 选择器渲染协议

当脚本输出包含 `interaction` 字段时，必须遵循以下规则：

1. 如果 `interaction.mode == "selector"`：
   - 必须使用当前 AI 执行器的原生选择器工具（如 `question` 工具）渲染
   - `question.question` → 映射为工具的 `question` 参数
   - `question.header` → 映射为工具的 `header` 参数
   - `question.options` → 逐项映射为工具的 `options`，保留 label/description/value 不变
   - `question.multiple` → 映射为工具的 `multiple` 参数
   - 不要把 options 改写为纯文本编号列表

2. 如果 `interaction.mode == "open_ended"`：
   - 由你自主决定如何与用户交互（追问、确认、讨论等）
   - 如有 `prompt_hint`，参考其引导但不必照搬
   - 不要强行把开放式追问改成选择器

3. 如果 `interaction.mode == "inform"`：
   - 只展示信息，不设计互动
   - 根据输出内容组织自然语言说明

4. 如果脚本输出缺少 `interaction` 字段：
   - 这是脚本的缺陷，不是设计
   - 自行决定交互方式，但必须在回复中声明：[交互模式未由脚本定义，当前为自主判断]
```

### 退化行为声明

当 `interaction.mode == "selector"` 但当前执行器不支持结构化选择时，LLM 应：

1. 退化为编号列表
2. 保持 `label`、`description`、`value` 的语义不变
3. 在退化时声明：[当前执行器不支持结构化选择器，已退化为文本列表]

这比 03 号规格的退化规则更精确：退化不是"执行器不支持"的隐性回退，而是需要显式声明的降级。

## 成功标准

本规格完成当且仅当：

1. 所有脚本输出点都包含 `interaction` 字段，声明明确的交互模式
2. `SKILL.md` 中包含选择器渲染协议，给出字段映射规则和退化声明规则
3. 任何 `interaction.mode == "selector"` 的输出点都同时提供 `question` 对象
4. 脚本行为仅做增量修改（加字段），不改变现有 `question` 对象结构
5. LLM 在缺少 `interaction` 字段时会显式声明而非静默推断

## 风险

1. **遗漏交互点**：如果有脚本输出点没有在规格表格中列出，LLM 仍然需要自行推断那一点的交互模式→通过完整审计脚本输出表格来缓解
2. **过度约束**：`open_ended` 模式上加 `prompt_hint` 是否会让 LLM 过于依赖脚本措辞→通过标注"参考而非照搬"来缓解
3. **变更范围**：涉及所有 7 个脚本模块的输出修改→通过只加字段不改结构来控制范围

## 开放问题

1. `exam --grade-mc / --grade-fill / --grade-essay` 是否需要 `interaction` 字段？当前这些是通过 stdin 传入数据、返回评分结果，不是面向用户的输出→倾向于不需要
2. 是否需要在 `interaction` 中加 `version` 字段以支持未来扩展？→MVP 中不加，等有实际需求再加
3. `profile` 模块的所有输出都是 `inform`，是否有必要让脚本逐一声明而不是默认？→统一声明更好，避免"默认"语义模糊