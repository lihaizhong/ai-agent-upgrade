# Code of Conduct

Behavioral guidelines for all contributors and AI agents working on this project.

## Core Principles

- **Clarity over cleverness**: Write code that is easy to understand
- **Security first**: Never commit secrets, keys, or sensitive data
- **Consistency**: Follow existing patterns and conventions
- **Documentation**: Keep docs in sync with code changes
- **Testing**: Verify changes work before committing

---

## Code Standards

### Python

- Use **4-space indentation** (defined in `.editorconfig`)
- Target **Python 3.11+**
- Use `uv` for dependency management — never `pip install`
- Run linting with **Ruff** before committing
- Follow PEP 8 naming conventions
- No comments unless they add meaningful context

### General

- 2-space indentation for non-Python files (Markdown, JSON, YAML, etc.)
- UTF-8 encoding, LF line endings
- Trailing whitespace trimming disabled (preserve intentional formatting)
- Final newline not enforced

---

## Git Workflow

### Commits

- Write clear, concise commit messages
- Use imperative mood: "Add feature" not "Added feature"
- One logical change per commit
- Never commit `.env`, `.venv/`, or files matching `.gitignore`

### Branches

- Keep branches focused on a single task
- Delete branches after merging

### Secrets

- **NEVER** commit API keys, tokens, passwords, or credentials
- Use `.env` for local secrets (already gitignored)
- Review diffs for accidental secret exposure before committing

---

## AI Agent Interaction

### When Working with AI Agents

- Be specific and explicit in requests
- Provide context: file paths, expected behavior, constraints
- Review all AI-generated code before accepting
- Run tests and linters on AI-generated changes

### Agent Behavior Expectations

- Ask clarifying questions when instructions are ambiguous
- Follow existing code patterns and project conventions
- Never introduce external dependencies without checking they're already in use
- Stop after completing the task — no unnecessary explanations or summaries
- Keep responses concise (fewer than 4 lines unless detail is requested)
- Never generate or guess URLs unless confident they help with programming

### Interaction & Change Discipline

- Prefer the current AI executor's native selector UI whenever a skill, script, or existing workflow provides structured choices
- Use plain-text numbered menus only as a fallback when the current executor clearly does not support structured selection
- Treat structured choice payloads as the source of truth for `label`, `description`, and `value`; do not rewrite them into ad hoc menu text unless fallback is necessary
- Do not implement UX, interaction flow, or product behavior changes before a spec change exists and plan/tasks have been created or explicitly approved
- If the user is still exploring, discussing, or refining direction, stay in analysis mode and help produce the spec change, plan, and tasks first

### Security Rules for Agents

- Never expose or log secrets and keys
- Never commit credentials to the repository
- Warn the user if asked to commit sensitive files

---

## Project Structure

### Directory Conventions

```
ai-agent-upgrade/
├── .codex/                     # Codex runtime config and skill links
├── agent-skills/              # Repository-owned custom skills, linked into runtime skill dirs
├── .opencode/                 # OpenCode config, agents, and skills
├── docs/                       # Documentation, histories, and architecture notes
├── notebook/                   # Learning notes organized by topic
├── practice/                   # Hands-on projects and experiments
├── prompt-learning-workspace/  # Persistent workspace data for the prompt-learning skill
├── rag-learning-workspace/     # Persistent workspace data for the rag-learning skill
├── labor-rights-defense-workspace/  # Persistent workspace data for the labor-rights-defense skill
├── specs/                      # Spec changes, plans, and tasks
├── tests/                      # Product-level test suites
├── main.py                     # Project entry script
├── README.md                   # Project overview and usage notes
└── AGENTS.md                   # This file — code of conduct
```

### File Naming

- Python: `snake_case.py`
- Markdown: `kebab-case.md`
- Directories: `kebab-case/`

### Adding New Components

- **Skill**: Create directory under `agent-skills/` with `SKILL.md`, then link it into both `.opencode/skills/` and `.codex/skills/`
- **Agent**: Create `.md` file under `.opencode/agents/`
- **Practice project**: Create directory under `practice/`
- Update this file and `README.md` when adding new components

---

## Development Process

### Before Committing

1. Run linting: `ruff check .`
2. Verify the change works as expected
3. Review diff for accidental secrets or debug code
4. Ensure docs are updated if needed

### Dependency Management

```bash
# Add a package
uv add <package-name>

# Sync environment
uv sync

# Run a script
.venv/bin/python <script.py>
```

- **Always use project venv** — run scripts with `uv run python <script.py>` (or `.venv/bin/python` if venv exists). If no venv exists, run `uv sync` to create one first.
- Always use `uv add`, never `pip install`
- Commit `pyproject.toml` and `uv.lock` changes together
- Document new dependencies if they introduce a major capability

### Code Review

- Self-review your changes before committing
- Check that code follows the patterns in neighboring files
- Ensure imports are organized and necessary

---

## Common Bad Habits

### Output directories in wrong locations

Never place tool-generated output directories inside `agent-skills/`. The `agent-skills/` directory is only for custom skill definitions (each with a `SKILL.md`). Output directories like `graphify-out/` belong at the project root.

**Example mistake:** `agent-skills/graphify-out/` — move to `./graphify-out/` instead.

---

## Resources

- [Prompt Engineering Guide](https://www.promptingguide.ai/zh)
- [A Programmer's Guide to English](https://a-programmers-guide-to-english.harryyu.me/)
- Project learning paths: see `prompt-learning` and `rag-learning` skills

## License

Apache License 2.0
