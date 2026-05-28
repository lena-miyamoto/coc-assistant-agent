#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

from extract_text import IMAGE_SUFFIXES, TEXT_SUFFIXES, extract_text

SUPPORTED_SUFFIXES = {".pdf", *TEXT_SUFFIXES, *IMAGE_SUFFIXES}


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


def render_markdown(scenario_name: str, extracted_documents: list[tuple[Path, str, str]]) -> str:
  lines = [
    f"# {scenario_name}",
    "",
    "Local extracted scenario text for keeper prep. Derived from private local source files.",
    "",
    "## Sources",
    "",
  ]

  for source_path, extractor_name, _text in extracted_documents:
    lines.append(f"- {source_path.as_posix()} ({extractor_name})")

  lines.extend(["", "## Extracted Scenario"])

  for source_path, _extractor_name, text in extracted_documents:
    lines.extend(["", f"### {source_path.name}", ""])
    lines.append(text.rstrip())

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

  extracted_documents: list[tuple[Path, str, str]] = []
  for candidate_path in source_files:
    extraction = extract_text(candidate_path)
    if extraction is None:
      continue

    extracted_text, extractor_name = extraction
    if not extracted_text.strip():
      continue

    extracted_documents.append((candidate_path, extractor_name, extracted_text))

  if not extracted_documents:
    print(f"Unable to extract text from: {source_path}", file=sys.stderr)
    return 1

  output_dir = Path("scenarios") / scenario_name
  output_dir.mkdir(parents=True, exist_ok=True)

  output_path = output_dir / "scenario.md"
  output_path.write_text(render_markdown(scenario_name, extracted_documents), encoding="utf-8")

  print(output_path.as_posix())
  return 0


if __name__ == "__main__":
  raise SystemExit(main(sys.argv))
