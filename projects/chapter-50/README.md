# Chapter 50 Project: 博客 REST API

## Goal

实现一个完整 FastAPI 博客 API，作为第一层主线的核心验收项目。

## Required APIs

- `POST /auth/register`
- `POST /auth/login`
- `GET /posts`
- `POST /posts`
- `GET /posts/{id}`
- `PATCH /posts/{id}`
- `DELETE /posts/{id}`
- `GET /users/{id}`

## Commands

```bash
uvicorn app.main:app --reload
python -m pytest
```

## Acceptance

- `/docs` 可访问。
- 注册、登录、文章 CRUD、分页、未授权、越权、404 都有测试。
- 响应不泄露密码或 password hash。
