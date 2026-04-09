# Tasks: RAG Learning Learning Platform Rearchitecture

## Status

- Status: Completed
- Updated: 2026-04-09
- Notes:
  - All spec-scoped tasks and verification gates are complete.
  - Ongoing work, if any, should be tracked as a new spec change rather than appended here.

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/01-learning-platform-rearchitecture/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/01-learning-platform-rearchitecture/implementation-plan.md)

Tasks are ordered by dependency, not by perceived importance.

## Phase 1: Foundation

- [x] Task: Add workspace path resolution and bootstrap support
  - Acceptance: A new `workspace.py` can resolve the normalized username, return the user workspace path, create the expected directory tree, and initialize the minimum JSON/JSONL files.
  - Verify: Run the new workspace bootstrap CLI path and confirm the expected directories/files exist under `rag-learning-workspace/<username>/`.
  - Files: `agent-skills/rag-learning/scripts/workspace.py`, `agent-skills/rag-learning/scripts/__main__.py`

- [x] Task: Add state storage to match the new platform state model
  - Acceptance: `state.py` can load and save `current-state.json`, `course-progress.json`, `build-progress.json`, and `competency.json` using workspace-provided paths and documented defaults.
  - Verify: Run minimal state update flows and inspect written JSON files for expected structure and timestamps.
  - Files: `agent-skills/rag-learning/scripts/state.py`, `agent-skills/rag-learning/scripts/workspace.py`

- [x] Task: Add platform home service and dashboard output
  - Acceptance: A new `home.py` can return `dashboard`, `resume`, and `recommend` outputs using the state layer and workspace user context.
  - Verify: Run the new `home` CLI commands and confirm stable structured JSON including cards, recommendation, and current context.
  - Files: `agent-skills/rag-learning/scripts/home.py`, `agent-skills/rag-learning/scripts/__main__.py`, `agent-skills/rag-learning/scripts/state.py`

## Phase 2: Learning and Build

- [x] Task: Extract course catalog and lesson metadata into a dedicated learning module
  - Acceptance: `learning.py` owns course catalog listing, learning-path recommendation, lesson metadata lookup, and course completion entry points while reusing existing course files.
  - Verify: Run `learning --catalog`, `learning --path --level <level>`, and `learning --lesson-meta --course <N>` and confirm outputs match the architecture docs.
  - Files: `agent-skills/rag-learning/scripts/learning.py`, `agent-skills/rag-learning/scripts/__main__.py`, `agent-skills/rag-learning/courses/`

- [x] Task: Connect course start and completion actions to the new state layer
  - Acceptance: Starting or completing a course updates `current-state.json` and `course-progress.json` consistently.
  - Verify: Trigger a course start/completion flow and inspect both state files for expected updates.
  - Files: `agent-skills/rag-learning/scripts/learning.py`, `agent-skills/rag-learning/scripts/state.py`

- [x] Task: Add build entry point routing for the platformized project flow
  - Acceptance: `build.py` exposes structured entry points for `本地最小 RAG` and future project placeholders with a stable step model.
  - Verify: Run `build --entry-points` and confirm the expected options and descriptions.
  - Files: `agent-skills/rag-learning/scripts/build.py`, `agent-skills/rag-learning/scripts/__main__.py`

- [x] Task: Implement build step panels for the minimum RAG path
  - Acceptance: The build center can return stable step panels for `scenario`, `chunking`, `embedding`, `vector_db`, `retrieval`, `rerank`, `generation`, and `evaluation`.
  - Verify: Run `build --step-panel --project local-minimum-rag --step <name>` for representative steps and confirm output includes current decision, recommendation, tradeoff, task, and next-step fields.
  - Files: `agent-skills/rag-learning/scripts/build.py`, `agent-skills/rag-learning/scripts/__main__.py`

- [x] Task: Record build progress and recommendation state from step completion
  - Acceptance: Build step recording writes summary progress to `build-progress.json` and updates current state recommendation fields.
  - Verify: Record sample step completions and inspect `build-progress.json` and `current-state.json` for expected changes.
  - Files: `agent-skills/rag-learning/scripts/build.py`, `agent-skills/rag-learning/scripts/state.py`

## Phase 3: RAG Lab and Review

- [x] Task: Add RAG Lab entry points and experiment blueprint generation
  - Acceptance: `lab.py` exposes structured experiment entry points and stable blueprints for `embedding`, `rerank`, and `chunking`.
  - Verify: Run `lab --entry-points` and `lab --blueprint --topic <topic>` and confirm output includes goal, variables, fixed conditions, metrics, and output fields.
  - Files: `agent-skills/rag-learning/scripts/lab.py`, `agent-skills/rag-learning/scripts/__main__.py`

- [x] Task: Persist experiment result summaries without storing process logs
  - Acceptance: Lab result recording appends summary events to `experiment-history.jsonl` and does not persist chain-of-thought, full chat logs, or transient drafts.
  - Verify: Record a sample lab result and inspect workspace artifacts for summary-only payloads.
  - Files: `agent-skills/rag-learning/scripts/lab.py`, `agent-skills/rag-learning/scripts/workspace.py`

