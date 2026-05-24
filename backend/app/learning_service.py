from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .course_content import CourseChapter, CourseContent
from .models import (
    ChapterProgress,
    CheckResult,
    Mistake,
    Note,
    PortfolioEvidence,
    ReviewCard,
    ReviewTask,
    StudyLog,
    User,
    ValidationRecord,
)
from .schemas import (
    CardAnswerRequest,
    CheckResultRequest,
    CheckRevealRequest,
    NoteRequest,
    PortfolioEvidenceRequest,
    ProgressRequest,
    ReviewCompleteRequest,
    ValidationRequest,
)


class LearningService:
    def __init__(self, db: Session, content: CourseContent):
        self.db = db
        self.content = content

    def summary(self, user: User) -> dict:
        chapters = self.chapters(user)
        completed = sum(1 for chapter in chapters if self._core_done(chapter["progress"]))
        current = next((chapter for chapter in chapters if not self._core_done(chapter["progress"])), None)
        due_reviews = [task for task in self.reviews(user) if task["due"]]
        logs = [
            self._log_to_dict(log)
            for log in self.db.scalars(
                select(StudyLog).where(StudyLog.user_id == user.id).order_by(StudyLog.created_at.desc()).limit(8)
            )
        ]
        return {
            "current": "全部完成" if current is None else f"{current['no']:02d}-{current['title']}",
            "completed": completed,
            "total": len(chapters),
            "percent": round(completed * 100 / len(chapters)) if chapters else 0,
            "currentChapter": current,
            "dueReviews": due_reviews,
            "recentLogs": logs,
        }

    def today(self, user: User) -> dict:
        summary = self.summary(user)
        due_cards = self.due_cards(user)
        return {
            "focus": "先复习，再学习新章节" if summary["dueReviews"] or due_cards else "推进当前章节并完成强验收",
            "currentChapter": summary["currentChapter"],
            "dueReviews": summary["dueReviews"],
            "dueCards": due_cards,
            "blocks": ["30 分钟：到期复习", "90 分钟：阅读 + 费曼输出", "60 分钟：编码 / Demo / AI 后端实践", "30 分钟：自测与复盘"],
            "acceptance": ["理论：写 3-5 句费曼总结", "Demo：记录运行命令和结果", "自测：先答题再看答案", "项目：留下可验证交付证据"],
        }

    def chapters(self, user: User) -> list[dict]:
        progress = {
            item.chapter_no: item
            for item in self.db.scalars(select(ChapterProgress).where(ChapterProgress.user_id == user.id))
        }
        return [self._chapter_meta(chapter, progress.get(chapter.no)) for chapter in self.content.list_chapters()]

    def chapter(self, user: User, chapter_no: int) -> dict:
        chapter = self.content.get_chapter(chapter_no)
        progress = self.db.scalar(
            select(ChapterProgress).where(ChapterProgress.user_id == user.id, ChapterProgress.chapter_no == chapter_no)
        )
        return {**self._chapter_meta(chapter, progress), "content": self.content.read_chapter_content(chapter_no)}

    def update_progress(self, user: User, request: ProgressRequest) -> None:
        progress = self._progress(user, request.chapter_no)
        was_done = progress.core_done()
        progress.set_layer(request.layer, request.done)
        if progress.core_done() and not progress.finished_date:
            progress.finished_date = date.today()
        self.db.add(progress)
        chapter = self.content.get_chapter(request.chapter_no)
        self._append_log(user, chapter.no, chapter.title, request.layer, "完成" if request.done else "取消完成")
        if not was_done and progress.core_done():
            self._ensure_reviews(user, chapter, progress.finished_date or date.today())
        self.db.commit()

    def submit_validation(self, user: User, request: ValidationRequest) -> None:
        if len(request.summary.strip()) < 12:
            raise HTTPException(status_code=400, detail="验收总结至少 12 个字")
        if request.layer in {"demo", "project"} and len(request.evidence.strip()) < 8:
            raise HTTPException(status_code=400, detail="Demo / 项目任务需要填写可验证证据")
        chapter = self.content.get_chapter(request.chapter_no)
        self.db.add(
            ValidationRecord(
                user_id=user.id,
                chapter_no=chapter.no,
                chapter_title=chapter.title,
                layer_name=request.layer,
                summary=request.summary.strip(),
                evidence=request.evidence.strip(),
            )
        )
        if request.layer == "project":
            self.db.add(
                PortfolioEvidence(
                    user_id=user.id,
                    chapter_no=chapter.no,
                    milestone=self._milestone(chapter),
                    evidence_type="project",
                    body=request.evidence.strip(),
                )
            )
        self.db.commit()
        self.update_progress(user, ProgressRequest(chapterNo=request.chapter_no, layer=request.layer, done=True))

    def reviews(self, user: User) -> list[dict]:
        rows = self.db.scalars(
            select(ReviewTask)
            .where(ReviewTask.user_id == user.id)
            .order_by(ReviewTask.due_date.asc(), ReviewTask.chapter_no.asc())
        )
        return [self._review_to_dict(row) for row in rows]

    def complete_review(self, user: User, task_id: Optional[int] = None, request: Optional[ReviewCompleteRequest] = None) -> None:
        if task_id is not None:
            task = self.db.get(ReviewTask, task_id)
            if task is None or task.user_id != user.id:
                raise HTTPException(status_code=404, detail="复习任务不存在")
            task.completed_at = datetime.utcnow()
            self._append_log(user, task.chapter_no, task.title, "review", "完成复习")
            self.db.commit()
            return
        if request is None:
            raise HTTPException(status_code=400, detail="缺少章节号")
        for task in self.db.scalars(
            select(ReviewTask).where(ReviewTask.user_id == user.id, ReviewTask.chapter_no == request.chapter_no)
        ):
            task.completed_at = datetime.utcnow()
        progress = self._progress(user, request.chapter_no)
        progress.review_done = True
        self.db.commit()

    def due_cards(self, user: User) -> list[dict]:
        cards = self.db.scalars(
            select(ReviewCard)
            .where(ReviewCard.user_id == user.id, ReviewCard.due_date <= date.today(), ReviewCard.status == "due")
            .order_by(ReviewCard.due_date.asc(), ReviewCard.chapter_no.asc())
        )
        return [self._card_to_dict(card) for card in cards]

    def answer_card(self, user: User, card_id: int, request: CardAnswerRequest) -> list[dict]:
        card = self.db.get(ReviewCard, card_id)
        if card is None or card.user_id != user.id:
            raise HTTPException(status_code=404, detail="复习卡不存在")
        if request.remembered:
            card.status = "done"
        else:
            card.due_date = date.today() + timedelta(days=1)
            card.status = "due"
            self.db.add(
                Mistake(
                    user_id=user.id,
                    chapter_no=card.chapter_no,
                    chapter_title=card.chapter_title,
                    symptom=card.prompt,
                    reason="复习卡答错或回忆不完整",
                    fix_text="明天重做，并补充费曼解释",
                    next_review=str(card.due_date),
                )
            )
        self._append_log(user, card.chapter_no, card.chapter_title, "card", "记住复习卡" if request.remembered else "复习卡需加练")
        self.db.commit()
        return self.due_cards(user)

    def save_note(self, user: User, request: NoteRequest) -> None:
        self.db.add(Note(user_id=user.id, chapter_no=request.chapter_no, title=request.title, body=request.body))
        self._append_log(user, request.chapter_no, request.title, "note", "记录笔记")
        self.db.commit()

    def save_check_result(self, user: User, request: CheckResultRequest) -> None:
        self.db.add(
            CheckResult(
                user_id=user.id,
                chapter_no=request.chapter_no,
                chapter_title=request.chapter_title,
                answer=request.answer,
                passed=request.passed,
            )
        )
        self.db.add(
            Note(
                user_id=user.id,
                chapter_no=request.chapter_no,
                title=request.chapter_title,
                body=f"### 自测记录\n\n**结果**：{'自测通过' if request.passed else '自测需复习'}\n\n**我的答案**：\n\n{request.answer}",
            )
        )
        self._append_log(user, request.chapter_no, request.chapter_title, "check", "自测通过" if request.passed else "自测需复习")
        if request.passed:
            self.db.commit()
            self.update_progress(user, ProgressRequest(chapterNo=request.chapter_no, layer="check", done=True))
            return
        self.db.add(
            Mistake(
                user_id=user.id,
                chapter_no=request.chapter_no,
                chapter_title=request.chapter_title,
                symptom=request.symptom or "自测未通过",
                reason=request.reason or "自评为需复习",
                fix_text=request.fix or "回看理论、重做 Demo，并在下次复习复盘",
                next_review=str(date.today() + timedelta(days=1)),
            )
        )
        self.db.add(
            ReviewCard(
                user_id=user.id,
                chapter_no=request.chapter_no,
                chapter_title=request.chapter_title,
                card_type="错题",
                prompt=request.symptom or "自测未通过",
                expected=request.fix or "回看理论、重做 Demo，并在下次复习复盘",
                due_date=date.today(),
            )
        )
        self.db.commit()

    def reveal_answer(self, user: User, request: CheckRevealRequest) -> None:
        self._append_log(user, request.chapter_no, request.chapter_title, "check", "查看参考答案")
        self.db.commit()

    def portfolio(self, user: User) -> dict:
        evidence = self.db.scalars(
            select(PortfolioEvidence).where(PortfolioEvidence.user_id == user.id).order_by(PortfolioEvidence.created_at.desc())
        )
        items = [self._evidence_to_dict(item) for item in evidence]
        return {
            "totalEvidence": len(items),
            "milestones": [
                "Day 10 Python SE 小项目",
                "Day 20 工具库项目",
                "Day 30 OOP 设计项目",
                "Day 40 并发爬虫项目",
                "Day 50 AI 助手 API",
                "Day 55 完整微服务项目",
            ],
            "evidence": items,
        }

    def save_portfolio_evidence(self, user: User, request: PortfolioEvidenceRequest) -> dict:
        if len(request.body.strip()) < 8:
            raise HTTPException(status_code=400, detail="作品集证据至少 8 个字")
        self.db.add(
            PortfolioEvidence(
                user_id=user.id,
                chapter_no=request.chapter_no,
                milestone=request.milestone,
                evidence_type=request.evidence_type,
                body=request.body.strip(),
            )
        )
        self.db.commit()
        return self.portfolio(user)

    def _progress(self, user: User, chapter_no: int) -> ChapterProgress:
        progress = self.db.scalar(
            select(ChapterProgress).where(ChapterProgress.user_id == user.id, ChapterProgress.chapter_no == chapter_no)
        )
        if progress is None:
            progress = ChapterProgress(user_id=user.id, chapter_no=chapter_no)
            self.db.add(progress)
            self.db.flush()
        return progress

    def _ensure_reviews(self, user: User, chapter: CourseChapter, finished: date) -> None:
        for label, days in [("+3", 3), ("+7", 7), ("+30", 30)]:
            exists = self.db.scalar(
                select(ReviewTask).where(
                    ReviewTask.user_id == user.id,
                    ReviewTask.chapter_no == chapter.no,
                    ReviewTask.review_round == label,
                )
            )
            if exists is None:
                self.db.add(
                    ReviewTask(
                        user_id=user.id,
                        chapter_no=chapter.no,
                        title=chapter.title,
                        review_round=label,
                        due_date=finished + timedelta(days=days),
                    )
                )

    def _append_log(self, user: User, chapter_no: Optional[int], title: Optional[str], layer: str, action: str) -> None:
        self.db.add(
            StudyLog(
                user_id=user.id,
                chapter_no=chapter_no,
                chapter_title=title,
                layer_name=layer,
                log_action=action,
                minutes="",
                reflection="",
            )
        )

    def _chapter_meta(self, chapter: CourseChapter, progress: Optional[ChapterProgress]) -> dict:
        progress_dict = {
            "theory": bool(progress and progress.theory_done),
            "demo": bool(progress and progress.demo_done),
            "check": bool(progress and progress.check_done),
            "project": bool(progress and progress.project_done),
            "review": bool(progress and progress.review_done),
        }
        return {
            "no": chapter.no,
            "title": chapter.title,
            "summary": chapter.summary,
            "priority": chapter.priority,
            "hours": chapter.hours,
            "folder": chapter.folder,
            "routeStatus": chapter.route_status,
            "finished": progress.finished_date.isoformat() if progress and progress.finished_date else "",
            "progress": progress_dict,
        }

    @staticmethod
    def _core_done(progress: dict) -> bool:
        return progress["theory"] and progress["demo"] and progress["check"] and progress["project"]

    @staticmethod
    def _review_to_dict(task: ReviewTask) -> dict:
        return {
            "id": str(task.id),
            "chapterNo": task.chapter_no,
            "title": task.title,
            "round": task.review_round,
            "dueDate": task.due_date.isoformat(),
            "status": "done" if task.completed_at else "due",
            "due": task.completed_at is None and task.due_date <= date.today(),
        }

    @staticmethod
    def _card_to_dict(card: ReviewCard) -> dict:
        return {
            "id": card.id,
            "chapterNo": card.chapter_no,
            "chapterTitle": card.chapter_title,
            "type": card.card_type,
            "prompt": card.prompt,
            "expected": card.expected,
            "dueDate": card.due_date.isoformat(),
            "status": card.status,
        }

    @staticmethod
    def _evidence_to_dict(item: PortfolioEvidence) -> dict:
        return {
            "id": item.id,
            "chapterNo": item.chapter_no,
            "milestone": item.milestone,
            "evidenceType": item.evidence_type,
            "body": item.body,
            "createdAt": item.created_at.isoformat(),
        }

    @staticmethod
    def _log_to_dict(log: StudyLog) -> dict:
        return {
            "date": log.created_at.date().isoformat(),
            "chapter": log.chapter_title or "",
            "layer": log.layer_name,
            "action": log.log_action,
            "minutes": log.minutes or "",
            "reflection": log.reflection or "",
        }

    @staticmethod
    def _milestone(chapter: CourseChapter) -> str:
        return f"Day {chapter.no:02d} {chapter.title}"
