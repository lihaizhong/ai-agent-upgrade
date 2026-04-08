# Stable Selector Interaction Protocol

## Problem Statement

How might we make selector rendering a stable, predictable behavior across all user-facing interaction points in the Prompt Learning skill — so that every LLM executor (regardless of model or context length) consistently uses the native `question` tool when the script defines a structured choice, and explicitly declares when it self-decides the interaction mode?

## Recommended Direction

**Add an `interaction` declaration to every script output point**, specifying one of three modes: `selector`, `open_ended`, or `inform`. When the mode is `selector`, the `question` object is provided and MUST be rendered via the `question` tool with no modification. When the mode is `open_ended` or `inform`, the LLM knows it has discretion — but the mode is still explicitly declared, not left to guesswork.

This is a "lazy script + explicit degradation" approach: the script declares the interaction mode for every touchpoint, and the LLM follows the declaration. If a script output lacks an `interaction` field, the LLM must explicitly note that it's self-deciding.

### Why this works

- **Eliminates ambiguity at the source**: Instead of the LLM inferring "should I use a selector here?" from the presence/absence of a `question` field, the script explicitly tells it the mode.
- **Makes degradation explicit and auditable**: When the LLM doesn't use a selector, it's because the script said `open_ended` or `inform`, not because the LLM forgot. If the `interaction` field is missing entirely, that's a bug in the script, not a failure of LLM compliance.
- **Covers all interaction points**: Including follow-up questions (Prompt Lab slots, practice question generation) — the script says "this is open_ended, LLM generates content" rather than silently leaving it to the LLM's judgment.
- **Minimal code change**: Adding an `interaction` dict to each script output is a small, mechanical change. No new CLI commands needed.

## Key Assumptions to Validate

- [ ] The `interaction.mode` field is sufficient to cover all current and foreseeable interaction patterns (selector / open_ended / inform) — test by auditing all script outputs
- [ ] LLMs will reliably follow a declared `mode: "selector"` instruction — test by running 3+ session starts and verifying selector usage
- [ ] Adding `interaction` to Prompt Lab slot-level outputs doesn't over-constrain the LLM's ability to ask natural follow-up questions — test by running a full Prompt Lab session

## MVP Scope

### In

1. **Add `interaction` field to all script outputs** that involve user-facing interaction
   - `home.py` → `get_dashboard()`: `interaction.mode = "selector"`
   - `learning.py` → `get_catalog()`: `interaction.mode = "selector"` (top-level and per-category)
   - `learning.py` → `get_category()`: `interaction.mode = "selector"`
   - `learning.py` → `get_lesson_panel()`: `interaction.mode = "selector"`
   - `learning.py` → `recommend_course()`: `interaction.mode = "open_ended"`
   - `learning.py` → `get_lesson_meta()`: `interaction.mode = "inform"`
   - `learning.py` → `get_code_meta()`: `interaction.mode = "inform"`
   - `learning.py` → `get_code_outline()`: `interaction.mode = "inform"`
   - `learning.py` → `complete_course()`: `interaction.mode = "inform"`
   - `practice.py` → `get_entry_points()`: `interaction.mode = "selector"`
   - `practice.py` → `get_resume_target()`: `interaction.mode = "open_ended"`
   - `practice.py` → `build_blueprint()`: `interaction.mode = "open_ended"`
   - `practice.py` → `get_practice_summary()`: `interaction.mode = "inform"`
   - `practice.py` → `list_open_mistakes()`: `interaction.mode = "inform"`
   - `practice.py` → `record_result()`: `interaction.mode = "inform"`
   - `exam.py` → `get_entry_points()`: `interaction.mode = "selector"`
   - `exam.py` → `build_exam_blueprint()`: `interaction.mode = "inform"`
   - `exam.py` → `generate_exam_structure()`: `interaction.mode = "inform"`
   - `prompt_lab.py` → `build_workflow()`: `interaction.mode = "inform"`
   - `prompt_lab.py` → `build_interview_blueprint()`: per-slot `interaction.mode = "open_ended"`
   - `prompt_lab.py` → `build_review_checklist()`: `interaction.mode = "inform"`
   - `profile.py` → all outputs: `interaction.mode = "inform"`

2. **Add Selector Rendering Protocol to SKILL.md** — a hard rule section with:
   - Trigger condition: when `interaction.mode == "selector"`, map `question` object to `question` tool
   - Concrete field-by-field mapping (question → question, header → header, options → options, multiple → multiple)
   - Positive example (selector output) and negative example (plain text output)
   - Degradation rule: if `interaction` field is missing, note it as a script bug and self-decide, but explicitly state "当前交互模式未由脚本定义"

3. **Verify** by running the full home → catalog → course flow and confirming selectors render consistently

### Not Doing (and Why)

- **Changing CLI command structure or adding new commands** — the current CLI is functional; we only add fields to existing outputs
- **Adding `render_hint` at the script level as a separate signal** — `interaction.mode` subsumes this; one field is enough
- **Making Prompt Lab slots into selectors** — SKILL.md explicitly says "Prompt Lab 的槽位澄清默认保持开放式追问"; `open_ended` mode respects this
- **Adding LLM-side guard check (stop-before-output pattern)** — this is a larger behavioral change; the `interaction.mode` field should be sufficient signal
- **Automated tests for selector rendering** — we can't programmatically assert LLM tool usage; manual verification is the pragmatic first step
- **Versioning the protocol** (e.g., `Selector Rendering Protocol v1`) — premature; version after we've validated the approach works

## Open Questions

- Should `interaction` be a top-level field or nested under a `meta` key? (Leaning top-level for discoverability.)
- When a script returns `interaction.mode = "open_ended"` with a `prompt_hint`, should the LLM be required to use that hint verbatim, or is it just guidance? (Leaning guidance — the LLM adapts the question to context.)
- Should we also add `interaction` to exam generation flow (`validate_mc_question`, etc.)? These are LLM-internal operations, not user-facing — leaning no for MVP.