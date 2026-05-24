# Chapter 45 Project: FastAPI AI Chat Gateway

## Goal

实现一个 FastAPI AI 网关原型，重点练习认证、统一错误、流式响应、后台任务和服务分层。

## Required APIs

- `POST /chat`
- `GET /chat/stream`
- `GET /health`

## Commands

```bash
uvicorn app.main:app --reload
python -m pytest
```

## Acceptance

- API Key 认证可用。
- `/chat` 返回结构化 JSON。
- `/chat/stream` 返回 SSE 片段和完成事件。
- 模型调用通过 mock `ModelClient` 封装。
- 测试不依赖真实模型供应商。
