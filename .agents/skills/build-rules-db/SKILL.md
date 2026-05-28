---
name: build-rules-db
description: 'Build the local Call of Cthulhu rules knowledge store in coc-db/ from purchased rule PDFs or extracts copied into resources/rules/. Use when bootstrapping a new workspace, rebuilding the private rules store, or preparing for future rules lookup.'
argument-hint: 'Optional: provide an alternate source directory or output directory; defaults are resources/rules/ and coc-db/.'
user-invocable: true
---

# Build Rules Knowledge Store

Build the local machine-readable rules knowledge store from the user's privately supplied rulebook files.

Follow the shared sourcing, extraction, and tooling rules in [assistant spec](../../assistant-spec.md).

## When To Use

- The user has copied purchased rulebook PDFs, text extracts, or scans into `resources/rules/`.
- The workspace is being bootstrapped for rules-heavy work.
- The local `coc-db/manifest.json` store manifest is missing or stale.

## Preconditions

- The user must already own the relevant rule PDFs or lawful local rule sources.
- The source files must already exist under `resources/rules/`.
- Do not attempt rules-heavy preparation until this knowledge store has been built.

## Procedure

1. Confirm that `resources/rules/` exists and contains source files.
2. Apply the extraction defaults from [assistant spec](../../assistant-spec.md#required-behavior).
3. If `coc-db/` already contains generated data, ask whether the user wants an in-place update or a full rebuild.
4. Run `uv run python .agents/scripts/build_rules_db.py` for a fresh build, `uv run python .agents/scripts/build_rules_db.py --update` to merge new or changed sources into the existing store, or `uv run python .agents/scripts/build_rules_db.py --rebuild` to replace the store completely.
5. Confirm that `coc-db/manifest.json`, `coc-db/indexes/`, `coc-db/sources/`, and `coc-db/topics/` were created.
6. Remind the user that `coc-db/` is local-only under the [copyright and sourcing rules](../../assistant-spec.md#copyright-and-sourcing-rules).

## Notes

- The resulting knowledge store is intended for future local lookup by the agent.
- This workflow should summarize and structure local source material, not redistribute it.
- The generated taxonomy uses fixed top-level CoC topic folders and keeps full source provenance alongside topic entry copies.
- `--update` compares `gxhash128` content hashes, reuses unchanged stored sources without reprocessing them, refreshes changed or newly supplied slugs, and keeps older stored sources that are not part of the current input set.
- Use `--rebuild` when the user wants a clean replacement that also prunes stale or removed sources.
- Shared coc-db reference: [database schema](../references/database-schema.md)

