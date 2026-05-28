---
name: import-scenario
description: 'Create a local keeper-facing markdown digest for a Call of Cthulhu scenario from a PDF or a folder of PDFs. Use when the first argument is the source PDF or folder and the second argument is the scenario name.'
argument-hint: 'Provide: <pdf-or-folder> <scenario-name>'
user-invocable: true
---

# Import Scenario

Create a local markdown keeper digest that shortens and structures the scenario for play.

Follow the shared sourcing, extraction, and tooling rules in [assistant spec](../../assistant-spec.md).

## When To Use

- The user gives a local PDF path or a folder containing PDFs for one scenario.
- The user also gives the scenario name to use under `scenarios/`.
- The keeper needs a local structured digest before building briefs, clue maps, rosters, or session plans.

## Preconditions

- The scenario source files must already exist locally.
- The first argument is always the source PDF or folder.
- The second argument is always the scenario name.
- The generated output follows the local-only rules in [assistant spec](../../assistant-spec.md#copyright-and-sourcing-rules).

## Procedure

1. Confirm that the provided source path exists.
2. Apply the extraction defaults from [assistant spec](../../assistant-spec.md#required-behavior).
3. Run `uv run python .agents/scripts/import_scenario.py <pdf-or-folder> <scenario-name>`.
4. Read `scenarios/<scenario-name>/.source-extract.md` as internal staging material.
5. Write `scenarios/<scenario-name>/scenario.md` as the final keeper-facing digest. Do not expose the staging extract as the final deliverable.
6. Match the final document language to the predominant language of the input material unless the user explicitly asks for translation.
7. Confirm that `scenarios/<scenario-name>/scenario.md` was created and contains the standardized keeper digest.
8. Remind the user that `scenarios/` is local-only under the [copyright and sourcing rules](../../assistant-spec.md#copyright-and-sourcing-rules).

## Notes

- Folder inputs are processed recursively in stable path order.
- `scenarios/<scenario-name>/.source-extract.md` is an internal staging artifact, not the keeper-facing result.
- The final `scenario.md` should shorten and restructure the scenario into keeper-facing sections such as premise, investigation flow, locations, NPCs, and clues.
- The final `scenario.md` must use one consistent language that matches the predominant language of the source material unless the user explicitly requests translation.
- This workflow structures local source material for private prep. It is not for redistribution.
