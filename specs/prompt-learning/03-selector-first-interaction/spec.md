# Spec: Prompt Learning Selector-First Interaction

## Assumptions

1. `prompt-learning` has already completed its platform rearchitecture, and the current product surface is:
   - `workspace`
   - `home`
   - `learning`
   - `practice`
   - `exam`
   - `lab`
   - `profile`
2. The current script layer already returns structured `question` payloads for at least these flows:
   - platform home
   - learning category selection
   - learning course selection
   - post-lesson follow-up panel
   - practice entry selection
   - exam entry selection
3. The current problem is not primarily missing option data; it is that the agent may still degrade into plain-text numbered menus even when structured choices already exist.
4. The user wants "prefer the current AI executor's native selector UI" to become an explicit `prompt-learning` product interaction rule, not just a general engineering preference.
5. This work should define the interaction contract first, then decide whether any script payload tightening is actually necessary.

## Objective

Make selector-first interaction the default behavior for choice-based flows in `prompt-learning`:

- prefer the current AI executor's native selector UI whenever a script or workflow already provides structured choices
- allow plain-text numbered menus only when the current executor clearly does not support structured selection
- treat `label`, `description`, and `value` in structured choice payloads as the stable interaction contract
- align `SKILL.md`, reference docs, agent prompt guidance, and eval expectations around the same rule

This work addresses the following problems:

- users may still see plain-text menus in learning, practice, or exam entry flows even though structured choices already exist
- the skill has `question` payloads, but does not yet define a strict consumption rule for them
- current docs mention structured interaction preference, but do not clearly define the native selector UI as the preferred execution path
- there is no stable acceptance criteria for selector-first behavior, so regressions can reintroduce plain-text menus

## Non-Goals

This spec does not include:

- redesigning the overall `prompt-learning` product information architecture
- adding new learning, practice, exam, or Prompt Lab capabilities
- replacing existing script module boundaries or the state model
- introducing new external dependencies or UI frameworks
- implementing code changes at the spec stage

## Scope

This work should cover:

1. Interaction contract definition
- define selector-first as the default interaction rule for eligible choice-based flows
- define the fallback condition for plain-text menus
- define structured choice payloads as the source of truth for selectable labels, descriptions, and values

2. Structured choice coverage review
- review which flows already return `question`
- confirm that home, course selection, practice entry, exam entry, and post-lesson follow-up are covered by the same contract
- decide whether Prompt Lab needs limited structured selection support or should remain primarily open-ended

3. Skill and reference alignment
- update `SKILL.md` to describe selector-first interaction clearly
- align `reference/learning-mode.md` and `reference/exam-mode.md`
- clarify that script-returned `question` payloads are selector data sources rather than presentation templates

4. Agent and evaluation alignment
- update `agents/openai.yaml` if needed so agent guidance reinforces selector-first execution
- update `evals/evals.json` to reduce regression into plain-text menus on key entry surfaces
- define fallback expectations in evaluation language

5. Optional script contract tightening
- evaluate whether `question` payloads need stable identifiers or metadata for better selector mapping
- if changes are needed, keep them minimal and contract-focused
- if changes are not needed, document that the current payload shape is sufficient

## Success Criteria

This spec is complete only when all of the following are true:

1. `prompt-learning` key choice surfaces are explicitly categorized as selector-first.
2. `SKILL.md` explicitly requires selector-first behavior whenever structured choices exist and the executor supports structured selection.
3. Reference docs reinforce the same selector-first rule.
4. `evals/evals.json` includes expectations that make plain-text menu regression less likely on critical entry flows.
5. Fallback behavior is narrowly defined as "the current executor does not support structured selection."
6. The change does not introduce new product modules or extra user-facing complexity.

## Key Interaction Surfaces

This work must cover at least these surfaces:

- platform home navigation
- learning category selection
- learning course selection
- post-lesson follow-up panel
- practice entry selection
- exam entry selection

This work may also review:

- profile follow-up actions
- limited Prompt Lab branching where structured choice is genuinely useful

This work should not force selector interaction onto:

- Prompt Lab slot clarification
- open-ended Q&A
- lesson teaching content
- free-form practice answers

## Risks

1. Updating only `SKILL.md` without updating evals and references may still allow regressions.
2. Making selector-first too rigid may reduce compatibility with executors that do not support structured selection.
3. If script payload contracts remain ambiguous, some environments may still reconstruct them into ad hoc text menus.
4. Over-extending selector-first into Prompt Lab may damage the open-ended teaching flow.

## Open Questions

1. Do all `question` payloads need a stable identifier such as `id`?
2. Should `agents/openai.yaml` explicitly mention selector-first execution behavior?
3. Should Prompt Lab gain limited structured branch selection, or stay primarily open-ended?
4. Should evals assert for structured-choice signals, absence of plain-text menus, or both?

## Project Structure

This work mainly affects:

```text
.opencode/skills/prompt-learning/
  SKILL.md
  agents/openai.yaml
  evals/evals.json
  reference/
    learning-mode.md
    exam-mode.md
    prompt-generation-mode.md
  scripts/
    home.py
    learning.py
    practice.py
    exam.py
    prompt_lab.py

specs/prompt-learning/
  03-selector-first-interaction/
    spec.md
    implementation-plan.md
    task-breakdown.md
```
