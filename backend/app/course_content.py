from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


LAYER_FILES = {
    "theory": "01-theory.md",
    "demo": "02-demo.md",
    "check": "03-check.md",
    "project": "04-project-task.md",
}


@dataclass(frozen=True)
class CourseChapter:
    no: int
    title: str
    summary: str
    priority: str
    hours: str
    route_status: str
    folder: str


class CourseContent:
    def __init__(self, content_root: Path):
        self.content_root = content_root

    def list_chapters(self) -> list[CourseChapter]:
        folder_by_no = {
            int(path.name[:2]): path.name
            for path in (self.content_root / "chapters").iterdir()
            if path.is_dir() and path.name[:2].isdigit()
        }
        chapters: list[CourseChapter] = []
        for line in (self.content_root / "README.md").read_text(encoding="utf-8").splitlines():
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.split("|")]
            if len(cells) < 7 or not cells[1].isdigit():
                continue
            no = int(cells[1])
            chapters.append(
                CourseChapter(
                    no=no,
                    title=self._clean(cells[2]),
                    summary=self._clean(cells[3]),
                    priority=self._clean(cells[4]),
                    hours=self._clean(cells[5]),
                    route_status=self._clean(cells[6]),
                    folder=folder_by_no.get(no, ""),
                )
            )
        return sorted(chapters, key=lambda chapter: chapter.no)

    def get_chapter(self, chapter_no: int) -> CourseChapter:
        for chapter in self.list_chapters():
            if chapter.no == chapter_no:
                return chapter
        raise KeyError(f"Chapter not found: {chapter_no}")

    def read_chapter_content(self, chapter_no: int) -> dict[str, str]:
        chapter = self.get_chapter(chapter_no)
        chapter_dir = self.content_root / "chapters" / chapter.folder
        return {
            layer: (chapter_dir / filename).read_text(encoding="utf-8") if (chapter_dir / filename).exists() else ""
            for layer, filename in LAYER_FILES.items()
        }

    @staticmethod
    def _clean(value: str) -> str:
        return " ".join(value.replace("`", "").split())
