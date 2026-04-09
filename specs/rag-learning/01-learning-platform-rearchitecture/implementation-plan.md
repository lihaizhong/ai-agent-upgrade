# Plan: RAG Learning Learning Platform Rearchitecture

## Status

- Status: Implemented
- Updated: 2026-04-09
- Execution record: see [task-breakdown.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/01-learning-platform-rearchitecture/task-breakdown.md)
- Notes:
  - The scoped platform rearchitecture defined by this spec has been implemented in the current codebase.
  - Platform scripts, contract switch, content/reference alignment, and verification coverage are in place.

## Source of Truth

This plan is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/01-learning-platform-rearchitecture/spec.md)
- [overview.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/rag-learning-architecture/overview.md)
- [cli-and-modules.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/rag-learning-architecture/cli-and-modules.md)
- [state-model.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/rag-learning-architecture/state-model.md)
- [migration-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/rag-learning-architecture/migration-plan.md)

This document defines the implementation order and verification checkpoints before task breakdown.

## Objective

Implement the `rag-learning` platform rearchitecture in a staged way that:

- establishes a stable platform skeleton first
- preserves reusable course and reference assets where practical
- avoids rewriting the entire skill in one pass
- keeps the spec and architecture docs aligned with code changes

## Implementation Strategy

Use a staged migration rather than a big-bang rewrite.

The rearchitecture has one critical dependency chain:

1. workspace and state must exist before platform navigation
2. platform navigation must exist before user-facing module routing
3. learning and build should be created before lab and review reuse their context
4. lab and review should be integrated before profile aggregation
5. `SKILL.md` should switch after the platform shell is real, not before
6. old route-centric references should be simplified only after new modules are stable

## Major Components

### 1. Workspace Layer

Primary responsibility:

- resolve workspace username
- create `rag-learning-workspace/<username>/`
- initialize persistence files and directories

Primary files:

- `agent-skills/rag-learning/scripts/workspace.py`

Dependencies:

- none beyond existing Python runtime and repository layout

### 2. State Layer

Primary responsibility:

- manage current platform state
- manage course progress
- manage build progress
- manage competency summaries

Primary files:

- `agent-skills/rag-learning/scripts/state.py`

Dependencies:

- workspace path resolution

### 3. Home Layer

Primary responsibility:

- dashboard
- resume target
- next-step recommendation

Primary files:

- `agent-skills/rag-learning/scripts/home.py`
- `agent-skills/rag-learning/scripts/__main__.py`

Dependencies:

- workspace
- state

### 4. Learning Layer

Primary responsibility:

- course catalog
- learning path recommendation
- lesson metadata
- course completion updates

Primary files:

- `agent-skills/rag-learning/scripts/learning.py`
- `agent-skills/rag-learning/scripts/__main__.py`

Dependencies:

- state
- existing course metadata

### 5. Build Layer

Primary responsibility:

- productize staged RAG implementation flow
- expose project entry points
- record build-step progress

Primary files:

- `agent-skills/rag-learning/scripts/build.py`
- `agent-skills/rag-learning/scripts/__main__.py`

Dependencies:

- workspace
- state
- learning layer for course-context handoff

### 6. Lab Layer

Primary responsibility:

- define experiment entry points
- generate stable experiment blueprints
- record experiment summaries

Primary files:

- `agent-skills/rag-learning/scripts/lab.py`
- `agent-skills/rag-learning/scripts/__main__.py`

Dependencies:

- workspace
- state
- build layer for project context

### 7. Review Layer

Primary responsibility:

- productize architecture review entry points
- generate stable review templates
- persist review summaries

Primary files:

- `agent-skills/rag-learning/scripts/review.py`
- `agent-skills/rag-learning/scripts/__main__.py`

Dependencies:

- workspace
- state
- lab/build outputs as optional evidence sources

### 8. Profile Layer

Primary responsibility:

- aggregate learning archive views
- expose progress, build history, experiments, and reviews

Primary files:

- `agent-skills/rag-learning/scripts/profile.py`
- `agent-skills/rag-learning/scripts/__main__.py`

Dependencies:

- workspace
- state
- build, lab, and review persistence outputs

### 9. Skill Contract Layer

Primary responsibility:

- replace old route-centered `SKILL.md`
- align agent behavior with the platform model

Primary files:

- `agent-skills/rag-learning/SKILL.md`

Dependencies:

- platform shell should already exist conceptually and partially in code

