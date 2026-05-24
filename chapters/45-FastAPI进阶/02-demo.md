# 第45章：FastAPI 进阶 — Demo

## Demo 1：统一依赖和错误响应

```python
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="AI API Demo")


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "request_id": request.headers.get("x-request-id"),
        },
    )


def require_api_key(authorization: str | None = Header(default=None)):
    if authorization != "Bearer dev-token":
        raise AppError("AUTH_REQUIRED", "缺少或无效的 API Key", 401)


@app.get("/secure-health", dependencies=[Depends(require_api_key)])
def secure_health():
    return {"status": "ok"}
```

验证：

```bash
uvicorn main:app --reload
curl http://127.0.0.1:8000/secure-health
curl -H "Authorization: Bearer dev-token" http://127.0.0.1:8000/secure-health
```

## Demo 2：流式聊天接口

```python
import asyncio
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()


async def model_stream(prompt: str) -> AsyncIterator[str]:
    words = ["收到：", prompt, "\n", "正在", "生成", "回答"]
    for word in words:
        await asyncio.sleep(0.2)
        yield f"data: {word}\n\n"
    yield "event: done\ndata: [DONE]\n\n"


@app.get("/chat/stream")
async def chat_stream(prompt: str):
    return StreamingResponse(
        model_stream(prompt),
        media_type="text/event-stream",
    )
```

验证：

```bash
curl -N "http://127.0.0.1:8000/chat/stream?prompt=hello"
```

观察重点：

- `curl -N` 可以看到分块返回。
- 每条消息使用 SSE 格式：`data: ...\n\n`。
- 最后用 `event: done` 告诉前端完成。

## Demo 3：后台任务记录模型调用

```python
from datetime import datetime
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

app = FastAPI()
LOG_FILE = Path("model-calls.log")


class ChatRequest(BaseModel):
    prompt: str


def write_call_log(prompt: str, answer: str) -> None:
    LOG_FILE.write_text(
        f"{datetime.now().isoformat()} | {prompt} | {answer}\n",
        encoding="utf-8",
    )


@app.post("/chat")
def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    answer = f"模拟回答：{request.prompt}"
    background_tasks.add_task(write_call_log, request.prompt, answer)
    return {"answer": answer}
```

复盘：

- 这个任务丢失是否可接受？
- 如果日志必须可靠保存，应该换成什么架构？
- 如果任务耗时 5 分钟，为什么不应该用 BackgroundTasks？

## Demo 4：AI 服务分层的最小结构

```python
from pydantic import BaseModel


class ChatInput(BaseModel):
    prompt: str
    temperature: float = 0.2


class ChatOutput(BaseModel):
    answer: str
    model: str


class ModelClient:
    def generate(self, prompt: str, temperature: float) -> str:
        return f"answer for: {prompt}, temperature={temperature}"


class ChatService:
    def __init__(self, model_client: ModelClient):
        self.model_client = model_client

    def chat(self, data: ChatInput) -> ChatOutput:
        answer = self.model_client.generate(data.prompt, data.temperature)
        return ChatOutput(answer=answer, model="mock-model")
```

这段代码的重点不是模型能力，而是服务边界：

- `ChatInput` 和 `ChatOutput` 管接口结构。
- `ModelClient` 管外部模型调用。
- `ChatService` 管业务编排。
- FastAPI Router 只负责 HTTP。
