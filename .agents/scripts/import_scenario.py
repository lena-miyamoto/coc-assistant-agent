#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from extract_text import IMAGE_SUFFIXES, TEXT_SUFFIXES, extract_text

SUPPORTED_SUFFIXES = {".pdf", *TEXT_SUFFIXES, *IMAGE_SUFFIXES}

PAGE_LINE_RE = re.compile(r"^Page\s+(?P<page>\d+):\s?(?P<body>.*)$")
TOC_ENTRY_RE = re.compile(r"^(?P<title>.+?)\.{3,}\s*(?P<page>\d+)\s*$")
MARKDOWN_HEADING_RE = re.compile(r"^\s{0,3}(?P<marks>#+)\s+(?P<body>.+?)\s*$")
HANDOUT_LABEL_RE = re.compile(r"\b[\wÄÖÜäöüß'.-]+-Handout\s+\d+(?:,\s*Seite\s*\d+)?\b", re.IGNORECASE)

LANGUAGE_MARKERS = {
  "German": (" der ", " die ", " das ", " und ", " nicht ", " mit ", " eine ", " einer ", " dem ", " den ", " von "),
  "English": (" the ", " and ", " with ", " from ", " this ", " that ", " after ", " into ", " for ", " are ", " of "),
}


@dataclass(frozen=True)
class SourceDocument:
  path: Path
  extractor_name: str
  text: str


@dataclass(frozen=True)
class PageBlock:
  number: int
  raw_lines: tuple[str, ...]
  body_lines: tuple[str, ...]


@dataclass(frozen=True)
class TocEntry:
  title: str
  normalized_title: str
  page: int


@dataclass(frozen=True)
class AnalyzedDocument:
  path: Path
  extractor_name: str
  text: str
  pages: tuple[PageBlock, ...]
  toc_entries: tuple[TocEntry, ...]
  has_anthology_signals: bool


@dataclass(frozen=True)
class ScopedDocument:
  path: Path
  extractor_name: str
  text: str
  scope_reason: str


@dataclass(frozen=True)
class ExcludedDocument:
  path: Path
  extractor_name: str
  reason: str


def normalize_scenario_name(value: str) -> str:
  normalized = " ".join(value.split())
  normalized = normalized.replace("/", " - ").replace("\\", " - ")
  normalized = normalized.strip(" .")
  if not normalized:
    raise ValueError("Scenario name must not be empty.")
  return normalized


def collect_source_files(source_path: Path) -> list[Path]:
  if source_path.is_file():
    return [source_path]

  if source_path.is_dir():
    return sorted(
      path
      for path in source_path.rglob("*")
      if path.is_file() and path.name != ".gitkeep" and path.suffix.lower() in SUPPORTED_SUFFIXES
    )

  return []


def normalize_extracted_text(value: str) -> str:
  return value.replace("\xad", "").rstrip()


def normalize_for_match(value: str) -> str:
  value = PAGE_LINE_RE.sub(lambda match: match.group("body"), value)
  heading_match = MARKDOWN_HEADING_RE.match(value)
  if heading_match is not None:
    value = heading_match.group("body")

  normalized = unicodedata.normalize("NFKD", value.casefold())
  normalized = "".join(character for character in normalized if not unicodedata.combining(character))
  normalized = normalized.replace("–", "-").replace("—", "-")
  normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
  return " ".join(normalized.split())


def markdown_heading_level(line: str) -> int:
  match = MARKDOWN_HEADING_RE.match(line)
  if match is None:
    return 0
  return len(match.group("marks"))


def extract_page_blocks(text: str) -> tuple[PageBlock, ...]:
  current_page: int | None = None
  current_raw_lines: list[str] = []
  current_body_lines: list[str] = []
  blocks: list[PageBlock] = []

  for line in text.splitlines():
    match = PAGE_LINE_RE.match(line)
    if match is not None:
      page_number = int(match.group("page"))
      if current_page is None:
        current_page = page_number
      elif page_number != current_page:
        blocks.append(PageBlock(number=current_page, raw_lines=tuple(current_raw_lines), body_lines=tuple(current_body_lines)))
        current_raw_lines = []
        current_body_lines = []
        current_page = page_number

      current_raw_lines.append(line)
      current_body_lines.append(match.group("body"))
      continue

    if current_page is None:
      continue

    current_raw_lines.append(line)
    current_body_lines.append(line)

  if current_page is not None:
    blocks.append(PageBlock(number=current_page, raw_lines=tuple(current_raw_lines), body_lines=tuple(current_body_lines)))

  return tuple(blocks)


