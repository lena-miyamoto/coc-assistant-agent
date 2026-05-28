#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

from extract_text import available_extractors, extract_text

try:
  from gxhash.hashlib import gxhash128
except ImportError:
  gxhash128 = None

HEADING_PREFIX = re.compile(r"^#{1,6}\s*")
SECOND_LEVEL_HEADING = re.compile(r"^##\s+")
SLUG_BREAKS = re.compile(r"[^a-z0-9]+")
FILENAME_BREAKS = re.compile(r"[_\-\s]+")
PAGE_PREFIX = re.compile(r"^\s*Page\s+\d+:\s*")
PAGE_ONLY_LINE = re.compile(r"^\s*Page\s+\d+:?\s*$", re.IGNORECASE)
GENERIC_SOURCE_TITLES = {
  "impressum",
  "inhalt",
  "inhalt / vorwort",
  "vorwort",
  "widmungen",
}
TARGET_CHUNK_CHARS = 1200
SOFT_BREAK_CHARS = 800
HASH_ALGORITHM = "gxhash128"
PROCESSING_VERSION = "coc-db-processing-v3"

TOPICS = [
  {
    "slug": "core-mechanics",
    "title": "Core Mechanics",
    "description": "Core percentile resolution, difficulty levels, luck, bonus and penalty dice, and general adjudication.",
    "keywords": ["percentile", "bonus die", "penalty die", "difficulty level", "hard success", "extreme success", "luck", "pushed roll", "opposed roll"],
  },
  {
    "slug": "investigator-creation",
    "title": "Investigator Creation",
    "description": "Characteristics, backstory, age, derived stats, and creating investigators.",
    "keywords": ["investigator creation", "characteristic", "backstory", "derived attribute", "hit points", "magic points", "build"],
  },
  {
    "slug": "occupations-and-backgrounds",
    "title": "Occupations And Backgrounds",
    "description": "Occupations, credit rating, contacts, and profession-specific setup.",
    "keywords": ["occupation", "credit rating", "profession", "background", "contacts", "personal interest"],
  },
  {
    "slug": "skills-and-rolls",
    "title": "Skills And Rolls",
    "description": "Skill checks, improvement, pushed rolls, and related adjudication.",
    "keywords": ["skill", "skill check", "improvement check", "bonus dice", "penalty dice", "hidden roll"],
  },
  {
    "slug": "combat-and-chases",
    "title": "Combat And Chases",
    "description": "Combat rounds, attacks, damage, firearms, maneuvers, armor, and chases.",
    "keywords": ["combat", "attack", "damage", "firearm", "fight", "dodge", "armor", "initiative", "chase", "maneuver", "hit points"],
  },
  {
    "slug": "sanity-and-horror",
    "title": "Sanity And Horror",
    "description": "Sanity loss, temporary insanity, long-term effects, and horror consequences.",
    "keywords": ["sanity", "insanity", "madness", "phobia", "mania", "delusion", "hallucination", "horror", "unnatural", "sanity loss"],
  },
  {
    "slug": "magic-spells-and-tomes",
    "title": "Magic, Spells, And Tomes",
    "description": "Magic points, spells, rituals, tomes, artifacts, and occult study.",
    "keywords": ["spell", "ritual", "magic point", "tome", "grimoire", "artifact", "enchant", "occult"],
  },
  {
    "slug": "creatures-and-mythos",
    "title": "Creatures And Mythos",
    "description": "Mythos entities, cults, monsters, deities, and unnatural threats.",
    "keywords": ["mythos", "monster", "creature", "entity", "cult", "great old one", "outer god", "deity", "byakhee"],
  },
  {
    "slug": "equipment-and-wealth",
    "title": "Equipment And Wealth",
    "description": "Gear, weapons, vehicles, prices, cash, and logistical resources.",
    "keywords": ["equipment", "gear", "weapon", "vehicle", "price", "cost", "cash", "wealth", "item"],
  },
  {
    "slug": "keeper-guidance",
    "title": "Keeper Guidance",
    "description": "Advice for running games, investigations, clues, pacing, and adjudication.",
    "keywords": ["keeper", "advice", "investigation", "clue", "pacing", "scene", "running the game", "guidance"],
  },
]

