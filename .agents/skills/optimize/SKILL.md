---
name: optimize
description: 'Optimize this repo''s instruction, skill, and agent files: cut redundancy, restore source-of-truth ownership, keep Copilot and Claude surfaces aligned. Use when cleaning up customization files in this workspace.'
argument-hint: 'Scope to optimize; report-only or apply fixes'
user-invocable: true
---

# Optimize

Cross-harness source of truth for optimizing this repo's customization and instruction files. Also the audit path: run report-only when the user wants findings without edits.

## When to Use

- Clean up or audit instruction files, skills, or agents.
- Re-verify any repo `*.md` for verbosity, repetition, padded explanation.
- Targets: redundancy, stale routing, harness drift, source-of-truth violations.

## Procedure

1. Mode: review-only (report) or cleanup (smallest edits that restore ownership and cut repetition).
2. Re-verify every in-scope `*.md` for writing quality:
   - Cut verbosity and repetition.
   - Compress explanation when meaning survives.
   - Tighten wording even when structure is fine.
3. Anchor on boundaries from `AGENTS.md` and `.github/copilot-instructions.md`:
   - Shared procedure: `.agents/skills/<name>/SKILL.md` (single source of truth; no `.github/skills` or `.claude/skills` wrappers — enforced by `tests/test_skill_mirrors.py`).
   - Repo-wide workflow: `AGENTS.md`.
   - Harness routing: `CLAUDE.md`, `.github/copilot-instructions.md`.
   - Agents: short, role-focused.
4. Audit before editing:
   - Duplicated procedure across shared skills and repo docs.
   - Stale paths or source-of-truth references.
   - Paired agents drifted beyond needed harness differences.
   - Repo docs restating routing owned elsewhere.
5. Narrowest useful fix:
   - Delete over rewrite.
   - Update references over adding explanation.
   - One owner per stable rule.
   - Keep discovery-critical frontmatter; shrink only duplicated body.
6. Re-check after edits:
   - Names, descriptions, argument hints aligned.
   - Repo docs advertise only surfaces worth exposing.

## Writing Rules

- Strict source-of-truth ownership.
- Paired agents stay short unless a harness difference forces more.
- Preserve keyword-rich frontmatter for discovery.
- Match the repo's direct procedural tone.
- Prefer brevity and clarity over grammatical smoothness in every repo `*.md`.
- Drop repetitive phrasing and padding when the meaning carries tighter.
- Never sacrifice meaning or expressiveness for shorter prose.
- Don't replace duplication with a new documentation layer.

## Validation

1. Markdown/frontmatter diagnostics on every changed file.
2. Grep for stale paths, outdated source-of-truth references, old duplicated phrases.
3. Re-read each changed `*.md` for verbosity and repetition; tighten until no obvious padding remains.
4. Shared skill files hold the procedure; no `SKILL.md` exists under `.github/skills` or `.claude/skills`.
5. Paired agents aligned except for needed harness differences.
6. Routing/README changes match actual file layout.

## Output

- Files optimized.
- Files audited, unchanged.
- Remaining inconsistencies left intentionally.
