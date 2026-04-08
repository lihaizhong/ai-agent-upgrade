# Tasks: Prompt Learning Learning Platform Rearchitecture

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/01-learning-platform-rearchitecture/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/01-learning-platform-rearchitecture/implementation-plan.md)

Tasks are ordered by dependency, not by perceived importance.

## Phase 1: Foundation

- [x] Task: Add workspace path resolution and bootstrap support
  - Acceptance: A new `workspace.py` can resolve the normalized username, return the user workspace path, create the expected directory tree, and initialize the minimum JSON files.
  - Verify: Run the new workspace bootstrap CLI path and confirm the expected directories/files exist under `prompt-learning-workspace/<username>/`.
  - Files: `.opencode/skills/prompt-learning/scripts/workspace.py`, `.opencode/skills/prompt-learning/scripts/__main__.py`

- [x] Task: Refactor state storage to match the new state model
  - Acceptance: `state.py` can load and save `current-state.json`, `course-progress.json`, and `mastery.json` using workspace-provided paths and documented defaults.
  - Verify: Run minimal state update flows and inspect written JSON files for expected structure and timestamps.
  - Files: `.opencode/skills/prompt-learning/scripts/state.py`, `.opencode/skills/prompt-learning/scripts/workspace.py`

- [x] Task: Add platform home service and dashboard output
  - Acceptance: A new `home.py` can return `dashboard`, `resume`, and `recommend` outputs using the state layer and workspace user context.
  - Verify: Run the new `home` CLI commands and confirm stable structured JSON including cards, recommendation, and current context.
  - Files: `.opencode/skills/prompt-learning/scripts/home.py`, `.opencode/skills/prompt-learning/scripts/__main__.py`, `.opencode/skills/prompt-learning/scripts/state.py`

## Phase 2: Prompt Lab

- [x] Task: Extract Prompt Lab workflow and validation logic into a dedicated module
  - Acceptance: Existing generate workflow, interview blueprint, checklist, slot validation, and draft validation are available through `prompt_lab.py` and exposed as `lab` CLI commands.
  - Verify: Run `lab --workflow`, `lab --interview-blueprint`, `lab --validate-slots`, and `lab --validate-draft` with sample payloads and confirm expected schema and validation behavior.
  - Files: `.opencode/skills/prompt-learning/scripts/prompt_lab.py`, `.opencode/skills/prompt-learning/scripts/__main__.py`

- [x] Task: Add Prompt Lab template persistence
  - Acceptance: Confirmed Prompt Lab templates can be saved to workspace and listed from a stable template index without persisting unconfirmed drafts.
  - Verify: Save a sample template, inspect `prompt-learning-workspace/<username>/prompt-lab/`, and confirm the template index and template file are both valid.
  - Files: `.opencode/skills/prompt-learning/scripts/prompt_lab.py`, `.opencode/skills/prompt-learning/scripts/workspace.py`, `.opencode/skills/prompt-learning/scripts/state.py`

## Phase 3: Learning Center

- [x] Task: Extract course catalog and lesson metadata into a dedicated learning module
  - Acceptance: `learning.py` owns course catalog listing, category listing, lesson metadata lookup, and course completion entry points while reusing existing course metadata.
  - Verify: Run `learning --catalog`, `learning --category <name>`, and `learning --lesson-meta --course <N>` and confirm outputs match the documented structures.
  - Files: `.opencode/skills/prompt-learning/scripts/learning.py`, `.opencode/skills/prompt-learning/scripts/course_catalog.py`, `.opencode/skills/prompt-learning/scripts/__main__.py`

- [x] Task: Move lesson panel and code outline generation into the learning module
  - Acceptance: Learning center exposes lesson panel and code outline outputs without relying on the old monolithic engine for those responsibilities.
  - Verify: Run `learning --lesson-panel --course <N>` and `learning --code-outline --course <N>` and confirm outputs match the architecture docs.
  - Files: `.opencode/skills/prompt-learning/scripts/learning.py`, `.opencode/skills/prompt-learning/scripts/__main__.py`

