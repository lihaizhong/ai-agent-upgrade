# Spec Change: Workspace 用户解析与首次创建隔离

## 根因

当前 `prompt-learning` 的用户隔离语义不够严谨。

按设计，`prompt-learning-workspace/<username>/` 应代表一个用户的长期 workspace；但实际问题表明：

1. 新用户首次进入时，没有稳定地创建自己的 workspace
2. 某些入口或运行流程在未命中当前用户 workspace 时，可能落入已有 workspace
3. 这种回退会让“workspace 隔离”失效，并让后续考试、学习进度、练习记录都读到别人的状态

这不是考试会话层的问题，而是 workspace 解析和首次 bootstrap 流程的问题。

## 目标

1. 明确 `prompt-learning-workspace/<username>/` 的唯一语义：它就是该用户的 workspace
2. 新用户首次进入时，若对应 workspace 不存在，系统必须创建该用户自己的 workspace
3. 禁止任何“找不到当前用户时回退到已有唯一 workspace”的行为
4. 所有模块都必须基于同一套 workspace 解析结果读写状态
5. 当身份解析异常或目标 workspace 与当前用户不一致时，脚本必须显式报错，而不是静默容错

## 非目标

1. 不引入第二层 `actor` 子目录来兜底隔离
2. 不修改练习、考试、Prompt Lab 的产品行为
3. 不把 workspace 持久化迁移到数据库或外部服务
4. 不改变现有长期状态 schema，只修正 workspace 归属和创建流程

## 设计

### 1. 用户解析结果必须是单值，不允许模糊匹配

脚本层只允许得到一个明确的 `workspace_user`：

- 显式 `--username`
- 或当前运行环境约定的默认用户来源

一旦解析完成，后续所有模块都必须使用这个结果。

禁止：

- 枚举 `prompt-learning-workspace/` 下现有目录并“猜”一个可用目录
- 因为仓库里只有一个 workspace 就默认使用它
- 将历史测试目录、样例目录或别人的真实目录当作当前用户目录

### 2. 新用户首次进入必须 bootstrap 自己的 workspace

若解析出的 `workspace_user` 目录不存在：

- `workspace --bootstrap` 必须创建 `prompt-learning-workspace/<workspace_user>/`
- 各产品入口在首次进入时也必须先确保 bootstrap 完成

这一步应是“为当前用户创建目录”，而不是“挑一个已有目录复用”。

### 3. workspace 校验必须 fail-fast

当出现以下情况时，脚本必须报错：

- 当前用户解析失败且没有明确回退规则
- 解析得到的 `workspace_user` 与命中的实际目录不一致
- 调用方显式传入 `--username new-user`，却试图访问 `prompt-learning-workspace/existing-user/`

脚本输出应清楚说明：

- 当前解析到的用户是谁
- 期望访问哪个 workspace
- 为什么拒绝继续

### 4. 所有状态读写统一依赖 workspace 解析层

以下模块都必须只通过统一的 workspace 解析函数获取路径：

- `home`
- `learning`
- `practice`
- `exam`
- `profile`
- `lab`

任何模块都不能自行扫描现有 workspace 或直接拼接“看起来像用户目录”的路径。

### 5. 文档要明确“首次进入”和“禁止回退”

需要把以下规则写进 spec 和架构文档：

- 新用户首次进入会创建自己的 workspace
- workspace 不存在时只能创建当前用户目录，不能复用已有目录
- workspace 是用户隔离边界，不允许额外定义第二层身份兜底

## 验收标准

- [ ] 新用户 `new-user` 首次进入时，会创建 `prompt-learning-workspace/new-user/`
- [ ] 不存在任何“唯一已有 workspace 自动回退”的逻辑
- [ ] 传入 `--username new-user` 时，所有模块都只会访问 `prompt-learning-workspace/new-user/`
- [ ] 若调用链试图访问其他用户目录，脚本会显式报错
- [ ] `home / learning / practice / exam / profile / lab` 共用同一套 workspace 解析规则
- [ ] 文档明确说明 workspace 是用户级隔离边界，首次进入必须创建当前用户目录

## 影响范围

主要影响文件：

- `agent-skills/prompt-learning/scripts/workspace.py`
- `agent-skills/prompt-learning/scripts/__main__.py`
- `agent-skills/prompt-learning/scripts/home.py`
- `agent-skills/prompt-learning/scripts/learning.py`
- `agent-skills/prompt-learning/scripts/practice.py`
- `agent-skills/prompt-learning/scripts/exam.py`
- `agent-skills/prompt-learning/scripts/profile.py`
- `agent-skills/prompt-learning/scripts/prompt_lab.py`
- `docs/prompt-learning-architecture/workspace-and-persistence.md`
- `agent-skills/prompt-learning/SKILL.md`
- `tests/prompt_learning/`

## 风险

1. 现有测试或样例数据依赖固定 workspace 目录
2. 某些 CLI 路径可能隐式依赖“目录已存在”
3. 如果调用方一直传固定 `--username`，修复后会暴露出上游调用问题

这些风险应通过测试补齐和显式报错来处理，而不是继续使用回退逻辑。
