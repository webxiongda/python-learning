# 第43章 自测题：Flask 进阶

## 题目1：Blueprint 的作用

**问题：** 解释 Blueprint 的作用，并说明以下代码中 `url_prefix` 的意义：

```python
from flask import Blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

@api_bp.route("/users")
def list_users():
    return "用户列表"
```

当用 `app.register_blueprint(api_bp)` 注册后，访问哪个 URL 可以触发 `list_users`？

### 参考答案

**Blueprint 的作用：**
1. **模块化**：将相关路由、视图函数、模板按功能组织到独立模块中
2. **可复用**：同一蓝图可以以不同 url_prefix 注册多次
3. **支持应用工厂模式**：方便创建多个 Flask 实例（测试、生产环境隔离）
4. **独立的错误处理和钩子**：蓝图可以有自己的 before_request 等钩子

**url_prefix 的意义：**  
`url_prefix="/api/v1"` 会为蓝图内的所有路由添加统一前缀。

注册后，`@api_bp.route("/users")` 的完整 URL 变为 `/api/v1/users`。

访问 `http://localhost:5000/api/v1/users` 会触发 `list_users()`。

---

## 题目2：before_request 钩子

**问题：** 下面的 `before_request` 钩子有什么问题？

```python
@app.before_request
def check_token():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "需要认证"}), 401
```

### 参考答案

**问题1：不区分公开路由和受保护路由**  
对所有路由（包括登录接口、健康检查等）都要求 Token，导致无法登录（登录接口本身也被拦截）。

**问题2：Token 格式验证不完整**  
只检查了 Token 是否存在，没有验证 `Bearer` 前缀格式，也没有验证 Token 的有效性。

**修复建议：**
```python
PUBLIC_PATHS = {"/login", "/health", "/"}

@app.before_request
def check_token():
    # 1. 跳过公开路由
    if request.path in PUBLIC_PATHS:
        return None
    
    # 2. 提取 Bearer Token
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "需要 Bearer Token"}), 401
    
    token = auth_header[7:]  # 去掉 "Bearer " 前缀
    
    # 3. 验证 Token 有效性（此处简化，实际应验证 JWT）
    if token != "valid-token":
        return jsonify({"error": "Token 无效或已过期"}), 401
    
    # 4. 将用户信息存入 g，供视图函数使用
    g.current_user = {"id": 1, "username": "alice"}
```

---

## 题目3：Flask-Login 概念

**问题：** `UserMixin` 类提供了哪些方法？为什么用户模型必须继承它？

### 参考答案

`UserMixin` 提供了 Flask-Login 要求的 4 个属性/方法的默认实现：

| 属性/方法          | 默认值  | 含义               |
|-------------------|------|------------------|
| `is_authenticated` | True | 用户是否已认证        |
| `is_active`        | True | 账户是否激活（未被禁用） |
| `is_anonymous`     | False| 是否匿名用户         |
| `get_id()`         | str(self.id) | 返回用户唯一标识符 |

**为什么必须继承：**  
Flask-Login 的 `login_user()`、`current_user`、`@login_required` 等功能都依赖这些接口。如果自定义用户类没有这些方法，Flask-Login 会报错。继承 `UserMixin` 可以直接使用默认实现，只需重写需要定制的方法（例如禁用用户时需要 `is_active` 返回 False）。

---

## 题目4：Flask-SQLAlchemy 关系

**问题：** 以下代码定义了用户和文章的关系，请解释 `lazy="dynamic"` 和 `back_populates` 的含义：

```python
class User(db.Model):
    posts = db.relationship("Post", back_populates="author", lazy="dynamic")

class Post(db.Model):
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = db.relationship("User", back_populates="posts")
```

### 参考答案

**`lazy="dynamic"` 的含义：**  
控制关联数据的加载时机。`lazy="dynamic"` 表示访问 `user.posts` 时**不立即执行 SQL 查询**，而是返回一个 **Query 对象**，只有在真正迭代或调用 `.all()` 时才执行查询。适合数据量大的场景（可以在查询前添加过滤条件）：

```python
# 不会立即查询
user.posts  # 返回 Query 对象

# 添加过滤后才查询
recent_posts = user.posts.filter(Post.created_at > some_date).all()
```

对比：`lazy="select"`（默认）会在第一次访问 `user.posts` 时立即执行 SELECT 查询。

**`back_populates` 的含义：**  
双向显式声明关系，让两个模型都知道彼此的关系属性名称。  
- `User.posts` 对应 `Post.author`，两者互为反向引用  
- 修改一方，另一方会自动同步：`post.author = user` 会自动把 post 加入 `user.posts`

对比 `backref`：`backref` 只需在一边声明，自动在另一边创建反向属性；`back_populates` 需要两边都写，更显式、更易读。

---

## 题目5：错误处理综合

**问题：** 为以下函数添加完整的错误处理（包括自定义异常和 errorhandler）：

```python
@app.route("/api/users/<int:user_id>/transfer", methods=["POST"])
def transfer_funds(user_id):
    data = request.get_json()
    amount = data["amount"]          # 可能 KeyError
    target_id = data["target_id"]    # 可能 KeyError
    # 假设 do_transfer() 可能抛出 ValueError（余额不足）
    do_transfer(user_id, target_id, float(amount))
    return jsonify({"status": "ok"})
```

### 参考答案

```python
# 1. 定义自定义异常
class InsufficientFundsError(Exception):
    def __init__(self, balance: float, required: float):
        self.balance = balance
        self.required = required
        super().__init__(f"余额不足：当前 {balance}，需要 {required}")

# 2. 注册错误处理器
@app.errorhandler(InsufficientFundsError)
def handle_insufficient_funds(error):
    return jsonify({
        "error": "INSUFFICIENT_FUNDS",
        "message": str(error),
        "balance": error.balance,
        "required": error.required
    }), 422

# 3. 改进视图函数
@app.route("/api/users/<int:user_id>/transfer", methods=["POST"])
def transfer_funds(user_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "需要 JSON 请求体"}), 400
    
    # 安全获取必填字段
    amount = data.get("amount")
    target_id = data.get("target_id")
    
    if amount is None or target_id is None:
        return jsonify({
            "error": "MISSING_FIELD",
            "message": "amount 和 target_id 为必填字段"
        }), 422
    
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError("转账金额必须大于0")
    except (TypeError, ValueError) as e:
        return jsonify({"error": "INVALID_AMOUNT", "message": str(e)}), 422
    
    # do_transfer 可能抛出 InsufficientFundsError（由 errorhandler 捕获）
    do_transfer(user_id, int(target_id), amount)
    return jsonify({"status": "ok", "transferred": amount})
```
