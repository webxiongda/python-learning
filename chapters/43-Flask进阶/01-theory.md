# 第43章：Flask 进阶

## 1. Blueprint（蓝图）

当应用规模增长，将所有路由放在一个文件会导致混乱。Blueprint 是 Flask 的模块化机制，将功能相关的路由、模板、静态文件组织成独立的子模块。

```
Blueprint 项目结构
═══════════════════════════════════════════════════════
myapp/
├── app.py                  ← 应用工厂函数
├── config.py
├── auth/                   ← 认证蓝图
│   ├── __init__.py
│   ├── routes.py           ← 路由定义
│   └── templates/
│       └── auth/
│           └── login.html
├── posts/                  ← 文章蓝图
│   ├── __init__.py
│   ├── routes.py
│   └── templates/
│       └── posts/
└── users/                  ← 用户蓝图
    ├── __init__.py
    └── routes.py
```

### 定义蓝图

```python
# auth/routes.py
from flask import Blueprint, jsonify, request

# 创建蓝图：名称, 模块名, URL 前缀
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    # 处理登录逻辑...
    return jsonify({"token": "xxx"}), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "已退出登录"})
```

```python
# posts/routes.py
from flask import Blueprint, jsonify

posts_bp = Blueprint("posts", __name__, url_prefix="/posts")

@posts_bp.route("/")
def list_posts():
    return jsonify({"posts": []})

@posts_bp.route("/<int:post_id>")
def get_post(post_id):
    return jsonify({"id": post_id})
```

### 注册蓝图（应用工厂模式）

```python
# app.py
from flask import Flask

def create_app(config=None):
    """应用工厂函数 — 利于测试和多环境部署"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object("config.DevelopmentConfig")
    if config:
        app.config.update(config)
    
    # 注册蓝图
    from auth.routes import auth_bp
    from posts.routes import posts_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
```

---

## 2. Flask-Login 用户认证

Flask-Login 管理用户会话，提供登录/注销/受保护路由功能。

```bash
pip install flask-login
```

```
Flask-Login 认证流程
═══════════════════════════════════════════════════════════

  客户端                      Flask-Login                 数据库
    │                              │                        │
    │── POST /login ──────────────▶│                        │
    │   {username, password}       │── 查询用户 ────────────▶│
    │                              │◀─ User 对象 ────────────│
    │                              │── 验证密码              │
    │                              │── login_user(user) ─▶ Session
    │◀── 响应 + Set-Cookie ────────│   session["user_id"]=1 │
    │                              │                        │
    │── GET /profile ─────────────▶│                        │
    │   Cookie: session=...        │── @login_required      │
    │                              │── 读 session → user_id  │
    │                              │── load_user(1) ────────▶│
    │◀── 200 用户数据 ─────────────│◀─ User 对象 ────────────│
```

```python
from flask import Flask, request, jsonify, redirect, url_for
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"  # Session 加密必需

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"  # 未登录时重定向到哪

# --- 用户模型（需实现 UserMixin 接口）---
class User(UserMixin):
    """UserMixin 提供 is_authenticated / is_active / get_id() 等方法"""
    
    def __init__(self, user_id: int, username: str, password_hash: str):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash

# 模拟数据库
USERS = {
    1: User(1, "alice", "hashed_pw_alice"),
    2: User(2, "bob",   "hashed_pw_bob"),
}

@login_manager.user_loader
def load_user(user_id: str):
    """Flask-Login 通过此函数从 session 中的 user_id 加载用户对象"""
    return USERS.get(int(user_id))

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    user = next((u for u in USERS.values() if u.username == username), None)
    if user and password == "correct_password":  # 实际应验证 hash
        login_user(user, remember=True)
        return jsonify({"message": f"欢迎，{user.username}！"})
    
    return jsonify({"error": "用户名或密码错误"}), 401

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "已退出登录"})

@app.route("/profile")
@login_required  # 未登录自动跳转到 login_view
def profile():
    return jsonify({
        "id": current_user.id,
        "username": current_user.username
    })
```

---

## 3. before_request 钩子

钩子函数在每次请求前（或后）自动执行，常用于认证、日志、数据库连接等。

