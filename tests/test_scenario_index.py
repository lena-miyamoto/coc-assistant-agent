from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
EXPECTED_PATH = REPO_ROOT / "tests/expected/scenario-index.tsv"
SCRIPT_PATH = REPO_ROOT / ".agents/scripts/build_scenario_index.py"
SOURCE_FIXTURE = REPO_ROOT / "tests/fixtures/synthetic/whisper-in-blackwater-house.md"


def test_build_scenario_index_matches_expected(tmp_path: Path) -> None:
  fixture_dir = tmp_path / "scenario-fixtures"
  fixture_dir.mkdir()
  temp_fixture = fixture_dir / SOURCE_FIXTURE.name
  temp_fixture.write_text(SOURCE_FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")

  output_path = tmp_path / "scenario-index.tsv"
  subprocess.run(
    [sys.executable, str(SCRIPT_PATH), str(fixture_dir), str(output_path)],
    cwd=REPO_ROOT,
    check=True,
    text=True,
    encoding="utf-8",
    errors="replace",
  )

  expected = EXPECTED_PATH.read_text(encoding="utf-8")

  rows: list[list[str]] = []
  with output_path.open("r", encoding="utf-8", newline="") as output_file:
    reader = csv.reader(output_file, delimiter="\t")
    rows = [row for row in reader]

  if len(rows) > 1 and rows[1][0] == str(temp_fixture):
    rows[1][0] = SOURCE_FIXTURE.relative_to(REPO_ROOT).as_posix()

  actual = "\n".join("\t".join(row) for row in rows) + "\n"

  assert actual == expected
