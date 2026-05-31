---
name: optimize
description: 'Optimize this repo\'s instruction, skill, and agent files by removing unnecessary redundancy, restoring clear source-of-truth ownership, and keeping Copilot and Claude surfaces aligned. Use when cleaning up customization files in this workspace.'
argument-hint: 'Provide the scope to optimize and whether to report only or apply fixes directly'
user-invocable: true
---

# Optimize

This shared skill file is the cross-harness source of truth for optimizing this repo's customization and instruction files.

## When to Use

- The user wants to clean up instruction files, skills, or agents in this repository.
- The task is to remove unnecessary redundancy, fix stale routing, reduce harness drift, or restore a single clear source of truth.
- The scope includes files such as `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/agents/*.md`, `.claude/agents/*.md`, `.agents/assistant-spec.md`, `.agents/skills/*/SKILL.md`, `.github/skills/*/SKILL.md`, and `.claude/skills/*/SKILL.md`.

## Procedure

1. Clarify the optimization mode:
   - If the user asked for review only, report findings without editing.
   - If the user asked for cleanup or optimization, make the smallest edits that restore clear ownership and reduce repetition.
2. Start from the established repo boundaries in `AGENTS.md` and `.agents/assistant-spec.md`:
   - Shared keeper-assistant behavior belongs in `.agents/assistant-spec.md`.
   - Shared procedural skill content belongs in `.agents/skills/<name>/SKILL.md`.
   - `.github/skills` and `.claude/skills` should stay thin wrappers.
   - Repo-wide workflow belongs in `AGENTS.md`.
   - Harness-specific routing belongs in `CLAUDE.md` and `.github/copilot-instructions.md`.
   - Agent files should stay short and role-focused.
3. Audit for optimization targets before editing:
   - Find duplicated procedures across shared skills and wrappers.
   - Find stale paths or outdated references to old source-of-truth files.
   - Find paired agent files that drift beyond justified harness-specific differences.
   - Find repo docs that restate routing rules already owned elsewhere.
4. Apply only the narrowest useful cleanup:
   - Prefer deleting redundant text over rewriting it.
   - Prefer updating references over adding another explanation layer.
   - Prefer a single authoritative owner for each stable rule.
   - Keep discovery-critical frontmatter intact while shrinking duplicated body text.
5. Re-check discoverability and consistency after edits:
   - Names, descriptions, and argument hints should remain aligned where they should be shared.
   - Wrapper bodies should still point to the correct shared file.
   - Repo docs should advertise only the surfaces worth exposing.

## Writing Rules

- Be strict about source-of-truth ownership.
- Keep wrappers and paired agents short unless a harness-specific difference is actually required.
- Preserve keyword-rich discovery text in frontmatter.
- Match the repo's direct procedural tone.
- Avoid replacing one duplication problem with a new documentation layer.

## Validation

1. Run markdown/frontmatter diagnostics on every changed instruction file.
2. Search for stale paths, outdated source-of-truth references, and old duplicated phrases after edits.
3. Confirm shared skill files still hold the substantive procedure and wrappers stay minimal.
4. Confirm paired agents remain aligned except for necessary harness-specific differences.
5. Confirm any routing or README changes still match the actual file layout.

## Output

- State which files were optimized.
- State which files were audited but left unchanged.
- Report any remaining inconsistencies that were intentionally left alone.
