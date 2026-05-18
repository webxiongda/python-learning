# 第42章 Demo：Flask 入门

## Demo 1：最小 Flask 应用

```python
# app_minimal.py
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Hello, Flask!</h1>"

@app.route("/hello/<name>")
def hello(name: str):
    return f"<h1>你好，{name}！</h1>"

@app.route("/add/<int:a>/<int:b>")
def add(a: int, b: int):
    result = a + b
    return f"{a} + {b} = {result}"

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

```
# 预期输出（启动服务）：
 * Serving Flask app 'app_minimal'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Restarting with stat
 * Debugger is active!

# 访问 http://127.0.0.1:5000/         → Hello, Flask!
# 访问 http://127.0.0.1:5000/hello/Alice → 你好，Alice！
# 访问 http://127.0.0.1:5000/add/3/5   → 3 + 5 = 8
```

---

## Demo 2：请求对象与 JSON API

```python
# app_api.py
from flask import Flask, request, jsonify

app = Flask(__name__)

# 模拟内存数据库
users_db = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob",   "email": "bob@example.com"},
}
next_id = 3

@app.route("/api/users", methods=["GET"])
def list_users():
    """列出所有用户，支持按 name 过滤"""
    name_filter = request.args.get("name", "")
    page = request.args.get("page", 1, type=int)
    
    users = list(users_db.values())
    if name_filter:
        users = [u for u in users if name_filter.lower() in u["name"].lower()]
    
    return jsonify({
        "total": len(users),
        "page": page,
        "data": users
    })

@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    """获取单个用户"""
    user = users_db.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    return jsonify(user)

@app.route("/api/users", methods=["POST"])
def create_user():
    """创建新用户"""
    global next_id
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "需要 JSON 请求体"}), 400
    
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    
    if not name or not email:
        return jsonify({"error": "name 和 email 不能为空"}), 422
    
    user = {"id": next_id, "name": name, "email": email}
    users_db[next_id] = user
    next_id += 1
    
    return jsonify(user), 201

@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int):
    """删除用户"""
    if user_id not in users_db:
        return jsonify({"error": "用户不存在"}), 404
    del users_db[user_id]
    return "", 204

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

```
# 预期输出（用 curl 或 httpie 测试）：

# GET /api/users
# → {"data": [{"email":"alice@example.com","id":1,"name":"Alice"}, ...], "page":1, "total":2}

# GET /api/users/1
# → {"email": "alice@example.com", "id": 1, "name": "Alice"}

# GET /api/users/999
# → 404 {"error": "用户不存在"}

# POST /api/users {"name": "Carol", "email": "carol@example.com"}
# → 201 {"email": "carol@example.com", "id": 3, "name": "Carol"}

# DELETE /api/users/1
# → 204 (空响应体)
```

---

## Demo 3：Jinja2 模板渲染

```python
# app_template.py
# 需要创建 templates/ 目录和对应 HTML 文件

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 模拟数据
POSTS = [
    {"id": 1, "title": "Flask 入门指南", "author": "Alice", "views": 120},
    {"id": 2, "title": "Jinja2 模板详解", "author": "Bob", "views": 85},
    {"id": 3, "title": "Python Web 开发", "author": "Alice", "views": 200},
]

@app.route("/")
def index():
    author = request.args.get("author")
    posts = POSTS
    if author:
        posts = [p for p in POSTS if p["author"] == author]
    
    return render_template(
        "index.html",
        posts=posts,
        author_filter=author,
        total=len(posts)
    )

@app.route("/posts/<int:post_id>")
def post_detail(post_id: int):
    post = next((p for p in POSTS if p["id"] == post_id), None)
    if not post:
        return render_template("404.html"), 404
    return render_template("post.html", post=post)

# ---- 模板内容（内联演示） ----
# templates/index.html 内容如下：
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh">
<head><title>文章列表</title></head>
<body>
<h1>文章列表（共 {{ total }} 篇）</h1>

{% if author_filter %}
<p>筛选作者：<strong>{{ author_filter }}</strong> 
   <a href="{{ url_for('index') }}">[清除筛选]</a></p>
{% endif %}

<ul>
{% for post in posts %}
  <li>
    <a href="{{ url_for('post_detail', post_id=post.id) }}">
      {{ post.title }}
    </a>
    — 作者: {{ post.author }}，阅读: {{ post.views }}次
    {% if post.views > 100 %}🔥{% endif %}
  </li>
{% else %}
  <li>没有找到相关文章</li>
{% endfor %}
</ul>

<h3>按作者筛选：</h3>
{% set authors = posts | map(attribute='author') | unique | list %}
{% for author in ['Alice', 'Bob'] %}
  <a href="{{ url_for('index', author=author) }}">{{ author }}</a> |
{% endfor %}
</body>
</html>
"""

# 动态注册模板（演示用，实际项目用文件）
from jinja2 import DictLoader
app.jinja_loader = DictLoader({
    "index.html": INDEX_TEMPLATE,
    "post.html": "<h1>{{ post.title }}</h1><p>作者: {{ post.author }}</p>",
    "404.html": "<h1>404 - 文章不存在</h1>",
})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
```

