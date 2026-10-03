from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import auth, interview, learning
from .database import Base, make_session_factory
from .interview_service import seed_interview_questions


def create_app(
    database_url: Optional[str] = None,
    content_root: Optional[Union[str, Path]] = None,
) -> FastAPI:
    app = FastAPI(title="Python FastAPI Learning Workbench")
    # 允许通过环境变量追加来源；默认放开全部，方便同一台服务器上的 Nginx 反代与本地联调
    extra_origins = [
        origin.strip()
        for origin in os.environ.get("PYTHON_WORKBENCH_CORS_ORIGINS", "*").split(",")
        if origin.strip()
    ]
    if "*" in extra_origins:
        allow_origins = ["*"]
        allow_credentials = False
    else:
        allow_origins = ["http://localhost:5173", "http://127.0.0.1:5173", *extra_origins]
        allow_credentials = True
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    root = Path(content_root or os.environ.get("PYTHON_WORKBENCH_CONTENT_ROOT", Path(__file__).resolve().parents[2])).resolve()
    db_url = database_url or os.environ.get("PYTHON_WORKBENCH_DATABASE_URL", f"sqlite:///{root / 'python-workbench.db'}")
    session_factory = make_session_factory(db_url)
    Base.metadata.create_all(session_factory.kw["bind"])
    with session_factory() as db:
        seed_interview_questions(db)
    app.state.session_factory = session_factory
    app.state.content_root = root
    app.include_router(auth.router)
    app.include_router(learning.router)
    app.include_router(interview.router)

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "ok", "framework": "FastAPI", "track": "Python + AI backend"}

    return app


app = create_app()
