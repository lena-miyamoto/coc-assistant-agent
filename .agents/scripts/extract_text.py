#!/usr/bin/env python3

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

TEXT_SUFFIXES = {".txt", ".md", ".markdown", ".json", ".yaml", ".yml", ".csv", ".tsv"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}


def available_extractors() -> dict[str, bool]:
  return {
    "rga": shutil.which("rga") is not None,
    "pdftotext": shutil.which("pdftotext") is not None,
    "tesseract": shutil.which("tesseract") is not None,
  }


def run_command(args: list[str]) -> str | None:
  completed = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
  if completed.returncode != 0:
    return None
  return completed.stdout


def extract_with_rga(source_path: Path) -> str | None:
  return run_command(["rga", "--no-heading", "--no-filename", "--color", "never", "-e", ".", str(source_path)])


def extract_with_pdftotext(source_path: Path) -> str | None:
  return run_command(["pdftotext", "-q", str(source_path), "-"])


def extract_with_tesseract(source_path: Path) -> str | None:
  return run_command(["tesseract", str(source_path), "stdout"])


def extract_text(source_path: Path) -> tuple[str, str] | None:
  tools = available_extractors()

  if tools["rga"]:
    extracted_text = extract_with_rga(source_path)
    if extracted_text is not None:
      return extracted_text, "rga"

  suffix = source_path.suffix.lower()

  if suffix in TEXT_SUFFIXES:
    return source_path.read_text(encoding="utf-8", errors="replace"), "text"

  if suffix == ".pdf" and tools["pdftotext"]:
    extracted_text = extract_with_pdftotext(source_path)
    if extracted_text is not None:
      return extracted_text, "pdftotext"

  if suffix in IMAGE_SUFFIXES and tools["tesseract"]:
    extracted_text = extract_with_tesseract(source_path)
    if extracted_text is not None:
      return extracted_text, "tesseract"

  return None


def main(argv: list[str]) -> int:
  if len(argv) != 2:
    print("Usage: uv run python .agents/scripts/extract_text.py <source-file>", file=sys.stderr)
    return 1

  source_path = Path(argv[1])
  if not source_path.is_file():
    print(f"Source not found: {source_path}", file=sys.stderr)
    return 1

  extraction = extract_text(source_path)
  if extraction is not None:
    extracted_text, _extractor_name = extraction
    sys.stdout.write(extracted_text)
    return 0

  print(
    f"No extractor available for {source_path}. Install rga, pdftotext, tesseract, or provide a text extract.",
    file=sys.stderr,
  )
  return 1


if __name__ == "__main__":
  raise SystemExit(main(sys.argv))