### 10. Content Alignment Layer

Primary responsibility:

- align `reference/` and `courses/` with the new platform model
- reduce old route-centric or stale guidance
- keep time-sensitive content clearly bounded

Primary files:

- `agent-skills/rag-learning/reference/*.md`
- `agent-skills/rag-learning/courses/*.md`
- `agent-skills/rag-learning/evals/evals.json`

Dependencies:

- learning, build, lab, and review module boundaries should already be stable

## Recommended Implementation Order

## Phase 1: Foundation

Scope:

- add `workspace.py`
- add `state.py`
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

## Phase 2: Learning and Build Skeleton

Scope:

- create `learning.py`
- create `build.py`
- define initial course catalog and project entry points
- connect course start/completion and build-step state updates

Why second:

- learning and build are the platform's main value path
- lab and review should reuse their context instead of inventing parallel models

Expected outcome:

- user-facing learning and build flows exist
- the platform can resume a course or project

Verification checkpoint:

- `learning --catalog` and `learning --lesson-meta` return stable outputs
- `build --entry-points` and `build --step-panel` return stable outputs
- course/build progress writes expected state files

## Phase 3: Lab and Review Modules

Scope:

- create `lab.py`
- create `review.py`
- define experiment blueprints and review templates
- persist summary-only history records

Why third:

- experiments and reviews depend on stable project and state context

Expected outcome:

- user can run at least one lab flow and one review flow
- experiment and review summaries are persisted

Verification checkpoint:

- `lab --blueprint` works for V1 topics
- `review --template` returns a stable structure
- history files store summary-only payloads

## Phase 4: Profile Aggregation

Scope:

- create `profile.py`
- aggregate current progress, build history, lab history, and review history
- expose recommendation-aware summary views

Why fourth:

- profile should aggregate real module outputs, not placeholders

Expected outcome:

- platform archive view exists
- home recommendation has a reliable downstream summary source

Verification checkpoint:

- `profile --summary` reflects real persisted state
- detail views match workspace contents

## Phase 5: Skill Contract Switch

Scope:

- rewrite `SKILL.md` to the platform contract model
- replace old route-first framing with platform-first framing

Why fifth:

- the product shell should be real before the contract fully switches

Expected outcome:

- agent behavior aligns with platform modules and script-first boundaries

Verification checkpoint:

- `SKILL.md` matches `docs/rag-learning-architecture/skill-contract.md`

## Phase 6: Content and Reference Alignment

Scope:

- simplify old `reference/` files that encode the previous route model
- align courses with the decision-sequence teaching model
- update evals if needed to reflect the platform mental model

Why last:

- content cleanup is safer after the new structure is stable

Expected outcome:

- old and new product mental models no longer conflict
- courses and references support the platform rather than compete with it

Verification checkpoint:

- search the skill directory for conflicting route-centric guidance
- review course and reference files for stale or conflicting mental models

## Verification Strategy

At minimum, verify:

- workspace bootstrap
- state file creation and updates
- home dashboard output
- learning/build entry points
- lab/review summary persistence
- profile aggregation
- `SKILL.md` contract alignment

Recommended command categories:

- `ruff check .`
- targeted module CLI runs
- workspace artifact inspection
- `rg` searches for conflicting legacy guidance
- `python -m unittest tests.test_rag_learning_platform`
- `python -m unittest tests.test_rag_learning_content_quality`
- `python -m unittest tests.test_rag_learning_config_units`
- `python -m unittest tests.test_rag_learning_state_flow`

## Current Progress Snapshot

Implemented:

- `workspace`, `state`, `home`
- `learning`, `build`
- `lab`, `review`, `profile`
- platform-oriented `SKILL.md`
- course organization and catalog alignment
- reference cleanup and platform config extraction
- eval alignment and automated verification coverage

No spec-scoped implementation items remain open.

## Risks and Controls

- Risk: building content-heavy docs before scripts may recreate a documentation-only product.
  Control: keep foundation and module CLI work ahead of large content rewrites.

- Risk: old `reference/` route logic may conflict with the new platform model.
  Control: schedule reference cleanup after the platform shell exists.

- Risk: time-sensitive model/database guidance may become stale quickly.
  Control: keep recommendations framed as conditional examples and preserve “verify latest” rules in contract/docs.

- Risk: profile and recommendation logic may become hard to explain.
  Control: keep state and recommendation enums small and explicit in V1.