TOPIC_BY_SLUG = {topic["slug"]: topic for topic in TOPICS}
TOPIC_ORDER = {topic["slug"]: index for index, topic in enumerate(TOPICS)}


def normalize_text(value: str) -> str:
  return " ".join(value.replace("\t", " ").replace("\r", " ").split())


def strip_heading_prefix(value: str) -> str:
  return HEADING_PREFIX.sub("", value).strip()


def slugify(value: str, default: str = "item") -> str:
  normalized = SLUG_BREAKS.sub("-", value.lower()).strip("-")
  return normalized or default


def humanize_filename(source_path: Path) -> str:
  tokens = [token for token in FILENAME_BREAKS.split(source_path.stem) if token]
  if not tokens:
    return source_path.stem

  formatted_tokens: list[str] = []
  for token in tokens:
    if token.isupper() or token.isdigit():
      formatted_tokens.append(token)
      continue
    formatted_tokens.append(token[:1].upper() + token[1:])
  return " ".join(formatted_tokens)


def display_path(path: Path) -> str:
  try:
    return path.relative_to(Path.cwd()).as_posix()
  except ValueError:
    return path.as_posix()


def compute_content_hash(source_path: Path) -> str:
  if gxhash128 is None:
    raise RuntimeError(
      "gxhash is required to build coc-db. Run `uv sync` in the project root before running build_rules_db.py."
    )
  return gxhash128(data=source_path.read_bytes()).hexdigest()


def read_manifest_hash(source_manifest: dict[str, object]) -> tuple[str, str]:
  content_hash = source_manifest.get("content_hash")
  if content_hash is not None:
    return str(content_hash), str(source_manifest.get("content_hash_algorithm", "unknown"))

  legacy_hash = source_manifest.get("sha256")
  if legacy_hash is not None:
    return str(legacy_hash), "sha256"

  raise KeyError("source manifest is missing content hash metadata")


def read_json(path: Path) -> object:
  return json.loads(path.read_text(encoding="utf-8"))


def normalize_extracted_text(source_path: Path, extracted_text: str) -> str:
  if source_path.suffix.lower() != ".pdf":
    return extracted_text

  normalized_lines: list[str] = []
  previous_blank = True
  for raw_line in extracted_text.splitlines():
    line = PAGE_PREFIX.sub("", raw_line).strip()
    if not line or PAGE_ONLY_LINE.fullmatch(raw_line) or line.isdigit():
      if not previous_blank:
        normalized_lines.append("")
      previous_blank = True
      continue

    normalized_lines.append(line)
    previous_blank = False

  return "\n".join(normalized_lines).strip()


def is_generic_title(value: str) -> bool:
  normalized = normalize_text(value).lower().strip(":")
  if not normalized:
    return True
  if normalized in GENERIC_SOURCE_TITLES:
    return True
  return normalized.startswith("page ")


def derive_source_title(source_path: Path, extracted_text: str) -> str:
  if source_path.suffix.lower() == ".pdf":
    return humanize_filename(source_path)

  for raw_line in extracted_text.splitlines():
    candidate = strip_heading_prefix(raw_line.strip())
    if not candidate:
      continue
    if is_generic_title(candidate):
      continue
    return candidate
  return humanize_filename(source_path)


def derive_chunk_title(heading: str | None, source_title: str, content: str) -> str:
  if heading and not is_generic_title(heading):
    return heading

  words = normalize_text(content).split()
  if words:
    snippet = " ".join(words[:10])
    if len(words) > 10:
      snippet += "..."
    return snippet

  return source_title


