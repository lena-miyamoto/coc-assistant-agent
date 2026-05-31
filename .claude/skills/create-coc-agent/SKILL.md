---
name: create-coc-agent
description: Use when you need to create a new repo agent for this workspace, with paired .github and .claude agent files that stay aligned while keeping shared workflow in .agents/assistant-spec.md, AGENTS.md, and shared skills.
argument-hint: Provide the new agent name, role, trigger description, tool scope, and whether it should be user-invocable or subagent-only
user-invocable: true
---

# Create CoC Agent

Harness wrapper for the shared skill instructions in `.agents/skills/create-coc-agent/SKILL.md`.

Follow `CLAUDE.md`, `AGENTS.md`, and `.agents/assistant-spec.md`, then load the shared skill file for the full procedure, writing rules, and validation. Keep this wrapper minimal so Copilot and Claude stay synchronized.
