@AGENTS.md

<!-- Maintainer note: keep this file small and route specialized behavior into dedicated Claude subagents. -->

## Claude Code

- Use the project subagent in `.claude/agents/coc-assistant.md` for Call of Cthulhu 7e keeper prep.
- Keep shared behavior in `.agents/assistant-spec.md` and repository-wide defaults in `AGENTS.md`.
- Use `.agents/skills/create-coc-skill/SKILL.md` when adding a new shared repo skill.
- Use `.agents/skills/create-coc-agent/SKILL.md` when adding a new paired repo agent for Copilot and Claude.
- Use `.agents/skills/optimize/SKILL.md` when auditing or cleaning up repo customization files.
