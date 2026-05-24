from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import current_user
from ..database import get_db
from ..interview_service import InterviewService
from ..models import User
from ..schemas import InterviewAttemptRequest


router = APIRouter(prefix="/api/interview", tags=["interview"])


def service(db: Session = Depends(get_db)) -> InterviewService:
    return InterviewService(db)


@router.get("/categories")
def categories(user: User = Depends(current_user), svc: InterviewService = Depends(service)) -> list[dict]:
    return svc.categories(user)


@router.get("/questions")
def questions(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    frequency: Optional[str] = None,
    q: Optional[str] = None,
    user: User = Depends(current_user),
    svc: InterviewService = Depends(service),
) -> list[dict]:
    return svc.questions(user, category, difficulty, frequency, q)


@router.get("/questions/{question_id}")
def question(question_id: int, user: User = Depends(current_user), svc: InterviewService = Depends(service)) -> dict:
    return svc.question(user, question_id)


@router.post("/attempts")
def attempts(request: InterviewAttemptRequest, user: User = Depends(current_user), svc: InterviewService = Depends(service)) -> dict:
    return svc.submit_attempt(user, request)


@router.get("/stats")
def stats(user: User = Depends(current_user), svc: InterviewService = Depends(service)) -> dict:
    return svc.stats(user)
