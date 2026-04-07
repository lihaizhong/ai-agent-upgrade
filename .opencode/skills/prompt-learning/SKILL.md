---
name: prompt-learning
description: 提示词工程学习、练习、考试和提示词生成技能。用户想系统学习 prompt engineering、浏览 17 门课程、做练习或考试、分析提示词问题、优化已有提示词，或通过结构化头脑风暴生成提示词时使用。
---

# 提示词工程学习系统

按 Script-First 执行：先让脚本固定流程、题位、字段和校验规则，再让 LLM 生成教学内容、题干、讲解或提示词草稿。不要把脚本输出当成题库；要把它当成结构约束。

在本技能目录执行命令：

- `/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts mode`
- `/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts learn --list`
- `/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts learn --content --course <N>`
- `/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts learn --practice-blueprint --course <N>`
- `/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts learn --code --course <N>`
- `/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts exam --structure`
- `/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts exam --blueprint`
- `/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts exam --validate-mc`
- `/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts exam --validate-fill`
- `/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts exam --validate-essay`
- `/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts exam --validate-paper`
- `/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts generate --workflow --topic "<主题>"`
- `/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts generate --review-checklist --topic "<主题>"`
- `/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts generate --validate-slots --topic "<主题>"`
- `/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts generate --validate-draft --topic "<主题>"`

## 模式选择

优先用脚本返回三大模式，再决定怎么和用户交互。

如果当前环境明确提供 `question` 一类单选工具，可用它展示模式、课程或选项。
如果当前环境没有这类工具，直接用纯文本编号菜单，不要假设交互式工具存在。

## 学习模式

执行顺序：

1. 用 `scripts learn --list` 获取按类别分组的课程列表。
2. 用户选课后，用 `scripts learn --content --course <N>` 读取课程内容。
3. 课程讲完后，同时给出三类下一步：
   - 启发式提问
   - 可选练习
   - 学习导航
4. 如果用户要做练习，先用 `scripts learn --practice-blueprint --course <N>` 拿到固定蓝图，再让 LLM 填充题干、参考答案和反馈。
5. 如果练习里出现选择题，确保正确答案随机落在 `A/B/C/D` 中，不要固定位置。
6. 用户完成练习后，主动提示查看配套代码；需要时用 `scripts learn --code --course <N>` 读取对应实现并解释关键逻辑。

只按需读取课程文件和代码文件，不要一次性加载整个课程库：

- 课程正文在 `courses/`
- 代码示例在 `code/`

需要细化教学流程时，再读：

- `reference/learning-mode.md`

## 考试模式

考试结构固定，开始前先告知用户分值构成：

- 选择题 5 题，每题 5 分，共 25 分
- 填空题 3 题，每题 10 分，共 30 分
- 大题 3 题，每题 15 分，共 45 分
- 总分固定 100 分

执行顺序：

1. 用 `scripts exam --structure` 告知考试结构。
2. 用 `scripts exam --blueprint` 获取 11 个固定题位。
3. 让 LLM 按题位生成题目内容，不改题型、分值、难度和字段。
4. 展示前调用对应校验命令，必要时再用 `--validate-paper` 校验整卷。
5. 即时反馈对错和简短说明；完整解析放到考试结束后。
6. 需要落盘报告时，用 `scripts exam --report`；如需覆盖默认值，再传 `--username <name>`。

如果当前环境明确提供单选工具，优先用它承载选择题。
如果当前环境没有单选工具，退化为纯文本选项输入，但仍保持同样的题位、分值和校验流程。

需要完整出题和反馈规范时，再读：

- `reference/exam-mode.md`

## 提示词生成模式

执行顺序：

1. 用 `scripts generate --workflow --topic "<主题>"` 获取固定工作流和必填槽位。
2. 通过头脑风暴补齐 `task`、`input`、`output_format`、`constraints`、`quality_bar`。
3. 用 `scripts generate --validate-slots` 校验槽位是否齐全。
4. 让 LLM 生成提示词草稿。
5. 用 `scripts generate --review-checklist --topic "<主题>"` 获取审查清单。
6. 逐项审查，只修改不合格项。
7. 用 `scripts generate --validate-draft --topic "<主题>"` 校验草稿和审查记录。

需要完整引导话术时，再读：

- `reference/prompt-generation-mode.md`

## 提示词分析与学习辅导

如果用户不是要正式进入三大模式，而是想：

- 分析某段提示词的问题
- 诊断输出不稳定、格式错误、幻觉、冗长等现象
- 让你推荐某种提示词模式
- 追问某个提示技术的差异、边界和适用场景

先判断是否能直接回答；需要更系统的辅助材料时，按需读取：

- `reference/common-problems.md`
- `reference/prompt-patterns.md`
- `reference/faq.md`

回答时优先给出：

1. 问题定位
2. 原因解释
3. 可直接复用的改写建议
4. 适合继续学习的课程编号

## 课程与代码映射

课程和代码一一对应，按编号读取即可：

- 01 `零样本提示` -> `code/01_zero_shot.py`
- 02 `少样本提示` -> `code/02_few_shot.py`
- 03 `思维链提示` -> `code/03_cot.py`
- 04 `自我一致性` -> `code/04_self_consistency.py`
- 05 `思维树` -> `code/05_tot.py`
- 06 `生成知识提示` -> `code/06_generated_knowledge.py`
- 07 `检索增强生成` -> `code/07_rag.py`
- 08 `链式提示` -> `code/08_prompt_chaining.py`
- 09 `ReAct框架` -> `code/09_react.py`
- 10 `程序辅助语言模型` -> `code/10_pal.py`
- 11 `自动推理和工具使用` -> `code/11_art.py`
- 12 `自动提示工程师` -> `code/12_ape.py`
- 13 `主动提示` -> `code/13_active_prompt.py`
- 14 `方向性刺激提示` -> `code/14_dsp.py`
- 15 `自我反思` -> `code/15_reflexion.py`
- 16 `多模态思维链` -> `code/16_multimodal_cot.py`
- 17 `图提示` -> `code/17_graph_prompt.py`
