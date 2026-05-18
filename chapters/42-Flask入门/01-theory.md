# 第42章：Flask 入门

## 1. Flask 简介

Flask 是 Python 最流行的轻量级 Web 框架之一，基于 Werkzeug（WSGI 工具库）和 Jinja2（模板引擎）构建。它遵循"微框架"哲学——核心保持简单，通过扩展满足复杂需求。

```
Flask 架构概览
═══════════════════════════════════════════════════════════

  浏览器/Client
       │
       │  HTTP 请求
       ▼
  ┌─────────────────────────────────────────────────────┐
  │                   Flask 应用                         │
  │                                                      │
  │  WSGI 层 (Werkzeug)                                  │
  │  ┌─────────────────────────────────────────────┐    │
  │  │  URL Router (路由匹配)                        │    │
  │  │  /users → users 视图函数                      │    │
  │  │  /posts/<id> → post_detail 视图函数           │    │
  │  └─────────────────────────────────────────────┘    │
  │                    │                                 │
  │                    ▼                                 │
  │  ┌─────────────────────────────────────────────┐    │
  │  │  视图函数 (View Function)                     │    │
  │  │  接收 request 对象，处理业务逻辑              │    │
  │  └─────────────────────────────────────────────┘    │
  │                    │                                 │
  │          ┌─────────┴─────────┐                      │
  │          ▼                   ▼                       │
  │  ┌──────────────┐   ┌──────────────────┐            │
  │  │ Jinja2 模板  │   │  jsonify 响应    │            │
  │  │ 渲染 HTML    │   │  返回 JSON       │            │
  │  └──────────────┘   └──────────────────┘            │
  └─────────────────────────────────────────────────────┘
       │
       │  HTTP 响应
       ▼
  浏览器/Client
```

---

## 2. 安装与创建第一个应用

```bash
pip install flask
```

```python
from flask import Flask

# 创建 Flask 应用实例
# __name__ 帮助 Flask 确定应用根目录（用于查找模板和静态文件）
app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, Flask!"

if __name__ == "__main__":
    # debug=True：开启调试模式（代码变更自动重载，显示详细错误信息）
    # 生产环境务必关闭 debug 模式！
    app.run(debug=True, host="0.0.0.0", port=5000)
```

---

## 3. 路由（Route）

路由是 URL 路径与视图函数的映射关系。

### 基本路由

```python
@app.route("/about")
def about():
    return "关于页面"

# 指定 HTTP 方法（默认只接受 GET）
@app.route("/login", methods=["GET", "POST"])
def login():
    return "登录页面"
```

### 动态路由（路径参数）

```python
# <变量名> 捕获路径片段，默认为 string 类型
@app.route("/users/<username>")
def user_profile(username):
    return f"用户：{username}"

# 类型转换器：int / float / path / uuid
@app.route("/posts/<int:post_id>")
def post_detail(post_id):
    return f"文章 ID：{post_id}"  # post_id 已是 int 类型

@app.route("/files/<path:filepath>")
def get_file(filepath):
    return f"文件路径：{filepath}"  # 可包含斜杠
```

### URL 构建（url_for）

```python
from flask import url_for

with app.test_request_context():
    # 根据视图函数名生成 URL（避免硬编码路径）
    print(url_for("index"))               # /
    print(url_for("user_profile", username="alice"))   # /users/alice
    print(url_for("post_detail", post_id=42))          # /posts/42
```

---

## 4. 请求对象（request）

```
HTTP 请求 → Flask request 对象
═══════════════════════════════════════════════════

  请求行: GET /search?q=python HTTP/1.1
             │
             ▼
  request.method   = "GET"
  request.path     = "/search"
  request.args     = {"q": "python"}   ← 查询参数

  请求头:
  Content-Type: application/json
             │
             ▼
  request.headers  = {...}
  request.content_type = "application/json"

  请求体: {"name": "Alice"}
             │
             ▼
  request.json     = {"name": "Alice"}   ← JSON 体
  request.form     = {...}               ← 表单数据
  request.data     = b"..."             ← 原始字节
  request.files    = {...}               ← 上传文件
```

