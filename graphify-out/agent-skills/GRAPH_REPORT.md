# Graph Report - agent-skills  (2026-04-20)

## Corpus Check
- Corpus is ~44,659 words - fits in a single context window. You may not need a graph.

## Summary
- 581 nodes · 1359 edges · 16 communities detected
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 304 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Prompt Engineering|Prompt Engineering]]
- [[_COMMUNITY_State Management|State Management]]
- [[_COMMUNITY_Service Layer|Service Layer]]
- [[_COMMUNITY_Law Parsing|Law Parsing]]
- [[_COMMUNITY_Exam Engine|Exam Engine]]
- [[_COMMUNITY_Workspace|Workspace]]
- [[_COMMUNITY_Build & Catalog|Build & Catalog]]
- [[_COMMUNITY_External APIs|External APIs]]
- [[_COMMUNITY_Profile & Review|Profile & Review]]
- [[_COMMUNITY_User State|User State]]
- [[_COMMUNITY_Star Categorization|Star Categorization]]
- [[_COMMUNITY_ART|ART]]
- [[_COMMUNITY_Prompt Chaining|Prompt Chaining]]
- [[_COMMUNITY_APE|APE]]
- [[_COMMUNITY_Initialization|Initialization]]
- [[_COMMUNITY_Singleton|Singleton]]

## God Nodes (most connected - your core abstractions)
1. `main()` - 97 edges
2. `call_llm()` - 45 edges
3. `ExamEngine` - 38 edges
4. `ProfileService` - 32 edges
5. `LearningStateStore` - 30 edges
6. `RagLearningStateStore` - 28 edges
7. `ensure_workspace()` - 27 edges
8. `ExamService` - 23 edges
9. `get_workspace_paths()` - 21 edges
10. `LearningService` - 20 edges

## Surprising Connections (you probably didn't know these)
- `RAG Learning 实战中心。 围绕最小 RAG 项目提供结构化步骤面板。` --uses--> `RagLearningStateStore`  [INFERRED]
  agent-skills/rag-learning/scripts/build.py → agent-skills/rag-learning/scripts/state.py
- `从实验与评审历史聚合稳定偏好并回写 preferences.json。` --uses--> `RagLearningStateStore`  [INFERRED]
  agent-skills/rag-learning/scripts/profile.py → agent-skills/rag-learning/scripts/state.py
- `读取 preferences.json，不存在时返回空结构。` --uses--> `RagLearningStateStore`  [INFERRED]
  agent-skills/rag-learning/scripts/profile.py → agent-skills/rag-learning/scripts/state.py
- `固定考试流程和槽位，题目内容由 LLM 生成。` --uses--> `LearningStateStore`  [INFERRED]
  agent-skills/prompt-learning/scripts/exam.py → agent-skills/prompt-learning/scripts/state.py
- `Prompt Lab 模块 负责 workflow、槽位校验、草稿校验和模板持久化。` --uses--> `LearningStateStore`  [INFERRED]
  agent-skills/prompt-learning/scripts/prompt_lab.py → agent-skills/prompt-learning/scripts/state.py

## Communities

### Community 0 - "Prompt Engineering"
Cohesion: 0.03
Nodes (74): basic_zero_shot(), main(), 01 - 零样本提示 (Zero-Shot Prompting)  零样本提示是最基础的提示词技术，直接给出任务指令，不提供示例。 这是初学者入门的必修课。, zero_shot_structured_output(), zero_shot_with_constraints(), basic_few_shot(), few_shot_for_format(), few_shot_with_reasoning() (+66 more)

### Community 1 - "State Management"
Cohesion: 0.07
Nodes (27): 提示词工程学习系统 - 课程目录 统一维护课程元数据，避免课程文档、代码示例和脚本逻辑各自漂移。, from_skill_dir(), 提示词工程学习系统 - 考试引擎 题目生成、评分、报告生成, from_skill_dir(), HomeService, Prompt Learning 首页服务 负责 dashboard、resume 和 recommendation 结构输出。, _read_json(), LabService (+19 more)

### Community 2 - "Service Layer"
Cohesion: 0.06
Nodes (30): DraftOutput, generate_arbitration_application(), _line(), load_case(), _render_citations(), json_dumps(), json_print(), get_course_metadata() (+22 more)

### Community 3 - "Law Parsing"
Cohesion: 0.07
Nodes (39): find_province_seeds(), load_procedure_seeds(), ProcedureSeeds, extract_links(), Link, _LinkExtractor, HTMLParser, assert_host_allowed() (+31 more)

### Community 4 - "Exam Engine"
Cohesion: 0.09
Nodes (3): ExamEngine, ExamService, 固定考试流程和槽位，题目内容由 LLM 生成。

