from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..auth import current_user
from ..course_content import CourseContent
from ..database import get_db
from ..learning_service import LearningService
from ..models import User
from ..schemas import (
    CardAnswerRequest,
    CheckResultRequest,
    CheckRevealRequest,
    NoteRequest,
    PortfolioEvidenceRequest,
    ProgressRequest,
    ReviewCompleteRequest,
    ValidationRequest,
)


router = APIRouter(prefix="/api", tags=["learning"])


def service(request: Request, db: Session = Depends(get_db)) -> LearningService:
    return LearningService(db, CourseContent(request.app.state.content_root))


@router.get("/summary")
def summary(user: User = Depends(current_user), svc: LearningService = Depends(service)) -> dict:
    return svc.summary(user)


@router.get("/today")
def today(user: User = Depends(current_user), svc: LearningService = Depends(service)) -> dict:
    return svc.today(user)


@router.get("/chapters")
def chapters(user: User = Depends(current_user), svc: LearningService = Depends(service)) -> list[dict]:
    return svc.chapters(user)


@router.get("/chapters/{chapter_no}")
def chapter(chapter_no: int, user: User = Depends(current_user), svc: LearningService = Depends(service)) -> dict:
    return svc.chapter(user, chapter_no)


@router.patch("/progress")
def progress(request: ProgressRequest, user: User = Depends(current_user), svc: LearningService = Depends(service)) -> dict:
    svc.update_progress(user, request)
    return {"ok": True}


@router.post("/validations")
def validations(request: ValidationRequest, user: User = Depends(current_user), svc: LearningService = Depends(service)) -> dict:
    svc.submit_validation(user, request)
    return {"ok": True}


@router.get("/reviews")
def reviews(user: User = Depends(current_user), svc: LearningService = Depends(service)) -> list[dict]:
    return svc.reviews(user)


@router.patch("/reviews")
def complete_reviews(request: ReviewCompleteRequest, user: User = Depends(current_user), svc: LearningService = Depends(service)) -> list[dict]:
    svc.complete_review(user, request=request)
    return svc.reviews(user)


@router.patch("/reviews/{task_id}")
def complete_review(task_id: int, user: User = Depends(current_user), svc: LearningService = Depends(service)) -> list[dict]:
    svc.complete_review(user, task_id=task_id)
    return svc.reviews(user)


@router.get("/cards/due")
def due_cards(user: User = Depends(current_user), svc: LearningService = Depends(service)) -> list[dict]:
    return svc.due_cards(user)


@router.post("/cards/{card_id}/answer")
def answer_card(card_id: int, request: CardAnswerRequest, user: User = Depends(current_user), svc: LearningService = Depends(service)) -> list[dict]:
    return svc.answer_card(user, card_id, request)


@router.post("/notes")
def notes(request: NoteRequest, user: User = Depends(current_user), svc: LearningService = Depends(service)) -> dict:
    svc.save_note(user, request)
    return {"ok": True}


@router.post("/check-result")
def check_result(request: CheckResultRequest, user: User = Depends(current_user), svc: LearningService = Depends(service)) -> dict:
    svc.save_check_result(user, request)
    return {"ok": True}


@router.post("/check-reveals")
def check_reveal(request: CheckRevealRequest, user: User = Depends(current_user), svc: LearningService = Depends(service)) -> dict:
    svc.reveal_answer(user, request)
    return {"ok": True}


@router.get("/portfolio")
def portfolio(user: User = Depends(current_user), svc: LearningService = Depends(service)) -> dict:
    return svc.portfolio(user)


@router.post("/portfolio/evidence")
def portfolio_evidence(request: PortfolioEvidenceRequest, user: User = Depends(current_user), svc: LearningService = Depends(service)) -> dict:
    return svc.save_portfolio_evidence(user, request)
