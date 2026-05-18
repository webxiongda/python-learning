# 第43章 Demo：Flask 进阶

## Demo 1：Blueprint 蓝图拆分应用

```python
# 单文件演示 Blueprint（实际项目应分多个文件）
from flask import Flask, Blueprint, jsonify, request

# --- 创建蓝图 ---
users_bp = Blueprint("users", __name__, url_prefix="/api/users")
products_bp = Blueprint("products", __name__, url_prefix="/api/products")

# 用户蓝图路由
users_data = {1: {"id": 1, "name": "Alice"}, 2: {"id": 2, "name": "Bob"}}

@users_bp.route("/")
def list_users():
    return jsonify(list(users_data.values()))

@users_bp.route("/<int:user_id>")
def get_user(user_id):
    user = users_data.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    return jsonify(user)

# 商品蓝图路由
products_data = {1: {"id": 1, "name": "Python书", "price": 89.0}}

@products_bp.route("/")
def list_products():
    return jsonify(list(products_data.values()))

@products_bp.route("/<int:product_id>")
def get_product(product_id):
    product = products_data.get(product_id)
    if not product:
        return jsonify({"error": "商品不存在"}), 404
    return jsonify(product)

# --- 应用工厂函数 ---
def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret"
    
    # 注册蓝图
    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    
    # 首页
    @app.route("/")
    def index():
        return jsonify({
            "endpoints": {
                "users": "/api/users/",
                "products": "/api/products/"
            }
        })
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

```
# 预期输出（访问各端点）：

# GET /
# → {"endpoints": {"products": "/api/products/", "users": "/api/users/"}}

# GET /api/users/
# → [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

# GET /api/users/1
# → {"id": 1, "name": "Alice"}

# GET /api/products/
# → [{"id": 1, "name": "Python书", "price": 89.0}]
```

---

## Demo 2：before_request 请求钩子与日志

```python
import time
import uuid
import logging
from flask import Flask, request, jsonify, g

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# 不需要认证的公开路由
PUBLIC_ROUTES = {"/health", "/"}
VALID_API_KEYS = {"key-alice-001", "key-bob-002"}

@app.before_request
def assign_request_id():
    """为每个请求分配唯一 ID，便于日志追踪"""
    g.request_id = str(uuid.uuid4())[:8]
    g.start_time = time.time()

@app.before_request
def check_api_key():
    """验证 API Key（公开路由除外）"""
    if request.path in PUBLIC_ROUTES:
        return None  # 放行
    
    api_key = request.headers.get("X-API-Key", "")
    if api_key not in VALID_API_KEYS:
        app.logger.warning(f"[{g.request_id}] 非法 API Key: '{api_key}' from {request.remote_addr}")
        return jsonify({
            "error": "Unauthorized",
            "message": "无效的 API Key，请在 X-API-Key Header 中提供"
        }), 401

@app.after_request
def log_request(response):
    """请求完成后记录访问日志"""
    elapsed = time.time() - g.start_time
    app.logger.info(
        f"[{g.request_id}] {request.method} {request.path} "
        f"→ {response.status_code} ({elapsed*1000:.1f}ms)"
    )
    response.headers["X-Request-ID"] = g.request_id
    return response

# 路由定义
@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "公开路由，无需认证"})

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/api/data")
def get_data():
    """需要 API Key 的路由"""
    return jsonify({
        "request_id": g.request_id,
        "data": [1, 2, 3, 4, 5]
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)
```

```
# 预期输出（服务器控制台）：

# 访问 GET /（公开路由）：
# 2024-01-15 10:30:00 - [a1b2c3d4] GET / → 200 (12.3ms)

# 访问 GET /api/data（无 API Key）：
# 2024-01-15 10:30:01 - [e5f6g7h8] 非法 API Key: '' from 127.0.0.1
# 2024-01-15 10:30:01 - [e5f6g7h8] GET /api/data → 401 (5.2ms)

# 访问 GET /api/data（带有效 API Key：X-API-Key: key-alice-001）：
# 2024-01-15 10:30:02 - [i9j0k1l2] GET /api/data → 200 (8.7ms)
# 响应体：{"data": [1, 2, 3, 4, 5], "request_id": "i9j0k1l2"}
```

---

## Demo 3：统一错误处理

```python
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

# --- 自定义业务异常 ---
class BusinessError(Exception):
    """业务逻辑异常基类"""
    def __init__(self, message: str, error_code: str, http_status: int = 400):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.http_status = http_status

class ResourceNotFound(BusinessError):
    def __init__(self, resource: str, resource_id):
        super().__init__(
            message=f"{resource} (ID={resource_id}) 不存在",
            error_code="RESOURCE_NOT_FOUND",
            http_status=404
        )

class ValidationError(BusinessError):
    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"字段 '{field}' 验证失败：{reason}",
            error_code="VALIDATION_ERROR",
            http_status=422
        )

