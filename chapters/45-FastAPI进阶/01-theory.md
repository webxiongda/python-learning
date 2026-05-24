# 第45章：FastAPI 进阶 — AI 应用后端重点

## 1. 本章定位

如果你已有 Java 后端基础，学习 FastAPI 不需要把时间花在“Web 是什么”上，而要重点掌握它如何高效承接 AI 应用：

- 对外提供结构清晰的 REST API。
- 对模型调用做超时、重试、限流、错误包装。
- 用 SSE / StreamingResponse 输出模型流式结果。
- 用 BackgroundTasks 或任务队列处理文档解析、嵌入生成、批量任务。
- 用依赖注入统一管理认证、数据库会话、模型客户端和配置。

## 2. FastAPI 进阶能力地图

| 能力 | AI 应用中的作用 | 必须掌握 |
|------|----------------|----------|
| Depends | 注入当前用户、数据库会话、模型客户端 | 是 |
| Middleware | 记录请求耗时、trace_id、统一 CORS | 是 |
| Exception Handler | 把模型错误、限流错误、权限错误转成统一响应 | 是 |
| BackgroundTasks | 轻量异步后处理，如写日志、发送通知、触发短任务 | 是 |
| StreamingResponse | 返回模型 token 流或进度流 | 是 |
| WebSocket | 双向实时交互，例如实时语音、协同状态 | 了解 |
| Lifespan | 初始化模型客户端、连接池、缓存 | 是 |

## 3. 依赖注入：把基础设施从业务里拿出去

AI 应用最容易写乱的地方是把 API Key、模型客户端、数据库、当前用户都塞进路由函数。FastAPI 的 `Depends` 可以把这些横切能力拆出去。

```python
from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI()


class Settings:
    model_name = "gpt-5"
    request_timeout = 30


def get_settings() -> Settings:
    return Settings()


def get_api_key(authorization: str | None = Header(default=None)) -> str:
    if authorization != "Bearer dev-token":
        raise HTTPException(status_code=401, detail="invalid api key")
    return authorization


@app.get("/health")
def health(settings: Settings = Depends(get_settings)):
    return {"status": "ok", "model": settings.model_name}
```

项目中建议形成固定依赖：

- `get_settings()`：读取配置。
- `get_current_user()`：认证和用户上下文。
- `get_db()`：数据库会话。
- `get_model_client()`：模型供应商客户端。
- `get_request_id()`：日志追踪 ID。

## 4. 统一错误响应

AI 接口不能把模型供应商的原始异常直接抛给前端。建议统一响应格式：

```json
{
  "code": "MODEL_TIMEOUT",
  "message": "模型响应超时，请稍后重试",
  "request_id": "req_123"
}
```

常见错误码：

- `AUTH_REQUIRED`：缺少认证。
- `RATE_LIMITED`：请求过快。
- `MODEL_TIMEOUT`：模型响应超时。
- `MODEL_PROVIDER_ERROR`：模型供应商异常。
- `VALIDATION_ERROR`：请求参数错误。
- `TASK_NOT_FOUND`：异步任务不存在。

## 5. 流式响应：AI 聊天接口的关键体验

AI 应用中，等待完整回答再返回会让用户感觉卡顿。流式响应可以边生成边返回。FastAPI 可以用 `StreamingResponse` 输出 Server-Sent Events。

```python
from collections.abc import AsyncIterator
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()


async def fake_model_stream(prompt: str) -> AsyncIterator[str]:
    for word in ["你好，", "这是", "流式", "响应。"]:
        yield f"data: {word}\n\n"


@app.get("/chat/stream")
async def chat_stream(prompt: str):
    return StreamingResponse(
        fake_model_stream(prompt),
        media_type="text/event-stream",
    )
```

流式接口必须额外考虑：

- 客户端断开连接时如何停止生成。
- 日志如何记录完整请求。
- 是否需要先做内容安全检查。
- 错误发生在流中时如何通知前端。
- 是否需要保存完整回答到数据库。

## 6. BackgroundTasks：适合轻量后处理，不是任务队列

FastAPI 官方 BackgroundTasks 适合“响应返回后继续做一点轻量工作”，例如写审计日志、发送通知、落库补充字段。它不适合长时间、必须可靠完成的任务。

适合 BackgroundTasks：

- 写访问日志。
- 发送非关键通知。
- 保存模型调用统计。
- 触发短时间缓存刷新。

不适合 BackgroundTasks：

- 大文件解析。
- 长时间 RAG 索引构建。
- 付费任务结算。
- 必须失败重试的任务。

这些应该交给队列、Worker 或第 55 章微服务项目处理。

## 7. AI 应用接口分层

建议目录：

```text
app/
├── main.py
├── config.py
├── dependencies.py
├── errors.py
├── routers/
│   ├── chat.py
│   ├── documents.py
│   └── tasks.py
├── services/
│   ├── model_client.py
│   ├── chat_service.py
│   └── retrieval_service.py
└── schemas/
    ├── chat.py
    └── common.py
```

分层原则：

- Router：只处理 HTTP 入参、状态码和响应模型。
- Schema：定义请求、响应和错误结构。
- Service：编排业务流程，如调用模型、检索、保存记录。
- Client：封装外部模型供应商 SDK 或 HTTP API。
- Dependency：注入配置、用户、数据库、客户端。

## 8. 本章验收

学完本章后应能：

- 写出带认证依赖的 FastAPI 路由。
- 用中间件记录请求耗时和 request_id。
- 为模型调用错误设计统一错误响应。
- 写一个 SSE 流式聊天接口。
- 判断 BackgroundTasks 和任务队列的边界。
- 说明 AI 应用后端的目录结构和职责划分。
