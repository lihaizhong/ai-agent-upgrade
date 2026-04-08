---
name: prompt-learning
description: 提示词工程学习、练习、考试和提示词生成技能。用户想系统学习 prompt engineering、浏览 17 门课程、做练习或考试、分析提示词问题、优化已有提示词，或通过结构化头脑风暴生成提示词时使用。
---

# 提示词工程学习系统

按 Script-First 执行：脚本负责固定流程、题位、字段、交互 schema 和校验规则；LLM 只负责教学内容、题干、讲解、反馈和提示词草稿。不要在文档里重新发明一套菜单或字段。

在执行脚本前，**必须先检查可用的 Python 执行器**：

1. **第一步**：先尝试系统 Python
   - macOS / Linux: `which python3` 或 `which python`
   - Windows: `where python`

2. **第二步**：只有第一步找不到可用的 Python 解释器时，才使用仓库虚拟环境
   - 相对路径（工作目录在 skill 根目录时）: `../../../.venv/bin/python`

**禁止**：直接调用 `python -m scripts ...` 而不先检查环境。

以下命令示例默认写成 `python -m scripts ...`。

`scripts/` 目录就在当前 skill 根目录下。执行器应先把当前工作目录切到本 skill 目录，再运行 `python -m scripts ...`；不要去仓库其他位置搜索同名 `scripts`，也不要自行猜测替代路径。

在本技能根目录执行：

- `python -m scripts mode`
- `python -m scripts learn --list`
- `python -m scripts learn --category "<类别>"`
- `python -m scripts learn --content --course <N>`
- `python -m scripts learn --practice-blueprint --course <N>`
- `python -m scripts learn --panel --course <N>`
- `python -m scripts learn --code --course <N>`
- `python -m scripts learn --code-outline --course <N>`
- `python -m scripts exam --structure`
- `python -m scripts exam --blueprint`
- `python -m scripts exam --validate-mc`
- `python -m scripts exam --validate-fill`
- `python -m scripts exam --validate-essay`
- `python -m scripts exam --validate-paper`
- `python -m scripts generate --workflow --topic "<主题>"`
- `python -m scripts generate --interview-blueprint --topic "<主题>"`
- `python -m scripts generate --review-checklist --topic "<主题>"`
- `python -m scripts generate --validate-slots --topic "<主题>"`
- `python -m scripts generate --validate-draft --topic "<主题>"`

## 执行原则

- 先读脚本输出，再决定如何和用户交互。
- 如果当前环境提供单选工具，优先直接使用脚本返回的 `question` 字段；没有工具时才退化成文本菜单。
- 课程、考试、生成模式的固定结构以脚本返回为准，不要手写新的 JSON schema。
- 只按需读取课程文件、代码文件和 reference 文档，不要一次性加载整个技能库。

## 模式选择

1. 先运行 `python -m scripts mode`。
2. 工具可用时，直接使用脚本返回的 `question` 字段发起选择。
3. 工具不可用时，再把 `modes` 渲染成文本菜单。

禁止：

- 工具可用时直接输出“1/2/3 请选择”
- 未读取脚本输出就默认进入某个模式
- 口头描述模式但不真正发起选择

## 学习模式

执行顺序：

1. 用 `python -m scripts learn --list` 获取六大类课程与选课 schema。
2. 用户指定类别时，用 `python -m scripts learn --category "<类别>"` 获取该类别课程。
3. 用户选课后，用 `python -m scripts learn --content --course <N>` 先完成教学，再进入后续交互。
4. 要出练习时，用 `python -m scripts learn --practice-blueprint --course <N>` 获取固定蓝图。
5. 课程教学结束后，用 `python -m scripts learn --panel --course <N>` 获取下一步面板。
6. 用户要看代码时，用 `python -m scripts learn --code --course <N>` 读取代码，再用 `python -m scripts learn --code-outline --course <N>` 按固定结构拆段讲解。

教学约束：

- 用户指定某一课时，直接进入；前置课程只作理解建议，不是门槛。
- 没有真正展示课程内容前，不要提前说“学完了”或直接弹课后面板。
- 练习题的结构、题型、评分关注点以脚本蓝图为准；LLM 只填充内容。
- 默认分段讲代码，不默认整段贴完整文件。

需要更多教学示例时，再读：

- `reference/learning-mode.md`

## 考试模式

执行顺序：

1. 用 `python -m scripts exam --structure` 告知固定分值结构。
2. 用 `python -m scripts exam --blueprint` 获取 11 个固定题位。
3. 让 LLM 按题位生成题目内容，不改题型、分值、难度和字段。
4. 展示前调用对应 `--validate-*` 命令，必要时再用 `--validate-paper` 校验整卷。
5. 每题给即时反馈，完整解析放到考试结束后。
6. 需要落盘报告时，用 `python -m scripts exam --report`。

需要详细示例或反馈风格时，再读：

- `reference/exam-mode.md`

## 提示词生成模式

执行顺序：

1. 用 `python -m scripts generate --workflow --topic "<主题>"` 获取固定流程与必填槽位。
2. 用 `python -m scripts generate --interview-blueprint --topic "<主题>"` 获取澄清槽位。
3. 通过头脑风暴补齐 `task`、`input`、`output_format`、`constraints`、`quality_bar`。
4. 用 `python -m scripts generate --validate-slots --topic "<主题>"` 校验槽位完整性。
5. 让 LLM 生成提示词草稿。
6. 用 `python -m scripts generate --review-checklist --topic "<主题>"` 获取审查清单。
7. 逐项审查，只修改未通过项。
8. 用 `python -m scripts generate --validate-draft --topic "<主题>"` 校验草稿和审查记录。

需要更多引导示例时，再读：

- `reference/prompt-generation-mode.md`

## 提示词分析与学习辅导

如果用户不是进入三大模式，而是要诊断提示词问题、比较技术边界、推荐学习路径或改写现有提示词：

1. 先直接回答。
2. 需要系统材料时，再按需读取：
   - `reference/common-problems.md`
   - `reference/prompt-patterns.md`
   - `reference/faq.md`
3. 回答优先给出：
   - 问题定位
   - 原因解释
   - 可直接复用的改写建议
   - 适合继续学习的课程编号
