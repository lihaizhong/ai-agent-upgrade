# Prompt-Learning 基准测试报告

> 生成时间：2026-04-20
> Skill 版本：8.2.0
> Evals 版本：8.1.0

---

## 一、执行摘要

| 指标 | 数值 |
|------|------|
| 总测试数 | 44 |
| 通过数 | 44 (100%) |
| 失败数 | 0 |
| 测试文件数 | 5 |
| 平均执行时间 | ~4.5s |
| 脚本代码总行数 | 4,492 |
| 课程文件数 | 17 |
| 代码示例数 | 19 |
| Evals 评估项 | 10 |

**结论**：测试全部通过，基础功能稳定。但测试覆盖存在结构性缺口，主要集中在学习中心、Prompt Lab 和练习中心的业务逻辑上。

---

## 二、测试结构分析

### 2.1 测试分布

```
test_platform.py          13 tests (29.5%)  ── 平台基础 + Smoke Test
test_exam_session.py      10 tests (22.7%)  ── 考试会话生命周期
test_state_flow.py         9 tests (20.5%)  ── 状态流转与推荐
test_workspace_fallback.py 7 tests (15.9%)  ── Workspace 隔离与回退
test_content_quality.py    5 tests (11.4%)  ── 内容契约与架构对齐
```

### 2.2 各模块覆盖详情

#### ✅ 已充分覆盖

| 模块 | 覆盖测试 | 关键场景 |
|------|---------|---------|
| Workspace 管理 | 20+ tests | Bootstrap、用户隔离、元数据冲突检测、fallback、路径安全 |
| 考试中心 | 10 tests | 会话创建/恢复/放弃、题目提交、答案提交、评分、报告生成、弱点分析 |
| 状态流 | 9 tests | 学习进度、练习记录、错题闭环、掌握度计算、推荐逻辑 |
| 平台首页 | 4 tests | Dashboard、课程目录、推荐逻辑 |

#### ⚠️ 部分覆盖

| 模块 | 覆盖测试 | 缺口 |
|------|---------|------|
| 学习中心 | 2 tests | 课程类别过滤、学习面板详情、课程搜索、课程完成后的 next course 推荐 |
| 练习中心 | 2 tests | Blueprint 按 mode 生成差异、专项练习 vs 当前课程练习、错题回练流程 |
| Prompt Lab | 4 tests | 审查清单生成、面试蓝图、模板列表/加载/删除、槽位追问流程 |
| 学习档案 | 1 test | 档案摘要详细字段、考试历史查询、模板索引查询 |

#### ❌ 未覆盖

| 模块 | 未覆盖场景 |
|------|-----------|
| 内容生成 | LLM 动态题目质量、课程讲解质量（需人工/LLM-as-judge 评估） |
| 选择器协议 | `interaction.mode` 各分支的完整输出格式验证 |
| 边界异常 | 大量参数校验、文件权限、并发访问、损坏数据恢复 |
| 性能 | 大数据量下的历史文件读写性能 |

---

## 三、修复记录

### 本次评估修复：1 项

**问题**：`test_workspace_root_resolves_from_skill_symlink_paths` 失败

- **根因**：`get_repo_root()` 对 `.codex/skills/prompt-learning` 这类不存在的 symlink 路径，`Path.resolve()` 不会向上追溯到 repo root
- **修复**：在 `get_repo_root()` 中增加对 `.opencode/skills/` 和 `.codex/skills/` 路径模式的显式处理
- **文件**：`agent-skills/prompt-learning/scripts/workspace.py`
- **验证**：修复后 44/44 测试全部通过

---

## 四、Evals 评估集分析

`evals/evals.json` 定义了 10 项 AI 行为层面的评估：

| # | 名称 | 类型 | 脚本支撑度 |
|---|------|------|-----------|
| 1 | 平台首页-统一入口 | 行为 | ✅ `home --dashboard` |
| 2 | 学习中心-课程目录 | 行为 | ✅ `learning --catalog` |
| 3 | 学习中心-指定课程直达 | 行为 | ⚠️ 依赖 LLM 路由 |
| 4 | 练习中心-统一入口 | 行为 | ✅ `practice --blueprint` |
| 5 | 练习中心-默认动态出题 | 行为 | ❌ LLM 生成，无脚本约束 |
| 6 | 考试中心-诊断与综合入口 | 行为 | ✅ `exam --structure` |
| 7 | Prompt Lab-实战入口 | 行为 | ✅ `lab --review-checklist` |
| 8 | 学习档案-进度与错题 | 行为 | ✅ `profile --summary` |
| 9 | 平台心智-不再暴露旧模式 | 行为 | ⚠️ 依赖 LLM 遵循 SKILL.md |
| 10 | 技能边界-不原样贴课文 | 行为 | ❌ LLM 生成，无脚本约束 |

**关键发现**：
- 脚本层能支撑 6/10 项评估的底层数据
- 4 项完全依赖 LLM 遵循 SKILL.md 的行为规范，缺乏自动化验证手段
- 建议补充 **LLM-as-judge** 或 **输出断言** 的自动化评估 pipeline

---

## 五、覆盖率评估（基于测试代码分析）

### 5.1 脚本函数覆盖

