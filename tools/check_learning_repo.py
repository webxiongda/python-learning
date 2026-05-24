from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "chapters"
PROJECTS = ROOT / "projects"

EXPECTED_CHAPTER_FILES = {
    "01-theory.md",
    "02-demo.md",
    "03-check.md",
    "04-project-task.md",
    "review.md",
}

MILESTONE_CHAPTERS = {"10", "20", "30", "40", "50", "55"}
FASTAPI_AI_FILES = {
    "docs/FASTAPI-AI-FOCUS.md",
    "projects/chapter-45/README.md",
    "projects/chapter-50/README.md",
}

TEMPLATE_PHRASES = {
    "本章围绕",
    "Demo 2：封装成可复用函数",
    "业务练习模块",
    "你正在维护一个 Python 全栈项目",
    "阅读下面代码，指出它的问题",
}

ROOT_PLACEHOLDERS = {
    "在这里写下",
    "目标1：",
    "___ 小时",
    "___ 天",
    "___ 个月",
}


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def chapter_dirs() -> list[Path]:
    return sorted(path for path in CHAPTERS.iterdir() if path.is_dir())


def parse_readme_chapters() -> list[str]:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    chapters: list[str] = []
    pattern = re.compile(r"^\|\s*(\d{2})\s*\|")
    for line in readme.splitlines():
        match = pattern.match(line)
        if match:
            chapters.append(match.group(1))
    return chapters


def check_chapter_structure() -> CheckResult:
    dirs = chapter_dirs()
    problems: list[str] = []
    for directory in dirs:
        files = {path.name for path in directory.glob("*.md")}
        missing = sorted(EXPECTED_CHAPTER_FILES - files)
        extra = sorted(files - EXPECTED_CHAPTER_FILES)
        if missing:
            problems.append(f"{directory.name}: missing {', '.join(missing)}")
        if extra:
            problems.append(f"{directory.name}: extra {', '.join(extra)}")

    readme_chapters = set(parse_readme_chapters())
    dir_chapters = {directory.name[:2] for directory in dirs}
    missing_dirs = sorted(readme_chapters - dir_chapters)
    extra_dirs = sorted(dir_chapters - readme_chapters)
    if missing_dirs:
        problems.append(f"README chapters without directory: {', '.join(missing_dirs)}")
    if extra_dirs:
        problems.append(f"directories not listed in README: {', '.join(extra_dirs)}")

    ok = len(dirs) == 60 and not problems
    detail = f"{len(dirs)} chapter directories checked"
    if problems:
        detail += "; " + " | ".join(problems[:8])
        if len(problems) > 8:
            detail += f" | ... {len(problems) - 8} more"
    return CheckResult("chapter_structure", ok, detail)


def check_root_placeholders() -> CheckResult:
    files = ["learning-goal.md", "progress.md", "review-plan.md", "mistakes.md"]
    hits: list[str] = []
    for filename in files:
        content = (ROOT / filename).read_text(encoding="utf-8")
        for phrase in ROOT_PLACEHOLDERS:
            if phrase in content:
                hits.append(f"{filename}: {phrase}")
    return CheckResult(
        "root_placeholders",
        not hits,
        "no root placeholders found" if not hits else "; ".join(hits),
    )


def check_template_phrases() -> CheckResult:
    counts = {phrase: 0 for phrase in TEMPLATE_PHRASES}
    file_counts: dict[Path, int] = {}
    for path in CHAPTERS.glob("**/*.md"):
        content = path.read_text(encoding="utf-8")
        for phrase in TEMPLATE_PHRASES:
            if phrase in content:
                phrase_count = content.count(phrase)
                counts[phrase] += phrase_count
                file_counts[path] = file_counts.get(path, 0) + phrase_count

    total_hits = sum(counts.values())
    detail = ", ".join(f"{phrase}={count}" for phrase, count in sorted(counts.items()))
    top_files = sorted(file_counts.items(), key=lambda item: (-item[1], rel(item[0])))[:8]
    top_detail = "; top files: " + ", ".join(f"{rel(path)}({count})" for path, count in top_files) if top_files else ""
    detail = f"{total_hits} hits in {len(file_counts)} files; {detail}{top_detail}"
    # This repository still contains generated content. Treat this as a warning
    # until the count is driven down chapter by chapter.
    return CheckResult("template_phrases", total_hits == 0, detail)


def check_projects_workspace() -> CheckResult:
    missing: list[str] = []
    if not PROJECTS.exists():
        missing.append("projects/")
    for chapter in sorted(MILESTONE_CHAPTERS):
        readme = PROJECTS / f"chapter-{chapter}" / "README.md"
        if not readme.exists():
            missing.append(str(readme.relative_to(ROOT)))

    return CheckResult(
        "projects_workspace",
        not missing,
        "all milestone project READMEs exist" if not missing else "missing " + ", ".join(missing),
    )


def check_fastapi_ai_focus() -> CheckResult:
    missing = [filename for filename in sorted(FASTAPI_AI_FILES) if not (ROOT / filename).exists()]
    content_checks = {
        "README.md": "FastAPI + AI 应用主线",
        "learning-goal.md": "FastAPI + AI 应用能力地图",
        "chapters/45-FastAPI进阶/01-theory.md": "AI 应用后端",
        "chapters/50-里程碑：AI助手API项目/04-project-task.md": "AI Assistant API",
    }
    for filename, phrase in content_checks.items():
        path = ROOT / filename
        if not path.exists() or phrase not in path.read_text(encoding="utf-8"):
            missing.append(f"{filename}: missing phrase {phrase}")
    return CheckResult(
        "fastapi_ai_focus",
        not missing,
        "FastAPI AI focus files are present" if not missing else "; ".join(missing),
    )


def check_review_files() -> CheckResult:
    missing = [rel(directory / "review.md") for directory in chapter_dirs() if not (directory / "review.md").exists()]
    return CheckResult(
        "review_files",
        not missing,
        "all chapter review files exist" if not missing else "missing " + ", ".join(missing[:12]),
    )


def check_milestone_tasks() -> CheckResult:
    problems: list[str] = []
    for chapter in sorted(MILESTONE_CHAPTERS):
        matches = sorted(CHAPTERS.glob(f"{chapter}-*/04-project-task.md"))
        if not matches:
            problems.append(f"chapter {chapter}: missing project task")
            continue
        content = matches[0].read_text(encoding="utf-8")
        if "业务练习模块" in content:
            problems.append(f"chapter {chapter}: still generic")
        if "验收清单" not in content:
            problems.append(f"chapter {chapter}: no acceptance checklist")
        if "projects/chapter-" not in content:
            problems.append(f"chapter {chapter}: no project directory")
        if len(content) < 1200:
            problems.append(f"chapter {chapter}: task spec too thin")

    return CheckResult(
        "milestone_tasks",
        not problems,
        "milestone tasks are specific" if not problems else "; ".join(problems),
    )


def run_checks() -> list[CheckResult]:
    return [
        check_chapter_structure(),
        check_review_files(),
        check_root_placeholders(),
        check_projects_workspace(),
        check_fastapi_ai_focus(),
        check_milestone_tasks(),
        check_template_phrases(),
    ]


def main() -> int:
    results = run_checks()
    required = [result for result in results if result.name != "template_phrases"]
    for result in results:
        status = "PASS" if result.ok else ("WARN" if result.name == "template_phrases" else "FAIL")
        print(f"[{status}] {result.name}: {result.detail}")
    return 0 if all(result.ok for result in required) else 1


if __name__ == "__main__":
    raise SystemExit(main())
