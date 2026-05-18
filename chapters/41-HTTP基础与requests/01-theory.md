# 第41章：HTTP基础与requests库

## 1. HTTP 协议概述

HTTP（HyperText Transfer Protocol）是 Web 通信的基础协议，采用**请求-响应**模型。

```
HTTP 请求-响应流程
═══════════════════════════════════════════════════════════

  客户端 (Client)                    服务器 (Server)
  ┌─────────────┐                   ┌─────────────────┐
  │   浏览器    │  ── HTTP Request ─▶│   Web Server    │
  │   Python    │                   │   (Nginx/Gunicorn)│
  │   脚本      │  ◀─ HTTP Response ─│                 │
  └─────────────┘                   └─────────────────┘

  请求结构：                         响应结构：
  ┌─────────────────────┐           ┌─────────────────────┐
  │ 请求行               │           │ 状态行               │
  │ GET /api/users HTTP/1.1│         │ HTTP/1.1 200 OK     │
  ├─────────────────────┤           ├─────────────────────┤
  │ 请求头               │           │ 响应头               │
  │ Host: example.com   │           │ Content-Type: json  │
  │ Authorization: ...  │           │ Content-Length: 256 │
  ├─────────────────────┤           ├─────────────────────┤
  │ 空行                 │           │ 空行                 │
  ├─────────────────────┤           ├─────────────────────┤
  │ 请求体（可选）        │           │ 响应体               │
  │ {"name": "Alice"}   │           │ {"id": 1, ...}      │
  └─────────────────────┘           └─────────────────────┘
```

---

## 2. HTTP 方法（Methods）

| 方法     | 用途           | 是否有请求体 | 幂等性 |
|--------|--------------|-----------|------|
| GET    | 获取资源         | 否         | 是    |
| POST   | 创建资源         | 是         | 否    |
| PUT    | 完整替换资源       | 是         | 是    |
| PATCH  | 部分更新资源       | 是         | 否    |
| DELETE | 删除资源         | 可选        | 是    |
| HEAD   | 获取响应头（无响应体）  | 否         | 是    |
| OPTIONS| 查询支持的方法      | 否         | 是    |

> **幂等性**：多次执行同一请求，结果相同。GET/PUT/DELETE 是幂等的；POST 不是（每次 POST 可能创建新资源）。

---

## 3. HTTP 状态码（Status Codes）

```
状态码分类
════════════════════════════════════════

  1xx  信息性    ──▶  100 Continue（继续）
  2xx  成功      ──▶  200 OK / 201 Created / 204 No Content
  3xx  重定向    ──▶  301 Moved Permanently / 302 Found
  4xx  客户端错误 ──▶  400 Bad Request / 401 Unauthorized
                      403 Forbidden / 404 Not Found
                      422 Unprocessable Entity / 429 Too Many Requests
  5xx  服务端错误 ──▶  500 Internal Server Error / 502 Bad Gateway
                      503 Service Unavailable
```

**常用状态码详解：**

- `200 OK`：请求成功
- `201 Created`：资源创建成功（通常 POST 后返回）
- `204 No Content`：成功但无响应体（通常 DELETE 后返回）
- `400 Bad Request`：请求参数错误
- `401 Unauthorized`：未认证（需要登录）
- `403 Forbidden`：已认证但无权限
- `404 Not Found`：资源不存在
- `422 Unprocessable Entity`：参数格式正确但语义错误（FastAPI 常用）
- `500 Internal Server Error`：服务器内部错误

---

## 4. HTTP Headers（请求头）

常见请求头：

| 头字段            | 说明               | 示例                                      |
|-----------------|------------------|-----------------------------------------|
| `Content-Type`  | 请求体格式            | `application/json`                      |
| `Authorization` | 认证信息             | `Bearer eyJhbGci...`                    |
| `Accept`        | 期望的响应格式          | `application/json`                      |
| `User-Agent`    | 客户端标识            | `Mozilla/5.0 ...`                       |
| `Cookie`        | 携带 Cookie         | `session=abc123`                        |
| `Content-Length`| 请求体字节数           | `256`                                   |

---

## 5. requests 库基础

`requests` 是 Python 最流行的 HTTP 客户端库，封装了底层的 urllib。

### 安装

```bash
pip install requests
```

### 基本 GET 请求

```python
import requests

# 发送 GET 请求
response = requests.get("https://httpbin.org/get")

# 响应对象属性
print(response.status_code)   # 200
print(response.headers)       # 响应头字典
print(response.text)          # 响应体（字符串）
print(response.json())        # 解析 JSON 响应体
print(response.content)       # 响应体（bytes）
print(response.url)           # 最终请求的 URL（含重定向）
```

