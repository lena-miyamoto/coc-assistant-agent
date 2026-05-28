---
name: lookup-rules-db
description: 'Look up Call of Cthulhu rules efficiently from the local coc-db/ knowledge store after it has been built. Use when answering rules questions, finding the right topic/source chunk, or tracing rules back to source-backed entries.'
argument-hint: 'Optional: describe the rule topic, keyword, or source to inspect inside coc-db/.'
user-invocable: true
---

# Look Up Rules Knowledge Store

Use the local `coc-db/` knowledge store to answer rules-heavy questions without reopening the original PDFs.

## When To Use

- The user asks a rules question and `coc-db/manifest.json` already exists.
- The agent needs to find the right rule topic, source chunk, or provenance trail quickly.
- A previous rules answer needs to be checked against the stored source-oriented or topic-oriented entries.

## Preconditions

- The local rules knowledge store must already exist under `coc-db/`.
- If it is missing or stale, use `/build-rules-db` first instead of guessing, and choose `--update` or `--rebuild` according to whether the user wants a merge or a clean replacement. Repository Python tooling should run through the project's `uv` environment.
- Treat `coc-db/` as private derived content and do not propose committing or publishing it.

## Procedure

1. Confirm that `coc-db/manifest.json` exists.
2. Start with the smallest relevant index:
   - `coc-db/indexes/topics.json` for topic-first lookup.
   - `coc-db/indexes/sources.json` for source-first lookup.
   - `coc-db/indexes/chunks.json` for keyword or chunk-level traversal.
3. Open the matching `topics/<topic>/index.json` or `sources/<source>/source.json` entry.
4. Read only the linked `overview.md`, `summary.md`, or specific chunk/entry markdown files needed to answer the question.
5. Return a concise answer that distinguishes source-backed rules from inference, and cite the local source path or stored chunk path when available.
6. If the knowledge store does not contain enough detail, ask for the original local rule source instead of inventing canon.

## Notes

- Prefer topic-first lookup for broad questions such as sanity, combat, or skills.
- Prefer source-first lookup when the user names a specific book, chapter, or excerpt.
- Keep quotes short; summaries and structured notes are preferred.
- PDF-derived source titles in `coc-db/` intentionally fall back to the local filename when extracted front matter is noisier than the document title.
- Shared coc-db reference: [database schema](../references/database-schema.md)
