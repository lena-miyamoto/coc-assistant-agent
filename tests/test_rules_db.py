from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / ".agents/scripts/build_rules_db.py"


def read_json(path: Path) -> object:
  return json.loads(path.read_text(encoding="utf-8"))


def load_builder_module(script_path: Path) -> object:
  sys.path.insert(0, str(script_path.parent))
  try:
    spec = importlib.util.spec_from_file_location("build_rules_db", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
  finally:
    sys.path.pop(0)


def run_builder(*args: str | Path, check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
  return subprocess.run(
    [sys.executable, str(SCRIPT_PATH), *(str(arg) for arg in args)],
    cwd=REPO_ROOT,
    check=check,
    text=True,
    encoding="utf-8",
    errors="replace",
    capture_output=capture_output,
  )


@pytest.fixture(scope="module")
def builder_module() -> object:
  return load_builder_module(SCRIPT_PATH)


def test_build_rules_db_generates_expected_store(tmp_path: Path) -> None:
  output_dir = tmp_path / "coc-db"
  run_builder("tests/fixtures/synthetic/rules", output_dir)

  duplicate_run = run_builder("tests/fixtures/synthetic/rules", output_dir, check=False, capture_output=True)
  assert duplicate_run.returncode == 2
  assert "--update to merge or --rebuild to replace" in duplicate_run.stderr

  manifest = read_json(output_dir / "manifest.json")
  assert manifest["layout"] == "coc-db-full-hybrid-v1"
  assert manifest["build_mode"] == "fresh"
  assert manifest["source_hash_algorithm"] == "gxhash128"
  assert manifest["source_count"] == 1
  assert manifest["chunk_count"] >= 2
  assert manifest["source_dir"].endswith("tests/fixtures/synthetic/rules")
  assert manifest["tools"]["tesseract"] in {True, False}

  sources_index = read_json(output_dir / "indexes/sources.json")
  topics_index = read_json(output_dir / "indexes/topics.json")
  chunks_index = read_json(output_dir / "indexes/chunks.json")
  assert len(sources_index) == 1
  assert len(chunks_index) >= 2

  source_dir = output_dir / "sources/keepers-compendium-excerpt-md"
  assert (source_dir / "source.json").is_file()
  assert (source_dir / "summary.md").is_file()
  assert (source_dir / "full.md").is_file()
  assert (source_dir / "chunks").is_dir()

  source_manifest = read_json(source_dir / "source.json")
  assert source_manifest["source_path"].endswith("tests/fixtures/synthetic/rules/keepers-compendium-excerpt.md")
  assert source_manifest["extractor"] in {"rga", "text", "pdftotext", "tesseract"}
  assert source_manifest["content_hash_algorithm"] == "gxhash128"
  assert len(source_manifest["content_hash"]) == 32
  assert source_manifest["topic_counts"]["skills-and-rolls"] >= 1
  assert source_manifest["artifacts"]["full_extract"] == "sources/keepers-compendium-excerpt-md/full.md"

  summary_text = (source_dir / "summary.md").read_text(encoding="utf-8")
  assert "## Topic Coverage" in summary_text
  assert "Skills And Rolls" in summary_text

  full_text = (source_dir / "full.md").read_text(encoding="utf-8")
  assert "Bonus And Penalty Dice" in full_text

  topic_slugs = {topic["slug"] for topic in topics_index}
  assert "skills-and-rolls" in topic_slugs
  assert "sanity-and-horror" in topic_slugs

  skills_topic = output_dir / "topics/skills-and-rolls"
  assert (skills_topic / "index.json").is_file()
  assert (skills_topic / "overview.md").is_file()
  assert (skills_topic / "entries").is_dir()

  skills_index = read_json(skills_topic / "index.json")
  assert skills_index["chunk_count"] >= 1
  assert any(entry["source_slug"] == "keepers-compendium-excerpt-md" for entry in skills_index["entries"])

  chunk_paths = {chunk["topic_entry_path"] for chunk in chunks_index}
  assert any(path.startswith("topics/skills-and-rolls/entries/") for path in chunk_paths)

  update_source_dir = tmp_path / "update-rules"
  update_source_dir.mkdir()
  update_fixture = update_source_dir / "keepers-update-addendum.md"
  update_fixture.write_text(
    """# Keeper Update Addendum

Synthetic update fixture.

## Combat Drill

Attack order matters when two investigators try to seize the same firing lane.
""",
    encoding="utf-8",
  )

  run_builder(update_source_dir, output_dir, "--update")

  updated_manifest = read_json(output_dir / "manifest.json")
  assert updated_manifest["build_mode"] == "update"
  assert updated_manifest["source_count"] == 2
  assert updated_manifest["updated_source_count"] == 1
  assert updated_manifest["unchanged_source_count"] == 0
  assert updated_manifest["retained_source_count"] == 1

  updated_sources_index = read_json(output_dir / "indexes/sources.json")
  updated_source_slugs = {entry["source_slug"] for entry in updated_sources_index}
  assert "keepers-compendium-excerpt-md" in updated_source_slugs
  assert "keepers-update-addendum-md" in updated_source_slugs

  assert (output_dir / "sources/keepers-compendium-excerpt-md/source.json").is_file()
  assert (output_dir / "sources/keepers-update-addendum-md/source.json").is_file()

  combat_topic = read_json(output_dir / "topics/combat-and-chases/index.json")
  assert any(entry["source_slug"] == "keepers-update-addendum-md" for entry in combat_topic["entries"])


def test_pdf_helpers_normalize_titles(builder_module: object) -> None:
  sample_pdf_path = Path("Cthulhu_GRW_Test.pdf")
  sample_pdf_text = """Page 1:
Page 2:
Page 4: Impressum
Page 4: Redaktion
Page 4: Heiko Gill

Page 5: WICHTIGER HINWEIS!
Page 5: Sanity loss follows exposure to horrors.
Page 5: Bonus dice apply in favorable circumstances.
"""
  normalized_pdf_text = builder_module.normalize_extracted_text(sample_pdf_path, sample_pdf_text)
  assert "Page 1:" not in normalized_pdf_text
  assert "Page 5:" not in normalized_pdf_text
  assert builder_module.derive_source_title(sample_pdf_path, normalized_pdf_text) == "Cthulhu GRW Test"
  assert builder_module.derive_chunk_title(None, "Cthulhu GRW Test", normalized_pdf_text) != "Page 1:"


def test_update_reuses_unchanged_source(tmp_path: Path) -> None:
  source_dir = tmp_path / "rules"
  output_dir = tmp_path / "coc-db"
  source_dir.mkdir()
  fixture_path = source_dir / "keepers-compendium-excerpt.md"
  fixture_path.write_text(
    (REPO_ROOT / "tests/fixtures/synthetic/rules/keepers-compendium-excerpt.md").read_text(encoding="utf-8"),
    encoding="utf-8",
  )

  run_builder(source_dir, output_dir)
  run_builder(source_dir, output_dir, "--update")

  unchanged_manifest = read_json(output_dir / "manifest.json")
  assert unchanged_manifest["build_mode"] == "update"
  assert unchanged_manifest["source_hash_algorithm"] == "gxhash128"
  assert unchanged_manifest["updated_source_count"] == 0
  assert unchanged_manifest["unchanged_source_count"] == 1
  assert unchanged_manifest["retained_source_count"] == 0