- [x] Task: Connect course start and completion actions to the new state layer
  - Acceptance: Starting or completing a course updates `current-state.json` and `course-progress.json` consistently.
  - Verify: Trigger a course start/completion flow and inspect both state files for expected updates.
  - Files: `.opencode/skills/prompt-learning/scripts/learning.py`, `.opencode/skills/prompt-learning/scripts/state.py`

## Phase 4: Practice Center

- [x] Task: Add practice entry point routing
  - Acceptance: `practice.py` exposes structured entry points for current-course practice, targeted practice, and mistake review.
  - Verify: Run `practice --entry-points` and confirm the expected three entry options and question structure.
  - Files: `.opencode/skills/prompt-learning/scripts/practice.py`, `.opencode/skills/prompt-learning/scripts/__main__.py`

- [x] Task: Implement dynamic practice blueprint generation
  - Acceptance: Practice center can generate stable blueprints for `current`, `targeted`, and `mistake` modes using course context and documented question types.
  - Verify: Run `practice --blueprint` for each supported mode and confirm output includes mode, goal, constraints, and response schema.
  - Files: `.opencode/skills/prompt-learning/scripts/practice.py`, `.opencode/skills/prompt-learning/scripts/course_catalog.py`

- [x] Task: Record practice results and mistake summaries
  - Acceptance: Practice result recording appends summary events to `practice-history.jsonl`, writes mistakes to `mistakes.jsonl`, and does not persist full draft content.
  - Verify: Record a sample result and inspect both JSONL files for the expected summary-only payloads.
  - Files: `.opencode/skills/prompt-learning/scripts/practice.py`, `.opencode/skills/prompt-learning/scripts/workspace.py`

- [x] Task: Update mastery and recommendation state from practice outcomes
  - Acceptance: Recording practice outcomes updates course mastery summaries and current recommendation fields through the state layer.
  - Verify: After recording multiple sample outcomes, inspect `mastery.json` and `current-state.json` for expected changes.
  - Files: `.opencode/skills/prompt-learning/scripts/practice.py`, `.opencode/skills/prompt-learning/scripts/state.py`, `.opencode/skills/prompt-learning/scripts/home.py`

## Phase 5: Exam Center

- [x] Task: Add exam entry points and exam-type routing
  - Acceptance: The exam module exposes structured entry points for diagnostic and final exam flows.
  - Verify: Run the new exam entry command and confirm the expected options and descriptions.
  - Files: `.opencode/skills/prompt-learning/scripts/exam.py`, `.opencode/skills/prompt-learning/scripts/__main__.py`

- [x] Task: Connect existing exam structure and validation logic to the product module flow
  - Acceptance: Existing exam structure, blueprint, validation, and report generation work through the productized `exam` command surface without losing existing constraints.
  - Verify: Run structure, blueprint, validation, and report commands with sample payloads and confirm behavior remains stable.
  - Files: `.opencode/skills/prompt-learning/scripts/exam.py`, `.opencode/skills/prompt-learning/scripts/__main__.py`

- [x] Task: Persist exam history summaries and weak-topic outputs
  - Acceptance: Completed exams append summary records to `exam-history.jsonl`, save reports under `exam/reports/`, and expose weak-topic data for later recommendation use.
  - Verify: Complete a sample exam report flow and inspect workspace persistence artifacts.
  - Files: `.opencode/skills/prompt-learning/scripts/exam.py`, `.opencode/skills/prompt-learning/scripts/workspace.py`, `.opencode/skills/prompt-learning/scripts/state.py`

## Phase 6: Profile and Archive

- [x] Task: Add profile summary aggregation
  - Acceptance: `profile.py` can aggregate current progress, mastery, open mistakes, exam history summary, and saved template counts into a coherent summary view.
  - Verify: Run `profile --summary` after seeding sample workspace data and confirm the output reflects real persisted state.
  - Files: `.opencode/skills/prompt-learning/scripts/profile.py`, `.opencode/skills/prompt-learning/scripts/state.py`, `.opencode/skills/prompt-learning/scripts/__main__.py`