```
# 预期输出（访问 http://127.0.0.1:5001/）：
# 显示文章列表，共3篇
# 访问 http://127.0.0.1:5001/?author=Alice → 显示 Alice 的2篇文章
# 访问 http://127.0.0.1:5001/posts/1 → 显示"Flask 入门指南"详情
# 访问 http://127.0.0.1:5001/posts/99 → 404 页面
```

---

## Demo 4：响应与 Cookie 操作

```python
# app_response.py
from flask import Flask, jsonify, make_response, request, redirect, url_for

app = Flask(__name__)

@app.route("/set-cookie")
def set_cookie():
    """设置 Cookie"""
    resp = make_response(jsonify({"message": "Cookie 已设置"}))
    resp.set_cookie(
        "user_pref",
        "theme=dark;lang=zh",
        max_age=3600,     # 1小时后过期
        httponly=True,    # 不允许 JavaScript 访问
        samesite="Lax"    # CSRF 保护
    )
    return resp

@app.route("/get-cookie")
def get_cookie():
    """读取 Cookie"""
    pref = request.cookies.get("user_pref", "未设置")
    return jsonify({"user_pref": pref})

@app.route("/custom-headers")
def custom_headers():
    """自定义响应头"""
    data = {"status": "ok", "version": "1.0"}
    resp = make_response(jsonify(data))
    resp.headers["X-API-Version"] = "1.0"
    resp.headers["Cache-Control"] = "no-cache, no-store"
    resp.headers["X-Request-ID"] = "req-abc123"
    return resp

@app.route("/redirect-demo")
def redirect_demo():
    """重定向演示"""
    # 302 临时重定向
    return redirect(url_for("set_cookie"))

@app.route("/download")
def download():
    """触发文件下载（设置 Content-Disposition）"""
    content = "姓名,年龄\nAlice,25\nBob,30"
    resp = make_response(content)
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = "attachment; filename=users.csv"
    return resp

if __name__ == "__main__":
    app.run(debug=True, port=5002)
```

```
# 预期输出：
# GET /set-cookie    → {"message": "Cookie 已设置"}，响应头含 Set-Cookie
# GET /get-cookie    → {"user_pref": "theme=dark;lang=zh"}
# GET /custom-headers → {"status":"ok","version":"1.0"}，含自定义响应头
# GET /redirect-demo → 302 跳转到 /set-cookie
# GET /download      → 触发下载 users.csv 文件
```

---

## Demo 5：错误处理与配置

```python
# app_errors.py
from flask import Flask, jsonify, request

app = Flask(__name__)

# 配置
app.config.update({
    "DEBUG": True,
    "MAX_CONTENT_LENGTH": 16 * 1024 * 1024,  # 最大请求体 16MB
    "JSON_SORT_KEYS": False,
})

# --- 自定义错误处理器 ---
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": "请求的资源不存在",
        "status_code": 404
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "Method Not Allowed",
        "message": f"该路由不支持 {request.method} 方法",
        "allowed_methods": error.valid_methods
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal Server Error",
        "message": "服务器内部错误，请稍后重试"
    }), 500

# --- 测试路由 ---
@app.route("/trigger-error")
def trigger_error():
    """故意触发 500 错误"""
    raise ValueError("测试错误")

@app.route("/api/items/<int:item_id>")
def get_item(item_id):
    items = {1: "苹果", 2: "香蕉"}
    if item_id not in items:
        # 手动返回 404
        return jsonify({"error": f"item {item_id} 不存在"}), 404
    return jsonify({"id": item_id, "name": items[item_id]})

if __name__ == "__main__":
    app.run(debug=False, port=5003)  # debug=False 才能触发 errorhandler(500)
```

```
# 预期输出：
# GET /api/items/1   → {"id": 1, "name": "苹果"}
# GET /api/items/99  → 404 {"error": "item 99 不存在"}
# GET /nonexistent   → 404 {"error":"Not Found","message":"请求的资源不存在",...}
# POST /api/items/1  → 405 {"error":"Method Not Allowed","allowed_methods":["GET"],...}
```
