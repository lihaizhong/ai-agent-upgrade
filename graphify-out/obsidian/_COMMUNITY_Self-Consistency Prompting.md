---
type: community
members: 18
---

# Self-Consistency Prompting

**Members:** 18 nodes

## Members
- [[04 - 自我一致性 (Self-Consistency)  自我一致性通过多次采样和投票提高答案可靠性。 核心思想：多想几遍，少数服从多数。  实现步骤： 1]] - rationale - agent-skills/prompt-learning/code/04_self_consistency.py
- [[04_self_consistency.py]] - code - agent-skills/prompt-learning/code/04_self_consistency.py
- [[call_anthropic()]] - code - agent-skills/prompt-learning/code/utils.py
- [[call_openai()]] - code - agent-skills/prompt-learning/code/utils.py
- [[extract_answer()]] - code - agent-skills/prompt-learning/code/utils.py
- [[get_anthropic_client()]] - code - agent-skills/prompt-learning/code/utils.py
- [[get_openai_client()]] - code - agent-skills/prompt-learning/code/utils.py
- [[logic_example()]] - code - agent-skills/prompt-learning/code/04_self_consistency.py
- [[main()_7]] - code - agent-skills/prompt-learning/code/04_self_consistency.py
- [[math_example()]] - code - agent-skills/prompt-learning/code/04_self_consistency.py
- [[self_consistency()]] - code - agent-skills/prompt-learning/code/04_self_consistency.py
- [[utils.py]] - code - agent-skills/prompt-learning/code/utils.py
- [[vote_most_common()]] - code - agent-skills/prompt-learning/code/utils.py
- [[从 LLM 输出中提取答案     简单实现：取最后一行或最后一个句子]] - rationale - agent-skills/prompt-learning/code/utils.py
- [[投票选出最常见的答案      Args         answers 答案列表      Returns         (最常见答案, 得票数, 总]] - rationale - agent-skills/prompt-learning/code/utils.py
- [[自我一致性实现      Args         question 问题         n_samples 采样次数         temperat]] - rationale - agent-skills/prompt-learning/code/04_self_consistency.py
- [[调用 Anthropic LLM      Args         prompt 用户提示词         model 模型名称         te]] - rationale - agent-skills/prompt-learning/code/utils.py
- [[调用 OpenAI LLM      Args         prompt 用户提示词         model 模型名称         tempe]] - rationale - agent-skills/prompt-learning/code/utils.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Self-Consistency_Prompting
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Chain-of-Thought & ToT]]
- 1 edge to [[_COMMUNITY_Reflexion Self-Reflection]]
- 1 edge to [[_COMMUNITY_RAG Implementation]]
- 1 edge to [[_COMMUNITY_Graph Prompting]]
- 1 edge to [[_COMMUNITY_DSP Directional Stimulus]]
- 1 edge to [[_COMMUNITY_PAL Program-Aided Language]]
- 1 edge to [[_COMMUNITY_Active Prompt]]
- 1 edge to [[_COMMUNITY_Generated Knowledge]]
- 1 edge to [[_COMMUNITY_Zero-Shot Prompting]]
- 1 edge to [[_COMMUNITY_ReAct Framework]]
- 1 edge to [[_COMMUNITY_APE Automatic Prompt Engineer]]
- 1 edge to [[_COMMUNITY_Few-Shot Prompting]]
- 1 edge to [[_COMMUNITY_ART Auto Reasoning & Tools]]
- 1 edge to [[_COMMUNITY_Prompt Chaining]]
- 1 edge to [[_COMMUNITY_Multimodal Chain-of-Thought]]

## Top bridge nodes
- [[utils.py]] - degree 24, connects to 15 communities
- [[self_consistency()]] - degree 7, connects to 1 community
- [[call_anthropic()]] - degree 4, connects to 1 community
- [[call_openai()]] - degree 4, connects to 1 community