def source_record_from_manifest(source_manifest: dict[str, object], source_state: str) -> dict[str, object]:
  content_hash, content_hash_algorithm = read_manifest_hash(source_manifest)
  chunk_records: list[dict[str, object]] = []
  for chunk in source_manifest["chunks"]:
    topic_aliases = list(chunk.get("topic_aliases", []))
    chunk_records.append(
      {
        "chunk_id": chunk["chunk_id"],
        "title": chunk["title"],
        "heading": chunk.get("heading"),
        "char_count": chunk["char_count"],
        "start_line": chunk["start_line"],
        "end_line": chunk["end_line"],
        "topic_slug": chunk["topic_slug"],
        "topic_title": TOPIC_BY_SLUG[str(chunk["topic_slug"])] ["title"],
        "topic_aliases": topic_aliases,
        "topic_alias_titles": [TOPIC_BY_SLUG[slug]["title"] for slug in topic_aliases if slug in TOPIC_BY_SLUG],
        "source_slug": source_manifest["source_slug"],
        "source_title": source_manifest["title"],
        "source_path": source_manifest["source_path"],
        "source_relative_path": source_manifest["relative_source_path"],
        "extractor": source_manifest["extractor"],
        "source_chunk_path": chunk["source_chunk_path"],
        "topic_entry_path": chunk["topic_entry_path"],
        "reuse_existing": True,
      }
    )

  return {
    "source_slug": source_manifest["source_slug"],
    "source_path": source_manifest["source_path"],
    "relative_source_path": source_manifest["relative_source_path"],
    "filename": source_manifest["filename"],
    "title": source_manifest["title"],
    "extractor": source_manifest["extractor"],
    "built_at": source_manifest["built_at"],
    "content_hash": content_hash,
    "content_hash_algorithm": content_hash_algorithm,
    "char_count": source_manifest["char_count"],
    "line_count": source_manifest["line_count"],
    "headings": source_manifest["headings"],
    "chunks": chunk_records,
    "topic_counts": dict(source_manifest["topic_counts"]),
    "reuse_existing": True,
    "source_state": source_state,
    "processing_version": source_manifest.get("processing_version", "unknown"),
  }


def load_existing_source_manifests(output_dir: Path) -> dict[str, dict[str, object]]:
  manifest_path = output_dir / "manifest.json"
  sources_root = output_dir / "sources"

  if not manifest_path.is_file() or not sources_root.is_dir():
    raise ValueError(
      f"Cannot update {display_path(output_dir)} because it does not contain a complete coc-db store. Use --rebuild instead."
    )

  manifests: dict[str, dict[str, object]] = {}
  for source_root in sorted(path for path in sources_root.iterdir() if path.is_dir()):
    source_manifest_path = source_root / "source.json"
    if not source_manifest_path.is_file():
      continue
    source_manifest = read_json(source_manifest_path)
    manifests[str(source_manifest["source_slug"])] = source_manifest
  return manifests


def parse_args(argv: list[str]) -> tuple[Path, Path, str | None]:
  positional: list[str] = []
  mode: str | None = None

  for argument in argv[1:]:
    if argument in {"--rebuild", "--update"}:
      next_mode = argument.removeprefix("--")
      if mode is not None and mode != next_mode:
        raise ValueError("Use either --update or --rebuild, not both.")
      mode = next_mode
      continue
    positional.append(argument)

  if len(positional) > 2:
    raise ValueError("Usage: uv run python .agents/scripts/build_rules_db.py [source-dir] [output-dir] [--update | --rebuild]")

  source_dir = Path(positional[0]) if positional else Path("resources/rules")
  output_dir = Path(positional[1]) if len(positional) > 1 else Path("coc-db")
  return source_dir, output_dir, mode


def clear_output_dir(output_dir: Path) -> None:
  for child in output_dir.iterdir():
    if child.name == ".gitignore":
      continue
    if child.is_dir():
      shutil.rmtree(child)
    else:
      child.unlink()


def existing_generated_content(output_dir: Path) -> list[Path]:
  if not output_dir.exists():
    return []
  return [child for child in output_dir.iterdir() if child.name != ".gitignore"]


def load_existing_source_records(existing_manifests: dict[str, dict[str, object]], replaced_slugs: set[str]) -> list[dict[str, object]]:
  retained_records: list[dict[str, object]] = []
  for source_slug, source_manifest in sorted(existing_manifests.items()):
    if source_slug in replaced_slugs:
      continue
    retained_records.append(source_record_from_manifest(source_manifest, "retained"))

  return retained_records


