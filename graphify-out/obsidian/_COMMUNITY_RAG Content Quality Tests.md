---
type: community
members: 12
---

# RAG Content Quality Tests

**Members:** 12 nodes

## Members
- [[.test_catalog_declares_learning_center_mainline_and_handoffs()]] - code - tests/rag_learning/test_content_quality.py
- [[.test_catalog_matches_course_files()]] - code - tests/rag_learning/test_content_quality.py
- [[.test_courses_readme_declares_platform_mainline()]] - code - tests/rag_learning/test_content_quality.py
- [[.test_evals_reflect_platform_mental_model()]] - code - tests/rag_learning/test_content_quality.py
- [[.test_key_courses_include_platform_positioning()]] - code - tests/rag_learning/test_content_quality.py
- [[.test_no_unassigned_track_left_in_catalog_mainline_logic()]] - code - tests/rag_learning/test_content_quality.py
- [[.test_platform_config_has_lab_and_review_definitions()]] - code - tests/rag_learning/test_content_quality.py
- [[.test_skill_contract_uses_platform_modules()]] - code - tests/rag_learning/test_content_quality.py
- [[RagLearningContentQualityTest]] - code - tests/rag_learning/test_content_quality.py
- [[parse_catalog_course_rows()]] - code - tests/rag_learning/test_content_quality.py
- [[read_text()]] - code - tests/rag_learning/test_content_quality.py
- [[test_content_quality.py]] - code - tests/rag_learning/test_content_quality.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/RAG_Content_Quality_Tests
SORT file.name ASC
```
