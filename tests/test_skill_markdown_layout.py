from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_FILES = [
  REPO_ROOT / ".agents" / "skills" / "build-rules-db" / "SKILL.md",
  REPO_ROOT / ".agents" / "skills" / "import-scenario" / "SKILL.md",
  REPO_ROOT / ".agents" / "skills" / "lookup-rules-db" / "SKILL.md",
]


def test_shared_skills_reference_assistant_spec_for_common_rules() -> None:
  for skill_file in SKILL_FILES:
    content = skill_file.read_text(encoding="utf-8")

    assert "../../assistant-spec.md" in content
    assert "Check for `rga` first and prefer it" not in content
    assert "If OCR is needed" not in content