```
workspace.py    ████████████████████  90%+  (全部核心函数均有测试)
exam.py         ████████████████░░░░  75%   (评分引擎覆盖充分，Service 层部分未测)
state.py        ████████████████░░░░  75%   (核心状态操作覆盖，边缘分支未测)
home.py         ████████░░░░░░░░░░░░  35%   (仅 dashboard 和 recommend 被测)
learning.py     ██████░░░░░░░░░░░░░░  25%   (仅 catalog 和 lesson-meta 被测)
practice.py     ██████░░░░░░░░░░░░░░  25%   (仅 blueprint 和 record-result 被测)
prompt_lab.py   ████████░░░░░░░░░░░░  35%   (save-template 和 validate-slots 被测)
profile.py      ████░░░░░░░░░░░░░░░░  20%   (仅 summary 被测)
__main__.py     ██████████░░░░░░░░░░  45%   (CLI 参数组合未充分覆盖)
```

### 5.2 代码行数 vs 测试行数

| 文件 | 代码行数 | 测试行数 | 测试/代码比 |
|------|---------|---------|------------|
| workspace.py | 332 | ~180 | 0.54 |
| exam.py | 1,166 | ~280 | 0.24 |
| state.py | 508 | ~120 | 0.24 |
| home.py | 257 | ~40 | 0.16 |
| learning.py | 398 | ~20 | 0.05 |
| practice.py | 414 | ~20 | 0.05 |
| prompt_lab.py | 344 | ~60 | 0.17 |
| profile.py | 127 | ~10 | 0.08 |
| __main__.py | 759 | ~50 | 0.07 |
| **总计** | **4,492** | **~780** | **0.17** |

行业参考：健康的测试/代码比通常在 0.3-0.8 之间。当前 0.17 偏低，主要因为学习中心和练习中心缺乏测试。

---

## 六、风险评估

### 6.1 高风险缺口

| 风险 | 说明 | 建议 |
|------|------|------|
| 学习中心无专项测试 | 课程讲解、学习路径推荐等核心业务无自动化保障 | 补充 `test_learning_center.py` |
| Prompt Lab 功能覆盖不全 | 模板生命周期管理（列表/加载/删除/更新）未测试 | 补充模板 CRUD 测试 |
| 练习中心模式差异 | `current` / `targeted` / `mistake` 三种模式的 blueprint 差异未验证 | 补充多模式 blueprint 测试 |
| 评分边界 | 填空题评分、大题 rubric 评分仅覆盖基础场景 | 补充边界评分测试 |

### 6.2 中风险缺口

| 风险 | 说明 | 建议 |
|------|------|------|
| 选择器协议输出格式 | `interaction.mode` 各分支的 JSON schema 未校验 | 增加 schema 校验测试 |
| 损坏数据恢复 | 损坏的 JSON 文件、缺失的字段未测试 | 增加容错测试 |
| 并发安全 | 同一用户多会话操作未测试 | 增加并发/竞态测试 |
| 大文件性能 | 历史记录累积后的读写性能未测试 | 增加性能基准 |

---

## 七、建议行动

### 短期（1-2 周）

1. **补充学习中心测试** (`test_learning_center.py`)
   - 课程类别过滤 (`--category`)
   - 课程完成后的 next course 推荐
   - 学习面板状态恢复 (`--resume`)

2. **补充 Prompt Lab 测试** (`test_prompt_lab.py`)
   - 审查清单生成 (`--review-checklist`)
   - 面试蓝图生成 (`--interview-blueprint`)
   - 模板列表/加载/删除

3. **补充练习中心测试** (`test_practice_center.py`)
   - 三种模式 blueprint 差异验证
   - 错题回练流程

### 中期（1 个月）

4. **增加 Evals 自动化评估**
   - 对 10 项 eval 建立自动化评分 pipeline
   - 使用 LLM-as-judge 或输出断言验证 LLM 行为合规性

5. **增加错误处理测试**
   - 损坏数据恢复
   - 非法参数处理
   - 文件权限异常

### 长期（持续）

6. **建立性能基准**
   - 考试会话完整流程耗时
   - 大历史文件读写性能
   - Workspace bootstrap 耗时

7. **引入覆盖率工具**
   - 安装 `pytest-cov`
   - 设定覆盖率门槛（建议 70%+）
   - CI 中强制执行

---

## 八、附录

### 8.1 测试运行命令

```bash
# 运行全部测试
.venv/bin/python -m pytest tests/prompt_learning/ -v

# 运行单文件
.venv/bin/python -m pytest tests/prompt_learning/test_exam_session.py -v

# 运行带覆盖率（需安装 pytest-cov）
uv add --dev pytest-cov
.venv/bin/python -m pytest tests/prompt_learning/ --cov=agent-skills/prompt-learning/scripts
```

### 8.2 版本演进关键节点

| 版本 | 日期 | 核心变更 |
|------|------|---------|
| v8.2.0 | 2026-04-09 | 考试题目存储与提交流程优化 |
| v8.1.0 | 2026-04-08 | Selector-first contract 确立 |
| v8.0.0 | 2026-04-08 | 移除 Legacy 兼容层，收敛为平台模块 |
| v7.0.11 | 2026-04-08 | 执行路径、生成流程与推荐语义修正 |

### 8.3 关键脚本接口速查

```
workspace  --bootstrap | --resolve-user | --username
home       --dashboard | --recommend | --resume
learning   --catalog | --category | --lesson-meta | --complete
practice   --blueprint | --record-result
exam       --start | --submit-question | --submit-answer | --finish
lab        --review-checklist | --validate-slots | --save-template
profile    --summary
```
