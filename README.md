# coc-assistant-agent

Local agent configuration for preparing Call of Cthulhu 7th Edition one-shots and campaigns from lawfully obtained scenario material.

## Goals

- Define reusable agent behavior for both GitHub Copilot and Claude Code.
- Help a keeper turn scenario source material into concise prep artifacts.
- Keep copyrighted PDFs and derived local extracts out of the public repository.

## Non-goals

- Redistributing purchased scenarios, handouts, or long verbatim excerpts.
- Treating assistant output as canon when the local source material says otherwise.
- Building a generic RPG assistant with no CoC-specific workflow.

## Repository layout

- `.agents/`: shared keeper-assistant spec and local helper scripts used by both agent implementations.
- `.agents/skills/`: shared on-demand workflows and slash-command skills.
- `.github/agents/`: GitHub Copilot custom agents.
- `.claude/agents/`: Claude Code custom agents.
- `coc-db/`: local-only text-based rules knowledge store built from purchased rulebook files.
- `templates/`: reusable keeper-facing output shapes.
- `tests/`: synthetic fixtures, prompt inputs, and regression checks.
- `resources/`: local-only PDFs, OCR, and working extracts. Ignored by git.

## Included scaffolding

- `.agents/scripts/`: Python 3 ingestion helpers for PDF text extraction, OCR, and scenario indexing.
- `.agents/skills/build-rules-db/`: shared skill for bootstrapping the local rules knowledge store.
- `.agents/skills/lookup-rules-db/`: shared skill for efficient lookup against an already built `coc-db/`.
- `.agents/skills/references/`: shared reference docs used by multiple rules knowledge-store skills.
- `templates/`: keeper-facing templates for scenario briefs, clue maps, NPC rosters, and session plans.
- `tests/fixtures/`: only synthetic or public-domain samples for prompt and workflow tests.
- `tests/`: regression checks that operate only on synthetic or public-domain inputs.

## Local helper scripts

- Utility and regression scripts in this repo should be implemented in Python 3 for cross-platform use, including Windows.
- This repo uses `uv` for Python environment and dependency management. Run `uv sync` before running repository scripts or tests.
- `uv run python .agents/scripts/extract_text.py <path>` extracts text from a local file and prefers `rga` when available.
- `uv run python .agents/scripts/build_scenario_index.py` builds a lightweight TSV index at `.agents/local/scenario-index.tsv`.
- `uv run python .agents/scripts/build_rules_db.py` builds the full-hybrid `coc-db/` knowledge store from the user-provided files in `resources/rules/`.
- If `coc-db/` already contains generated content, ask whether the user wants `--update` to merge new or changed sources while reusing unchanged ones by `gxhash128` content hash or `--rebuild` to replace the store completely.
- `uv run pytest` runs the repository test suite.
- `uv run pytest tests/test_scenario_index.py` validates the synthetic fixture and index pipeline without touching copyrighted inputs.
- `uv run pytest tests/test_rules_db.py` validates the synthetic rules-db builder without touching copyrighted rulebooks.

## Mandatory Rules Bootstrap

Before doing rules-heavy work with the assistant, the user must build the private rules knowledge store.

1. Purchase the relevant Call of Cthulhu rulebook PDFs or other lawful local rule sources.
2. Manually copy those files into `resources/rules/`.
3. If `coc-db/` already exists, ask whether the user wants an in-place update or a full rebuild. The current helper supports explicit merges via `uv run python .agents/scripts/build_rules_db.py --update`, which skips unchanged sources by `gxhash128` content hash, and clean replacements via `uv run python .agents/scripts/build_rules_db.py --rebuild`.
4. Run the shared skill `/build-rules-db` or execute `uv run python .agents/scripts/build_rules_db.py` with the chosen mode.
5. Confirm that `coc-db/manifest.json` was created locally.

This knowledge store is intentionally local-only and must not be committed. Agents should prefer it for future rules lookup once it exists.

The generated `coc-db/` layout exposes `manifest.json`, JSON indexes under `indexes/`, per-source provenance under `sources/`, and a fixed CoC topic taxonomy under `topics/`.

If the inputs are scans or image-heavy pages, the workflow should prefer `rga` first and use `tesseract` for OCR when that makes sense.

## Expected workflow

1. Store purchased rulebook PDFs under `resources/rules/` and scenario material under `resources/scenarios/`.
2. Build the local rules knowledge store in `coc-db/` before doing further rules-heavy agent work.
3. Use the CoC assistant agent to build keeper prep artifacts from those local sources.
4. Keep generated public repo content limited to prompts, instructions, templates, schemas, and synthetic fixtures.

## Copyright boundary

Anything under `resources/` is local working material and must not be committed. If the project needs test cases or examples, add synthetic or public-domain material outside `resources/`.

Anything under `coc-db/` is derived local database content and must not be committed either.
