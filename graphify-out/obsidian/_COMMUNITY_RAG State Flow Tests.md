---
type: community
members: 12
---

# RAG State Flow Tests

**Members:** 12 nodes

## Members
- [[.test_build_flow_updates_project_and_competency_state()]] - code - tests/rag_learning/test_state_flow.py
- [[.test_home_recommendation_consumes_neutral_state_as_fallback()]] - code - tests/rag_learning/test_state_flow.py
- [[.test_lab_flow_updates_state_and_history()]] - code - tests/rag_learning/test_state_flow.py
- [[.test_learning_start_updates_current_state_and_course_progress()]] - code - tests/rag_learning/test_state_flow.py
- [[.test_preference_rollup_after_lab_and_review()]] - code - tests/rag_learning/test_state_flow.py
- [[.test_review_flow_updates_state_and_competency()]] - code - tests/rag_learning/test_state_flow.py
- [[RagLearningStateFlowTest]] - code - tests/rag_learning/test_state_flow.py
- [[read_json()]] - code - tests/rag_learning/test_state_flow.py
- [[run_cli()]] - code - tests/rag_learning/test_state_flow.py
- [[setUpClass()]] - code - tests/rag_learning/test_state_flow.py
- [[tearDownClass()]] - code - tests/rag_learning/test_state_flow.py
- [[test_state_flow.py]] - code - tests/rag_learning/test_state_flow.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/RAG_State_Flow_Tests
SORT file.name ASC
```
