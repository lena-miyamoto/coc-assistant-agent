---
name: import-scenario
description: 'Create a local keeper-facing markdown digest for a Call of Cthulhu scenario from a PDF or a folder of PDFs. Use when the first argument is the source PDF or folder and the second argument is the scenario name.'
argument-hint: 'Provide: <pdf-or-folder> <scenario-name>'
user-invocable: true
---

# Import Scenario

Create a local keeper-facing scenario package that shortens and structures the scenario for play.

Follow the shared sourcing, extraction, and tooling rules in [assistant spec](../../assistant-spec.md).

## When To Use

- The user gives a local PDF path or a folder containing PDFs for one scenario.
- The user also gives the scenario name to use under `scenarios/`.
- The keeper needs a local structured scenario package before building further prep artifacts.

## Preconditions

- The scenario source files must already exist locally.
- The first argument is always the source PDF or folder.
- The second argument is always the scenario name.
- The generated output follows the local-only rules in [assistant spec](../../assistant-spec.md).

## Procedure

1. Confirm that the provided source path exists.
2. Apply the extraction defaults from [assistant spec](../../assistant-spec.md).
3. Run `uv run python .agents/scripts/import_scenario.py <pdf-or-folder> <scenario-name>`.
4. Read `scenarios/<scenario-name>/.source-extract.md` as internal staging material.
5. Write `scenarios/<scenario-name>/npcs-and-enemies.md` as a complete standalone index of all NPCs and enemies in the scenario.
6. Write `scenarios/<scenario-name>/story-overview.md` as a concise full-plot overview covering the major beats, twists, branches, and endings. Keep it under 500 lines.
7. Write `scenarios/<scenario-name>/keeper-notes.md` as the main keeper document covering the scenario from start to finish. Keep character explanations out of this file and refer to `npcs-and-enemies.md` instead.
8. Match all three final documents to the predominant language of the input material unless the user explicitly asks for translation.
9. Perform a final lossless-coverage validation pass against `scenarios/<scenario-name>/.source-extract.md` and confirm that no important scenario information was dropped from the three final files.
10. If essential information is missing, revise the final files before finishing.
11. Confirm that all three final files were created, passed the coverage check, and contain the standardized keeper-facing output.
12. Remind the user that `scenarios/` is local-only under the [assistant spec](../../assistant-spec.md).

## Notes

- Folder inputs are processed recursively in stable path order.
- `scenarios/<scenario-name>/.source-extract.md` is an internal staging artifact, not the keeper-facing result.
- `npcs-and-enemies.md` should include every NPC and enemy that appears in the scenario, summarize them without dropping important details, and include stat tables only when the source actually provides stats.
- `npcs-and-enemies.md` must stand on its own and must not rely on `keeper-notes.md` to explain who a character or enemy is.
- `story-overview.md` should cover the full plot, including twists, alternate paths, and endings, while staying brief enough for a fast keeper read.
- `keeper-notes.md` should focus on scenes, reveals, clue flow, and player-facing action from start to finish, while referring to `npcs-and-enemies.md` instead of repeating character dossiers.
- The reference direction is one-way: `keeper-notes.md` may point to `npcs-and-enemies.md`, but `npcs-and-enemies.md` should not point back to `keeper-notes.md` for core character detail.
- All final output files must use one consistent language that matches the predominant language of the source material unless the user explicitly requests translation.
- The workflow must end with an explicit coverage check against `.source-extract.md`; if important facts, clues, endings, NPCs, enemies, or stats from the source are missing from the final package, the agent must revise the files before finishing.
- This workflow structures local source material for private prep. It is not for redistribution.
