# coc-db Reference

The rules builder writes a local text-based knowledge store to `coc-db/`.

## Top-Level Structure

```text
coc-db/
	manifest.json
	README.md
	indexes/
		chunks.json
		sources.json
		topics.json
	sources/
		<source-slug>/
			full.md
			summary.md
			source.json
			chunks/
				001-<chunk-slug>.md
				002-<chunk-slug>.md
	topics/
		<topic-slug>/
			overview.md
			index.json
			entries/
				<source-slug>--001-<chunk-slug>.md
```

## Machine-Readable Files

- `manifest.json`: build metadata, tool availability, the active source hash algorithm, source count, chunk count, and the generated topic manifest.
- `indexes/sources.json`: one entry per ingested rule source, pointing at its summary and `source.json` metadata.
- `indexes/topics.json`: one entry per populated fixed CoC topic folder.
- `indexes/chunks.json`: flat chunk index for machine traversal across sources and topics.
- `sources/<source-slug>/source.json`: provenance, extractor, `content_hash`, `content_hash_algorithm`, headings, topic counts, and per-chunk pointers.
- `topics/<topic-slug>/index.json`: per-topic lookup index with entry paths back into the duplicated markdown entries.

## Human-Readable Files

- `sources/<source-slug>/full.md`: full extracted text mirror for the ingested source.
- `sources/<source-slug>/summary.md`: concise overview of headings, topic coverage, and preview text.
- `sources/<source-slug>/chunks/*.md`: per-source chunk files with source path, topic assignment, aliases, and content.
- `topics/<topic-slug>/overview.md`: topic summary with source coverage and entry counts.
- `topics/<topic-slug>/entries/*.md`: duplicated chunk markdown organized by topic for cheap local lookup.

## Fixed Topic Taxonomy

- `core-mechanics`
- `investigator-creation`
- `occupations-and-backgrounds`
- `skills-and-rolls`
- `combat-and-chases`
- `sanity-and-horror`
- `magic-spells-and-tomes`
- `creatures-and-mythos`
- `equipment-and-wealth`
- `keeper-guidance`

## Efficient Lookup Order

1. Use `manifest.json` to confirm the store exists and inspect the build metadata.
2. Use `indexes/topics.json` for broad rules categories and `indexes/sources.json` for named-book lookups.
3. Use `indexes/chunks.json` when you already have a keyword, heading, or narrow rule phrase.
4. Open the relevant `topics/<topic>/index.json` or `sources/<source>/source.json` file to identify the exact stored entry.
5. Read the linked `overview.md`, `summary.md`, or the smallest matching chunk markdown file instead of scanning full extracts first.
6. Only fall back to `sources/<source>/full.md` or the original `resources/rules/` input when the chunked views are insufficient.

## Update And Rebuild Behavior

- A fresh build writes into an empty `coc-db/` target.
- `--update` compares `gxhash128` content hashes, reuses unchanged stored sources without reprocessing them, replaces matching slugs when the source changed, and retains older stored sources that are not part of the current input set.
- `--rebuild` replaces the entire generated store and is the way to prune stale or removed sources.
- If `coc-db/` already contains generated data, agents should ask the user whether they want `--update` or `--rebuild` before running either mode.

## Notes

- The builder keeps both source provenance and topic-oriented duplication so future rules lookup does not need to reopen the original PDFs in normal cases.
- `extractor` records whether `rga`, `pdftotext`, `tesseract`, or native text reading provided the text.
