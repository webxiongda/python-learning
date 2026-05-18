# 第42章 项目任务：个人书单管理 API

## 业务背景

开发一个简单的个人书单管理 REST API，用于记录已读/在读/待读的书籍。该 API 需要支持书籍的增删改查，并能按阅读状态过滤。作为入门项目，数据存储在内存字典中（无需数据库）。

## 技术要求

使用 Flask 实现以下 REST API 端点：

### 接口清单

| 方法   | 路径                  | 功能         |
|------|--------------------|------------|
| GET  | `/api/books`        | 获取书单（支持过滤） |
| GET  | `/api/books/<id>`   | 获取单本书详情    |
| POST | `/api/books`        | 添加新书       |
| PUT  | `/api/books/<id>`   | 更新书籍信息     |
| DELETE | `/api/books/<id>` | 删除书籍       |

### 数据结构

```python
# 书籍数据格式
{
    "id": 1,
    "title": "Python 编程：从入门到实践",
    "author": "Eric Matthes",
    "status": "reading",    # 可选值：'to-read' / 'reading' / 'done'
    "rating": null,         # 评分 1-5，未读时为 null
    "notes": "第5章很有意思"  # 读书笔记（可选）
}
```

### 功能细节

1. **GET /api/books** 支持查询参数：
   - `?status=reading` — 按阅读状态过滤
   - `?author=Eric` — 按作者名模糊搜索

2. **POST /api/books** 必填字段：`title`、`author`、`status`；可选：`rating`、`notes`

3. **PUT /api/books/<id>** 只更新请求体中提供的字段（partial update）

4. **统一错误响应格式**：
```json
{"error": "Not Found", "message": "ID 为 99 的书籍不存在"}
```

5. **自定义 404 错误处理器**

## 代码框架

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

books_db = {}
next_id = 1

VALID_STATUS = {"to-read", "reading", "done"}

@app.route("/api/books", methods=["GET"])
def list_books():
    # TODO: 支持 status 和 author 过滤
    pass

@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    # TODO: 返回单本书或 404
    pass

@app.route("/api/books", methods=["POST"])
def create_book():
    # TODO: 验证必填字段，创建书籍
    pass

@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    # TODO: 部分更新
    pass

@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    # TODO: 删除或 404
    pass

@app.errorhandler(404)
def not_found(e):
    # TODO: 统一 404 响应
    pass
```

## 验收标准

- [ ] 5个 CRUD 端点全部可用
- [ ] GET 支持 status 和 author 两种过滤
- [ ] POST 对缺失必填字段返回 `422` 状态码和明确错误信息
- [ ] DELETE 成功返回 `204`（无响应体）
- [ ] 自定义 `404` 错误处理器返回 JSON 格式
- [ ] 所有成功响应均为 JSON 格式

## 加分项

- 添加 `GET /api/books/stats` 端点，返回各状态书籍数量统计
- 支持按评分排序：`?sort=rating&order=desc`
- 使用 `url_for` 在响应中包含资源链接（HATEOAS 风格）
