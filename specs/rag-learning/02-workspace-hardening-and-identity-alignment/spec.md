# Spec Change: Workspace Hardening And Identity Alignment

## Objective

在不改变 `rag-learning` 平台模块划分的前提下，收敛 workspace 身份解析、目录安全和用户隔离语义，使 `rag-learning-workspace/<username>/` 成为单一真相。

本次 change 主要解决以下问题：

1. 当前用户名规范化只做空格替换，缺少路径安全约束
2. workspace 解析没有 ownership 校验，后续容易误读或误写其他用户目录
3. 各模块虽然共用 `get_workspace_paths()`，但还没有明确的 identity contract 和 fail-fast 规则
4. spec / code / tests 对“身份解析失败时如何处理”尚未形成单一真相

## Assumptions

以下假设用于本次变更；如果不成立，应先修订本 spec：

1. `rag-learning` 当前使用单层用户 workspace 结构：`rag-learning-workspace/<username>/`
2. 本次 change 不引入数据库，也不增加 `actor/tenant` 等第二层目录
3. 显式 `--username` 仍然允许存在，但必须与身份解析规则保持一致
4. 所有模块都应只通过统一 workspace 解析函数获取读写路径
5. 本次 change 只修正 identity、ownership 和路径安全，不扩展产品功能

## Background

`rag-learning` 第一轮平台化重构已经建立了 workspace 骨架，但当前实现仍比较宽松：

- `normalize_workspace_username()` 仅做空格替换
- `get_user_workspace()` 直接拼接路径
- `ensure_workspace()` 默认创建目录，但不校验已有 workspace 的归属
- 缺少对 identity mismatch、路径逃逸和 metadata 缺失的 fail-fast 检查

这类问题在 `prompt-learning` 中已经演变成后续多个补丁规格，因此应在 `rag-learning` 第二轮重构前先收紧。

## Scope

### 1. 收敛 identity 解析入口

新增或明确一个统一的 workspace identity 解析函数，负责产出：

- `explicit_username`
- `source_git_username`
- `workspace_user`
- `using_fallback`

所有模块只允许消费这一解析结果，不允许自行扫描现有目录或拼接猜测路径。

### 2. 强化用户名净化和路径安全

用户名规范化必须满足：

- 空白输入返回单一默认值
- 只保留稳定、可预期的安全字符
- 禁止 `.`、`..`、路径分隔符和其他可能导致逃逸的输入
- 最终解析路径必须显式校验位于 `rag-learning-workspace/` 根目录下

### 3. 增加 ownership 与 metadata 校验

若目标 workspace 已存在，脚本必须校验：

- `learner.json` 存在
- `learner.json.workspace_user` 与当前解析结果一致
- 已有状态文件不能在缺少 metadata 的情况下被静默复用

发现不一致时，必须显式报错，而不是继续写入。

### 4. 明确首次进入与 fallback 语义

当解析出的 `workspace_user` 目录不存在时：

- `workspace --bootstrap` 必须创建当前用户目录
- 其他产品入口也必须先确保 bootstrap 完成

如果 `git config user.name` 无法解析，本次 change 必须明确唯一产品行为：

- 要么统一 fallback 到单一默认目录
- 要么统一 fail-fast

无论选择哪一种，都必须让 code / spec / docs / tests 只表达这一种行为。

### 5. 文档与 contract 对齐

需要更新：

- `agent-skills/rag-learning/SKILL.md`
- `docs/rag-learning-architecture/workspace-and-persistence.md`
- 对应测试

使其清楚表达：

- workspace 是用户级隔离边界
- 首次进入如何创建目录
- 不允许模糊命中已有 workspace

## Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_platform
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_state_flow
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_config_units
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/rag-learning/scripts tests/rag_learning
```

## Project Structure

- `agent-skills/rag-learning/scripts/workspace.py`
  - workspace identity 解析、目录安全、最小文件初始化
- `agent-skills/rag-learning/scripts/__main__.py`
  - bootstrap 与入口统一行为
- `agent-skills/rag-learning/scripts/home.py`
- `agent-skills/rag-learning/scripts/learning.py`
- `agent-skills/rag-learning/scripts/build.py`
- `agent-skills/rag-learning/scripts/lab.py`
- `agent-skills/rag-learning/scripts/review.py`
- `agent-skills/rag-learning/scripts/profile.py`
  - 全部只通过统一 workspace 入口读写
- `docs/rag-learning-architecture/workspace-and-persistence.md`
- `agent-skills/rag-learning/SKILL.md`
- `tests/rag_learning/`

## Code Style

保持现有 Python 风格，优先直接、可解释的实现，不引入新的依赖层。

```python
def normalize_workspace_username(raw_name: str | None) -> str:
    if not raw_name or not raw_name.strip():
        return DEFAULT_WORKSPACE_USERNAME

    candidate = raw_name.strip().replace(" ", "-")
    safe = re.sub(r"[^A-Za-z0-9._-]", "-", candidate)
    safe = safe.strip("._-")
    return safe or DEFAULT_WORKSPACE_USERNAME
```

约束：

- 所有路径安全判断都在 workspace 层完成
- 不允许各模块重复实现自己的 identity 逻辑
- 错误必须暴露，而不是通过静默回退掩盖

## Testing Strategy

- 采用 bug-first 回归策略，优先补表达缺陷的测试
- 至少覆盖以下场景：
  - 新用户首次进入自动创建自己的 workspace
  - 恶意用户名不能逃逸 `rag-learning-workspace/`
  - 已有其他用户目录时，不会误命中现有 workspace
  - `learner.json` 缺失或 ownership 不一致时显式报错
  - 所有主要模块共用同一套 workspace 解析规则

## Boundaries

- Always:
  - 让 workspace identity 成为单一真相
  - 通过自动化测试覆盖路径安全和 ownership 校验
  - 对齐 spec、实现、测试和文档中的 fallback 语义
- Ask first:
  - 改变 workspace 目录层级
  - 引入数据库或外部身份系统
  - 扩展为多租户语义
- Never:
  - 允许未经净化的用户名直接参与路径拼接
  - 在 identity 不一致时继续读写已有 workspace
  - 通过扫描现有目录“猜一个可用 workspace”

## Success Criteria

- [x] workspace identity 解析有唯一入口
- [x] 任意用户名输入都不能写出 `rag-learning-workspace/` 根目录之外
- [x] 新用户首次进入时创建自己的 workspace，而不是复用已有目录
- [x] `learner.json` ownership mismatch 会显式报错
- [x] 各模块只通过统一 workspace 解析层获取路径
- [x] 文档和 `SKILL.md` 明确 workspace 隔离边界与 fallback 语义
- [x] `tests.rag_learning` 对应回归通过

## Non-Goals

- 不重构状态模型
- 不新增平台模块
- 不修改课程、实验或评审内容
- 不把 workspace 迁移到数据库

## Open Questions

1. `rag-learning` 应沿用 `default-zoom` fallback，还是切换到更明确的默认目录名？
2. 显式 `--username` 与当前 `git user.name` 不一致时，默认直接拒绝，还是保留可控 override？
