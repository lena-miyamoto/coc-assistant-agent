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
- `.agents/skills/`: canonical shared on-demand workflows and slash-command skills for both GitHub Copilot and Claude Code.
- `.github/agents/`: GitHub Copilot custom agents.
- `.claude/agents/`: Claude Code custom agents.
- `coc-db/`: local-only text-based rules knowledge store built from purchased rulebook files.
- `templates/`: reusable keeper-facing output shapes.
- `tests/`: synthetic fixtures, prompt inputs, and regression checks.
- `resources/`: local-only PDFs, OCR, and working extracts. Ignored by git.

Shared operating rules live in `.agents/assistant-spec.md`. Keep `.github/` and `.claude/` limited to agent-specific wrappers.

## Included scaffolding

- `.agents/scripts/`: Python 3 ingestion helpers for PDF text extraction, OCR, and scenario indexing.
- `.agents/skills/build-rules-db/`: shared skill for bootstrapping the local rules knowledge store.
- `.agents/skills/import-scenario/`: shared skill for turning a local scenario PDF or PDF folder into a keeper-facing markdown extract under `scenarios/`.
- `.agents/skills/lookup-rules-db/`: shared skill for efficient lookup against an already built `coc-db/`.
- `.agents/skills/references/`: shared reference docs used by multiple rules knowledge-store skills.
- `templates/`: keeper-facing templates for scenario briefs, clue maps, NPC rosters, and session plans.
- `tests/fixtures/`: only synthetic or public-domain samples for prompt and workflow tests.
- `tests/`: regression checks that operate only on synthetic or public-domain inputs.

## Local helper scripts

- Repository Python helpers use Python 3 and run through `uv`.
- Run `uv sync` once for setup, then use `uv run ...` for scripts and tests.
- `uv run python .agents/scripts/extract_text.py <path>` extracts text from a local file and prefers `rga` when available.
- `uv run python .agents/scripts/build_scenario_index.py` builds a lightweight TSV index at `.agents/local/scenario-index.tsv`.
- `uv run python .agents/scripts/import_scenario.py <pdf-or-folder> <scenario-name>` extracts the full local scenario text into `scenarios/<scenario-name>/scenario.md`.
- `uv run python .agents/scripts/build_rules_db.py` builds the full-hybrid `coc-db/` knowledge store from the user-provided files in `resources/rules/`.
- If `coc-db/` already contains generated content, ask whether the user wants `--update` or `--rebuild`.
- `uv run pytest` runs the repository test suite.
- `uv run pytest tests/test_import_scenario.py` validates the synthetic scenario-extraction workflow without touching copyrighted inputs.
- `uv run pytest tests/test_scenario_index.py` validates the synthetic fixture and index pipeline without touching copyrighted inputs.
- `uv run pytest tests/test_rules_db.py` validates the synthetic rules-db builder without touching copyrighted rulebooks.

## Mandatory Rules Bootstrap

Before doing rules-heavy work with the assistant, the user must build the private rules knowledge store.

1. Purchase the relevant Call of Cthulhu rulebook PDFs or other lawful local rule sources.
2. Manually copy those files into `resources/rules/`.
3. If `coc-db/` already exists, ask whether the user wants `--update` or `--rebuild`.
4. Run the shared skill `/build-rules-db` or execute `uv run python .agents/scripts/build_rules_db.py` with the chosen mode.
5. Confirm that `coc-db/manifest.json` was created locally.

This knowledge store is local-only and should be the default source for future rules lookup. For the generated layout, see `.agents/skills/references/database-schema.md`.

## Expected workflow

1. Store purchased rulebook PDFs under `resources/rules/` and scenario material under `resources/scenarios/`.
2. Build the local rules knowledge store in `coc-db/` before doing further rules-heavy agent work.
3. When the user provides a scenario PDF or folder plus a scenario name, materialize a local extract under `scenarios/<scenario-name>/scenario.md` before building derivative keeper notes.
4. Use the CoC assistant agent to build keeper prep artifacts from those local sources.
5. Keep generated public repo content limited to prompts, instructions, templates, schemas, and synthetic fixtures.

## Copyright boundary

- `resources/`, `coc-db/`, and `scenarios/` are local-only and must not be committed.
- If the project needs examples or fixtures in version control, use synthetic or public-domain material outside `resources/`.

Shared skills should live once under `.agents/skills/`. If GitHub Copilot or Claude Code need agent-specific behavior around those workflows, keep only the agent-specific layer under `.github/` or `.claude/` and reference shared `.agents/` files instead of duplicating the full skill body.
