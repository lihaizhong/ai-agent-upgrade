# Plan: Prompt Learning Selector-First Interaction

## Status

- Status: Implemented
- Updated: 2026-04-08
- Execution record: see [task-breakdown.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/03-selector-first-interaction/task-breakdown.md)
- Notes:
  - Selector-first interaction has been aligned across skill instructions, references, agent metadata, eval expectations, and script payload identifiers.
  - Verification was performed with CLI payload checks, JSON validation, and `ruff`.

## Source of Truth

This plan is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/03-selector-first-interaction/spec.md)
- [SKILL.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.opencode/skills/prompt-learning/SKILL.md)
- [reference/learning-mode.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.opencode/skills/prompt-learning/reference/learning-mode.md)
- [reference/exam-mode.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.opencode/skills/prompt-learning/reference/exam-mode.md)
- [reference/prompt-generation-mode.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.opencode/skills/prompt-learning/reference/prompt-generation-mode.md)

This document defines the execution order for aligning `prompt-learning` around a selector-first interaction contract.

## Objective

Make selector-first interaction the stable default for choice-based flows in `prompt-learning`:

- prefer the current AI executor's native selector UI whenever structured choices already exist
- allow plain-text numbered menus only as explicit fallback behavior
- align skill instructions, references, agent prompts, script contracts, and eval expectations around the same interaction rule

## Implementation Strategy

Use a staged contract-first approach rather than jumping straight into script edits.

The dependency order is:

1. define selector-first behavior at the product contract level
2. align skill and reference documents with that contract
3. align agent prompt and eval expectations
4. tighten script payloads only if the existing contract is insufficient
5. verify fallback behavior remains explicit and narrow

## Recommended Implementation Order

## Phase 1: Interaction Contract Definition

Scope:

- define selector-first as the default interaction rule for choice-based flows
- define the fallback condition for plain-text menus
- define structured choice payloads as the source of truth

Why first:

- without a clear contract, later script and doc changes will drift
- this phase turns a preference into a product rule

Expected outcome:

- `prompt-learning` has one explicit rule for structured-choice interactions

Verification checkpoint:

- the spec clearly distinguishes selector-first behavior from fallback behavior

## Phase 2: Skill and Reference Alignment

Scope:

- update `SKILL.md` to require selector-first behavior when structured choices are available
- align `reference/learning-mode.md` and `reference/exam-mode.md`
- review whether `reference/prompt-generation-mode.md` needs selector-first guidance or explicit exemption

Why second:

- the skill contract is the primary behavioral source for the agent
- reference docs must reinforce the same rule and not undermine it

Expected outcome:

- docs consistently describe selector-first as the default behavior for eligible flows

Verification checkpoint:

- searches across the skill and reference files show one consistent interaction rule

## Phase 3: Agent Prompt and Eval Alignment

Scope:

- update `agents/openai.yaml` if needed to reinforce selector-first execution
- update `evals/evals.json` so critical entry flows are less likely to regress into plain-text menus
- define what counts as acceptable fallback behavior in evaluation language

Why third:

- agent prompts and evals are the main levers that stabilize behavior after docs are updated

Expected outcome:

- selector-first behavior is reinforced in both execution guidance and regression checks

Verification checkpoint:

- eval expectations explicitly distinguish structured-choice behavior from fallback text behavior

## Phase 4: Script Contract Review and Optional Tightening

Scope:

- audit `question` payloads returned by `home`, `learning`, `practice`, and `exam`
- decide whether existing fields are sufficient for stable selector mapping
- add stable metadata only if the current payloads are too weak or ambiguous

Why fourth:

- script changes should follow contract clarification, not precede it
- unnecessary payload churn should be avoided if the current structures are already adequate

Expected outcome:

- either the current payload is confirmed as sufficient, or a minimal contract-tightening change is scoped

Verification checkpoint:

- every selector-first surface has an unambiguous structured payload contract

## Phase 5: Verification and Spec Sync

Scope:

- verify the documented selector-first rule across key interaction surfaces
- confirm fallback remains limited to unsupported environments
- sync spec artifacts once the interaction contract is fully aligned

Why last:

- final verification should reflect the shipped contract, not assumptions

Expected outcome:

- the spec, plan, tasks, and aligned product docs describe the same behavior

Verification checkpoint:

- `spec.md`, `implementation-plan.md`, `task-breakdown.md`, and affected skill docs are aligned

## Key Surfaces to Review

This plan should at minimum review:

- platform home navigation
- learning category selection
- learning course selection
- post-lesson follow-up panel
- practice entry selection
- exam entry selection

This plan may also review:

- profile follow-up actions
- limited Prompt Lab branch selection where structured choice is actually appropriate

## Risks

- over-specifying selector behavior may make fallback environments harder to support cleanly
- under-specifying script payload requirements may leave room for future regressions
- expanding selector-first into open-ended Prompt Lab clarification could damage teaching flow
- updating docs without eval alignment will not be enough to stabilize behavior

## Verification Commands

These commands should be used only after implementation exists:

```bash
ruff check .opencode/skills/prompt-learning/scripts
```

```bash
.venv/bin/python -m scripts home --dashboard
.venv/bin/python -m scripts learning --catalog
.venv/bin/python -m scripts learning --category 基础课程
.venv/bin/python -m scripts practice --entry-points
.venv/bin/python -m scripts exam --entry-points
```

```bash
rg "plain-text|numbered menu|selector|structured choices|question" .opencode/skills/prompt-learning
```
