from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CamelModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class AuthRequest(CamelModel):
    username: str
    secret: str


class ProgressRequest(CamelModel):
    chapter_no: int = Field(alias="chapterNo")
    layer: str
    done: bool


class ValidationRequest(CamelModel):
    chapter_no: int = Field(alias="chapterNo")
    layer: str
    summary: str
    evidence: str = ""


class ReviewCompleteRequest(CamelModel):
    chapter_no: int = Field(alias="chapterNo")


class NoteRequest(CamelModel):
    chapter_no: int = Field(alias="chapterNo")
    title: str
    body: str


class CheckResultRequest(CamelModel):
    chapter_no: int = Field(alias="chapterNo")
    chapter_title: str = Field(alias="chapterTitle")
    answer: str
    passed: bool
    symptom: str = ""
    reason: str = ""
    fix: str = ""


class CheckRevealRequest(CamelModel):
    chapter_no: int = Field(alias="chapterNo")
    chapter_title: str = Field(alias="chapterTitle")


class CardAnswerRequest(CamelModel):
    answer: str = ""
    remembered: bool


class PortfolioEvidenceRequest(CamelModel):
    chapter_no: int = Field(alias="chapterNo")
    milestone: str
    evidence_type: str = Field(default="manual", alias="evidenceType")
    body: str


class InterviewAttemptRequest(CamelModel):
    question_id: int = Field(alias="questionId")
    answer: str
    self_assessed: str = Field(alias="selfAssessed")
