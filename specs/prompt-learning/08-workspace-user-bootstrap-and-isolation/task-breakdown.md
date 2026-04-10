# Tasks: Workspace 用户解析与首次创建隔离

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/08-workspace-user-bootstrap-and-isolation/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/08-workspace-user-bootstrap-and-isolation/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: Workspace Contract

- [x] Task: 明确并实现唯一的 `workspace_user` 解析规则
  - Acceptance: `workspace.py` 中只有一套 workspace 解析入口，不会扫描现有目录做候选选择
  - Verify: 审查 `workspace.py`
  - Files: `agent-skills/prompt-learning/scripts/workspace.py`

- [x] Task: 为 workspace 解析增加 fail-fast 校验
  - Acceptance: 解析结果与目标目录不一致时，脚本显式报错
  - Verify: 新增测试覆盖错误目录命中场景
  - Files: `agent-skills/prompt-learning/scripts/workspace.py`, `tests/prompt_learning/`

## Phase 2: Bootstrap Flow

- [x] Task: 修正新用户首次进入的 bootstrap 流程
  - Acceptance: 新用户首次进入时创建 `prompt-learning-workspace/<username>/`
  - Verify: 新增测试覆盖不存在目录时的首次进入
  - Files: `agent-skills/prompt-learning/scripts/workspace.py`, `agent-skills/prompt-learning/scripts/__main__.py`, `tests/prompt_learning/`

- [x] Task: 禁止回退到已有唯一 workspace
  - Acceptance: 当仓库中仅存在 `lihzsky/` 等旧目录时，新用户 `baitanggao` 不会落入该目录
  - Verify: 构造“仓库内已有其他用户 workspace”的场景并运行 CLI 测试
  - Files: `agent-skills/prompt-learning/scripts/workspace.py`, `tests/prompt_learning/`

## Phase 3: Module Alignment

- [x] Task: 对齐 `home / learning / practice / exam / profile / lab` 的 workspace 读取入口
  - Acceptance: 所有模块只通过统一 workspace 路径读写，不存在旁路逻辑
  - Verify: 搜索调用链并做最小集成测试
  - Files: `agent-skills/prompt-learning/scripts/home.py`, `agent-skills/prompt-learning/scripts/learning.py`, `agent-skills/prompt-learning/scripts/practice.py`, `agent-skills/prompt-learning/scripts/exam.py`, `agent-skills/prompt-learning/scripts/profile.py`, `agent-skills/prompt-learning/scripts/prompt_lab.py`

## Phase 4: Testing

- [x] Task: 增加 workspace 首次创建测试
  - Acceptance: 新用户首次进入后，目标 workspace 目录与默认文件集被创建
  - Verify: `python -m unittest ...`
  - Files: `tests/prompt_learning/test_platform.py`, `tests/prompt_learning/test_state_flow.py`

- [x] Task: 增加禁止误入他人 workspace 的测试
  - Acceptance: 当已有 `lihzsky/` 目录时，`baitanggao` 仍创建并使用自己的 workspace，或在配置错误时显式失败
  - Verify: `python -m unittest ...`
  - Files: `tests/prompt_learning/test_platform.py`, `tests/prompt_learning/test_exam_session.py`, `tests/prompt_learning/test_state_flow.py`

- [x] Task: 增加显式 username 不匹配报错测试
  - Acceptance: 调用链试图命中非当前用户目录时返回清晰错误
  - Verify: `python -m unittest ...`
  - Files: `tests/prompt_learning/`

## Phase 5: Docs

- [x] Task: 更新 workspace 架构文档
  - Acceptance: 文档明确“新用户首次创建”和“禁止回退到已有 workspace”
  - Verify: 审查文档措辞
  - Files: `docs/prompt-learning-architecture/workspace-and-persistence.md`

- [x] Task: 更新 skill contract 中的持久化边界说明
  - Acceptance: `SKILL.md` 不再允许模糊命中已有 workspace
  - Verify: 文档审查
  - Files: `agent-skills/prompt-learning/SKILL.md`

## Global Gates

- [x] Gate: workspace 仍然保持单层用户语义
  - Acceptance: 不新增 `actor`、`worker` 等第二层隔离目录
  - Verify: 审查路径实现

- [x] Gate: 错误通过显式检查暴露，而不是通过回退逻辑掩盖
  - Acceptance: 找不到当前用户 workspace 时只允许创建或报错，不允许复用已有目录
  - Verify: 代码审查 + 测试
