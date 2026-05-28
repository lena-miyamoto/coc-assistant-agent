#!/usr/bin/env python3

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from extract_text import IMAGE_SUFFIXES, TEXT_SUFFIXES, extract_text

SUPPORTED_SUFFIXES = {".pdf", *TEXT_SUFFIXES, *IMAGE_SUFFIXES}

LANGUAGE_MARKERS = {
  "German": (" der ", " die ", " das ", " und ", " nicht ", " mit ", " eine ", " einer ", " dem ", " den ", " von "),
  "English": (" the ", " and ", " with ", " from ", " this ", " that ", " after ", " into ", " for ", " are ", " of "),
}


@dataclass(frozen=True)
class SourceDocument:
  path: Path
  extractor_name: str
  text: str


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


def detect_predominant_language(extracted_documents: list[SourceDocument]) -> str:
  combined_text = " ".join(document.text.casefold() for document in extracted_documents)
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
  target_language = detect_predominant_language(extracted_documents)
  lines = [
    f"# {scenario_name} Import Staging",
    "",
    "Internal local extraction for assistant use. This is not the keeper-facing deliverable.",
    "",
    "## Output Language",
    "",
    f"- Predominant source language: {target_language}",
    f"- Final deliverable: scenarios/{scenario_name}/scenario.md",
    "- Requirement: Author the final keeper digest entirely in the predominant source language and keep the language consistent throughout the document.",
    "",
    "## Sources",
    "",
  ]

  for document in extracted_documents:
    lines.append(f"- {document.path.as_posix()} ({document.extractor_name})")

  lines.extend(["", "## Extracted Source Material"])

  for document in extracted_documents:
    lines.extend(["", f"### {document.path.name}", ""])
    lines.append(f"Source path: {document.path.as_posix()}")
    lines.append(f"Extractor: {document.extractor_name}")
    lines.extend(["", normalize_extracted_text(document.text)])

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