- [x] Task: Add architecture review entry points and review template generation
  - Acceptance: `review.py` exposes entry points and returns a stable template including scenario, constraints, recommended architecture, component choices, risks, and evaluation plan.
  - Verify: Run `review --entry-points` and `review --template --scenario <name>` and confirm outputs match the architecture docs.
  - Files: `agent-skills/rag-learning/scripts/review.py`, `agent-skills/rag-learning/scripts/__main__.py`

- [x] Task: Persist review summaries for later recall
  - Acceptance: Completed review summaries append to `review-history.jsonl` using summary-only payloads and optional saved drafts are only written when explicitly confirmed.
  - Verify: Record a sample review result and inspect workspace artifacts for expected fields and absence of transient drafts.
  - Files: `agent-skills/rag-learning/scripts/review.py`, `agent-skills/rag-learning/scripts/workspace.py`

## Phase 4: Profile and Archive

- [x] Task: Add profile summary aggregation
  - Acceptance: `profile.py` can aggregate current progress, course progress, build progress, lab history summary, review summary, and recommendation context into a coherent archive view.
  - Verify: Run `profile --summary` after seeding sample workspace data and confirm the output reflects real persisted state.
  - Files: `agent-skills/rag-learning/scripts/profile.py`, `agent-skills/rag-learning/scripts/state.py`, `agent-skills/rag-learning/scripts/__main__.py`

- [x] Task: Add profile detail views for progress, experiments, and reviews
  - Acceptance: Profile detail commands return stable structured views for the main archive categories without duplicating persistence logic.
  - Verify: Run `profile --progress`, `profile --experiments`, and `profile --reviews` and confirm outputs are accurate.
  - Files: `agent-skills/rag-learning/scripts/profile.py`, `agent-skills/rag-learning/scripts/__main__.py`

## Phase 5: Skill Contract Switch

- [x] Task: Rewrite `SKILL.md` to the platform contract model
  - Acceptance: `SKILL.md` aligns with `docs/rag-learning-architecture/skill-contract.md`, refers to platform modules rather than the old route-centered model, and removes detailed flow definitions that now belong in scripts/docs.
  - Verify: Review the rewritten file against `docs/rag-learning-architecture/skill-contract.md` and confirm major responsibilities and prohibited behaviors are aligned.
  - Files: `agent-skills/rag-learning/SKILL.md`

## Phase 6: Content and Reference Alignment

- [x] Task: Simplify route-centric reference ownership
  - Acceptance: `reference/router.md`, `reference/ambiguous-intent.md`, `reference/learning-mode.md`, and `reference/practice-mode.md` no longer act as the primary product shell and instead align with the platform module model.
  - Verify: Inspect the reference files and confirm they support, rather than override, the new platform contract.
  - Files: `agent-skills/rag-learning/reference/router.md`, `agent-skills/rag-learning/reference/ambiguous-intent.md`, `agent-skills/rag-learning/reference/learning-mode.md`, `agent-skills/rag-learning/reference/practice-mode.md`

- [x] Task: Align course organization with the decision-sequence learning model
  - Acceptance: The course set is mapped cleanly to the new learning sequence and no longer reads as a disconnected topic list.
  - Verify: Inspect `courses/README.md`, `reference/catalog.md`, and representative course files for alignment with the documented learning-center flow.
  - Files: `agent-skills/rag-learning/courses/README.md`, `agent-skills/rag-learning/reference/catalog.md`, `agent-skills/rag-learning/courses/*.md`

- [x] Task: Update eval expectations to reflect the platform mental model where needed
  - Acceptance: `evals/evals.json` no longer assumes only the old route model and includes expectations consistent with the platformized skill contract.
  - Verify: Inspect the eval file and confirm key platform surfaces are represented or the legacy assumptions have been removed.
  - Files: `agent-skills/rag-learning/evals/evals.json`

## Global Verification Gates

- [x] Gate: Foundation commands are stable before learning/build extraction begins
  - Acceptance: Workspace bootstrap, state defaults, and home dashboard all work.
  - Verify: Run foundation CLI commands in sequence.
  - Files: `agent-skills/rag-learning/scripts/workspace.py`, `agent-skills/rag-learning/scripts/state.py`, `agent-skills/rag-learning/scripts/home.py`

- [x] Gate: Learning and build are stable before lab/review integration
  - Acceptance: Course flows can update state, and build steps correctly update persistence and recommendations.
  - Verify: Run a lesson-to-build scenario end to end.
  - Files: `agent-skills/rag-learning/scripts/learning.py`, `agent-skills/rag-learning/scripts/build.py`, `agent-skills/rag-learning/scripts/state.py`

- [x] Gate: Lab and review persistence are stable before profile aggregation
  - Acceptance: Experiment and review summary writes work and no transient content leakage occurs.
  - Verify: Run sample record flows and inspect workspace artifacts.
  - Files: `agent-skills/rag-learning/scripts/lab.py`, `agent-skills/rag-learning/scripts/review.py`

- [x] Gate: Archive views and contract switch are stable before reference cleanup
  - Acceptance: Profile summary works and `SKILL.md` reflects the new model.
  - Verify: Run profile commands and review the final contract.
  - Files: `agent-skills/rag-learning/scripts/profile.py`, `agent-skills/rag-learning/SKILL.md`
