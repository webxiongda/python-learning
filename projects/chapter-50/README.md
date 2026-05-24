# Chapter 50 Project: AI Assistant API

## Goal

实现一个完整 FastAPI AI 应用后端，作为第一层主线的核心验收项目。

## Required APIs

- `GET /health`
- `POST /chat`
- `GET /chat/stream`
- `POST /conversations`
- `GET /conversations/{id}`
- `POST /tasks/document-ingest`
- `GET /tasks/{id}`

## Commands

```bash
uvicorn app.main:app --reload
python -m pytest
```

## Acceptance

- `/docs` 可访问。
- 普通聊天、流式聊天、会话历史、任务状态、认证失败、模型超时都有测试。
- 模型调用通过 `ModelClient` 封装，不直接写在 Router 中。
- 响应不泄露 API Key 或模型 Key。
