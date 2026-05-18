# 第43章 项目任务：多模块博客后端

## 业务背景

将第42章的书单 API 升级为一个结构更完整的博客后端。业务需求是：用户可以注册和登录，登录后才能发布文章；文章支持分类；所有接口有统一的错误响应格式。

## 技术要求

使用 Blueprint + Flask-Login + Flask-SQLAlchemy 实现以下功能：

### 项目结构

```
blog_app/
├── app.py          ← 应用工厂 + 启动入口
├── models.py       ← User + Post + Category 模型
├── auth/
│   └── routes.py   ← /auth/register, /auth/login, /auth/logout
└── posts/
    └── routes.py   ← /api/posts CRUD
```

### 数据模型

```python
# User: id, username, email, password_hash
# Post: id, title, content, author_id(FK), category_id(FK), created_at
# Category: id, name
```

### 接口要求

**认证相关（auth 蓝图，前缀 /auth）：**
- `POST /auth/register` — 注册（username、email、password）
- `POST /auth/login` — 登录，成功返回 `{"message": "登录成功"}`
- `POST /auth/logout` — 注销（需要 @login_required）

**文章相关（posts 蓝图，前缀 /api）：**
- `GET /api/posts` — 公开，支持 `?category=` 过滤
- `POST /api/posts` — 需要登录，创建文章
- `DELETE /api/posts/<id>` — 需要登录，只能删除自己的文章

### 统一错误格式

所有错误响应必须使用：
```json
{"error": "ERROR_CODE", "message": "人类可读描述"}
```

## 验收标准

- [ ] 使用应用工厂函数 `create_app()`
- [ ] auth 和 posts 各为独立 Blueprint
- [ ] Flask-SQLAlchemy 创建 User、Post、Category 三张表
- [ ] 密码使用 `werkzeug.security.generate_password_hash` 存储
- [ ] 未登录访问 `POST /api/posts` 返回 `401`
- [ ] 删除他人文章返回 `403`
- [ ] `@app.errorhandler(Exception)` 兜底处理 500 错误
- [ ] 所有错误响应使用统一 JSON 格式

## 加分项

- 使用 `before_request` 记录每个请求的耗时日志
- 注册时验证邮箱格式和密码强度（至少8位）
- 添加文章分页：`GET /api/posts?page=1&per_page=10`
