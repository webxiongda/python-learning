# 第50章：里程碑：博客API项目 — 项目任务

## 项目名称

博客 REST API（FastAPI + 数据库 + 测试）

## 目标

交付一个完整后端 API 项目，覆盖认证、用户、文章 CRUD、分页、错误处理、数据库持久化和自动化测试。这是第一层主线的核心验收项目。

## 交付目录

在 `projects/chapter-50/` 下完成：

```text
projects/chapter-50/
├── README.md
├── pyproject.toml
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── routers/
│   │   ├── users.py
│   │   └── posts.py
│   └── services/
│       └── posts.py
└── tests/
    ├── test_auth.py
    └── test_posts.py
```

## API 要求

- `POST /auth/register`：注册用户。
- `POST /auth/login`：登录并返回访问令牌。
- `GET /posts`：文章列表，支持分页和关键词搜索。
- `POST /posts`：创建文章，仅登录用户可用。
- `GET /posts/{id}`：文章详情。
- `PATCH /posts/{id}`：更新文章，仅作者可用。
- `DELETE /posts/{id}`：删除文章，仅作者可用。
- `GET /users/{id}`：用户公开信息。

## 数据模型

- User：`id`、`username`、`email`、`password_hash`、`created_at`。
- Post：`id`、`title`、`content`、`author_id`、`published`、`created_at`、`updated_at`。

## 设计约束

- 不在响应中返回密码或 password hash。
- 请求体和响应体使用 Pydantic schema。
- 数据库会话边界清晰，测试使用独立测试数据库。
- 错误响应统一包含 `code` 和 `message`。
- 分页参数必须限制范围，避免一次返回过多数据。

## 测试要求

- 使用 FastAPI TestClient 或 httpx 测试接口。
- 至少覆盖注册、登录、创建文章、分页、未授权、越权更新、404。
- 测试可重复运行，不依赖本地已有数据。

## 运行命令

```bash
uvicorn app.main:app --reload
python -m pytest
```

## 阶段拆分

1. **应用骨架**：创建 FastAPI app、数据库连接、健康检查和测试数据库配置。
2. **用户认证**：实现注册、登录、密码哈希和令牌校验。
3. **文章 CRUD**：实现文章列表、详情、创建、更新、删除。
4. **权限和错误**：加入作者权限、404、401、403、统一错误响应。
5. **测试和文档**：补接口测试、README、示例请求和设计取舍。

## 完成定义

这个项目完成时，你应该能解释清楚：

- Pydantic schema 和 ORM model 为什么要分开。
- 密码为什么只能存 hash，不能明文保存或返回。
- 分页参数为什么要设置默认值和最大值。
- 数据库会话应该在哪里创建、提交、回滚和关闭。
- API 测试如何保证每次运行都是干净数据。

## 验收清单

- [ ] `/docs` 能展示完整 API 文档。
- [ ] 所有核心接口能通过测试。
- [ ] 未登录、无权限、资源不存在都有明确响应。
- [ ] README 写清安装、启动、测试和 API 示例。
- [ ] 至少记录 1 个接口设计取舍。
