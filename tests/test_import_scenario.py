from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / ".agents/scripts/import_scenario.py"
SOURCE_FIXTURE = REPO_ROOT / "tests/fixtures/synthetic/whisper-in-blackwater-house.md"
ANTHOLOGY_FIXTURE_DIR = REPO_ROOT / "tests/fixtures/synthetic/anthology"
PEGASUS_ANTHOLOGY_FIXTURE_DIR = REPO_ROOT / "tests/fixtures/synthetic/anthology-pegasus"


def test_import_scenario_writes_keeper_markdown_from_single_file(tmp_path: Path) -> None:
  source_path = tmp_path / SOURCE_FIXTURE.name
  source_path.write_text(SOURCE_FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")

  subprocess.run(
    [sys.executable, str(SCRIPT_PATH), str(source_path), "Blackwater House"],
    cwd=tmp_path,
    check=True,
    text=True,
    encoding="utf-8",
    errors="replace",
  )

  output_dir = tmp_path / "scenarios" / "Blackwater House"
  output_path = output_dir / ".source-extract.md"
  assert output_path.is_file()
  assert not (output_dir / "scenario.md").exists()

  output_text = output_path.read_text(encoding="utf-8")
  assert "# Blackwater House Import Staging" in output_text
  assert "## Output Language" in output_text
  assert "- Predominant source language: English" in output_text
  assert "## Scenario Scope" in output_text
  assert "- Target scenario: Blackwater House" in output_text
  assert "clue-map.md" in output_text
  assert "session-plan.md" in output_text
  assert f"- {source_path.as_posix()} (rga)" in output_text or f"- {source_path.as_posix()} (text)" in output_text
  assert "## Extracted Source Material" in output_text
  assert f"### {source_path.name}" in output_text
  assert "Synthetic scenario fixture for regression testing." in output_text


def test_import_scenario_writes_sorted_sections_from_directory(tmp_path: Path) -> None:
  source_dir = tmp_path / "scenario-source"
  source_dir.mkdir()

  intro_path = source_dir / "01-intro.md"
  ending_path = source_dir / "02-ending.md"
  intro_path.write_text("# Intro\n\nFirst scene.", encoding="utf-8")
  ending_path.write_text("# Ending\n\nFinal scene.", encoding="utf-8")

  subprocess.run(
    [sys.executable, str(SCRIPT_PATH), str(source_dir), "House of Echoes"],
    cwd=tmp_path,
    check=True,
    text=True,
    encoding="utf-8",
    errors="replace",
  )

  output_dir = tmp_path / "scenarios" / "House of Echoes"
  output_path = output_dir / ".source-extract.md"
  output_text = output_path.read_text(encoding="utf-8")

  assert output_path.is_file()
  assert not (output_dir / "scenario.md").exists()
  assert "## Sources" in output_text
  assert "## Scenario Scope" in output_text
  assert "- Target scenario: House of Echoes" in output_text
  assert f"- {intro_path.as_posix()} (rga)" in output_text or f"- {intro_path.as_posix()} (text)" in output_text
  assert f"- {ending_path.as_posix()} (rga)" in output_text or f"- {ending_path.as_posix()} (text)" in output_text
  assert output_text.index(intro_path.as_posix()) < output_text.index(ending_path.as_posix())
  assert f"### {intro_path.name}" in output_text
  assert f"### {ending_path.name}" in output_text
  assert "First scene." in output_text
  assert "Final scene." in output_text


def test_import_scenario_records_german_output_language_for_german_source(tmp_path: Path) -> None:
  source_path = tmp_path / "windschiefes-haus.md"
  source_path.write_text(
    "# Das windschiefe Haus\n\nDas Haus ist alt und die Bewohner sprechen nicht gern darueber.\n",
    encoding="utf-8",
  )

  subprocess.run(
    [sys.executable, str(SCRIPT_PATH), str(source_path), "Das windschiefe Haus"],
    cwd=tmp_path,
    check=True,
    text=True,
    encoding="utf-8",
    errors="replace",
  )

  output_path = tmp_path / "scenarios" / "Das windschiefe Haus" / ".source-extract.md"
  output_text = output_path.read_text(encoding="utf-8")

  assert output_path.is_file()
  assert "- Predominant source language: German" in output_text


def test_import_scenario_scopes_anthology_sources_to_requested_scenario(tmp_path: Path) -> None:
  source_dir = tmp_path / "anthology-source"
  source_dir.mkdir()

  for fixture_path in ANTHOLOGY_FIXTURE_DIR.iterdir():
    target_path = source_dir / fixture_path.name
    target_path.write_text(fixture_path.read_text(encoding="utf-8"), encoding="utf-8")

  subprocess.run(
    [sys.executable, str(SCRIPT_PATH), str(source_dir), "Blackwater House"],
    cwd=tmp_path,
    check=True,
    text=True,
    encoding="utf-8",
    errors="replace",
  )

  output_path = tmp_path / "scenarios" / "Blackwater House" / ".source-extract.md"
  output_text = output_path.read_text(encoding="utf-8")

  assert output_path.is_file()
  assert "Page 5: Blackwater House" in output_text
  assert "Page 8: Escape the cellar before the walls begin breathing." in output_text
  assert "Page 3: Blackwater-Handout 1" in output_text
  assert "Page 5: Blackwater Estate - Player Map" in output_text
  assert "## Excluded Source Files" in output_text
  assert "pregens.md" in output_text
  assert "no in-scope scenario material detected" in output_text
  assert "Page 1: Linked Contents" not in output_text
  assert "Page 1: Blackwater House........5" not in output_text
  assert "Page 9: Lantern in the Marsh" not in output_text
  assert "Page 6: Lantern-Handout 1" not in output_text
  assert "This pregen file mentions Blackwater House but is not scenario text." not in output_text


def test_import_scenario_skips_pegasus_style_handout_index_pages(tmp_path: Path) -> None:
  source_dir = tmp_path / "anthology-source-pegasus"
  source_dir.mkdir()

  for fixture_path in PEGASUS_ANTHOLOGY_FIXTURE_DIR.iterdir():
    target_path = source_dir / fixture_path.name
    target_path.write_text(fixture_path.read_text(encoding="utf-8"), encoding="utf-8")

  subprocess.run(
    [sys.executable, str(SCRIPT_PATH), str(source_dir), "Blackwater House"],
    cwd=tmp_path,
    check=True,
    text=True,
    encoding="utf-8",
    errors="replace",
  )

  output_path = tmp_path / "scenarios" / "Blackwater House" / ".source-extract.md"
  output_text = output_path.read_text(encoding="utf-8")

  assert output_path.is_file()
  assert "Scope: scenario handouts/maps pages 15-22" in output_text
  assert "Page 15: Blackwater-Handout 1" in output_text
  assert "Page 20: Blackwater-Handout 6" in output_text
  assert "Page 21: Blackwater Estate - Player Map" in output_text
  assert "Page 22: Blackwater Cellar - Player Map" in output_text
  assert "Page 2: VERKNÜPFTES INHALTSVERZEICHNIS" not in output_text
  assert "Page 2: Corbitt-Handout 1........3" not in output_text
  assert "Page 2: Lantern-Handout 1........30" not in output_text
  assert "Page 30: Lantern-Handout 1" not in output_text