```
请求生命周期钩子
═══════════════════════════════════════════════════════

  HTTP 请求
      │
      ▼
  @app.before_request        ← 每次请求前执行（如 Token 校验）
      │  如果返回非 None，中断后续处理
      ▼
  路由匹配 + 视图函数
      │
      ▼
  @app.after_request         ← 每次请求后（响应发出前）
      │  接收 response 对象，可修改后返回
      ▼
  @app.teardown_request      ← 请求上下文销毁时（即使有异常）
      │  用于释放资源（如关闭数据库连接）
      ▼
  响应发送给客户端
```

```python
import time
from flask import Flask, request, jsonify, g

app = Flask(__name__)

@app.before_request
def start_timer():
    """记录请求开始时间"""
    g.start_time = time.time()

@app.before_request
def verify_api_key():
    """验证 API Key（跳过公开路由）"""
    public_routes = ["/health", "/login"]
    if request.path in public_routes:
        return  # 不返回值则继续正常处理
    
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != "valid-key-123":
        return jsonify({"error": "无效的 API Key"}), 401

@app.after_request
def add_timing_header(response):
    """添加处理时间到响应头"""
    if hasattr(g, "start_time"):
        elapsed = time.time() - g.start_time
        response.headers["X-Processing-Time"] = f"{elapsed:.4f}s"
    return response

@app.teardown_request
def close_db(exception):
    """请求结束时关闭数据库连接"""
    db = g.pop("db", None)
    if db is not None:
        db.close()
```

---

## 4. 错误处理

```python
from flask import Flask, jsonify, request
from werkzeug.exceptions import NotFound, BadRequest, HTTPException

app = Flask(__name__)

# --- 自定义异常类 ---
class AppError(Exception):
    """应用级别自定义异常"""
    def __init__(self, message: str, status_code: int = 400, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "APP_ERROR"

# --- 注册错误处理器 ---
@app.errorhandler(AppError)
def handle_app_error(error):
    return jsonify({
        "error": error.error_code,
        "message": error.message
    }), error.status_code

@app.errorhandler(HTTPException)
def handle_http_exception(error):
    """处理所有 Werkzeug HTTP 异常（404, 405, 400 等）"""
    return jsonify({
        "error": error.name,
        "message": error.description,
        "status_code": error.code
    }), error.code

@app.errorhandler(Exception)
def handle_unexpected_error(error):
    """处理所有未预期的异常（500）"""
    app.logger.error(f"未预期错误: {error}", exc_info=True)
    return jsonify({
        "error": "InternalServerError",
        "message": "服务器内部错误"
    }), 500

# 使用自定义异常
@app.route("/users/<int:user_id>")
def get_user(user_id):
    users = {1: "Alice"}
    if user_id not in users:
        raise AppError(f"用户 {user_id} 不存在", 404, "USER_NOT_FOUND")
    return jsonify({"name": users[user_id]})
```

---

## 5. Flask-SQLAlchemy 集成

```bash
pip install flask-sqlalchemy
```

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --- 模型定义 ---
class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 一对多关系（一个用户有多篇文章）
    posts = db.relationship("Post", back_populates="author", lazy="dynamic")
    
    def to_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email}

class Post(db.Model):
    __tablename__ = "posts"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    author = db.relationship("User", back_populates="posts")

# --- 路由中使用 ---
@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json()
    user = User(username=data["username"], email=data["email"])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@app.route("/api/users/<int:user_id>/posts")
def get_user_posts(user_id):
    user = User.query.get_or_404(user_id)
    posts = user.posts.all()
    return jsonify([{"id": p.id, "title": p.title} for p in posts])

# 初始化数据库
with app.app_context():
    db.create_all()
```

---

## 6. 知识点总结

```
Flask 进阶核心组件
══════════════════════════════════════════════════════

  Blueprint（蓝图）          Flask-Login（认证）
  ──────────────────         ────────────────────
  模块化路由                  UserMixin
  url_prefix                 login_user()
  应用工厂模式                @login_required
  register_blueprint()       current_user
                             user_loader 回调

  钩子函数                    Flask-SQLAlchemy
  ──────────────────         ────────────────────
  @before_request            db = SQLAlchemy(app)
  @after_request             db.Model（模型基类）
  @teardown_request          db.session.add()
  g 对象（请求上下文）         db.session.commit()
                             relationship()
  错误处理
  ──────────────────
  @errorhandler(404)
  自定义 AppError 异常
  HTTPException 统一处理
```
