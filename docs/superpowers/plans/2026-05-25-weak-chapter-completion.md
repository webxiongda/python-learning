# Weak Chapter Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fill all weak Python learning chapters with complete theory, demo, check, and project-task content.

**Architecture:** Add a deterministic enhancement script that parses existing chapter metadata, detects weak chapters, and writes topic-specific Markdown. Keep review files untouched because they are learner-owned progress records.

**Tech Stack:** Python standard library, Markdown files, existing repository quality checks.

---

### Task 1: Add Weak Chapter Enhancement Script

**Files:**
- Create: `tools/enhance_weak_chapters.py`

- [ ] Build metadata parsing from `README.md`.
- [ ] Build weak chapter detection using line counts and skeletal content signals.
- [ ] Add topic-specific content blueprints.
- [ ] Generate four learning files per weak chapter.
- [ ] Print modified chapter numbers.

### Task 2: Run Generation

**Files:**
- Modify: `chapters/*/01-theory.md`
- Modify: `chapters/*/02-demo.md`
- Modify: `chapters/*/03-check.md`
- Modify: `chapters/*/04-project-task.md`

- [ ] Run `python3 tools/enhance_weak_chapters.py`.
- [ ] Inspect the modified chapter list.
- [ ] Confirm `review.md` files are untouched.

### Task 3: Wire Verification

**Files:**
- Modify: `Makefile`

- [ ] Add `enhance-weak` command for repeatable regeneration.
- [ ] Keep `make all` as the quality gate.

### Task 4: Verify

**Files:**
- Read: representative generated chapter files.

- [ ] Run `make all`.
- [ ] Inspect one basic chapter, one OOP chapter, one Web/data chapter, one engineering chapter, and one final chapter.
- [ ] Fix generic or contradictory content found during inspection.