def build_chunks(text: str) -> list[dict[str, int | str | None]]:
  chunks: list[dict[str, int | str | None]] = []
  heading: str | None = None
  buffer: list[str] = []
  start_line: int | None = None
  lines = text.splitlines()

  def flush(end_line: int) -> None:
    nonlocal buffer, start_line
    content = normalize_text(" ".join(buffer))
    if not content:
      buffer = []
      start_line = None
      return
    chunks.append(
      {
        "heading": heading,
        "start_line": start_line or 1,
        "end_line": end_line,
        "content": content,
        "char_count": len(content),
      }
    )
    buffer = []
    start_line = None

  for line_number, raw_line in enumerate(lines, start=1):
    line = raw_line.strip()

    if not line:
      if buffer and len(" ".join(buffer)) >= SOFT_BREAK_CHARS:
        flush(line_number - 1)
      continue

    if SECOND_LEVEL_HEADING.match(line) or (line.startswith("#") and HEADING_PREFIX.match(line)):
      if buffer:
        flush(line_number - 1)
      heading = strip_heading_prefix(line)
      continue

    if start_line is None:
      start_line = line_number

    buffer.append(line)
    if len(" ".join(buffer)) >= TARGET_CHUNK_CHARS:
      flush(line_number)

  if buffer:
    flush(len(lines))

  if chunks:
    return chunks

  normalized_text = normalize_text(text)
  if not normalized_text:
    return []

  return [
    {
      "heading": None,
      "start_line": 1,
      "end_line": max(len(lines), 1),
      "content": normalized_text,
      "char_count": len(normalized_text),
    }
  ]


def classify_topics(heading: str | None, content: str) -> tuple[str, list[str], dict[str, int]]:
  haystack = normalize_text(f"{heading or ''} {content}").lower()
  scores: dict[str, int] = {}

  for topic in TOPICS:
    score = 0
    for keyword in topic["keywords"]:
      if keyword in haystack:
        score += 1
    if score:
      scores[topic["slug"]] = score

  if not scores:
    return "keeper-guidance", [], {}

  ordered = sorted(scores.items(), key=lambda item: (-item[1], TOPIC_ORDER[item[0]], item[0]))
  primary = ordered[0][0]
  aliases = [slug for slug, score in ordered[1:] if score == ordered[0][1] or score > 1]
  return primary, aliases, scores


def render_chunk_markdown(chunk: dict[str, object]) -> str:
  lines = [f"# {chunk['heading'] or chunk['title']}", ""]
  lines.extend(
    [
      f"- Source: {chunk['source_path']}",
      f"- Topic: {chunk['topic_title']}",
      f"- Aliases: {', '.join(chunk['topic_alias_titles']) if chunk['topic_alias_titles'] else 'None'}",
      f"- Lines: {chunk['start_line']}-{chunk['end_line']}",
      f"- Extractor: {chunk['extractor']}",
      "",
      str(chunk["content"]),
      "",
    ]
  )
  return "\n".join(lines)


def render_source_summary(source_record: dict[str, object]) -> str:
  topic_counts = source_record["topic_counts"]
  topic_lines = [f"- {TOPIC_BY_SLUG[slug]['title']}: {count}" for slug, count in sorted(topic_counts.items())]
  headings = source_record["headings"]
  lines = [f"# {source_record['title']}", "", f"- Source path: {source_record['source_path']}", f"- Extractor: {source_record['extractor']}", f"- Built at: {source_record['built_at']}", "", "## Topic Coverage", ""]
  lines.extend(topic_lines or ["- Keeper Guidance: 1"])
  lines.extend(["", "## Headings", ""])
  lines.extend([f"- {heading}" for heading in headings] or ["- No headings detected"])
  lines.extend(["", "## Preview", "", str(source_record["preview"]), ""])
  return "\n".join(lines)


def render_full_extract(source_record: dict[str, object]) -> str:
  return "\n".join(
    [
      f"# Full Extract: {source_record['title']}",
      "",
      f"- Source path: {source_record['source_path']}",
      f"- Extractor: {source_record['extractor']}",
      f"- Built at: {source_record['built_at']}",
      "",
      str(source_record["content"]),
      "",
    ]
  )


