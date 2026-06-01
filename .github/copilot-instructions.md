# Copilot Repository Instructions

This file only covers Copilot-specific routing. Shared repo workflow belongs in `AGENTS.md`, shared keeper-assistant behavior belongs in `.agents/assistant-spec.md`, and shared cross-harness skill procedure belongs in `.agents/skills/`.

## Instruction Boundaries

- Keep only Copilot-specific routing and discovery notes in this file.
- Repo-wide workflow: `AGENTS.md`.
- Shared keeper-assistant behavior: `.agents/assistant-spec.md`.
- Shared skill procedure: `.agents/skills/<name>/SKILL.md` (single source of truth; no `.github/skills` wrappers).
- Repo maintenance skills: `.agents/skills/create-coc-skill/SKILL.md`, `.agents/skills/create-coc-agent/SKILL.md`, `.agents/skills/optimize-repo/SKILL.md`.
- Keep specialized keeper-prep workflow in the dedicated `coc-assistant` agent files, not in `AGENTS.md`.