def parse_toc_entries(pages: tuple[PageBlock, ...]) -> tuple[TocEntry, ...]:
  entries: list[TocEntry] = []
  seen: set[tuple[str, int]] = set()

  for page in pages:
    for line in page.body_lines:
      match = TOC_ENTRY_RE.match(line.strip())
      if match is None:
        continue

      title = match.group("title").strip()
      normalized_title = normalize_for_match(title)
      page_number = int(match.group("page"))
      if not normalized_title:
        continue

      key = (normalized_title, page_number)
      if key in seen:
        continue

      seen.add(key)
      entries.append(TocEntry(title=title, normalized_title=normalized_title, page=page_number))

  return tuple(sorted(entries, key=lambda entry: entry.page))


def count_top_level_headings(text: str) -> int:
  return sum(1 for line in text.splitlines() if markdown_heading_level(line) == 1)


def analyze_document(document: SourceDocument) -> AnalyzedDocument:
  pages = extract_page_blocks(document.text)
  toc_entries = parse_toc_entries(pages)
  has_anthology_signals = bool(toc_entries) or count_top_level_headings(document.text) > 1
  return AnalyzedDocument(
    path=document.path,
    extractor_name=document.extractor_name,
    text=document.text,
    pages=pages,
    toc_entries=toc_entries,
    has_anthology_signals=has_anthology_signals,
  )


def select_pages_by_toc_title(document: AnalyzedDocument, scenario_name: str) -> set[int]:
  scenario_name_normalized = normalize_for_match(scenario_name)
  matching_entries = [entry for entry in document.toc_entries if entry.normalized_title == scenario_name_normalized]
  if not matching_entries:
    return set()

  start_page = matching_entries[0].page
  end_page = next((entry.page for entry in document.toc_entries if entry.page > start_page), None)
  selected_pages = {
    page.number
    for page in document.pages
    if page.number >= start_page and (end_page is None or page.number < end_page)
  }
  return selected_pages


def scope_text_by_heading(text: str, scenario_name: str) -> str | None:
  scenario_name_normalized = normalize_for_match(scenario_name)
  lines = text.splitlines()
  candidates: list[tuple[int, int, int]] = []

  for index, line in enumerate(lines):
    heading_level = markdown_heading_level(line)
    normalized_line = normalize_for_match(line)
    if not normalized_line:
      continue

    exact_match = normalized_line == scenario_name_normalized
    contains_match = scenario_name_normalized in normalized_line
    if not exact_match and not contains_match:
      continue
    if not exact_match and heading_level == 0:
      continue

    score = 3 if exact_match and heading_level else 2 if exact_match else 1
    candidates.append((score, index, heading_level or 99))

  if not candidates:
    return None

  candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
  _score, start_index, start_heading_level = candidates[0]
  end_index = len(lines)
  if start_heading_level != 99:
    for index in range(start_index + 1, len(lines)):
      next_heading_level = markdown_heading_level(lines[index])
      if next_heading_level and next_heading_level <= start_heading_level:
        end_index = index
        break

  scoped_text = "\n".join(lines[start_index:end_index]).strip()
  return scoped_text or None


def render_selected_pages(pages: tuple[PageBlock, ...], selected_pages: set[int]) -> str:
  selected_lines: list[str] = []
  for page in pages:
    if page.number not in selected_pages:
      continue

    if selected_lines and selected_lines[-1] != "":
      selected_lines.append("")
    selected_lines.extend(page.raw_lines)

  return normalize_extracted_text("\n".join(selected_lines))


def select_primary_scope(document: AnalyzedDocument, scenario_name: str) -> ScopedDocument | None:
  if document.pages:
    selected_pages = select_pages_by_toc_title(document, scenario_name)
    if selected_pages:
      scoped_text = render_selected_pages(document.pages, selected_pages)
      page_numbers = sorted(selected_pages)
      return ScopedDocument(
        path=document.path,
        extractor_name=document.extractor_name,
        text=scoped_text,
        scope_reason=f"scenario pages {page_numbers[0]}-{page_numbers[-1]}",
      )

  scoped_text = scope_text_by_heading(document.text, scenario_name)
  if scoped_text is None:
    return None

  return ScopedDocument(
    path=document.path,
    extractor_name=document.extractor_name,
    text=normalize_extracted_text(scoped_text),
    scope_reason="scenario heading match",
  )


def extract_handout_labels(scoped_documents: list[ScopedDocument]) -> set[str]:
  labels: set[str] = set()
  for document in scoped_documents:
    for line in document.text.splitlines():
      for match in HANDOUT_LABEL_RE.finditer(line):
        labels.add(normalize_for_match(match.group(0)))
  return labels


def page_heading(page: PageBlock) -> str:
  for line in page.body_lines:
    stripped_line = line.strip()
    if not stripped_line:
      continue

    normalized_line = normalize_for_match(stripped_line)
    if not normalized_line:
      continue
    if normalized_line.isdigit():
      continue
    if normalized_line in {
      "cthulhu hauser des horrors",
      "handouts und spielerkarten",
      "verknupftes inhaltsverzeichnis",
      "linked contents",
      "contents",
      "table of contents",
    }:
      continue
    return stripped_line

  return ""


