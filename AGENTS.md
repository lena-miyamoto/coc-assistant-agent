# AGENTS.md

This repo contains reusable Call of Cthulhu 7e keeper-assistant configuration for GitHub Copilot and Claude Code.

## Shared

- Make the smallest local change that works; if patch context is stale, re-read the exact snippet and retry; treat scratch files as ephemeral unless asked to preserve them.
- For German prose, use standard German orthography by default: write umlauts and `ß` normally instead of ASCII substitutions like `ae`, `oe`, `ue`, or `ss`, unless the user explicitly asks for ASCII or a technical constraint requires it.
- For CoC-specific sourcing, extraction, privacy, repository tooling, and output rules, follow `.agents/assistant-spec.md`.
- Keep cross-harness skill procedure in `.agents/skills/<name>/SKILL.md`; `.github/skills` and `.claude/skills` should stay as thin wrappers only.
- Keep shared behavior aligned with `.agents/assistant-spec.md`; keep tool-specific agent files thin.

## Scope

- This project is for Call of Cthulhu 7e preparation workflows based on lawfully obtained scenarios.
- It is not a repository for copyrighted scenario text, scans, or handouts.
- Repository-wide onboarding for GitHub Copilot lives in `.github/copilot-instructions.md`.
- Detailed shared-skill creation behavior belongs in `.agents/skills/create-coc-skill/SKILL.md`; harness-specific skill wrappers live in `.github/skills/create-coc-skill/SKILL.md` and `.claude/skills/create-coc-skill/SKILL.md`.
- Detailed paired-agent creation behavior belongs in `.agents/skills/create-coc-agent/SKILL.md`; harness-specific skill wrappers live in `.github/skills/create-coc-agent/SKILL.md` and `.claude/skills/create-coc-agent/SKILL.md`.
- Detailed instruction cleanup behavior belongs in `.agents/skills/optimize/SKILL.md`; harness-specific skill wrappers live in `.github/skills/optimize/SKILL.md` and `.claude/skills/optimize/SKILL.md`.
