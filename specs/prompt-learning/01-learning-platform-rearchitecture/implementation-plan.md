# Plan: Prompt Learning Learning Platform Rearchitecture

## Status

- Status: Implemented
- Updated: 2026-04-08
- Execution record: see [task-breakdown.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/01-learning-platform-rearchitecture/task-breakdown.md)
- Notes:
  - All planned phases in this document have been implemented in the current codebase.
  - Verification was performed primarily through `ruff`, CLI command checks, and targeted workspace persistence inspection.

## Source of Truth

This plan is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/01-learning-platform-rearchitecture/spec.md)
- [overview.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/prompt-learning-architecture/overview.md)
- [cli-and-modules.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/prompt-learning-architecture/cli-and-modules.md)
- [state-model.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/prompt-learning-architecture/state-model.md)
- [migration-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/prompt-learning-architecture/migration-plan.md)

This document defines the implementation order and verification checkpoints before task breakdown.

## Objective

Implement the `prompt-learning` productization rearchitecture in a staged way that:

- establishes a stable platform skeleton first
- preserves existing skill behavior where practical
- avoids rewriting the entire skill in one pass
- keeps the spec and architecture docs aligned with code changes

## Implementation Strategy

Use a staged migration rather than a big-bang rewrite.

The rearchitecture has one critical dependency chain:

1. workspace and state must exist before platform navigation
2. platform navigation must exist before user-facing module routing
3. Prompt Lab can be migrated early because it is relatively self-contained
4. learning and practice should be separated after the platform shell exists
5. exam should be integrated after shared state and profile flows are stable
6. `SKILL.md` should switch after the product shell is real, not before

## Major Components

### 1. Workspace Layer

Primary responsibility:

- resolve workspace username
- create `prompt-learning-workspace/<username>/`
- initialize persistence files and directories

Primary files:

- `scripts/workspace.py`

Dependencies:

- none beyond existing Python runtime and repository layout

### 2. State Layer

Primary responsibility:

- manage current platform state
- manage course progress
- manage mastery summaries

Primary files:

- `scripts/state.py`

Dependencies:

- workspace path resolution

### 3. Home Layer

Primary responsibility:

- dashboard
- resume target
- next-step recommendation

Primary files:

- `scripts/home.py`
- `scripts/__main__.py`

Dependencies:

- workspace
- state

### 4. Prompt Lab Layer

Primary responsibility:

- migrate old `generate` flow into `lab`
- preserve slot validation and review logic
- support saved templates in workspace

Primary files:

- `scripts/prompt_lab.py`
- `scripts/__main__.py`

Dependencies:

- workspace
- state for current module updates

### 5. Learning Layer

Primary responsibility:

- course catalog
- lesson metadata
- lesson panel
- code outline
- course completion updates

Primary files:

- `scripts/learning.py`
- `scripts/course_catalog.py`
- `scripts/__main__.py`

Dependencies:

- state
- existing course metadata

### 6. Practice Layer

Primary responsibility:

- practice entry points
- dynamic practice blueprints
- result recording
- mistake tracking

Primary files:

- `scripts/practice.py`
- `scripts/state.py`
- `scripts/__main__.py`

Dependencies:

- state
- workspace
- learning layer for course context

### 7. Exam Layer

Primary responsibility:

- productize exam entry points
- connect existing exam structure to platform flows
- persist report history

Primary files:

- `scripts/exam.py`
- `scripts/__main__.py`

Dependencies:

- workspace
- state
- profile/history aggregation

### 8. Profile Layer

Primary responsibility:

- aggregate learning archive views
- expose progress, mistakes, exams, templates

Primary files:

- `scripts/profile.py`
- `scripts/__main__.py`

Dependencies:

- workspace
- state
- practice, exam, and lab persistence outputs

### 9. Skill Contract Layer

Primary responsibility:

- replace old mode-centered `SKILL.md`
- align agent behavior with platform model

Primary files:

- `.opencode/skills/prompt-learning/SKILL.md`

Dependencies:

- platform shell should already exist conceptually and partially in code

## Recommended Implementation Order

## Phase 1: Foundation

Scope:

- add `workspace.py`
- refactor `state.py` to match the new state model
- add `home.py`
- expose `workspace` and `home` commands in `__main__.py`

Why first:

- every later module depends on persistence and product-level navigation

Expected outcome:

- the platform can initialize user workspace
- the platform can show dashboard, recommendation, and resume target

Verification checkpoint:

- workspace directory is created correctly
- initial JSON files exist with valid defaults
- `home --dashboard` returns stable structured output

## Phase 2: Prompt Lab Migration

Scope:

- create `prompt_lab.py`
- move generate-related workflow/checklist/validation logic into `lab`
- add template save/list support
- keep old `generate` path compatible where needed

Why second:

- Prompt Lab is the most self-contained product module
- it proves the new platform shell can support a real module

Expected outcome:

- user-facing Prompt Lab flow exists as `lab`
- confirmed templates are saved into workspace

Verification checkpoint:

- workflow, interview blueprint, slot validation, draft validation all work via `lab`
- template save writes only confirmed artifacts

## Phase 3: Learning Center Extraction

Scope:

- create `learning.py`
- move catalog, lesson meta, lesson panel, code outline, and completion logic out of `engine.py`
- wire `home --resume` and learning entry points together

Why third:

- learning is the main user flow and should be separated before practice is upgraded

Expected outcome:

- learning center exists as a distinct module
- lesson flow can start from platform navigation

Verification checkpoint:

- `learning --catalog` and `learning --lesson-meta` work
- `learning --lesson-panel` is stable and follows the documented structure

## Phase 4: Practice Center Extraction

Scope:

- create `practice.py`
- implement entry points
- implement dynamic blueprint generation
- write practice summaries and mistakes
- update mastery summaries through state layer

Why fourth:

- practice depends on learning context and shared persistence

Expected outcome:

- practice is a standalone module
- mistakes and summaries feed recommendations

Verification checkpoint:

- `practice --entry-points` and `practice --blueprint` work
- recording results updates persistence and state summaries

## Phase 5: Exam Center Productization

Scope:

- adapt `exam.py` to product module structure
- add exam entry points and type-based flows
- write report history and weak-topic summaries

Why fifth:

- exam should consume the same persistence and recommendation framework already established

Expected outcome:

- exam integrates into the platform rather than behaving like an isolated mode

Verification checkpoint:

- diagnostic and final exam entry flows are stable
- reports persist and can be surfaced later

## Phase 6: Profile and Archive

Scope:

- create `profile.py`
- aggregate progress, mistakes, exam history, and templates

Why sixth:

- profile depends on upstream modules already producing usable persistence artifacts

Expected outcome:

- platform can expose a coherent learning archive view

Verification checkpoint:

- `profile --summary` and related commands show accurate aggregated state

## Phase 7: Skill Contract Switch

Scope:

- rewrite `.opencode/skills/prompt-learning/SKILL.md`
- align the skill with the platform model

Why seventh:

- changing the skill contract too early creates drift between docs and implementation

Expected outcome:

- user-facing behavior and internal architecture are aligned

Verification checkpoint:

- `SKILL.md` references product modules and script-first boundaries instead of old mode-centric flow

## Phase 8: Compatibility Cleanup

Scope:

- reduce direct logic in legacy paths
- keep old command names as compatibility shims if still useful
- simplify `engine.py`

Why last:

- cleanup should happen only after replacement paths are stable

Expected outcome:

- old commands no longer own primary logic
- new module boundaries are clear in code

Verification checkpoint:

- no behavior regressions in key flows
- new modules are the primary execution path

## Risks and Mitigations

### Risk 1: The rewrite becomes a second system with duplicate logic

Mitigation:

- migrate logic in phases
- prefer moving existing behavior behind new module boundaries rather than re-implementing from scratch

### Risk 2: `SKILL.md` and scripts drift apart again

Mitigation:

- keep `SKILL.md` minimal
- treat spec and architecture docs as the canonical design source

### Risk 3: Persistence grows into noisy storage

Mitigation:

- enforce summary-only persistence
- keep draft and intermediate artifacts out of workspace

### Risk 4: Practice and exam flows become over-engineered too early

Mitigation:

- keep V1 to documented entry points and fixed blueprint categories
- avoid adaptive difficulty or broad analytics until core flows are stable

### Risk 5: Existing behavior regresses during migration

Mitigation:

- preserve compatibility layers
- verify each phase through CLI and manual scenario checks

## Parallel vs Sequential Work

Sequential critical path:

1. workspace
2. state
3. home
4. Prompt Lab
5. learning
6. practice
7. exam
8. profile
9. `SKILL.md`

Parallelizable work after foundation:

- documentation refinements can continue in parallel
- Prompt Lab and partial learning extraction can overlap once state and home are stable
- profile aggregation can begin after at least one upstream persistence-producing module is stable

## Verification Checkpoints

Each phase should stop at a reviewable checkpoint before proceeding:

### Checkpoint A: Foundation

- workspace paths created
- default state files valid
- dashboard output stable

### Checkpoint B: Prompt Lab

- `lab` commands functional
- templates save correctly
- no unconfirmed drafts persisted

### Checkpoint C: Learning

- catalog and lesson entry stable
- lesson panel follows architecture docs

### Checkpoint D: Practice

- blueprint generation works
- mistake recording works
- mastery updates work

### Checkpoint E: Exam

- exam reports persist
- weak-topic summaries exist

### Checkpoint F: Profile and Contract

- archive views are coherent
- `SKILL.md` reflects the new architecture

## Out of Scope for Initial Implementation

The following are intentionally excluded from the first implementation wave:

- adaptive difficulty engines
- static question banks
- database-backed persistence
- multi-user remote sync
- advanced analytics dashboards
- template version history

## Exit Criteria for Task Breakdown

We are ready for the TASKS phase when:

1. the implementation order is approved
2. the phase boundaries look correct
3. the verification checkpoints are accepted
4. no blocking open questions remain for foundation work