def page_is_contents_index(page: PageBlock) -> bool:
  return any(normalize_for_match(line) in {"verknupftes inhaltsverzeichnis", "linked contents", "contents", "table of contents"} for line in page.body_lines)


def handout_group_key(label: str) -> str | None:
  match = re.match(r"(?P<prefix>.+?) handout \d+", normalize_for_match(label))
  if match is None:
    return None
  return match.group("prefix")


def is_player_map_label(label: str) -> bool:
  normalized_label = normalize_for_match(label)
  return "spielerkarte" in normalized_label or "player map" in normalized_label


def page_contains_target_handout(page: PageBlock, handout_labels: set[str]) -> bool:
  if not handout_labels:
    return False
  if page_is_contents_index(page):
    return False

  for line in page.body_lines:
    for match in HANDOUT_LABEL_RE.finditer(line):
      if normalize_for_match(match.group(0)) in handout_labels:
        return True

  return False


def select_supplemental_pages(document: AnalyzedDocument, handout_labels: set[str]) -> set[int]:
  if not document.pages or not handout_labels:
    return set()

  matched_pages = [page.number for page in document.pages if page_contains_target_handout(page, handout_labels)]
  if not matched_pages:
    return set()

  selected_pages = set(matched_pages)
  page_numbers = [page.number for page in document.pages]
  page_indexes = {page_number: index for index, page_number in enumerate(page_numbers)}

  for page_number in matched_pages:
    page = document.pages[page_indexes[page_number]]
    group_key = handout_group_key(page_heading(page))
    if group_key is None:
      continue

    next_index = page_indexes[page_number] + 1
    while next_index < len(document.pages):
      next_page = document.pages[next_index]
      next_heading = page_heading(next_page)
      if not next_heading:
        break

      next_group_key = handout_group_key(next_heading)
      if next_group_key is not None:
        if next_group_key != group_key:
          break
        selected_pages.add(next_page.number)
        next_index += 1
        continue

      if is_player_map_label(next_heading):
        selected_pages.add(next_page.number)
        next_index += 1
        continue

      break

  return selected_pages


def scope_extracted_documents(scenario_name: str, extracted_documents: list[SourceDocument]) -> tuple[list[ScopedDocument], list[ExcludedDocument]]:
  analyzed_documents = [analyze_document(document) for document in extracted_documents]
  primary_scoped_documents = [scoped for document in analyzed_documents if (scoped := select_primary_scope(document, scenario_name)) is not None]

  if not primary_scoped_documents:
    if any(document.has_anthology_signals for document in analyzed_documents):
      raise ValueError(
        f"Unable to isolate scenario '{scenario_name}' from the provided sources. Provide a narrower source file/folder or add a text extract with a clear scenario heading."
      )

    return (
      [
        ScopedDocument(
          path=document.path,
          extractor_name=document.extractor_name,
          text=normalize_extracted_text(document.text),
          scope_reason="single-scenario source file",
        )
        for document in extracted_documents
      ],
      [],
    )

  handout_labels = extract_handout_labels(primary_scoped_documents)
  scoped_documents_by_path = {document.path: document for document in primary_scoped_documents}

  for document in analyzed_documents:
    supplemental_pages = select_supplemental_pages(document, handout_labels)
    if not supplemental_pages:
      continue

    supplemental_text = render_selected_pages(document.pages, supplemental_pages)
    existing_document = scoped_documents_by_path.get(document.path)
    if existing_document is None:
      scoped_documents_by_path[document.path] = ScopedDocument(
        path=document.path,
        extractor_name=document.extractor_name,
        text=supplemental_text,
        scope_reason=f"scenario handouts/maps pages {min(supplemental_pages)}-{max(supplemental_pages)}",
      )
      continue

    combined_text = normalize_extracted_text(f"{existing_document.text}\n\n{supplemental_text}")
    combined_reason = f"{existing_document.scope_reason}; handouts/maps pages {min(supplemental_pages)}-{max(supplemental_pages)}"
    scoped_documents_by_path[document.path] = ScopedDocument(
      path=document.path,
      extractor_name=document.extractor_name,
      text=combined_text,
      scope_reason=combined_reason,
    )

  scoped_documents = [scoped_documents_by_path[document.path] for document in extracted_documents if document.path in scoped_documents_by_path]
  excluded_documents = [
    ExcludedDocument(path=document.path, extractor_name=document.extractor_name, reason="no in-scope scenario material detected")
    for document in extracted_documents
    if document.path not in scoped_documents_by_path
  ]
  return scoped_documents, excluded_documents


