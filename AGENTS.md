# AGENTS.md

This repo contains reusable Call of Cthulhu 7e keeper-assistant configuration for GitHub Copilot and Claude Code.

## Shared

- Make the smallest local change that works; if patch context is stale, re-read the exact snippet and retry; treat scratch files as ephemeral unless asked to preserve them.
- For German prose, use standard German orthography by default: write umlauts and `ß` normally instead of ASCII substitutions like `ae`, `oe`, `ue`, or `ss`, unless the user explicitly asks for ASCII or a technical constraint requires it.
- For CoC-specific sourcing, extraction, privacy, repository tooling, and output rules, follow `.agents/assistant-spec.md`.
- Keep shared behavior aligned with `.agents/assistant-spec.md`; keep tool-specific agent files thin.

## Scope

- This project is for Call of Cthulhu 7e preparation workflows based on lawfully obtained scenarios.
- It is not a repository for copyrighted scenario text, scans, or handouts.
