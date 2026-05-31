---
name: optimize
description: 'Optimize this repo\'s instruction, skill, and agent files by removing unnecessary redundancy, restoring clear source-of-truth ownership, and keeping Copilot and Claude surfaces aligned. Use when cleaning up customization files in this workspace.'
argument-hint: 'Provide the scope to optimize and whether to report only or apply fixes directly'
user-invocable: true
---

# Optimize

Harness wrapper for the shared skill instructions in `.agents/skills/optimize/SKILL.md`.

Use the shared skill file as the source of truth for procedure, writing rules, and validation. Keep this wrapper minimal so Copilot and Claude stay synchronized.