```python
from flask import Flask, request

app = Flask(__name__)

@app.route("/search")
def search():
    # 获取查询参数 ?q=python&page=2
    keyword = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)  # 自动转换类型
    return f"搜索：{keyword}，第 {page} 页"

@app.route("/api/users", methods=["POST"])
def create_user():
    # 获取 JSON 请求体
    data = request.get_json()
    if not data:
        return {"error": "需要 JSON 数据"}, 400
    
    name = data.get("name")
    email = data.get("email")
    return {"message": f"用户 {name} 创建成功", "email": email}, 201
```

---

## 5. 响应（Response）

```python
from flask import Flask, jsonify, make_response, redirect, url_for

app = Flask(__name__)

# 1. 直接返回字符串（状态码默认 200）
@app.route("/text")
def text_response():
    return "纯文本响应"

# 2. 返回元组 (body, status_code, headers)
@app.route("/created")
def created_response():
    return "创建成功", 201

# 3. jsonify 返回 JSON
@app.route("/api/data")
def json_response():
    return jsonify({"status": "ok", "data": [1, 2, 3]})

# 4. make_response 手动构造响应
@app.route("/custom")
def custom_response():
    resp = make_response(jsonify({"msg": "success"}), 200)
    resp.headers["X-Custom-Header"] = "my-value"
    resp.set_cookie("session_token", "abc123", httponly=True)
    return resp

# 5. 重定向
@app.route("/old-path")
def old_path():
    return redirect(url_for("index"))  # 302 跳转
```

---

## 6. Jinja2 模板基础

Jinja2 是 Flask 内置的模板引擎，模板文件存放在 `templates/` 目录下。

```
项目结构
═══════════════════════════════
myapp/
├── app.py
├── templates/
│   ├── base.html      ← 基础模板（含公共结构）
│   ├── index.html     ← 继承 base.html
│   └── user.html
└── static/
    ├── css/
    └── js/
```

### templates/base.html

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My App{% endblock %}</title>
</head>
<body>
    <nav><a href="/">首页</a></nav>
    
    {% block content %}{% endblock %}
    
    <footer>版权所有</footer>
</body>
</html>
```

### templates/index.html

```html
{% extends "base.html" %}

{% block title %}首页 - My App{% endblock %}

{% block content %}
<h1>欢迎, {{ username }}!</h1>

{# 条件判断 #}
{% if is_admin %}
    <p>您是管理员</p>
{% else %}
    <p>普通用户</p>
{% endif %}

{# 列表循环 #}
<ul>
{% for post in posts %}
    <li>
        <a href="{{ url_for('post_detail', post_id=post.id) }}">
            {{ post.title }}
        </a>
        {% if loop.first %} [最新] {% endif %}
    </li>
{% else %}
    <li>暂无文章</li>
{% endfor %}
</ul>
{% endblock %}
```

### 视图函数渲染模板

```python
from flask import render_template

@app.route("/")
def index():
    posts = [
        {"id": 1, "title": "Flask 入门"},
        {"id": 2, "title": "Jinja2 模板"},
    ]
    return render_template(
        "index.html",
        username="Alice",
        is_admin=False,
        posts=posts
    )
```

---

## 7. 配置管理

```python
app = Flask(__name__)

# 方式1：直接设置
app.config["SECRET_KEY"] = "dev-secret-key-change-in-prod"
app.config["DEBUG"] = True

# 方式2：从类加载（推荐）
class Config:
    SECRET_KEY = "production-secret"
    DEBUG = False
    DATABASE_URI = "postgresql://localhost/mydb"

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URI = "sqlite:///dev.db"

app.config.from_object(DevelopmentConfig)
```

---

## 8. 知识点总结

```
Flask 核心组件图
═══════════════════════════════════════════════════

  @app.route()          request 对象           响应
  路由装饰器              ─────────────         ──────────
  ├─ path              ├─ args（查询参数）      ├─ return str
  ├─ methods           ├─ form（表单）          ├─ return json, 201
  └─ 变量规则           ├─ json（JSON体）        ├─ jsonify()
     <int:id>          ├─ headers              ├─ make_response()
     <path:fp>         └─ files（上传）         └─ redirect()

  Jinja2 模板
  ─────────────────────────────────
  {{ 变量 }}           {# 注释 #}
  {% if/for/block %}   {% extends "base.html" %}
  url_for()            模板继承与块覆盖
```