- [x] Task: Add profile detail views for progress, mistakes, exams, and templates
  - Acceptance: Profile detail commands return stable structured views for the main archive categories without duplicating persistence logic.
  - Verify: Run `profile --progress`, `profile --mistakes`, `profile --exam-history`, and `profile --templates` and confirm outputs are accurate.
  - Files: `.opencode/skills/prompt-learning/scripts/profile.py`, `.opencode/skills/prompt-learning/scripts/__main__.py`

## Phase 7: Skill Contract Switch

- [x] Task: Rewrite `SKILL.md` to the platform contract model
  - Acceptance: `SKILL.md` aligns with `skill-contract.md`, refers to platform modules rather than the old mode-centered mental model, and removes detailed flow definitions that now belong in scripts/docs.
  - Verify: Review the rewritten file against `docs/prompt-learning-architecture/skill-contract.md` and confirm major responsibilities and prohibited behaviors are aligned.
  - Files: `.opencode/skills/prompt-learning/SKILL.md`

## Phase 8: Compatibility Cleanup

- [x] Task: Reduce legacy command ownership and convert old paths into compatibility shims
  - Acceptance: Old `learn`, `exam`, and `generate` command paths no longer own primary platform logic where a new module exists, while preserving expected behavior during migration.
  - Verify: Run representative old command flows and confirm they still work while tracing to new module behavior or shared logic.
  - Files: `.opencode/skills/prompt-learning/scripts/__main__.py`, `.opencode/skills/prompt-learning/scripts/engine.py`, `.opencode/skills/prompt-learning/scripts/exam.py`, `.opencode/skills/prompt-learning/scripts/prompt_lab.py`, `.opencode/skills/prompt-learning/scripts/learning.py`

- [x] Task: Simplify or retire monolithic engine responsibilities
  - Acceptance: `engine.py` is reduced to only the responsibilities that still make sense, with learning/practice/platform concerns migrated to dedicated modules.
  - Verify: Inspect `engine.py` diff and confirm major platform concerns are no longer concentrated there.
  - Files: `.opencode/skills/prompt-learning/scripts/engine.py`, `.opencode/skills/prompt-learning/scripts/learning.py`, `.opencode/skills/prompt-learning/scripts/practice.py`

## Global Verification Gates

- [x] Gate: Foundation commands are stable before Prompt Lab migration begins
  - Acceptance: Workspace bootstrap, state defaults, and home dashboard all work.
  - Verify: Run foundation CLI commands in sequence.
  - Files: `.opencode/skills/prompt-learning/scripts/workspace.py`, `.opencode/skills/prompt-learning/scripts/state.py`, `.opencode/skills/prompt-learning/scripts/home.py`

- [x] Gate: Prompt Lab persistence is stable before learning/practice extraction begins
  - Acceptance: Confirmed template save/list flows work and no draft leakage occurs.
  - Verify: Run sample save/list flow and inspect workspace artifacts.
  - Files: `.opencode/skills/prompt-learning/scripts/prompt_lab.py`

- [x] Gate: Learning and practice are stable before exam/profile integration
  - Acceptance: Learning flows can enter practice, and practice results correctly update persistence and recommendations.
  - Verify: Run a lesson-to-practice scenario end to end.
  - Files: `.opencode/skills/prompt-learning/scripts/learning.py`, `.opencode/skills/prompt-learning/scripts/practice.py`, `.opencode/skills/prompt-learning/scripts/state.py`

- [x] Gate: Archive views and contract switch are stable before compatibility cleanup
  - Acceptance: Profile summary works and `SKILL.md` reflects the new model.
  - Verify: Run profile commands and review the final contract.
  - Files: `.opencode/skills/prompt-learning/scripts/profile.py`, `.opencode/skills/prompt-learning/SKILL.md`
