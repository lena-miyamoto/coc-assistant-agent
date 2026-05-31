---
name: create-coc-skill
description: 'Create a new shared repo skill for this workspace, with the source of truth in .agents/skills and thin .github/.claude wrappers. Use when adding a new skill that must work cleanly in both Copilot and Claude.'
argument-hint: 'Provide the new skill name and what it should do; include description keywords, optional argument hint, and any routing or doc updates needed'
user-invocable: true
---

# Create CoC Skill

Harness wrapper for the shared skill instructions in `.agents/skills/create-coc-skill/SKILL.md`.

Use the shared skill file as the source of truth for procedure, writing rules, and validation. Keep this wrapper minimal so Copilot and Claude stay synchronized.
