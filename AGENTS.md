# AGENTS.md

This repo contains reusable Call of Cthulhu 7e keeper-assistant configuration for GitHub Copilot and Claude Code.

## Shared

- Make the smallest local change that works; if patch context is stale, re-read the exact snippet and retry; treat scratch files as ephemeral unless asked to preserve them.
- For German prose, use standard German orthography by default: write umlauts and `ß` normally instead of ASCII substitutions like `ae`, `oe`, `ue`, or `ss`, unless the user explicitly asks for ASCII or a technical constraint requires it.
- Treat `resources/` as local private input. Do not propose committing, publishing, or quoting long excerpts from those files.
- Treat `coc-db/` as local generated data derived from purchased rulebooks. Do not propose committing or publishing its contents.
- Prefer structured keeper prep outputs over open-ended prose: scenario briefs, NPC rosters, clue chains, timelines, session plans, and adaptation notes.
- Distinguish clearly between scenario facts backed by source material and assistant-created ideas or adaptations.
- If a scenario fact is missing, ambiguous, or not yet ingested from local material, ask for the relevant file, page, or excerpt instead of inventing canon.
- Before extracting information from PDFs, images, and similar binary-heavy sources, check whether `rga` is available and prefer it over manual parsing when present.
- When images or scanned material need OCR and `tesseract` is available, use it.
- Utility scripts, test helpers, and similar repository automation should be written in Python 3 for cross-platform compatibility; avoid new shell-script helpers.
- For repository Python commands, use the project's `uv` environment: run `uv sync` for setup and `uv run python ...` for scripts and tests.
- Rules-heavy work should prefer the local `coc-db/` knowledge store, especially `indexes/`, `topics/`, and `sources/`, after the user has built it from `resources/rules/`.
- If `coc-db/` already contains generated data, ask whether the user wants `--update` to merge new or changed sources while reusing unchanged ones by `gxhash128` content hash or `--rebuild` to replace the store completely.
- Keep shared behavior aligned with `.agents/assistant-spec.md`; keep tool-specific agent files thin.

## Scope

- This project is for Call of Cthulhu 7e preparation workflows based on lawfully obtained scenarios.
- It is not a repository for copyrighted scenario text, scans, or handouts.
