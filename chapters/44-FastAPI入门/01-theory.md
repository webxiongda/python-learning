# 第44章：FastAPI 入门

## 0. Java 背景学习建议

如果你已经熟悉 Java / Spring Boot，可以这样类比 FastAPI：

| Spring Boot | FastAPI | 说明 |
|-------------|---------|------|
| Controller | Router / path operation | 处理 HTTP 请求 |
| DTO / VO | Pydantic BaseModel | 请求和响应结构 |
| Bean 注入 | Depends | 依赖注入，但更函数式、更轻量 |
| Filter / Interceptor | Middleware / Dependency | 横切逻辑 |
| ExceptionHandler | exception_handler | 统一异常响应 |
| Swagger/OpenAPI | `/docs` / `/redoc` | 自动接口文档 |

学习 FastAPI 的关键不是“再学一套 Web”，而是掌握 Python 生态如何快速封装 AI 能力：模型调用、流式返回、任务状态、文件处理、向量检索和自动化工具接口。

## 1. FastAPI 简介

FastAPI 是基于 Python 类型注解的现代高性能 Web 框架，基于 Starlette（ASGI）和 Pydantic 构建。相比 Flask，它有几个核心优势：

```
Flask vs FastAPI 对比
═════════════════════════════════════════════════════════

  特性              Flask                FastAPI
  ────────────────────────────────────────────────────
  协议              WSGI（同步）          ASGI（异步/同步）
  类型支持           需要手动             原生 Python 类型注解
  数据验证           需要插件（WTForms）   Pydantic 内置
  自动文档           需要 flask-restx     内置 Swagger + ReDoc
  性能              中等                 极高（接近 NodeJS）
  学习曲线           较低                 中等
  生态成熟度          非常成熟             快速成长
```

```
FastAPI 请求处理流程
═══════════════════════════════════════════════════════════

  HTTP 请求
       │
       ▼
  ASGI Server (Uvicorn)
       │
       ▼
  Starlette（路由/中间件）
       │
       ▼
  FastAPI 路由匹配
       │
       ▼
  Pydantic 数据验证
  ┌────────────────────────────────┐
  │  路径参数 → Python 类型自动转换  │
  │  查询参数 → 类型验证            │
  │  请求体   → Pydantic 模型验证   │
  └────────────────────────────────┘
       │  验证失败 → 422 自动响应
       ▼
  依赖注入（Depends）
       │
       ▼
  视图函数（同步/异步）
       │
       ▼
  Pydantic 响应序列化
       │
       ▼
  HTTP 响应
```

---

## 2. 安装与基础应用

```bash
pip install fastapi uvicorn[standard]
```

```python
# main.py
from fastapi import FastAPI

# 创建应用，自动生成 /docs 和 /redoc 文档
app = FastAPI(
    title="我的 API",
    description="FastAPI 入门示例",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Hello, FastAPI!"}

# 启动：uvicorn main:app --reload
```

访问 `http://127.0.0.1:8000/docs` 即可看到 Swagger UI 自动文档。

### AI 应用最小接口形态

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="AI Assistant API")


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    model: str


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return ChatResponse(
        answer=f"模拟回答：{request.prompt}",
        model="mock-model",
    )
```

这个例子体现 FastAPI 的三个核心价值：

- Pydantic 自动校验请求体。
- `response_model` 明确响应结构。
- `/docs` 自动生成可调试 API 文档。

---

## 3. 路径参数与查询参数

```
URL 参数类型对比
════════════════════════════════════════════════════

  路径参数（Path Parameters）：
  /users/{user_id}  → URL 结构的一部分，必须提供

  查询参数（Query Parameters）：
  /users?page=1&size=10  → URL 中 ? 后的键值对，可选
```

### 路径参数

```python
from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    # FastAPI 自动将路径参数转换为 int
    # 如果传入非数字（如 /users/abc），自动返回 422
    return {"user_id": user_id}

# 使用 Path() 添加验证和文档说明
@app.get("/items/{item_id}")
def get_item(
    item_id: int = Path(
        description="商品 ID",
        ge=1,       # greater than or equal to 1
        le=999      # less than or equal to 999
    )
):
    return {"item_id": item_id}

# 枚举类型路径参数
from enum import Enum

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    vgg = "vgg"

@app.get("/models/{model_name}")
def get_model(model_name: ModelName):
    return {"model": model_name.value}
```

### 查询参数

```python
from typing import Optional

@app.get("/articles")
def list_articles(
    page: int = 1,                     # 有默认值 → 可选查询参数
    size: int = 10,
    keyword: Optional[str] = None,     # None 默认值 → 可选
    published: bool = True             # bool 自动解析 true/false/1/0
):
    """
    查询文章列表
    - page: 页码（默认 1）
    - size: 每页数量（默认 10）
    - keyword: 搜索关键词（可选）
    - published: 是否只显示已发布（默认 True）
    """
    return {
        "page": page,
        "size": size,
        "keyword": keyword,
        "published": published
    }
