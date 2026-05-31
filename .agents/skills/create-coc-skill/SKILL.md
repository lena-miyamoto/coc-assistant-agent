---
name: create-coc-skill
description: 'Create a new shared repo skill for this workspace. The single source of truth lives at .agents/skills/<name>/SKILL.md; no .github or .claude wrappers. Use when adding a skill that must work cleanly in both Copilot and Claude.'
argument-hint: 'Provide the new skill name and what it should do; include description keywords, optional argument hint, and any routing or doc updates needed'
user-invocable: true
---

# Create CoC Skill

Cross-harness source of truth for adding new repo skills. Skills live once under `.agents/skills/`; `.github/skills/` and `.claude/skills/` are not used and are enforced empty by `tests/test_skill_mirrors.py`.

## When to Use

- User wants to add a new skill available through both Copilot and Claude.

## Procedure

1. Clarify the contract:
   - Skill name in lowercase kebab-case.
   - What it accomplishes and when to invoke it.
   - Discovery description, optional argument hint, `user-invocable` value.
   - If the request is really for an agent, stop and route to `create-coc-agent`.
2. Create `.agents/skills/<name>/SKILL.md`:
   - Frontmatter `name` matches the folder name exactly.
   - `description` is keyword-rich and specific enough for discovery.
   - Body is self-contained: `When to Use`, `Procedure`, `Writing Rules` (when needed), `Validation`, `Output`.
3. Adapt to repo conventions:
   - Shared CoC behavior belongs in `.agents/assistant-spec.md`; do not restate it.
   - Copyright and local-only rules defer to `.agents/assistant-spec.md` and `AGENTS.md`.
   - Prefer existing `uv`-based helpers in `.agents/scripts/` and existing templates.
4. Update routing or repo docs only when the new skill changes discoverability:
   - Update `README.md` if the skill should be visible in repo surface docs.
   - Update `CLAUDE.md` or `.github/copilot-instructions.md` only when routing boundaries shift.
   - Skip incidental doc churn for internal-only skills.

## Writing Rules

- ASCII unless the file already needs non-ASCII content.
- Concrete, keyword-rich descriptions.
- Direct procedural tone; no repetition.
- Single source of truth: never spawn a parallel skill body under `.github/` or `.claude/`.

## Validation

1. Only `.agents/skills/<name>/SKILL.md` exists; no `SKILL.md` under `.github/skills/` or `.claude/skills/`.
2. Frontmatter parses cleanly.
3. Markdown diagnostics clean on every changed file.
4. `uv run pytest tests/test_skill_mirrors.py` passes.
5. If repo docs were updated, their references match the created path.

## Output

- Skill file created or updated.
- Repo docs updated, if any.
- Any unresolved ambiguity the user still needs to decide.
