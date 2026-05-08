# Graph Report - .  (2026-05-08)

## Corpus Check
- Large corpus: 288 files · ~124,746 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder, or use --no-semantic to run AST-only.

## Summary
- 999 nodes · 1775 edges · 67 communities (63 shown, 4 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 85 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Labor Rights Defense Core|Labor Rights Defense Core]]
- [[_COMMUNITY_RAG Learning Platform Build|RAG Learning Platform Build]]
- [[_COMMUNITY_Exam Engine|Exam Engine]]
- [[_COMMUNITY_Prompt Learning Course System|Prompt Learning Course System]]
- [[_COMMUNITY_Test Utilities|Test Utilities]]
- [[_COMMUNITY_Practice Agent Loops|Practice Agent Loops]]
- [[_COMMUNITY_Profile & Workspace Management|Profile & Workspace Management]]
- [[_COMMUNITY_Labor Rights CLI & Drafting|Labor Rights CLI & Drafting]]
- [[_COMMUNITY_RAG Learning Catalog|RAG Learning Catalog]]
- [[_COMMUNITY_RAG Knowledge Base Engine|RAG Knowledge Base Engine]]
- [[_COMMUNITY_Practice Center Tests|Practice Center Tests]]
- [[_COMMUNITY_Poetry Skill|Poetry Skill]]
- [[_COMMUNITY_Profile Service|Profile Service]]
- [[_COMMUNITY_Prompt Lab Tests|Prompt Lab Tests]]
- [[_COMMUNITY_Exam Session Tests|Exam Session Tests]]
- [[_COMMUNITY_Learning Center Tests|Learning Center Tests]]
- [[_COMMUNITY_Platform Smoke Tests|Platform Smoke Tests]]
- [[_COMMUNITY_Self-Consistency Prompting|Self-Consistency Prompting]]
- [[_COMMUNITY_Home Service & Dashboard|Home Service & Dashboard]]
- [[_COMMUNITY_Skills Agent Loop|Skills Agent Loop]]
- [[_COMMUNITY_Chain-of-Thought & ToT|Chain-of-Thought & ToT]]
- [[_COMMUNITY_Data Analysis Agent|Data Analysis Agent]]
- [[_COMMUNITY_RAG Platform Smoke Tests|RAG Platform Smoke Tests]]
- [[_COMMUNITY_Greeting Module|Greeting Module]]
- [[_COMMUNITY_RAG Edge Case Tests|RAG Edge Case Tests]]
- [[_COMMUNITY_State Flow Tests|State Flow Tests]]
- [[_COMMUNITY_Graph Prompting|Graph Prompting]]
- [[_COMMUNITY_Practice Service|Practice Service]]
- [[_COMMUNITY_Todo Management Agent|Todo Management Agent]]
- [[_COMMUNITY_Auto-Compact Agent|Auto-Compact Agent]]
- [[_COMMUNITY_RAG State Flow Tests|RAG State Flow Tests]]
- [[_COMMUNITY_RAG Content Quality Tests|RAG Content Quality Tests]]
- [[_COMMUNITY_ART Auto Reasoning & Tools|ART Auto Reasoning & Tools]]
- [[_COMMUNITY_ReAct Framework|ReAct Framework]]
- [[_COMMUNITY_Reflexion Self-Reflection|Reflexion Self-Reflection]]
- [[_COMMUNITY_Subagent Spawning|Subagent Spawning]]
- [[_COMMUNITY_RAG Implementation|RAG Implementation]]
- [[_COMMUNITY_Tool-Using Agent|Tool-Using Agent]]
- [[_COMMUNITY_Multimodal Chain-of-Thought|Multimodal Chain-of-Thought]]
- [[_COMMUNITY_DSP Directional Stimulus|DSP Directional Stimulus]]
- [[_COMMUNITY_Prompt Chaining|Prompt Chaining]]
- [[_COMMUNITY_Content Quality Tests|Content Quality Tests]]
- [[_COMMUNITY_APE Automatic Prompt Engineer|APE Automatic Prompt Engineer]]
- [[_COMMUNITY_PAL Program-Aided Language|PAL Program-Aided Language]]
- [[_COMMUNITY_Few-Shot Prompting|Few-Shot Prompting]]
- [[_COMMUNITY_Zero-Shot Prompting|Zero-Shot Prompting]]
- [[_COMMUNITY_Basic Agent Loop|Basic Agent Loop]]
- [[_COMMUNITY_Active Prompt|Active Prompt]]
- [[_COMMUNITY_Generated Knowledge|Generated Knowledge]]
- [[_COMMUNITY_Hello Module|Hello Module]]
- [[_COMMUNITY_Greet Module|Greet Module]]
- [[_COMMUNITY_Concurrent Ping Test|Concurrent Ping Test]]
- [[_COMMUNITY_RAG Package Init|RAG Package Init]]

