# Tasks: Prompt Learning Selector-First Interaction

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/03-selector-first-interaction/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/03-selector-first-interaction/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: Interaction Contract Definition

- [x] Task: Define selector-first behavior in the prompt-learning spec
  - Acceptance: `spec.md` clearly states that structured-choice flows must prefer the current AI executor's native selector UI and may use plain-text numbered menus only as fallback.
  - Verify: Inspect `spec.md` and confirm selector-first and fallback conditions are both explicit.
  - Files: `specs/prompt-learning/03-selector-first-interaction/spec.md`

- [x] Task: Enumerate the interaction surfaces covered by the selector-first contract
  - Acceptance: `spec.md` explicitly lists the key surfaces that must follow selector-first behavior.
  - Verify: Inspect the `Key Interaction Surfaces` section in `spec.md`.
  - Files: `specs/prompt-learning/03-selector-first-interaction/spec.md`

## Phase 2: Skill and Reference Alignment

- [x] Task: Update `SKILL.md` to require selector-first interaction for structured-choice flows
  - Acceptance: `SKILL.md` explicitly instructs the agent to use the current executor's native selector UI whenever structured choices already exist.
  - Verify: Search `SKILL.md` for selector-first and fallback guidance.
  - Files: `.opencode/skills/prompt-learning/SKILL.md`

- [x] Task: Align learning and exam reference docs with selector-first behavior
  - Acceptance: `reference/learning-mode.md` and `reference/exam-mode.md` reinforce selector-first interaction and no longer leave room for plain-text menus as the default.
  - Verify: Inspect both reference files and confirm selector-first guidance is explicit.
  - Files: `.opencode/skills/prompt-learning/reference/learning-mode.md`, `.opencode/skills/prompt-learning/reference/exam-mode.md`

- [x] Task: Review Prompt Lab reference for selector-first applicability or exemption
  - Acceptance: `reference/prompt-generation-mode.md` either documents limited selector-first usage where appropriate or explicitly states why open-ended slot clarification is not covered.
  - Verify: Inspect the Prompt Lab reference and confirm the boundary is documented.
  - Files: `.opencode/skills/prompt-learning/reference/prompt-generation-mode.md`

## Phase 3: Agent Prompt and Eval Alignment

- [x] Task: Align `agents/openai.yaml` with selector-first execution guidance
  - Acceptance: The agent-facing prompt or metadata reinforces selector-first behavior for structured-choice flows.
  - Verify: Inspect `agents/openai.yaml` and confirm the interaction guidance is consistent with the spec.
  - Files: `.opencode/skills/prompt-learning/agents/openai.yaml`

- [x] Task: Add selector-first regression expectations to `evals/evals.json`
  - Acceptance: Critical entry flows include assertions that reduce regression to plain-text numbered menus when structured-choice behavior is expected.
  - Verify: Inspect relevant eval cases and confirm selector-first expectations are represented.
  - Files: `.opencode/skills/prompt-learning/evals/evals.json`

## Phase 4: Script Contract Review and Optional Tightening

- [x] Task: Audit the structured-choice payloads emitted by key prompt-learning scripts
  - Acceptance: The current `question` payloads for home, learning, practice, and exam are reviewed for selector compatibility.
  - Verify: Inspect `home.py`, `learning.py`, `practice.py`, and `exam.py` and record whether the payload contract is sufficient.
  - Files: `.opencode/skills/prompt-learning/scripts/home.py`, `.opencode/skills/prompt-learning/scripts/learning.py`, `.opencode/skills/prompt-learning/scripts/practice.py`, `.opencode/skills/prompt-learning/scripts/exam.py`

- [x] Task: Decide whether payload contract tightening is required
  - Acceptance: The implementation notes or follow-up decision clearly state either that the current payload is sufficient or that minimal additional metadata is required.
  - Verify: Inspect the final aligned spec, plan, tasks, and implementation notes for an explicit decision.
  - Files: `specs/prompt-learning/03-selector-first-interaction/spec.md`, `specs/prompt-learning/03-selector-first-interaction/implementation-plan.md`

- [x] Task: If required, scope minimal payload changes without expanding product behavior
  - Acceptance: Any payload refinement is limited to contract clarity and does not introduce unrelated UX or feature changes.
  - Verify: Review the scoped files and confirm only selector contract fields are affected.
  - Files: `.opencode/skills/prompt-learning/scripts/home.py`, `.opencode/skills/prompt-learning/scripts/learning.py`, `.opencode/skills/prompt-learning/scripts/practice.py`, `.opencode/skills/prompt-learning/scripts/exam.py`

## Phase 5: Verification and Spec Sync

- [x] Task: Verify selector-first coverage across key interaction surfaces
  - Acceptance: home, learning selection, post-lesson panel, practice entry, and exam entry are all covered by aligned selector-first guidance.
  - Verify: Inspect docs, prompts, evals, and script payloads together.
  - Files: `.opencode/skills/prompt-learning/SKILL.md`, `.opencode/skills/prompt-learning/reference/`, `.opencode/skills/prompt-learning/evals/evals.json`, `.opencode/skills/prompt-learning/scripts/`

- [x] Task: Verify fallback behavior is explicit and narrow
  - Acceptance: plain-text numbered menus are documented only as fallback behavior for executors that do not support structured selection.
  - Verify: Search the prompt-learning skill directory for menu guidance and inspect remaining fallback language.
  - Files: `.opencode/skills/prompt-learning/`

- [x] Task: Sync spec artifacts after the work lands
  - Acceptance: `spec.md`, `implementation-plan.md`, and `task-breakdown.md` reflect the same selector-first contract and status.
  - Verify: Inspect all three files for alignment.
  - Files: `specs/prompt-learning/03-selector-first-interaction/spec.md`, `specs/prompt-learning/03-selector-first-interaction/implementation-plan.md`, `specs/prompt-learning/03-selector-first-interaction/task-breakdown.md`

## Global Verification Gates

- [x] Gate: Selector-first contract is defined before script payload changes are considered
  - Acceptance: The product rule is written and agreed before any payload tightening work begins.
  - Verify: `spec.md` and `implementation-plan.md` are complete before script contract edits are made.
  - Files: `specs/prompt-learning/03-selector-first-interaction/spec.md`, `specs/prompt-learning/03-selector-first-interaction/implementation-plan.md`

- [x] Gate: Docs and evals are aligned before the work is considered complete
  - Acceptance: `SKILL.md`, reference docs, `agents/openai.yaml`, and `evals/evals.json` all reinforce the same selector-first rule.
  - Verify: Inspect the aligned files and search for conflicting guidance.
  - Files: `.opencode/skills/prompt-learning/SKILL.md`, `.opencode/skills/prompt-learning/reference/`, `.opencode/skills/prompt-learning/agents/openai.yaml`, `.opencode/skills/prompt-learning/evals/evals.json`

- [x] Gate: Payload tightening, if any, remains minimal and contract-focused
  - Acceptance: Script changes are limited to structured-choice contract clarity and do not expand unrelated features.
  - Verify: Review diffs for `home.py`, `learning.py`, `practice.py`, and `exam.py`.
  - Files: `.opencode/skills/prompt-learning/scripts/home.py`, `.opencode/skills/prompt-learning/scripts/learning.py`, `.opencode/skills/prompt-learning/scripts/practice.py`, `.opencode/skills/prompt-learning/scripts/exam.py`
