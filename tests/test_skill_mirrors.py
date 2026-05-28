from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SHARED_SKILLS = REPO_ROOT / ".agents" / "skills"
PLATFORM_ROOTS = [
  REPO_ROOT / ".github" / "skills",
  REPO_ROOT / ".claude" / "skills",
]


def test_shared_skills_live_only_in_agents_directory() -> None:
  shared_skill_dirs = sorted(path for path in SHARED_SKILLS.iterdir() if path.is_dir() and path.name != "references")

  assert shared_skill_dirs

  for shared_skill_dir in shared_skill_dirs:
    shared_skill = shared_skill_dir / "SKILL.md"
    assert shared_skill.is_file(), shared_skill.as_posix()

    skill_text = shared_skill.read_text(encoding="utf-8")
    assert f"name: {shared_skill_dir.name}" in skill_text

    for platform_root in PLATFORM_ROOTS:
      mirrored_skill = platform_root / shared_skill_dir.name / "SKILL.md"
      assert not mirrored_skill.exists(), mirrored_skill.as_posix()


def test_platform_skill_directories_do_not_contain_skill_files() -> None:
  for platform_root in PLATFORM_ROOTS:
    if not platform_root.exists():
      continue

    mirrored_skills = sorted(platform_root.rglob("SKILL.md"))
    assert not mirrored_skills, [path.as_posix() for path in mirrored_skills]