## God Nodes (most connected - your core abstractions)
1. `call_llm()` - 45 edges
2. `ExamEngine` - 40 edges
3. `main()` - 30 edges
4. `ProfileService` - 26 edges
5. `LearningStateStore` - 23 edges
6. `ensure_workspace()` - 22 edges
7. `ExamService` - 22 edges
8. `RagLearningStateStore` - 20 edges
9. `PromptLearningPracticeCenterTest` - 19 edges
10. `LearningService` - 18 edges

## Surprising Connections (you probably didn't know these)
- `TestProcedureCrawler` --uses--> `FetchedPage`  [INFERRED]
  tests/labor_rights_defense/test_procedure_crawler.py → agent-skills/labor-rights-defense/scripts/procedure_crawler.py
- `retrieve()` --calls--> `cosine_similarity()`  [INFERRED]
  rag-learning-workspace/lihzsky/lab/embedding-comparison.py → practice/build-rag-agent/main.py
- `main()` --calls--> `load_procedure_seeds()`  [INFERRED]
  agent-skills/prompt-learning/scripts/__main__.py → agent-skills/labor-rights-defense/scripts/config.py
- `main()` --calls--> `find_province_seeds()`  [INFERRED]
  agent-skills/prompt-learning/scripts/__main__.py → agent-skills/labor-rights-defense/scripts/config.py
- `main()` --calls--> `load_case()`  [INFERRED]
  agent-skills/prompt-learning/scripts/__main__.py → agent-skills/labor-rights-defense/scripts/draft_service.py

## Communities (67 total, 4 thin omitted)

### Community 0 - "Labor Rights Defense Core"
Cohesion: 0.06
Nodes (41): HTMLParser, setUpClass(), TestLawParser, TestProcedureCrawler, find_province_seeds(), load_procedure_seeds(), ProcedureSeeds, extract_links() (+33 more)

### Community 1 - "RAG Learning Platform Build"
Cohesion: 0.06
Nodes (18): RagLearningConfigUnitTest, BuildService, RAG Learning 实战中心。 围绕最小 RAG 项目提供结构化步骤面板。, load_build_projects(), load_build_step_panels(), load_lab_topics(), load_platform_config(), load_review_fields() (+10 more)

### Community 2 - "Exam Engine"
Cohesion: 0.09
Nodes (3): ExamEngine, ExamService, 固定考试流程和槽位，题目内容由 LLM 生成。

### Community 3 - "Prompt Learning Course System"
Cohesion: 0.1
Nodes (21): 提示词工程学习系统 - 课程目录 统一维护课程元数据，避免课程文档、代码示例和脚本逻辑各自漂移。, from_skill_dir(), 提示词工程学习系统 - 考试引擎 题目生成、评分、报告生成, from_skill_dir(), 学习中心模块 负责课程目录、课程元数据、推荐课程和课程完成状态更新。, from_skill_dir(), 练习中心模块 负责练习入口和动态练习蓝图。, default_build_progress() (+13 more)

### Community 4 - "Test Utilities"
Cohesion: 0.05
Nodes (34): Tests for utils module., Test capitalizing an empty string., Tests for the greet function., Test greet with a name., Test greet with an empty name., Tests for the calculate_sum function., Test sum with integers., Test sum with floats. (+26 more)