def detect_predominant_language(scoped_documents: list[ScopedDocument]) -> str:
  combined_text = " ".join(document.text.casefold() for document in scoped_documents)
  combined_text = f" {' '.join(combined_text.split())} "

  scores = {
    language: sum(combined_text.count(marker) for marker in markers)
    for language, markers in LANGUAGE_MARKERS.items()
  }
  ranked_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
  if not ranked_scores or ranked_scores[0][1] == 0:
    return "Match source document language manually"
  if len(ranked_scores) > 1 and ranked_scores[0][1] == ranked_scores[1][1]:
    return "Match source document language manually"
  return ranked_scores[0][0]


def render_staging_markdown(scenario_name: str, extracted_documents: list[SourceDocument]) -> str:
  scoped_documents, excluded_documents = scope_extracted_documents(scenario_name, extracted_documents)
  target_language = detect_predominant_language(scoped_documents)
  lines = [
    f"# {scenario_name} Import Staging",
    "",
    "Internal local extraction for assistant use. This is not the keeper-facing deliverable.",
    "Only scenario-scoped source material is included below.",
    "",
    "## Output Language",
    "",
    f"- Predominant source language: {target_language}",
    "- Final deliverables:",
    f"  - scenarios/{scenario_name}/npcs-and-enemies.md",
    f"  - scenarios/{scenario_name}/story-overview.md",
    f"  - scenarios/{scenario_name}/keeper-notes.md",
    f"  - scenarios/{scenario_name}/clue-map.md",
    f"  - scenarios/{scenario_name}/session-plan.md",
    "- Requirement: Author the final keeper package entirely in the predominant source language and keep the language consistent throughout the documents.",
    "",
    "## Scenario Scope",
    "",
    f"- Target scenario: {scenario_name}",
    "- The importer has already isolated the requested scenario by exact title and scenario-specific handout/map references where possible.",
    "- Treat anthology front matter, neighboring scenarios, pregens, and unrelated handouts as out of scope unless this scenario directly points to them.",
    "- If the scoped extract still looks ambiguous, treat that as a scoping failure instead of filling the gap from nearby anthology material.",
    "- Every fact in the final files must be traceable to the scoped scenario section or its scenario-specific handouts/maps.",
    "",
    "## Sources",
    "",
  ]

  for document in extracted_documents:
    if any(scoped_document.path == document.path for scoped_document in scoped_documents):
      lines.append(f"- {document.path.as_posix()} ({document.extractor_name}) [included]")
      continue
    excluded_document = next(item for item in excluded_documents if item.path == document.path)
    lines.append(f"- {document.path.as_posix()} ({document.extractor_name}) [excluded: {excluded_document.reason}]")

  lines.extend(["", "## Extracted Source Material"])

  for document in scoped_documents:
    lines.extend(["", f"### {document.path.name}", ""])
    lines.append(f"Source path: {document.path.as_posix()}")
    lines.append(f"Extractor: {document.extractor_name}")
    lines.append(f"Scope: {document.scope_reason}")
    lines.extend(["", normalize_extracted_text(document.text)])

  if excluded_documents:
    lines.extend(["", "## Excluded Source Files", ""])
    for document in excluded_documents:
      lines.append(f"- {document.path.as_posix()} ({document.extractor_name}): {document.reason}")

  lines.append("")
  return "\n".join(lines)


def main(argv: list[str]) -> int:
  if len(argv) != 3:
    print("Usage: uv run python .agents/scripts/import_scenario.py <pdf-or-folder> <scenario-name>", file=sys.stderr)
    return 1

  source_path = Path(argv[1])
  if not source_path.exists():
    print(f"Source not found: {source_path}", file=sys.stderr)
    return 1

  try:
    scenario_name = normalize_scenario_name(argv[2])
  except ValueError as error:
    print(str(error), file=sys.stderr)
    return 1

  source_files = collect_source_files(source_path)
  if not source_files:
    print(f"No supported source files found in: {source_path}", file=sys.stderr)
    return 1

  extracted_documents: list[SourceDocument] = []
  for candidate_path in source_files:
    extraction = extract_text(candidate_path)
    if extraction is None:
      continue

    extracted_text, extractor_name = extraction
    if not extracted_text.strip():
      continue

    extracted_documents.append(SourceDocument(path=candidate_path, extractor_name=extractor_name, text=extracted_text))

  if not extracted_documents:
    print(f"Unable to extract text from: {source_path}", file=sys.stderr)
    return 1

  output_dir = Path("scenarios") / scenario_name
  output_dir.mkdir(parents=True, exist_ok=True)

  output_path = output_dir / ".source-extract.md"
  output_path.write_text(render_staging_markdown(scenario_name, extracted_documents), encoding="utf-8")

  print(output_path.as_posix())
  return 0


if __name__ == "__main__":
  raise SystemExit(main(sys.argv))
