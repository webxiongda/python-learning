# Weak Chapter Completion Design

## Goal

Complete every weak Python learning chapter so the course can be used as a real learning track instead of a set of placeholders.

## Scope

A chapter is considered weak when its learning files are short, generic, or do not support the learning loop. The first pass targets chapters whose theory file is still skeletal or whose Demo, check, and project task files are too thin to support practice.

The generated content covers the four learning files for each selected chapter:

- `01-theory.md`
- `02-demo.md`
- `03-check.md`
- `04-project-task.md`

`review.md` remains a learner-owned record and is not overwritten.

## Content Standard

Each generated chapter must be specific to its topic and oriented toward Python + FastAPI + AI application backend work. It must include:

- Clear learning goals.
- Core concepts and mental models.
- Real project use cases.
- Common mistakes and debugging signals.
- At least two practical demos.
- Self-check questions with reference answers.
- A project task that writes to `projects/chapter-xx/`.
- Concrete acceptance criteria.

## Implementation Approach

Add a repository script, `tools/enhance_weak_chapters.py`, that:

1. Parses chapter metadata from `README.md`.
2. Detects weak chapters by line-count thresholds and known skeletal structure.
3. Uses chapter-specific blueprints for topics, traps, demos, and project tasks.
4. Rewrites only selected weak chapters.
5. Prints the modified chapter numbers for audit.

The script keeps content generation deterministic so the course can be regenerated consistently after metadata changes.

## Verification

Run:

```bash
python3 tools/enhance_weak_chapters.py
make all
```

Then manually inspect representative chapters from basic Python, OOP, Web/data, engineering, and final review phases.