### Community 5 - "Workspace"
Cohesion: 0.11
Nodes (39): from_skill_dir(), 学习档案模块 负责聚合读取当前进度、练习、考试和模板摘要。, from_skill_dir(), _default_build_progress(), _default_competency(), _default_course_progress(), _default_current_state(), _default_learner() (+31 more)

### Community 6 - "Build & Catalog"
Cohesion: 0.09
Nodes (23): BuildService, RAG Learning 实战中心。 围绕最小 RAG 项目提供结构化步骤面板。, _difficulty_to_code(), _duration_to_minutes(), _extract_learning_tracks(), _extract_recommended_paths(), _extract_table(), _lines() (+15 more)

### Community 7 - "External APIs"
Cohesion: 0.08
Nodes (19): main(), 15 - 自我反思 (Reflexion)  自我反思通过语言反馈强化学习，让模型从错误中学习。 核心循环：执行 → 评估 → 反思 → 改进  工作流程： 1, ReflexionAgent, fetch_stars(), main(), Fetch starred repos using gh CLI., resolve_username(), main() (+11 more)

### Community 8 - "Profile & Review"
Cohesion: 0.12
Nodes (6): ProfileService, 从实验与评审历史聚合稳定偏好并回写 preferences.json。, 读取 preferences.json，不存在时返回空结构。, RAG Learning 架构评审模块。 提供评审入口、结构化模板、结果记录和历史聚合。, ReviewService, _timestamp()

### Community 9 - "User State"
Cohesion: 0.14
Nodes (6): 初始化数据加载器                  Args:             cache_dir: 数据缓存目录，默认为 ~/.chinese-poe, _category_course_ids(), _get_category_for_course(), 优先使用用户指定目录，失败时回退到临时目录。, 获取推荐学习路径。          规则：         - 允许自由选课，不强制线性推进。         - 如果当前课程存在未完成前置课，优先建议补前, UserState

### Community 10 - "Star Categorization"
Cohesion: 0.24
Nodes (12): categorize_repo(), format_date(), format_stars(), generate_category_doc(), generate_readme(), generate_repo_entry(), main(), Categorize a single repo using priority-based matching. (+4 more)

### Community 11 - "ART"
Cohesion: 0.27
Nodes (4): ART, main(), 11 - 自动推理和工具使用 (ART)  ART (Automatic Reasoning and Tool-use) 让模型自动选择和使用工具。 核心：从任, Tool

### Community 12 - "Prompt Chaining"
Cohesion: 0.39
Nodes (4): document_analysis_example(), main(), PromptChain, 08 - 链式提示 (Prompt Chaining)  链式提示将复杂任务分解为多个简单步骤，顺序执行。 核心：每个步骤的输出作为下一步的输入。  适用场景：

### Community 13 - "APE"
Cohesion: 0.48
Nodes (6): ape_optimize(), calculate_similarity(), evaluate_prompt(), generate_candidate_prompts(), main(), 12 - 自动提示工程师 (APE)  APE (Automatic Prompt Engineer) 自动生成和优化提示词。 核心：通过 LLM 生成多个候选

### Community 14 - "Initialization"
Cohesion: 0.67
Nodes (1): RAG Learning platform scripts.

### Community 15 - "Singleton"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **59 isolated node(s):** `Fetch starred repos using gh CLI.`, `Categorize a single repo using priority-based matching.`, `Format ISO date to readable string.`, `Generate markdown entry for a single repo.`, `Generate markdown document for a category.` (+54 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Singleton`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `Service Layer` to `State Management`, `Law Parsing`, `Exam Engine`, `Workspace`, `Build & Catalog`, `External APIs`, `Profile & Review`, `User State`?**
  _High betweenness centrality (0.495) - this node is a cross-community bridge._
- **Why does `call_llm()` connect `Prompt Engineering` to `ART`, `Prompt Chaining`, `APE`, `External APIs`?**
  _High betweenness centrality (0.344) - this node is a cross-community bridge._
- **Why does `resolve_git_username()` connect `Workspace` to `Service Layer`, `External APIs`?**
  _High betweenness centrality (0.230) - this node is a cross-community bridge._
- **Are the 85 inferred relationships involving `main()` (e.g. with `resolve_git_username()` and `json_print()`) actually correct?**
  _`main()` has 85 INFERRED edges - model-reasoned connections that need verification._
- **Are the 41 inferred relationships involving `call_llm()` (e.g. with `.execute()` and `.evaluate()`) actually correct?**
  _`call_llm()` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `ExamEngine` (e.g. with `LearningStateStore` and `提示词工程学习系统 - CLI 入口 提供命令行接口供 AI Agent 调用`) actually correct?**
  _`ExamEngine` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `ProfileService` (e.g. with `RagLearningStateStore` and `ReviewService`) actually correct?**
  _`ProfileService` has 10 INFERRED edges - model-reasoned connections that need verification._