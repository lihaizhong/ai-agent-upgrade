# Plan: Prompt Learning Remove Legacy Compatibility

## Status

- Status: Implemented
- Updated: 2026-04-08
- Execution record: see [task-breakdown.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/02-remove-legacy-compatibility/task-breakdown.md)
- Notes:
  - The legacy compatibility layer has been removed from the active product surface.
  - Verification was performed with `ruff`, new-platform CLI checks, JSON validation, and repository search.

## Source of Truth

This plan is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/02-remove-legacy-compatibility/spec.md)
- [SKILL.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.opencode/skills/prompt-learning/SKILL.md)
- [task-breakdown.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/01-learning-platform-rearchitecture/task-breakdown.md)

This document defines the implementation order for removing the remaining legacy compatibility surface after the platform rearchitecture.

## Objective

Remove the old mode-centered compatibility layer so `prompt-learning` exposes only the new platform model:

- `workspace`
- `home`
- `learning`
- `practice`
- `exam`
- `lab`
- `profile`

## Implementation Strategy

Use a staged cleanup rather than deleting everything in one edit.

The dependency order is:

1. remove old CLI ownership first
2. remove legacy exports and wrapper engine second
3. clean references, configs, and eval assumptions third
4. verify only the new platform surface remains
5. sync spec artifacts last

## Recommended Implementation Order

## Phase 1: CLI Surface Cleanup

Scope:

- remove `mode`
- remove `learn`
- remove `generate`
- remove `state`
- keep only the new platform commands in `scripts/__main__.py`

Why first:

- the CLI is the primary product surface
- once the old commands are gone, the remaining cleanup becomes unambiguous

Expected outcome:

- users can only access the new platform command model

Verification checkpoint:

- `python -m scripts --help` shows only the new platform commands

## Phase 2: Legacy Engine and Export Removal

Scope:

- remove `PromptLearningEngine` from `scripts/__init__.py`
- delete `scripts/engine.py`, or reduce it to a non-exported internal stub only if strictly necessary
- remove imports and references that only exist for compatibility

Why second:

- once the old CLI is gone, the legacy wrapper should no longer be needed

Expected outcome:

- there is no formal public code path for the old engine

Verification checkpoint:

- repository search finds no active product code depending on `PromptLearningEngine`

## Phase 3: Reference and Config Cleanup

Scope:

- update or retire legacy reference docs
- clean old mode wording from config/evals/version metadata where needed
- ensure `SKILL.md` and adjacent docs no longer imply dual support

Why third:

- after command and code cleanup, supporting materials can be aligned precisely

Expected outcome:

- docs and config describe only the new platform model

Verification checkpoint:

- search for `learn / exam / generate` mode-centered guidance no longer returns active usage docs

## Phase 4: New Surface Verification

Scope:

- run lint
- verify new platform commands
- verify no persistence regressions were introduced by cleanup

Why fourth:

- confirms that cleanup removed only legacy surface, not current functionality

Expected outcome:

- the new product surface remains fully usable

Verification checkpoint:

- `home`, `learning`, `practice`, `exam`, `lab`, and `profile` all run successfully

## Phase 5: Spec Sync

Scope:

- create `task-breakdown.md`
- mark implementation progress after execution
- add status note to this plan when complete

Why last:

- spec artifacts should reflect what actually shipped, not intended cleanup

Expected outcome:

- `02` spec chain is complete and auditable

Verification checkpoint:

- `spec.md`, `implementation-plan.md`, and `task-breakdown.md` are aligned

## Risks

- removing old commands may break ad hoc local usage patterns
- lingering legacy references in docs can cause hidden inconsistency
- deleting `engine.py` too early could obscure whether another file still imports it

## Verification Commands

```bash
ruff check .opencode/skills/prompt-learning/scripts
```

```bash
.venv/bin/python -m scripts home --dashboard
.venv/bin/python -m scripts learning --catalog
.venv/bin/python -m scripts practice --entry-points
.venv/bin/python -m scripts exam --entry-points
.venv/bin/python -m scripts lab --workflow --topic "会议纪要总结"
.venv/bin/python -m scripts profile --summary
```

```bash
rg "PromptLearningEngine|learn --|generate --|mode|state --" .opencode/skills/prompt-learning
```
