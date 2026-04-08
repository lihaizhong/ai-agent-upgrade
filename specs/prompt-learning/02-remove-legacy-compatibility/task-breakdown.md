# Tasks: Prompt Learning Remove Legacy Compatibility

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/02-remove-legacy-compatibility/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/02-remove-legacy-compatibility/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: CLI Surface Cleanup

- [x] Task: Remove old CLI commands from `scripts/__main__.py`
  - Acceptance: `mode`, `learn`, `generate`, and `state` are no longer exposed as supported commands.
  - Verify: Run the CLI help output and confirm only `workspace`, `home`, `learning`, `practice`, `exam`, `lab`, and `profile` remain.
  - Files: `.opencode/skills/prompt-learning/scripts/__main__.py`

- [x] Task: Remove legacy command-specific compatibility routing
  - Acceptance: The CLI no longer contains compatibility shims that translate old commands into new module behavior.
  - Verify: Inspect `__main__.py` and confirm product routing exists only for the new module commands.
  - Files: `.opencode/skills/prompt-learning/scripts/__main__.py`

## Phase 2: Legacy Engine and Export Removal

- [x] Task: Remove `PromptLearningEngine` export from `scripts/__init__.py`
  - Acceptance: `scripts/__init__.py` no longer exports `PromptLearningEngine`.
  - Verify: Inspect `__all__` and imports in `scripts/__init__.py`.
  - Files: `.opencode/skills/prompt-learning/scripts/__init__.py`

- [x] Task: Delete or retire `scripts/engine.py`
  - Acceptance: `engine.py` is removed, or retained only as a clearly non-public deprecated stub with no active product ownership.
  - Verify: Search the repository and confirm no active product code depends on `PromptLearningEngine`.
  - Files: `.opencode/skills/prompt-learning/scripts/engine.py`, `.opencode/skills/prompt-learning/scripts/__main__.py`, `.opencode/skills/prompt-learning/scripts/__init__.py`

## Phase 3: Reference and Config Cleanup

- [x] Task: Clean legacy mode-centered reference docs
  - Acceptance: reference docs no longer instruct users or agents to use the old `learn / exam / generate` mode model as the primary interface.
  - Verify: Search the reference directory for mode-centered usage guidance and confirm it is either removed, archived, or rewritten.
  - Files: `.opencode/skills/prompt-learning/reference/learning-mode.md`, `.opencode/skills/prompt-learning/reference/exam-mode.md`, `.opencode/skills/prompt-learning/reference/prompt-generation-mode.md`

- [x] Task: Align configs and metadata with the new platform-only model
  - Acceptance: `VERSION.md`, `agents/openai.yaml`, and `evals/evals.json` no longer describe or depend on old command surfaces where that would conflict with the new product boundary.
  - Verify: Search these files for outdated CLI and mode references.
  - Files: `.opencode/skills/prompt-learning/VERSION.md`, `.opencode/skills/prompt-learning/agents/openai.yaml`, `.opencode/skills/prompt-learning/evals/evals.json`

## Phase 4: Verification

- [x] Task: Verify the new platform command surface after cleanup
  - Acceptance: `home`, `learning`, `practice`, `exam`, `lab`, and `profile` continue to work after legacy removal.
  - Verify: Run representative commands for each new platform module.
  - Files: `.opencode/skills/prompt-learning/scripts/__main__.py`, `.opencode/skills/prompt-learning/scripts/home.py`, `.opencode/skills/prompt-learning/scripts/learning.py`, `.opencode/skills/prompt-learning/scripts/practice.py`, `.opencode/skills/prompt-learning/scripts/exam.py`, `.opencode/skills/prompt-learning/scripts/prompt_lab.py`, `.opencode/skills/prompt-learning/scripts/profile.py`

- [x] Task: Run repository search to confirm legacy surface is gone
  - Acceptance: searches for `PromptLearningEngine` and old mode-entry guidance do not return active supported product surfaces.
  - Verify: Run `rg` against the skill directory and inspect remaining matches.
  - Files: `.opencode/skills/prompt-learning/`

## Phase 5: Spec Sync

- [x] Task: Mark this task breakdown complete after implementation
  - Acceptance: Completed tasks and verification gates are checked off after the work lands.
  - Verify: Inspect this file and confirm status reflects reality.
  - Files: `specs/prompt-learning/02-remove-legacy-compatibility/task-breakdown.md`

- [x] Task: Add completion status to the `02` implementation plan
  - Acceptance: `implementation-plan.md` clearly indicates when the cleanup has been implemented.
  - Verify: Inspect the plan header for status metadata.
  - Files: `specs/prompt-learning/02-remove-legacy-compatibility/implementation-plan.md`

## Global Verification Gates

- [x] Gate: Old CLI surface is removed before engine deletion
  - Acceptance: `mode`, `learn`, `generate`, and `state` are no longer supported CLI entry points.
  - Verify: Inspect help output and command parser definitions.
  - Files: `.opencode/skills/prompt-learning/scripts/__main__.py`

- [x] Gate: Engine removal is complete before config cleanup is finalized
  - Acceptance: No active platform code depends on `PromptLearningEngine`.
  - Verify: Run repository search for `PromptLearningEngine`.
  - Files: `.opencode/skills/prompt-learning/scripts/engine.py`, `.opencode/skills/prompt-learning/scripts/__init__.py`

- [x] Gate: Platform-only surface is stable before spec sync
  - Acceptance: New platform commands pass lint and representative command verification after legacy cleanup.
  - Verify: Run `ruff` and the new command checks listed in the implementation plan.
  - Files: `.opencode/skills/prompt-learning/scripts/`
