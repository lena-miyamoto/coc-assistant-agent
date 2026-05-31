@AGENTS.md

<!-- Maintainer note: keep this file small and route specialized behavior into dedicated Claude subagents. -->

## Claude Code

- Use the project subagent in `.claude/agents/coc-assistant.md` for Call of Cthulhu 7e keeper prep.
- Keep shared behavior in `.agents/assistant-spec.md` and repository-wide defaults in `AGENTS.md`.
- Use the skill in `.claude/skills/create-coc-skill/SKILL.md` when the user wants to add a new shared repo skill that works in both Copilot and Claude.
- Use the skill in `.claude/skills/create-coc-agent/SKILL.md` when the user wants to add a new paired repo agent for Copilot and Claude.
- Use the skill in `.claude/skills/optimize/SKILL.md` when the user wants to audit and clean up repo customization files for redundancy and consistency.