### Community 5 - "Practice Agent Loops"
Cohesion: 0.06
Nodes (21): display_menu(), get_available_loops(), import_loop_module(), main(), Main entry point for the Coding Agent  Usage:     python main.py  This script pr, Scan the code directory for all s*-loop.py files     Returns a list of (module_n, Dynamically import a loop module from the code directory, Display a menu of available loops and return the selected module name (+13 more)

### Community 6 - "Profile & Workspace Management"
Cohesion: 0.11
Nodes (38): from_skill_dir(), 学习档案模块 负责聚合读取当前进度、练习、考试和模板摘要。, _default_build_progress(), _default_competency(), _default_course_progress(), _default_current_state(), _default_learner(), _default_mastery() (+30 more)

### Community 7 - "Labor Rights CLI & Drafting"
Cohesion: 0.1
Nodes (28): DraftOutput, generate_arbitration_application(), _line(), load_case(), _render_citations(), json_dumps(), json_print(), _ensure_workspace_or_exit() (+20 more)

### Community 8 - "RAG Learning Catalog"
Cohesion: 0.11
Nodes (14): _difficulty_to_code(), _duration_to_minutes(), _extract_learning_tracks(), _extract_recommended_paths(), _extract_table(), _lines(), load_course_catalog(), load_recommended_paths() (+6 more)

### Community 9 - "RAG Knowledge Base Engine"
Cohesion: 0.11
Nodes (22): build_index(), chunk_text(), cosine_similarity(), get_embedding(), get_embeddings_batch(), load_documents(), 加载 knowledge_base 目录下所有 .md 文件内容。, 按字符长度分块，相邻块之间保留 overlap 重叠。 (+14 more)

### Community 10 - "Practice Center Tests"
Cohesion: 0.14
Nodes (4): PromptLearningPracticeCenterTest, read_json(), run_cli(), setUpClass()

### Community 11 - "Poetry Skill"
Cohesion: 0.15
Nodes (12): main(), PoetryLoader, 加载本地 JSON 文件                  Args:             local_path: 本地文件路径, 加载诗歌数据                  Args:             dynasty: 朝代筛选（tang, song, song_ci, all, 标准化诗歌数据格式                  Args:             poem: 原始诗歌数据             dynasty: 朝, 按作者搜索                  Args:             author: 作者姓名             poems: 诗歌数据列表，, 按标题搜索                  Args:             title: 诗歌标题             poems: 诗歌数据列表，如, 按关键词搜索                  Args:             keyword: 关键词             poems: 诗歌数据列表 (+4 more)

### Community 12 - "Profile Service"
Cohesion: 0.15
Nodes (3): ProfileService, 从实验与评审历史聚合稳定偏好并回写 preferences.json。, 读取 preferences.json，不存在时返回空结构。

### Community 13 - "Prompt Lab Tests"
Cohesion: 0.16
Nodes (4): PromptLearningPromptLabTest, read_json(), run_cli(), setUpClass()

### Community 14 - "Exam Session Tests"
Cohesion: 0.17
Nodes (5): PromptLearningExamSessionTest, read_json(), run_cli(), run_cli_error(), setUpClass()

### Community 15 - "Learning Center Tests"
Cohesion: 0.16
Nodes (4): PromptLearningLearningCenterTest, read_json(), run_cli(), setUpClass()

### Community 16 - "Platform Smoke Tests"
Cohesion: 0.18
Nodes (5): PromptLearningPlatformSmokeTest, run_cli(), run_cli_error_for(), run_cli_for(), setUpClass()

### Community 17 - "Self-Consistency Prompting"
Cohesion: 0.16
Nodes (16): logic_example(), main(), math_example(), 04 - 自我一致性 (Self-Consistency)  自我一致性通过多次采样和投票提高答案可靠性。 核心思想：多想几遍，少数服从多数。  实现步骤： 1, 自我一致性实现      Args:         question: 问题         n_samples: 采样次数         temperat, self_consistency(), call_anthropic(), call_openai() (+8 more)

### Community 18 - "Home Service & Dashboard"
Cohesion: 0.18
Nodes (4): from_skill_dir(), HomeService, Prompt Learning 首页服务 负责 dashboard、resume 和 recommendation 结构输出。, _read_json()

### Community 19 - "Skills Agent Loop"
Cohesion: 0.15
Nodes (11): agent_loop(), main(), Skills  Two-layer skill injection that avoids bloating the system prompt:      L, Layer 2: full skill body returned in tool_result., Parse YAML frontmatter between --- delimiters., Layer 1: short descriptions for the system prompt., run_edit(), run_read() (+3 more)

### Community 20 - "Chain-of-Thought & ToT"
Cohesion: 0.21
Nodes (15): few_shot_cot(), logical_reasoning(), main(), math_reasoning(), 03 - 思维链提示 (Chain-of-Thought Prompting)  思维链提示引导模型展示推理过程，提高复杂问题的准确性。 核心：在答案前加入"让, zero_shot_cot(), creative_writing_planning(), evaluate_thought() (+7 more)

### Community 21 - "Data Analysis Agent"
Cohesion: 0.17
Nodes (16): calculate_statistics(), create_data_analysis_agent(), create_daytona_backend(), create_local_backend(), create_sample_data(), get_current_time(), main(), LangChain DeepAgent 数据分析 Agent  本项目演示如何使用 LangChain DeepAgent 构建一个智能数据分析 Agent，能 (+8 more)

### Community 22 - "RAG Platform Smoke Tests"
Cohesion: 0.22
Nodes (4): RagLearningPlatformSmokeTest, run_cli(), run_cli_for(), setUpClass()

### Community 23 - "Greeting Module"
Cohesion: 0.12
Nodes (15): casual_greet(), formal_greet(), get_greeting_style_styles(), greet(), late_night_greet(), poetic_greet(), Advanced greeting module with multiple greeting styles., Returns a casual/informal greeting message.      Args:         name: The name to (+7 more)

### Community 24 - "RAG Edge Case Tests"
Cohesion: 0.2
Nodes (4): RagLearningEdgeCaseTest, run_cli(), run_json(), setUpClass()

### Community 25 - "State Flow Tests"
Cohesion: 0.29
Nodes (4): PromptLearningStateFlowTest, read_json(), run_cli(), setUpClass()

### Community 26 - "Graph Prompting"
Cohesion: 0.31
Nodes (5): GraphPrompting, knowledge_graph_example(), main(), 17 - 图提示 (Graph Prompting)  图提示利用图结构数据进行学习和推理。 核心：将图结构信息转换为模型可以理解的提示。  适用场景： - 社, social_network_example()

### Community 28 - "Todo Management Agent"
Cohesion: 0.22
Nodes (8): agent_loop(), main(), TodoWrite  The model tracks its own progress via a TodoManger. A nag reminder fo, run_edit(), run_read(), run_write(), safe_path(), TodoManager

### Community 29 - "Auto-Compact Agent"
Cohesion: 0.24
Nodes (11): agent_loop(), auto_compact(), estimate_tokens(), main(), micro_compact(), Compact  Three-layer compression pipeline so the agent can work forever:      Ev, Rough token count: ~4 chars per token., run_edit() (+3 more)

### Community 30 - "RAG State Flow Tests"
Cohesion: 0.36
Nodes (4): RagLearningStateFlowTest, read_json(), run_cli(), setUpClass()

### Community 31 - "RAG Content Quality Tests"
Cohesion: 0.3
Nodes (3): parse_catalog_course_rows(), RagLearningContentQualityTest, read_text()

### Community 32 - "ART Auto Reasoning & Tools"
Cohesion: 0.27
Nodes (4): ART, main(), 11 - 自动推理和工具使用 (ART)  ART (Automatic Reasoning and Tool-use) 让模型自动选择和使用工具。 核心：从任, Tool

### Community 33 - "ReAct Framework"
Cohesion: 0.24
Nodes (6): ThoughtState, Action, main(), 09 - ReAct 框架 (Reason + Act)  ReAct 结合推理和行动，让模型能够与环境交互。 核心循环：思考 → 行动 → 观察 → 重复, react_loop(), Enum

### Community 34 - "Reflexion Self-Reflection"
Cohesion: 0.33
Nodes (3): main(), 15 - 自我反思 (Reflexion)  自我反思通过语言反馈强化学习，让模型从错误中学习。 核心循环：执行 → 评估 → 反思 → 改进  工作流程： 1, ReflexionAgent

### Community 35 - "Subagent Spawning"
Cohesion: 0.31
Nodes (8): agent_loop(), main(), Subagents  Spawn a child agent with fresh messages=[]. The child works in its ow, run_edit(), run_read(), run_subagent(), run_write(), safe_path()

### Community 36 - "RAG Implementation"
Cohesion: 0.36
Nodes (3): main(), 07 - 检索增强生成 (RAG)  RAG 通过检索外部知识来增强生成质量。 核心组件： 1. 文档分块 (Chunking) 2. 向量化 (Embeddi, SimpleRAG

### Community 37 - "Tool-Using Agent"
Cohesion: 0.33
Nodes (7): agent_loop(), main(), Tools  The agent loop from s01 didn't change. We just added tools to the array a, run_edit(), run_read(), run_write(), safe_path()

### Community 38 - "Multimodal Chain-of-Thought"
Cohesion: 0.39
Nodes (3): main(), MultimodalCoT, 16 - 多模态思维链 (Multimodal Chain-of-Thought)  多模态思维链结合文本和图像进行推理。 核心：利用视觉信息增强文本推理能力。

### Community 39 - "DSP Directional Stimulus"
Cohesion: 0.39
Nodes (3): DirectionalStimulusPrompting, main(), 14 - 方向性刺激提示 (DSP)  DSP (Directional Stimulus Prompting) 使用强化学习优化提示词。 核心：学习什么样的"

### Community 40 - "Prompt Chaining"
Cohesion: 0.39
Nodes (4): document_analysis_example(), main(), PromptChain, 08 - 链式提示 (Prompt Chaining)  链式提示将复杂任务分解为多个简单步骤，顺序执行。 核心：每个步骤的输出作为下一步的输入。  适用场景：

### Community 42 - "APE Automatic Prompt Engineer"
Cohesion: 0.48
Nodes (6): ape_optimize(), calculate_similarity(), evaluate_prompt(), generate_candidate_prompts(), main(), 12 - 自动提示工程师 (APE)  APE (Automatic Prompt Engineer) 自动生成和优化提示词。 核心：通过 LLM 生成多个候选

### Community 43 - "PAL Program-Aided Language"
Cohesion: 0.53
Nodes (5): compare_cot_vs_pal(), execute_python(), main(), pal_solve(), 10 - 程序辅助语言模型 (PAL)  PAL 让 LLM 生成代码来解决问题，而不是进行自然语言推理。 核心：用代码执行替代复杂的数学/逻辑推理。  适用场

### Community 44 - "Few-Shot Prompting"
Cohesion: 0.53
Nodes (5): basic_few_shot(), few_shot_for_format(), few_shot_with_reasoning(), main(), 02 - 少样本提示 (Few-Shot Prompting)  少样本提示通过提供示例来引导模型理解任务。 适用于： - 模型不熟悉的任务格式 - 需要特定输

### Community 45 - "Zero-Shot Prompting"
Cohesion: 0.53
Nodes (5): basic_zero_shot(), main(), 01 - 零样本提示 (Zero-Shot Prompting)  零样本提示是最基础的提示词技术，直接给出任务指令，不提供示例。 这是初学者入门的必修课。, zero_shot_structured_output(), zero_shot_with_constraints()

### Community 46 - "Basic Agent Loop"
Cohesion: 0.47
Nodes (5): agent_loop(), main(), The Agent Loop  The entire secret of an AI coding agent in one pattern:      whi, Main entry point for the s01-loop agent, run_bash()

### Community 47 - "Active Prompt"
Cohesion: 0.6
Nodes (4): active_prompt_select(), calculate_disagreement(), main(), 13 - 主动提示 (Active-Prompt)  主动提示根据问题的不确定性选择最有效的示例。 核心：计算每个问题的推理不确定性，选择最需要示例的问题。

### Community 48 - "Generated Knowledge"
Cohesion: 0.6
Nodes (4): compare_with_baseline(), generated_knowledge_prompt(), main(), 06 - 生成知识提示 (Generated Knowledge Prompting)  生成知识提示让模型先生成相关知识，再基于知识回答问题。 核心：两阶段处

### Community 49 - "Hello Module"
Cohesion: 0.5
Nodes (3): greet(), A simple program that prints a greeting message., Returns a greeting message.      Returns:         A greeting string.

### Community 50 - "Greet Module"
Cohesion: 0.5
Nodes (3): greet(), A simple program that prints a greeting message., Returns a personalized greeting message.      Args:         name: The name to gr

## Knowledge Gaps
- **126 isolated node(s):** `初始化数据加载器                  Args:             cache_dir: 数据缓存目录，默认为 ~/.chinese-poe`, `下载文件到本地                  Args:             url: 远程文件 URL             local_path:`, `从 GitHub 拉取最新数据（自然语言方式）                  Returns:             是否成功拉取`, `加载本地 JSON 文件                  Args:             local_path: 本地文件路径`, `加载诗歌数据                  Args:             dynasty: 朝代筛选（tang, song, song_ci, all` (+121 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.