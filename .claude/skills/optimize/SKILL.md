---
name: optimize
description: Use when you need to optimize this repo's instruction, skill, and agent files by removing unnecessary redundancy, restoring clear source-of-truth ownership, and keeping Copilot and Claude surfaces aligned.
argument-hint: Provide the scope to optimize and whether to report only or apply fixes directly
user-invocable: true
---

# Optimize

Harness wrapper for the shared skill instructions in `.agents/skills/optimize/SKILL.md`.

Follow `CLAUDE.md`, `AGENTS.md`, and `.agents/assistant-spec.md`, then load the shared skill file for the full procedure, writing rules, and validation. Keep this wrapper minimal so Copilot and Claude stay synchronized.