def render_topic_overview(topic: dict[str, str], entries: list[dict[str, object]]) -> str:
  unique_sources = sorted({entry["source_title"] for entry in entries})
  lines = [f"# {topic['title']}", "", topic["description"], "", f"- Entries: {len(entries)}", f"- Sources: {len(unique_sources)}", "", "## Sources", ""]
  lines.extend([f"- {source_title}" for source_title in unique_sources])
  lines.extend(["", "## Entries", ""])
  lines.extend([f"- {entry['title']} ({entry['source_title']})" for entry in entries])
  lines.append("")
  return "\n".join(lines)


def render_db_readme(manifest: dict[str, object]) -> str:
  topic_lines = [f"- {topic['title']}: {topic['chunk_count']} chunks" for topic in manifest["topics"]]
  return "\n".join(
    [
      "# coc-db",
      "",
      "Local full-hybrid rules knowledge store built from purchased rulebook files.",
      "",
      f"Built at: {manifest['built_at']}",
      f"Build mode: {manifest['build_mode']}",
      f"Source directory: {manifest['source_dir']}",
      f"Sources archived: {manifest['source_count']}",
      f"Chunks archived: {manifest['chunk_count']}",
      f"Updated sources this run: {manifest['updated_source_count']}",
      f"Unchanged sources reused: {manifest['unchanged_source_count']}",
      f"Retained sources from previous runs: {manifest['retained_source_count']}",
      "",
      "## Structure",
      "",
      "- `sources/`: per-source provenance, full extracts, summaries, and chunk files",
      "- `topics/`: fixed CoC taxonomy with duplicated lookup entries",
      "- `indexes/`: JSON indexes for machine traversal",
      "- `manifest.json`: build-level metadata",
      "",
      "## Topics",
      "",
      *topic_lines,
      "",
    ]
  )


def write_json(path: Path, payload: object) -> None:
  path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def copy_tree(source_root: Path, output_dir: Path) -> None:
  output_dir.mkdir(parents=True, exist_ok=True)
  for child in source_root.iterdir():
    destination = output_dir / child.name
    if child.is_dir():
      shutil.copytree(child, destination, dirs_exist_ok=True)
    else:
      shutil.copy2(child, destination)


def build_source_records(
  source_dir: Path,
  source_files: list[Path],
  built_at: str,
  existing_manifests: dict[str, dict[str, object]] | None = None,
) -> list[dict[str, object]]:
  source_records: list[dict[str, object]] = []

  for source_path in source_files:
    relative_source_path = source_path.relative_to(source_dir).as_posix()
    source_slug = slugify(relative_source_path.replace("/", "-"), default=source_path.stem)
    source_content_hash = compute_content_hash(source_path)

    if existing_manifests is not None:
      existing_manifest = existing_manifests.get(source_slug)
      existing_content_hash = None
      existing_hash_algorithm = None
      if existing_manifest is not None:
        existing_content_hash, existing_hash_algorithm = read_manifest_hash(existing_manifest)
      if (
        existing_manifest is not None
        and existing_content_hash == source_content_hash
        and existing_hash_algorithm == HASH_ALGORITHM
        and str(existing_manifest.get("processing_version", "unknown")) == PROCESSING_VERSION
      ):
        source_records.append(source_record_from_manifest(existing_manifest, "unchanged"))
        continue

    extraction = extract_text(source_path)
    if extraction is None:
      continue

    extracted_text, extractor_name = extraction
    normalized_text = normalize_extracted_text(source_path, extracted_text)
    if not normalized_text.strip():
      continue

    title = derive_source_title(source_path, normalized_text)
    raw_chunks = build_chunks(normalized_text)
    topic_counts: Counter[str] = Counter()
    headings = [chunk["heading"] for chunk in raw_chunks if chunk["heading"]]
    preview = normalize_text(" ".join(str(chunk["content"]) for chunk in raw_chunks[:2]))
    source_record: dict[str, object] = {
      "source_slug": source_slug,
      "source_path": display_path(source_path.resolve()),
      "relative_source_path": relative_source_path,
      "filename": source_path.name,
      "title": title,
      "extractor": extractor_name,
      "built_at": built_at,
      "content_hash": source_content_hash,
      "content_hash_algorithm": HASH_ALGORITHM,
      "content": normalized_text,
      "char_count": len(normalized_text),
      "line_count": len(normalized_text.splitlines()),
      "headings": headings,
      "preview": preview,
      "chunks": [],
      "topic_counts": topic_counts,
      "source_state": "updated",
      "processing_version": PROCESSING_VERSION,
    }

    for chunk_index, raw_chunk in enumerate(raw_chunks, start=1):
      heading = raw_chunk["heading"] if raw_chunk["heading"] else None
      chunk_title = derive_chunk_title(heading, title, str(raw_chunk["content"]))
      topic_slug, aliases, scores = classify_topics(str(heading or chunk_title), str(raw_chunk["content"]))
      topic_counts[topic_slug] += 1
      chunk_slug = slugify(chunk_title, default=f"chunk-{chunk_index:03d}")
      source_chunk_file = f"{chunk_index:03d}-{chunk_slug}.md"
      topic_entry_file = f"{source_slug}--{chunk_index:03d}-{chunk_slug}.md"

      chunk_record = {
        "chunk_id": f"{source_slug}--{chunk_index:03d}",
        "title": chunk_title,
        "heading": heading,
        "content": raw_chunk["content"],
        "char_count": raw_chunk["char_count"],
        "start_line": raw_chunk["start_line"],
        "end_line": raw_chunk["end_line"],
        "topic_slug": topic_slug,
        "topic_title": TOPIC_BY_SLUG[topic_slug]["title"],
        "topic_aliases": aliases,
        "topic_alias_titles": [TOPIC_BY_SLUG[slug]["title"] for slug in aliases],
        "topic_scores": scores,
        "source_slug": source_slug,
        "source_title": title,
        "source_path": display_path(source_path.resolve()),
        "source_relative_path": relative_source_path,
        "extractor": extractor_name,
        "source_chunk_path": f"sources/{source_slug}/chunks/{source_chunk_file}",
        "topic_entry_path": f"topics/{topic_slug}/entries/{topic_entry_file}",
      }

      source_record["chunks"].append(chunk_record)

    source_records.append(source_record)

  return source_records


