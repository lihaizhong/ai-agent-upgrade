# RAG Learning 测试与验证

## 目标

为 `rag-learning` 提供可重复执行的最小验证入口，确保平台脚本、配置源、内容资产和状态流转不会在后续迭代中静默回退。

## 当前测试层次

### 1. 平台 Smoke Tests

文件：

- `tests/rag_learning/test_platform.py`

覆盖：

- workspace 初始化
- 首页 dashboard
- 学习中心目录
- 实战中心入口与步骤记录
- RAG Lab 结果记录
- 架构评审结果记录
- 学习档案聚合

运行：

```bash
./.venv/bin/python -m unittest tests.rag_learning.test_platform
```

### 2. 内容质量测试

文件：

- `tests/rag_learning/test_content_quality.py`

覆盖：

- `SKILL.md` 是否仍然是平台 contract
- `catalog.md` 是否与课程资产一致
- `courses/README.md` 是否保留平台主线
- 关键课程是否包含平台定位与使用提醒
- `platform-config.json` 结构是否完整
- `evals/evals.json` 是否反映平台心智

运行：

```bash
./.venv/bin/python -m unittest tests.rag_learning.test_content_quality
```

### 3. 配置解析单元测试

文件：

- `tests/rag_learning/test_config_units.py`

覆盖：

- `catalog.py` 的课程目录解析
- 推荐学习路径解析
- 场景到 project id 的映射
- `config.py` 的实验与评审配置加载

运行：

```bash
./.venv/bin/python -m unittest tests.rag_learning.test_config_units
```

### 4. 状态流转测试

文件：

- `tests/rag_learning/test_state_flow.py`

覆盖：

- 课程启动后的状态更新
- 项目启动与步骤记录后的状态更新
- 实验完成后的状态与历史更新
- 评审完成后的状态与能力摘要更新

运行：

```bash
./.venv/bin/python -m unittest tests.rag_learning.test_state_flow
```

## 统一运行命令

Lint：

```bash
./.venv/bin/ruff check agent-skills/rag-learning/scripts tests/rag_learning
```

全部测试：

```bash
./.venv/bin/python -m unittest \
  tests.rag_learning.test_platform \
  tests.rag_learning.test_content_quality \
  tests.rag_learning.test_config_units \
  tests.rag_learning.test_state_flow
```

## 验证策略

### 优先验证什么

每次修改以下内容后，应至少运行对应测试：

- 改脚本入口或 CLI：`test_rag_learning_platform`
- 改 `catalog.md`、课程说明或 `SKILL.md`：`test_rag_learning_content_quality`
- 改 `catalog.py`、`config.py` 或 `platform-config.json`：`test_rag_learning_config_units`
- 改 `state.py`、workspace 写盘或状态推荐：`test_rag_learning_state_flow`

### 当前边界

当前测试仍主要是：

- 结构正确性
- 配置正确性
- 状态流转正确性

尚未覆盖：

- LLM 讲解质量
- 课程正文是否过时
- 更复杂的多轮真实交互评测

这些应作为后续增强，而不是先把现有稳定性验证推迟。
