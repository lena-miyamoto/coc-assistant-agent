#!/usr/bin/env python3

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

from extract_text import extract_text

HEADING_PREFIX = re.compile(r"^#{1,6}\s*")
SECOND_LEVEL_HEADING = re.compile(r"^##\s+")


def normalize_text(value: str) -> str:
  return " ".join(value.replace("\t", " ").replace("\r", " ").split())


def strip_heading_prefix(value: str) -> str:
  return HEADING_PREFIX.sub("", value).strip()


def main(argv: list[str]) -> int:
  source_dir = Path(argv[1]) if len(argv) > 1 else Path("resources/scenarios")
  output_path = Path(argv[2]) if len(argv) > 2 else Path(".agents/local/scenario-index.tsv")

  if not source_dir.is_dir():
    print(f"Source directory not found: {source_dir}", file=sys.stderr)
    return 1

  output_path.parent.mkdir(parents=True, exist_ok=True)

  with output_path.open("w", encoding="utf-8", newline="") as output_file:
    writer = csv.writer(output_file, delimiter="\t", lineterminator="\n")
    writer.writerow(["path", "title", "first_heading", "summary"])

    source_files = sorted(path for path in source_dir.rglob("*") if path.is_file() and path.name != ".gitkeep")
    for source_path in source_files:
      extraction = extract_text(source_path)
      if extraction is None:
        continue

      extracted_text, _extractor_name = extraction
      if not extracted_text.strip():
        continue

      lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]
      if not lines:
        continue

      title = strip_heading_prefix(lines[0]) or source_path.name

      first_heading = title
      for line in lines:
        if SECOND_LEVEL_HEADING.match(line):
          first_heading = strip_heading_prefix(line)
          break

      summary = normalize_text(" ".join(strip_heading_prefix(line) for line in lines[:4]))

      writer.writerow([source_path.as_posix(), title, first_heading, summary])

  return 0


if __name__ == "__main__":
  raise SystemExit(main(sys.argv))