### GET 请求携带参数

```python
# 方式1：手动拼接
response = requests.get("https://httpbin.org/get?page=1&size=10")

# 方式2：params 字典（推荐，自动 URL 编码）
params = {"page": 1, "size": 10, "keyword": "hello world"}
response = requests.get("https://httpbin.org/get", params=params)
# 实际 URL：https://httpbin.org/get?page=1&size=10&keyword=hello+world
```

### POST 请求

```python
import requests

# 发送 JSON 数据
payload = {"username": "alice", "password": "secret"}
response = requests.post(
    "https://httpbin.org/post",
    json=payload  # 自动设置 Content-Type: application/json
)

# 发送表单数据
response = requests.post(
    "https://httpbin.org/post",
    data={"username": "alice", "password": "secret"}
    # 自动设置 Content-Type: application/x-www-form-urlencoded
)
```

---

## 6. 认证方式

### Bearer Token（JWT）认证

```python
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("https://api.example.com/me", headers=headers)
```

### Basic 认证

```python
# 方式1：手动设置 Header
import base64
credentials = base64.b64encode(b"user:password").decode()
headers = {"Authorization": f"Basic {credentials}"}

# 方式2：requests 内置（推荐）
response = requests.get(
    "https://api.example.com/data",
    auth=("username", "password")
)
```

---

## 7. Session 会话

`Session` 对象可以跨请求保持状态（如 Cookies、Headers），避免重复设置。

```
Session 工作原理
═══════════════════════════════════════════════════
  Session 对象
  ┌─────────────────────────────────────┐
  │  持久化配置：                         │
  │  - Headers（如 Authorization）       │
  │  - Cookies（自动维护）               │
  │  - 连接池（TCP 连接复用）             │
  └─────────────────────────────────────┘
          │         │         │
         ▼         ▼         ▼
    请求1        请求2       请求3
   (复用配置)   (复用配置)  (复用配置)
```

```python
import requests

# 使用 Session
session = requests.Session()
session.headers.update({"Authorization": "Bearer mytoken"})

# 所有请求自动携带 Authorization Header
r1 = session.get("https://api.example.com/users")
r2 = session.get("https://api.example.com/posts")
session.close()

# 推荐使用 with 语句（自动关闭）
with requests.Session() as s:
    s.headers["Authorization"] = "Bearer mytoken"
    r = s.get("https://api.example.com/profile")
```

---

## 8. 超时与重试

### 超时设置

```python
# connect timeout（连接超时）+ read timeout（读取超时）
response = requests.get(
    "https://api.example.com/data",
    timeout=(5, 30)  # 5秒连接超时，30秒读取超时
)

# 单一值（connect 和 read 使用相同超时）
response = requests.get("https://api.example.com/data", timeout=10)
```

### 重试机制（urllib3 Retry）

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retry():
    """创建带重试策略的 Session"""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,               # 最大重试次数
        backoff_factor=1,      # 退避因子（等待时间：1, 2, 4 秒）
        status_forcelist=[429, 500, 502, 503, 504],  # 触发重试的状态码
        allowed_methods=["GET", "POST"]  # 允许重试的方法
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    return session

session = create_session_with_retry()
response = session.get("https://api.example.com/data", timeout=10)
```

---

## 9. 错误处理

```python
import requests
from requests.exceptions import (
    Timeout, ConnectionError, HTTPError, RequestException
)

try:
    response = requests.get("https://api.example.com/data", timeout=5)
    response.raise_for_status()  # 4xx/5xx 自动抛出 HTTPError
    data = response.json()
    
except Timeout:
    print("请求超时")
except ConnectionError:
    print("网络连接失败")
except HTTPError as e:
    print(f"HTTP 错误：{e.response.status_code}")
except RequestException as e:
    print(f"请求异常：{e}")
```

---

## 10. 知识点总结

```
requests 核心知识图谱
═══════════════════════════════════════════════════════

             HTTP 方法
         GET / POST / PUT / PATCH / DELETE
                    │
                    ▼
           requests 库核心
    ┌───────────────────────────────┐
    │  get() / post() / put() ...   │
    │  params / json / data / files │
    │  headers / auth / timeout     │
    └───────────────────────────────┘
           │              │
           ▼              ▼
      Response         Session
    .status_code    .headers.update()
    .json()         .get() / .post()
    .text           连接池复用
    .raise_for_status()
           │
           ▼
       重试策略
    HTTPAdapter + Retry
    backoff_factor / status_forcelist
```
