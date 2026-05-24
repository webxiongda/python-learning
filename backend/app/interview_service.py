from __future__ import annotations

from collections import defaultdict
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import InterviewAttempt, InterviewQuestion, User
from .schemas import InterviewAttemptRequest


SEED_QUESTIONS = [
    {
        "category": "python_core",
        "label": "Python 基础",
        "difficulty": "medium",
        "frequency": "high",
        "prompt": "解释 Python 可变对象作为默认参数的风险，并给出修复方式。",
        "reference_answer": "默认参数在函数定义时创建一次，可变对象会被多次调用共享。应使用 None 作为默认值，在函数内部创建新对象。",
        "follow_up": "这和闭包、作用域有什么关系？",
        "related_chapter_no": 4,
        "related_chapter_title": "函数基础",
    },
    {
        "category": "fastapi",
        "label": "FastAPI 后端",
        "difficulty": "medium",
        "frequency": "high",
        "prompt": "FastAPI 的 Depends 适合放哪些逻辑？哪些逻辑不应该放进去？",
        "reference_answer": "Depends 适合认证、数据库 session、参数解析、共享依赖。复杂业务规则应放在 service 层，避免路由和依赖函数过重。",
        "follow_up": "如何测试依赖注入中的数据库 session？",
        "related_chapter_no": 45,
        "related_chapter_title": "FastAPI进阶",
    },
    {
        "category": "ai_backend",
        "label": "AI 应用后端",
        "difficulty": "hard",
        "frequency": "high",
        "prompt": "设计一个支持流式输出的 AI 聊天接口时，你会如何划分 Controller、Service 和模型适配层？",
        "reference_answer": "路由层只处理 HTTP/SSE 协议和鉴权，Service 编排会话、限流、日志和工具调用，模型适配层封装供应商 SDK 和流式事件转换。",
        "follow_up": "如果后续加入 RAG，哪些边界需要保持稳定？",
        "related_chapter_no": 50,
        "related_chapter_title": "里程碑：AI助手API项目",
    },
]


def seed_interview_questions(db: Session) -> None:
    if db.scalar(select(func.count(InterviewQuestion.id))) > 0:
        return
    for item in SEED_QUESTIONS:
        db.add(InterviewQuestion(source="built-in", **item))
    db.commit()


class InterviewService:
    def __init__(self, db: Session):
        self.db = db

    def categories(self, user: User) -> list[dict]:
        questions = list(self.db.scalars(select(InterviewQuestion).order_by(InterviewQuestion.category.asc())))
        attempts = list(self.db.scalars(select(InterviewAttempt).where(InterviewAttempt.user_id == user.id)))
        attempted_ids = {attempt.question_id for attempt in attempts}
        mastered_ids = {attempt.question_id for attempt in attempts if (attempt.ai_score or 0) >= 80}
        grouped: dict[str, list[InterviewQuestion]] = defaultdict(list)
        for question in questions:
            grouped[question.category].append(question)
        return [
            {
                "category": category,
                "label": items[0].label,
                "total": len(items),
                "attempted": sum(1 for item in items if item.id in attempted_ids),
                "mastered": sum(1 for item in items if item.id in mastered_ids),
            }
            for category, items in grouped.items()
        ]

    def questions(
        self,
        user: User,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        frequency: Optional[str] = None,
        q: Optional[str] = None,
    ) -> list[dict]:
        statement = select(InterviewQuestion).order_by(InterviewQuestion.category.asc(), InterviewQuestion.id.asc())
        if category:
            statement = statement.where(InterviewQuestion.category == category)
        if difficulty:
            statement = statement.where(InterviewQuestion.difficulty == difficulty)
        if frequency:
            statement = statement.where(InterviewQuestion.frequency == frequency)
        if q:
            statement = statement.where(InterviewQuestion.prompt.contains(q))
        attempted = {
            attempt.question_id: attempt
            for attempt in self.db.scalars(select(InterviewAttempt).where(InterviewAttempt.user_id == user.id))
        }
        return [self._list_item(question, attempted) for question in self.db.scalars(statement)]

    def question(self, user: User, question_id: int) -> dict:
        question = self.db.get(InterviewQuestion, question_id)
        if question is None:
            raise HTTPException(status_code=404, detail="面试题不存在")
        attempts = self.db.scalars(
            select(InterviewAttempt)
            .where(InterviewAttempt.user_id == user.id, InterviewAttempt.question_id == question_id)
            .order_by(InterviewAttempt.created_at.desc())
            .limit(5)
        )
        return {
            **self._question_base(question),
            "referenceAnswer": question.reference_answer,
            "followUp": question.follow_up,
            "recentAttempts": [self._attempt_to_dict(attempt) for attempt in attempts],
        }

    def submit_attempt(self, user: User, request: InterviewAttemptRequest) -> dict:
        question = self.db.get(InterviewQuestion, request.question_id)
        if question is None:
            raise HTTPException(status_code=404, detail="面试题不存在")
        if len(request.answer.strip()) < 12:
            raise HTTPException(status_code=400, detail="回答至少 12 个字")
        score = self._score_answer(request.answer)
        feedback = f"AI 评分占位：当前为本地规则评分 {score} 分。后续可替换为模型评分、追问生成和结构化反馈。"
        attempt = InterviewAttempt(
            user_id=user.id,
            question_id=question.id,
            answer=request.answer.strip(),
            self_assessed=request.self_assessed,
            ai_score=score,
            ai_feedback=feedback,
        )
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return self._attempt_to_dict(attempt)

    def stats(self, user: User) -> dict:
        attempts = list(self.db.scalars(select(InterviewAttempt).where(InterviewAttempt.user_id == user.id)))
        mastered = sum(1 for attempt in attempts if (attempt.ai_score or 0) >= 80)
        return {"attempted": len({attempt.question_id for attempt in attempts}), "mastered": mastered, "totalAttempts": len(attempts)}

    def _list_item(self, question: InterviewQuestion, attempts: dict[int, InterviewAttempt]) -> dict:
        attempt = attempts.get(question.id)
        return {
            **self._question_base(question),
            "attempted": attempt is not None,
            "mastered": bool(attempt and (attempt.ai_score or 0) >= 80),
        }

    @staticmethod
    def _question_base(question: InterviewQuestion) -> dict:
        return {
            "id": question.id,
            "category": question.category,
            "difficulty": question.difficulty,
            "frequency": question.frequency,
            "prompt": question.prompt,
            "relatedChapterNo": question.related_chapter_no,
            "relatedChapterTitle": question.related_chapter_title,
            "source": question.source,
        }

    @staticmethod
    def _attempt_to_dict(attempt: InterviewAttempt) -> dict:
        return {
            "id": attempt.id,
            "answer": attempt.answer,
            "selfAssessed": attempt.self_assessed,
            "aiScore": attempt.ai_score,
            "aiFeedback": attempt.ai_feedback,
            "createdAt": attempt.created_at.isoformat(),
        }

    @staticmethod
    def _score_answer(answer: str) -> int:
        score = 60
        keywords = ["service", "stream", "流式", "日志", "模型", "RAG", "工具", "FastAPI", "SSE"]
        score += min(30, sum(6 for keyword in keywords if keyword.lower() in answer.lower()))
        if len(answer) >= 80:
            score += 10
        return min(score, 100)