def main(argv: list[str]) -> int:
  try:
    source_dir, output_dir, mode = parse_args(argv)
  except ValueError as error:
    print(error, file=sys.stderr)
    return 1

  if not source_dir.is_dir():
    print(f"Source directory not found: {source_dir}", file=sys.stderr)
    return 1

  existing = existing_generated_content(output_dir)
  if existing and mode is None:
    print(
      f"Output directory {display_path(output_dir)} already contains generated data. Re-run with --update to merge or --rebuild to replace after confirming.",
      file=sys.stderr,
    )
    return 2

  source_files = sorted(path for path in source_dir.rglob("*") if path.is_file() and path.name != ".gitkeep")
  if not source_files:
    print(f"No rule source files found under {source_dir}", file=sys.stderr)
    return 1

  built_at = datetime.now(UTC).isoformat()
  tools = available_extractors()
  existing_manifests: dict[str, dict[str, object]] | None = None
  if existing and mode == "update":
    try:
      existing_manifests = load_existing_source_manifests(output_dir)
    except ValueError as error:
      print(error, file=sys.stderr)
      return 1

  updated_source_records = build_source_records(source_dir, source_files, built_at, existing_manifests)

  if not updated_source_records:
    print("No extractable rule content was found.", file=sys.stderr)
    return 1

  current_source_slugs = {slugify(path.relative_to(source_dir).as_posix().replace("/", "-"), default=path.stem) for path in source_files}
  retained_source_records: list[dict[str, object]] = []
  if existing_manifests is not None:
    retained_source_records = load_existing_source_records(existing_manifests, current_source_slugs)

  source_records = sorted(updated_source_records + retained_source_records, key=lambda item: str(item["source_slug"]))
  topic_entries: dict[str, list[dict[str, object]]] = defaultdict(list)
  chunk_index_records: list[dict[str, object]] = []
  for source_record in source_records:
    for chunk_record in source_record["chunks"]:
      topic_entries[str(chunk_record["topic_slug"])].append(chunk_record)
      chunk_index_records.append(
        {
          "chunk_id": chunk_record["chunk_id"],
          "title": chunk_record["title"],
          "topic_slug": chunk_record["topic_slug"],
          "topic_aliases": chunk_record["topic_aliases"],
          "source_slug": chunk_record["source_slug"],
          "source_path": chunk_record["source_path"],
          "start_line": chunk_record["start_line"],
          "end_line": chunk_record["end_line"],
          "char_count": chunk_record["char_count"],
          "source_chunk_path": chunk_record["source_chunk_path"],
          "topic_entry_path": chunk_record["topic_entry_path"],
        }
      )

  topic_manifest = [
    {
      "slug": slug,
      "title": TOPIC_BY_SLUG[slug]["title"],
      "description": TOPIC_BY_SLUG[slug]["description"],
      "chunk_count": len(entries),
      "source_slugs": sorted({entry["source_slug"] for entry in entries}),
      "index_path": f"topics/{slug}/index.json",
      "overview_path": f"topics/{slug}/overview.md",
    }
    for slug, entries in sorted(topic_entries.items())
  ]

  manifest = {
    "layout": "coc-db-full-hybrid-v1",
    "build_mode": mode or "fresh",
    "built_at": built_at,
    "source_dir": display_path(source_dir.resolve()),
    "source_hash_algorithm": HASH_ALGORITHM,
    "source_count": len(source_records),
    "chunk_count": len(chunk_index_records),
    "updated_source_count": sum(1 for record in source_records if record.get("source_state") == "updated"),
    "unchanged_source_count": sum(1 for record in source_records if record.get("source_state") == "unchanged"),
    "retained_source_count": sum(1 for record in source_records if record.get("source_state") == "retained"),
    "processing_version": PROCESSING_VERSION,
    "tools": tools,
    "topics": topic_manifest,
  }

  with tempfile.TemporaryDirectory() as temp_dir_name:
    temp_root = Path(temp_dir_name)
    write_json(temp_root / "manifest.json", manifest)

    indexes_dir = temp_root / "indexes"
    sources_dir = temp_root / "sources"
    topics_dir = temp_root / "topics"
    indexes_dir.mkdir(parents=True)
    sources_dir.mkdir(parents=True)
    topics_dir.mkdir(parents=True)

    sources_index: list[dict[str, object]] = []
    for source_record in source_records:
      source_slug = str(source_record["source_slug"])
      source_root = sources_dir / source_slug
      chunks_root = source_root / "chunks"

      full_extract_rel = f"sources/{source_slug}/full.md"
      summary_rel = f"sources/{source_slug}/summary.md"
      source_manifest_rel = f"sources/{source_slug}/source.json"

      if source_record.get("reuse_existing"):
        shutil.copytree(output_dir / "sources" / source_slug, source_root, dirs_exist_ok=True)
      else:
        chunks_root.mkdir(parents=True)
        (source_root / "full.md").write_text(render_full_extract(source_record), encoding="utf-8")
        (source_root / "summary.md").write_text(render_source_summary(source_record), encoding="utf-8")

      chunk_entries: list[dict[str, object]] = []
      for chunk_record in source_record["chunks"]:
        if not source_record.get("reuse_existing"):
          chunk_path = temp_root / str(chunk_record["source_chunk_path"])
          chunk_path.write_text(render_chunk_markdown(chunk_record), encoding="utf-8")
        chunk_entries.append(
          {
            "chunk_id": chunk_record["chunk_id"],
            "title": chunk_record["title"],
            "heading": chunk_record["heading"],
            "topic_slug": chunk_record["topic_slug"],
            "topic_aliases": chunk_record["topic_aliases"],
            "start_line": chunk_record["start_line"],
            "end_line": chunk_record["end_line"],
            "char_count": chunk_record["char_count"],
            "source_chunk_path": chunk_record["source_chunk_path"],
            "topic_entry_path": chunk_record["topic_entry_path"],
          }
        )

      if not source_record.get("reuse_existing"):
        source_manifest = {
          "source_slug": source_slug,
          "source_path": source_record["source_path"],
          "relative_source_path": source_record["relative_source_path"],
          "filename": source_record["filename"],
          "title": source_record["title"],
          "extractor": source_record["extractor"],
          "built_at": source_record["built_at"],
          "content_hash": source_record["content_hash"],
          "content_hash_algorithm": source_record["content_hash_algorithm"],
          "processing_version": source_record["processing_version"],
          "char_count": source_record["char_count"],
          "line_count": source_record["line_count"],
          "headings": source_record["headings"],
          "topic_counts": dict(sorted(source_record["topic_counts"].items())),
          "artifacts": {
            "full_extract": full_extract_rel,
            "summary": summary_rel,
            "chunks": f"sources/{source_slug}/chunks/",
          },
          "chunks": chunk_entries,
        }

      if source_record.get("reuse_existing"):
        source_manifest = {
          "source_slug": source_slug,
          "source_path": source_record["source_path"],
          "relative_source_path": source_record["relative_source_path"],
          "filename": source_record["filename"],
          "title": source_record["title"],
          "extractor": source_record["extractor"],
          "built_at": source_record["built_at"],
          "content_hash": source_record["content_hash"],
          "content_hash_algorithm": source_record["content_hash_algorithm"],
          "processing_version": source_record["processing_version"],
          "char_count": source_record["char_count"],
          "line_count": source_record["line_count"],
          "headings": source_record["headings"],
          "topic_counts": dict(sorted(source_record["topic_counts"].items())),
          "artifacts": {
            "full_extract": full_extract_rel,
            "summary": summary_rel,
            "chunks": f"sources/{source_slug}/chunks/",
          },
          "chunks": chunk_entries,
        }

      write_json(source_root / "source.json", source_manifest)

      sources_index.append(
        {
          "source_slug": source_slug,
          "title": source_record["title"],
          "source_path": source_record["source_path"],
          "extractor": source_record["extractor"],
          "topic_counts": dict(sorted(dict(source_record["topic_counts"]).items())),
          "chunk_count": len(source_record["chunks"]),
          "manifest_path": source_manifest_rel,
          "summary_path": summary_rel,
        }
      )

    topics_index: list[dict[str, object]] = []
    for slug, entries in sorted(topic_entries.items()):
      topic_root = topics_dir / slug
      entries_root = topic_root / "entries"
      entries_root.mkdir(parents=True)
      topic = TOPIC_BY_SLUG[slug]

      for entry in entries:
        topic_entry_path = temp_root / str(entry["topic_entry_path"])
        if entry.get("reuse_existing"):
          topic_entry_path.parent.mkdir(parents=True, exist_ok=True)
          shutil.copy2(output_dir / str(entry["topic_entry_path"]), topic_entry_path)
        else:
          topic_entry_path.write_text(render_chunk_markdown(entry), encoding="utf-8")

      topic_index_payload = {
        "slug": slug,
        "title": topic["title"],
        "description": topic["description"],
        "chunk_count": len(entries),
        "source_slugs": sorted({entry["source_slug"] for entry in entries}),
        "entries": [
          {
            "chunk_id": entry["chunk_id"],
            "title": entry["title"],
            "source_slug": entry["source_slug"],
            "source_title": entry["source_title"],
            "topic_aliases": entry["topic_aliases"],
            "entry_path": entry["topic_entry_path"],
            "source_chunk_path": entry["source_chunk_path"],
          }
          for entry in entries
        ],
      }
      write_json(topic_root / "index.json", topic_index_payload)
      (topic_root / "overview.md").write_text(render_topic_overview(topic, entries), encoding="utf-8")
      topics_index.append(
        {
          "slug": slug,
          "title": topic["title"],
          "description": topic["description"],
          "chunk_count": len(entries),
          "source_slugs": sorted({entry["source_slug"] for entry in entries}),
          "index_path": f"topics/{slug}/index.json",
          "overview_path": f"topics/{slug}/overview.md",
        }
      )

    write_json(indexes_dir / "sources.json", sources_index)
    write_json(indexes_dir / "topics.json", topics_index)
    write_json(indexes_dir / "chunks.json", chunk_index_records)
    (temp_root / "README.md").write_text(render_db_readme(manifest), encoding="utf-8")

    output_dir.mkdir(parents=True, exist_ok=True)
    clear_output_dir(output_dir)
    copy_tree(temp_root, output_dir)

  print(f"Built rules knowledge store at {display_path(output_dir.resolve())}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main(sys.argv))