# --- 错误处理器 ---
@app.errorhandler(BusinessError)
def handle_business_error(error):
    return jsonify({
        "error": error.error_code,
        "message": error.message
    }), error.http_status

@app.errorhandler(HTTPException)
def handle_http_error(error):
    return jsonify({
        "error": error.name.upper().replace(" ", "_"),
        "message": error.description
    }), error.code

@app.errorhandler(Exception)
def handle_server_error(error):
    app.logger.exception("未预期的服务器错误")
    return jsonify({
        "error": "INTERNAL_SERVER_ERROR",
        "message": "服务器内部错误，请稍后重试"
    }), 500

# --- 测试路由 ---
ARTICLES = {1: {"id": 1, "title": "Flask 入门", "author_id": 1}}

@app.route("/api/articles/<int:article_id>")
def get_article(article_id):
    article = ARTICLES.get(article_id)
    if not article:
        raise ResourceNotFound("文章", article_id)
    return jsonify(article)

@app.route("/api/articles", methods=["POST"])
def create_article():
    data = request.get_json() or {}
    
    title = data.get("title", "").strip()
    if not title:
        raise ValidationError("title", "标题不能为空")
    if len(title) > 200:
        raise ValidationError("title", "标题不超过200个字符")
    
    new_id = max(ARTICLES.keys()) + 1
    article = {"id": new_id, "title": title, "author_id": 1}
    ARTICLES[new_id] = article
    return jsonify(article), 201

if __name__ == "__main__":
    app.run(debug=False, port=5002)
```

```
# 预期输出：

# GET /api/articles/1
# → 200 {"author_id": 1, "id": 1, "title": "Flask 入门"}

# GET /api/articles/999
# → 404 {"error": "RESOURCE_NOT_FOUND", "message": "文章 (ID=999) 不存在"}

# POST /api/articles {}
# → 422 {"error": "VALIDATION_ERROR", "message": "字段 'title' 验证失败：标题不能为空"}

# GET /nonexistent
# → 404 {"error": "NOT_FOUND", "message": "The requested URL was not found on the server..."}
```

---

## Demo 4：Flask-SQLAlchemy 基本操作

```python
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///demo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "demo-secret"

db = SQLAlchemy(app)

# --- 模型 ---
class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# 多对多中间表
post_tags = db.Table("post_tags",
    db.Column("post_id", db.Integer, db.ForeignKey("posts.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"))
)

class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.relationship("Tag", secondary=post_tags, backref="posts")
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "tags": [t.name for t in self.tags],
            "created_at": self.created_at.isoformat()
        }

# --- 路由 ---
@app.route("/api/posts", methods=["POST"])
def create_post():
    data = request.get_json()
    
    post = Post(title=data["title"], content=data.get("content", ""))
    
    # 处理标签（不存在则创建）
    for tag_name in data.get("tags", []):
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        post.tags.append(tag)
    
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_dict()), 201

@app.route("/api/posts")
def list_posts():
    tag_filter = request.args.get("tag")
    
    if tag_filter:
        posts = Post.query.join(Post.tags).filter(Tag.name == tag_filter).all()
    else:
        posts = Post.query.order_by(Post.created_at.desc()).all()
    
    return jsonify([p.to_dict() for p in posts])

@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return "", 204

# 初始化数据库
with app.app_context():
    db.create_all()
    # 插入测试数据
    if Post.query.count() == 0:
        p1 = Post(title="Flask 入门", content="...")
        p2 = Post(title="SQLAlchemy 指南", content="...")
        t_python = Tag(name="python")
        t_web = Tag(name="web")
        p1.tags = [t_python, t_web]
        p2.tags = [t_python]
        db.session.add_all([p1, p2])
        db.session.commit()
        print("测试数据已初始化")

if __name__ == "__main__":
    app.run(debug=True, port=5003)
```

```
# 预期输出（初始化时）：
测试数据已初始化

# GET /api/posts
# → [
#     {"created_at": "...", "id": 2, "tags": ["python"], "title": "SQLAlchemy 指南"},
#     {"created_at": "...", "id": 1, "tags": ["python", "web"], "title": "Flask 入门"}
#   ]

# GET /api/posts?tag=web
# → [{"id": 1, "tags": ["python", "web"], "title": "Flask 入门", ...}]

# POST /api/posts {"title": "Redis 缓存", "tags": ["python", "cache"]}
# → 201 {"id": 3, "tags": ["python", "cache"], "title": "Redis 缓存", ...}
```
