---
name: create-coc-skill
description: 'Create a new shared repo skill for this workspace, with the source of truth in .agents/skills and thin .github/.claude wrappers. Use when adding a new skill that must work cleanly in both Copilot and Claude.'
argument-hint: 'Provide the new skill name and what it should do; include description keywords, optional argument hint, and any routing or doc updates needed'
user-invocable: true
---

# Create CoC Skill

This shared skill file is the cross-harness source of truth for creating new repo skills that work in both Copilot and Claude.

## When to Use

- The user wants to add a new skill to this repository.
- The new skill must be available through both Copilot and Claude.
- The new skill should follow this repo's shared-skill convention: one shared skill file plus thin harness wrappers.

## Procedure

1. Clarify the new skill contract before writing files:
   - Confirm the skill name in lowercase kebab-case.
   - Confirm what the skill should accomplish and when it should be used.
   - Capture the discovery description, optional argument hint, and whether `user-invocable` should remain true.
   - If the request is actually for a custom agent rather than a skill, stop and route to `create-coc-agent` instead of guessing.
2. Create the shared source-of-truth file at `.agents/skills/<name>/SKILL.md`:
   - The frontmatter `name` must match the folder name exactly.
   - The `description` must be keyword-rich and specific enough for discovery.
   - Keep the body self-contained for the procedure, writing rules, validation, and output format.
   - Prefer the same section structure used in this repo's shared skills: `When to Use`, `Procedure`, `Writing Rules` when needed, `Validation`, and `Output`.
3. Create the Copilot wrapper at `.github/skills/<name>/SKILL.md`:
   - Keep the same frontmatter discovery fields as the shared skill when practical.
   - Keep the body minimal.
   - Point explicitly to `.agents/skills/<name>/SKILL.md` as the source of truth.
4. Create the Claude wrapper at `.claude/skills/<name>/SKILL.md`:
   - Keep the same `name`, description, and argument hint semantics as the shared skill.
   - Keep the body minimal.
   - Point explicitly to `.agents/skills/<name>/SKILL.md` as the source of truth.
   - Mention `CLAUDE.md`, `AGENTS.md`, and `.agents/assistant-spec.md` only when needed for harness context.
5. Keep stable workflow in shared files, not wrappers:
   - Do not duplicate the procedure across `.agents`, `.github`, and `.claude`.
   - Put long-lived workflow knowledge in `.agents/skills/<name>/SKILL.md`.
   - Keep wrappers limited to discovery and redirection.
6. Adapt the new skill to this repo's keeper-assistant conventions when needed:
   - Shared CoC-specific behavior belongs in `.agents/assistant-spec.md`.
   - Copyright, sourcing, and local-only material rules should defer to `.agents/assistant-spec.md` and `AGENTS.md`, not be copied into wrappers.
   - Prefer existing `uv`-based helpers in `.agents/scripts/` and existing repo templates before inventing parallel tooling.
7. Update routing or repo docs only when the new skill changes discoverability or should be advertised:
   - Update `README.md` when the new skill should be visible in repo surface docs.
   - Update `CLAUDE.md` or `.github/copilot-instructions.md` only when routing boundaries need to mention the new skill.
   - Avoid incidental doc churn when the new skill is internal-only.

## Writing Rules

- Use ASCII unless the file already needs non-ASCII content.
- Keep skill descriptions concrete and keyword-rich.
- Keep wrappers short; the shared file should carry the real workflow.
- Match the repo's existing tone: direct, procedural, and low on repetition.
- Do not invent a second source of truth outside `.agents/skills/<name>/SKILL.md`.

## Validation

1. Confirm the new skill exists in all three locations:
   - `.agents/skills/<name>/SKILL.md`
   - `.github/skills/<name>/SKILL.md`
   - `.claude/skills/<name>/SKILL.md`
2. Confirm frontmatter parses cleanly in all three files.
3. Confirm the shared file contains the substantive procedure and the wrappers do not duplicate it.
4. Confirm the wrapper bodies reference the shared file path exactly.
5. Run markdown diagnostics on every changed instruction file.
6. If repo docs were updated, confirm their references match the created paths.

## Output

- State which skill files were created or updated.
- State whether any repo docs or routing files were updated.
- Call out any unresolved ambiguity that the user still needs to decide.
