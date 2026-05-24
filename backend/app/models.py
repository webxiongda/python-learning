from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def now() -> datetime:
    return datetime.utcnow()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    secret_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class ChapterProgress(Base):
    __tablename__ = "chapter_progress"
    __table_args__ = (UniqueConstraint("user_id", "chapter_no", name="uk_progress_user_chapter"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    chapter_no: Mapped[int] = mapped_column(Integer, index=True)
    theory_done: Mapped[bool] = mapped_column(Boolean, default=False)
    demo_done: Mapped[bool] = mapped_column(Boolean, default=False)
    check_done: Mapped[bool] = mapped_column(Boolean, default=False)
    project_done: Mapped[bool] = mapped_column(Boolean, default=False)
    review_done: Mapped[bool] = mapped_column(Boolean, default=False)
    finished_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    def core_done(self) -> bool:
        return self.theory_done and self.demo_done and self.check_done and self.project_done

    def set_layer(self, layer: str, done: bool) -> None:
        mapping = {
            "theory": "theory_done",
            "demo": "demo_done",
            "check": "check_done",
            "project": "project_done",
            "review": "review_done",
        }
        if layer not in mapping:
            raise ValueError(f"Unknown layer: {layer}")
        setattr(self, mapping[layer], done)


class ReviewTask(Base):
    __tablename__ = "review_tasks"
    __table_args__ = (UniqueConstraint("user_id", "chapter_no", "review_round", name="uk_review_round"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    chapter_no: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(255))
    review_round: Mapped[str] = mapped_column(String(16))
    due_date: Mapped[date] = mapped_column(Date)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    chapter_no: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class CheckResult(Base):
    __tablename__ = "check_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    chapter_no: Mapped[int] = mapped_column(Integer, index=True)
    chapter_title: Mapped[str] = mapped_column(String(255))
    answer: Mapped[str] = mapped_column(Text)
    passed: Mapped[bool] = mapped_column(Boolean)
    revealed_answer: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Mistake(Base):
    __tablename__ = "mistakes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    chapter_no: Mapped[int] = mapped_column(Integer, index=True)
    chapter_title: Mapped[str] = mapped_column(String(255))
    symptom: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(Text)
    fix_text: Mapped[str] = mapped_column(Text)
    next_review: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class StudyLog(Base):
    __tablename__ = "study_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    chapter_no: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    chapter_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    layer_name: Mapped[str] = mapped_column(String(32))
    log_action: Mapped[str] = mapped_column(String(64))
    minutes: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    reflection: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class ValidationRecord(Base):
    __tablename__ = "validation_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    chapter_no: Mapped[int] = mapped_column(Integer, index=True)
    chapter_title: Mapped[str] = mapped_column(String(255))
    layer_name: Mapped[str] = mapped_column(String(32))
    summary: Mapped[str] = mapped_column(Text)
    evidence: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class ReviewCard(Base):
    __tablename__ = "review_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    chapter_no: Mapped[int] = mapped_column(Integer, index=True)
    chapter_title: Mapped[str] = mapped_column(String(255))
    card_type: Mapped[str] = mapped_column(String(64))
    prompt: Mapped[str] = mapped_column(Text)
    expected: Mapped[str] = mapped_column(Text)
    due_date: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(32), default="due")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class PortfolioEvidence(Base):
    __tablename__ = "portfolio_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    chapter_no: Mapped[int] = mapped_column(Integer, index=True)
    milestone: Mapped[str] = mapped_column(String(255))
    evidence_type: Mapped[str] = mapped_column(String(64))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(64), index=True)
    label: Mapped[str] = mapped_column(String(64))
    difficulty: Mapped[str] = mapped_column(String(32))
    frequency: Mapped[str] = mapped_column(String(32))
    prompt: Mapped[str] = mapped_column(Text, unique=True)
    reference_answer: Mapped[str] = mapped_column(Text)
    follow_up: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    related_chapter_no: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    related_chapter_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="built-in")

    attempts: Mapped[list["InterviewAttempt"]] = relationship(back_populates="question")


class InterviewAttempt(Base):
    __tablename__ = "interview_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("interview_questions.id", ondelete="CASCADE"), index=True)
    answer: Mapped[str] = mapped_column(Text)
    self_assessed: Mapped[str] = mapped_column(String(32))
    ai_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ai_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

    question: Mapped[InterviewQuestion] = relationship(back_populates="attempts")