```

---

## 4. Pydantic 模型（请求体）

Pydantic 是 FastAPI 的核心数据验证库，通过类型注解自动验证和解析数据。

```python
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """创建用户的请求体模型"""
    username: str = Field(
        min_length=3,
        max_length=50,
        description="用户名，3-50个字符"
    )
    email: str = Field(description="邮箱地址")
    password: str = Field(min_length=8, description="密码，至少8位")
    age: Optional[int] = Field(None, ge=0, le=150)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").isalnum():
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v.lower()  # 统一转小写

class UserResponse(BaseModel):
    """响应给客户端的用户信息（不含敏感字段）"""
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # 支持 ORM 对象转换

# 使用 Pydantic 模型
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    # user 已通过验证，字段类型已转换
    print(user.username)   # 已转小写
    print(user.age)        # int 或 None
    # ... 保存到数据库 ...
    return {"id": 1, **user.model_dump(exclude={"password"}), "created_at": datetime.now()}
```

---

## 5. 请求体嵌套与多个参数

```python
from pydantic import BaseModel
from typing import List, Optional

class Tag(BaseModel):
    name: str
    color: str = "#000000"

class PostCreate(BaseModel):
    title: str
    content: str
    tags: List[Tag] = []          # 嵌套模型列表
    category_id: Optional[int] = None

@app.post("/posts")
def create_post(
    post: PostCreate,             # JSON 请求体
    author_id: int = 1,           # 查询参数（与请求体同时使用）
):
    return {
        "title": post.title,
        "tag_count": len(post.tags),
        "author_id": author_id
    }
```

---

## 6. 依赖注入（Depends）

依赖注入是 FastAPI 最强大的特性之一，用于解耦公共逻辑（分页、认证、数据库连接等）。

```
依赖注入工作流
═══════════════════════════════════════════════════════

  @app.get("/items")
  def list_items(
      commons: CommonParams = Depends(get_common_params),
      db: Session = Depends(get_db)
  ):
      ...
                │
                ▼
  FastAPI 在调用 list_items 前，自动：
  1. 调用 get_common_params() → 注入 commons
  2. 调用 get_db() → 注入 db（生成器依赖可自动管理生命周期）
  3. 参数验证通过后才调用视图函数
```

```python
from fastapi import FastAPI, Depends, Query
from typing import Annotated

app = FastAPI()

# --- 可复用的分页参数依赖 ---
class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(10, ge=1, le=100, description="每页数量")
    ):
        self.page = page
        self.size = size
        self.offset = (page - 1) * size

# 类型别名（Python 3.9+）
Pagination = Annotated[PaginationParams, Depends(PaginationParams)]

@app.get("/articles")
def list_articles(pagination: Pagination):
    return {
        "page": pagination.page,
        "size": pagination.size,
        "offset": pagination.offset
    }

@app.get("/users")
def list_users(pagination: Pagination):
    # 所有需要分页的端点共享同一逻辑
    return {"page": pagination.page, "size": pagination.size}

# --- 生成器依赖（管理资源生命周期）---
def get_db():
    """模拟数据库 Session 依赖"""
    db = {"connection": "fake_db_connection"}
    try:
        yield db      # 请求处理期间使用
    finally:
        pass          # 请求结束后关闭连接（清理资源）

@app.get("/db-test")
def test_db(db: dict = Depends(get_db)):
    return {"db_status": "connected", "connection": db["connection"]}
```

---

## 7. 自动文档（Swagger UI）

FastAPI 无需任何配置，自动生成两种文档：

```
自动文档地址
═══════════════════════════════════════════
  /docs     → Swagger UI（交互式）
  /redoc    → ReDoc（更易读）
  /openapi.json → OpenAPI 规范 JSON
```

通过 `summary`、`description`、`tags` 等参数增强文档：

```python
@app.post(
    "/users",
    summary="创建用户",
    description="注册新用户账号，需要提供用户名、邮箱和密码。",
    tags=["用户管理"],
    status_code=201,
    response_model=UserResponse
)
def create_user(user: UserCreate):
    """
    创建新用户。

    - **username**: 用户名（3-50字符，字母数字下划线）
    - **email**: 有效的邮箱地址
    - **password**: 密码（至少8位）
    """
    ...
```

---

## 8. 知识点总结

```
FastAPI 核心概念图
═══════════════════════════════════════════════════════

  路径参数                查询参数               请求体
  ──────────             ──────────            ──────────
  /users/{id}            ?page=1&size=10       Pydantic BaseModel
  自动类型转换             有/无默认值            Field() 验证
  Path() 验证             Query() 验证           嵌套模型
  ge/le/min_length        Optional[T]           response_model

  依赖注入 (Depends)       自动文档
  ──────────             ──────────
  Depends(func)          /docs  Swagger UI
  类/函数依赖             /redoc ReDoc
  生成器依赖（yield）      tags/summary/description
  资源生命周期管理          OpenAPI 规范自动生成
```
