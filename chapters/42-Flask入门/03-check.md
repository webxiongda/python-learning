# 第42章 自测题：Flask 入门

## 题目1：路由配置

**问题：** 下面的路由定义有什么问题？如何修改？

```python
from flask import Flask, request
app = Flask(__name__)

@app.route("/users")
def create_user():
    data = request.get_json()
    return {"id": 1, "name": data["name"]}, 201
```

### 参考答案

**问题：** 路由 `/users` 默认只允许 `GET` 请求，但视图函数的功能是创建用户（应该用 POST），并且没有指定 `methods=["POST"]`，发送 POST 请求会得到 `405 Method Not Allowed`。

**修复：**
```python
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or "name" not in data:
        return {"error": "name 字段必填"}, 400
    return {"id": 1, "name": data["name"]}, 201
```

另外原代码还缺少对 `data` 为 None（请求体非 JSON）的处理，以及 `KeyError` 保护。

---

## 题目2：request 对象属性

**问题：** 对于以下 HTTP 请求，`request` 对象的哪个属性可以获取对应数据？

请求：
```
POST /search?page=2 HTTP/1.1
Content-Type: application/json
Authorization: Bearer token123

{"keyword": "python", "category": "tech"}
```

1. 获取 `page=2` 的值
2. 获取 `keyword` 字段
3. 获取 Authorization 头的值
4. 获取请求方法
5. 获取请求路径

### 参考答案

```python
# 1. 获取查询参数 page（URL 中 ?page=2）
page = request.args.get("page", 1, type=int)   # → 2

# 2. 获取 JSON 请求体中的 keyword
data = request.get_json()
keyword = data.get("keyword")   # → "python"
# 也可以用: request.json["keyword"]

# 3. 获取请求头
auth = request.headers.get("Authorization")   # → "Bearer token123"

# 4. 请求方法
method = request.method   # → "POST"

# 5. 请求路径
path = request.path   # → "/search"
```

---

## 题目3：Jinja2 模板语法

**问题：** 将以下 Python 逻辑转换为 Jinja2 模板语法：

```python
# Python 逻辑
users = [
    {"name": "Alice", "role": "admin"},
    {"name": "Bob",   "role": "user"},
]
for user in users:
    if user["role"] == "admin":
        print(f"[管理员] {user['name']}")
    else:
        print(f"[用户] {user['name']}")
```

### 参考答案

```html
<ul>
{% for user in users %}
  <li>
    {% if user.role == "admin" %}
      [管理员] {{ user.name }}
    {% else %}
      [用户] {{ user.name }}
    {% endif %}
  </li>
{% else %}
  <li>暂无用户</li>
{% endfor %}
</ul>
```

**关键对比：**
- Python 用 `user["role"]`，Jinja2 用 `user.role`（也支持 `user["role"]`）
- Jinja2 的 `{% for %}` 必须有 `{% endfor %}` 结尾
- Jinja2 的 `{% if %}` 必须有 `{% endif %}` 结尾
- `{% else %}` 在 `for` 循环里表示"列表为空时"执行的内容

---

## 题目4：状态码与响应格式

**问题：** 实现一个 `DELETE /api/users/<id>` 端点，要求：
- 如果用户存在，删除并返回 `204`（无响应体）
- 如果用户不存在，返回 `404` 和 JSON 错误信息

```python
users = {1: "Alice", 2: "Bob"}

@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    # 请补全代码
    pass
```

### 参考答案

```python
from flask import Flask, jsonify

users = {1: "Alice", 2: "Bob"}

@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    if user_id not in users:
        return jsonify({
            "error": "Not Found",
            "message": f"ID 为 {user_id} 的用户不存在"
        }), 404
    
    del users[user_id]
    return "", 204  # 204 不能有响应体
    # 也可以写成：
    # return make_response("", 204)
```

**注意：** HTTP 204 规范要求响应体**必须为空**，所以返回 `"", 204` 而不是 `jsonify({...}), 204`。

---

## 题目5：综合题

**问题：** 阅读以下代码，描述访问 `GET /profile?token=abc` 时会发生什么？

```python
from flask import Flask, request, jsonify, redirect, url_for

app = Flask(__name__)
VALID_TOKEN = "abc"

@app.route("/login")
def login():
    return jsonify({"message": "请登录"})

@app.route("/profile")
def profile():
    token = request.args.get("token")
    if token != VALID_TOKEN:
        return redirect(url_for("login"))
    return jsonify({"username": "Alice", "email": "alice@example.com"})
```

### 参考答案

**执行流程：**

1. 请求到达路由 `/profile`，Flask 调用 `profile()` 函数
2. `request.args.get("token")` 获取查询参数，值为 `"abc"`
3. 条件 `token != VALID_TOKEN` 即 `"abc" != "abc"` 为 **False**，不执行重定向
4. 返回 `jsonify({"username": "Alice", "email": "alice@example.com"})`
5. 客户端收到 `200 OK` 响应，响应体为：
   ```json
   {"email": "alice@example.com", "username": "Alice"}
   ```

**补充说明：**
- 如果访问 `GET /profile?token=wrong`，则会 `302 重定向` 到 `/login`
- 如果访问 `GET /profile`（不带 token），`request.args.get("token")` 返回 `None`，`None != "abc"` 为 True，同样会重定向
- 这种用查询参数传 token 的方式不安全，实际应用中应使用 `Authorization` Header 或 Cookie
