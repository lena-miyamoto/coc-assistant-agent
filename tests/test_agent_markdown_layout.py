from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_FILES = [
  REPO_ROOT / ".claude" / "agents" / "coc-assistant.md",
  REPO_ROOT / ".github" / "agents" / "coc-assistant.agent.md",
]


def strip_frontmatter(markdown: str) -> str:
  if not markdown.startswith("---\n"):
    return markdown

  _frontmatter, _separator, body = markdown.partition("\n---\n")
  return body.strip()


def test_platform_agents_reference_shared_assistant_spec() -> None:
  for agent_file in AGENT_FILES:
    content = agent_file.read_text(encoding="utf-8")
    body = strip_frontmatter(content)

    assert ".agents/assistant-spec.md" in body
    assert "canonical source for shared behavior" in body
    assert "Check for `rga`" not in body
    assert "Use `tesseract`" not in body
    assert "uv sync" not in body
    assert "Scenario briefing" not in body
