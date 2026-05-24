from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    from app.main import create_app

    app = create_app(
        database_url=f"sqlite:///{tmp_path / 'workbench.db'}",
        content_root=ROOT,
    )
    with TestClient(app) as test_client:
        yield test_client


def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/auth/register",
        json={"username": "python_ai_dev", "secret": "local-secret"},
    )
    assert response.status_code == 200
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_auth_and_course_content_are_available(client: TestClient) -> None:
    headers = auth_headers(client)

    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["username"] == "python_ai_dev"

    chapters = client.get("/api/chapters", headers=headers)
    assert chapters.status_code == 200
    assert len(chapters.json()) == 60
    assert chapters.json()[43]["title"] == "FastAPI入门"

    chapter = client.get("/api/chapters/44", headers=headers)
    assert chapter.status_code == 200
    body = chapter.json()
    assert body["no"] == 44
    assert "FastAPI" in body["content"]["theory"]
    assert set(body["content"]) == {"theory", "demo", "check", "project"}


def test_validation_completion_creates_reviews_and_portfolio_evidence(client: TestClient) -> None:
    headers = auth_headers(client)

    theory = client.post(
        "/api/validations",
        headers=headers,
        json={
            "chapterNo": 44,
            "layer": "theory",
            "summary": "我能解释 FastAPI 路由、Pydantic 模型和自动文档之间的关系。",
            "evidence": "",
        },
    )
    assert theory.status_code == 200

    demo = client.post(
        "/api/validations",
        headers=headers,
        json={
            "chapterNo": 44,
            "layer": "demo",
            "summary": "我跑通了 FastAPI Demo 并理解请求响应流程。",
            "evidence": "uvicorn app.main:app --reload 返回 200",
        },
    )
    assert demo.status_code == 200

    check = client.post(
        "/api/check-result",
        headers=headers,
        json={
            "chapterNo": 44,
            "chapterTitle": "FastAPI入门",
            "answer": "路径函数负责接收请求，Pydantic 负责请求和响应模型校验。",
            "passed": True,
            "symptom": "",
            "reason": "",
            "fix": "",
        },
    )
    assert check.status_code == 200

    project = client.post(
        "/api/validations",
        headers=headers,
        json={
            "chapterNo": 44,
            "layer": "project",
            "summary": "我完成了一个最小 FastAPI 接口并保留了运行证据。",
            "evidence": "projects/chapter-44 README 记录接口、命令和响应",
        },
    )
    assert project.status_code == 200

    reviews = client.get("/api/reviews", headers=headers)
    assert reviews.status_code == 200
    assert [task["round"] for task in reviews.json()] == ["+3", "+7", "+30"]

    portfolio = client.get("/api/portfolio", headers=headers)
    assert portfolio.status_code == 200
    assert portfolio.json()["totalEvidence"] == 1
    assert portfolio.json()["evidence"][0]["chapterNo"] == 44


def test_failed_self_check_creates_mistake_card(client: TestClient) -> None:
    headers = auth_headers(client)

    response = client.post(
        "/api/check-result",
        headers=headers,
        json={
            "chapterNo": 45,
            "chapterTitle": "FastAPI进阶",
            "answer": "我还分不清依赖注入和中间件。",
            "passed": False,
            "symptom": "依赖注入和中间件边界不清",
            "reason": "没有画出请求生命周期",
            "fix": "重看 Demo 并补一张流程图",
        },
    )
    assert response.status_code == 200

    cards = client.get("/api/cards/due", headers=headers)
    assert cards.status_code == 200
    assert len(cards.json()) == 1
    assert cards.json()[0]["chapterNo"] == 45
    assert cards.json()[0]["status"] == "due"


def test_interview_questions_and_attempts_are_ai_ready(client: TestClient) -> None:
    headers = auth_headers(client)

    categories = client.get("/api/interview/categories", headers=headers)
    assert categories.status_code == 200
    labels = {item["label"] for item in categories.json()}
    assert {"Python 基础", "FastAPI 后端", "AI 应用后端"} <= labels

    questions = client.get("/api/interview/questions?category=ai_backend", headers=headers)
    assert questions.status_code == 200
    assert questions.json()
    question_id = questions.json()[0]["id"]

    attempt = client.post(
        "/api/interview/attempts",
        headers=headers,
        json={
            "questionId": question_id,
            "answer": "我会把模型调用封装在 service 层，用流式响应返回 token，并记录请求日志。",
            "selfAssessed": "partial",
        },
    )
    assert attempt.status_code == 200
    assert attempt.json()["aiScore"] >= 60
    assert "AI 评分占位" in attempt.json()["aiFeedback"]
