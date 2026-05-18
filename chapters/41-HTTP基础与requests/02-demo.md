# 第41章 Demo：HTTP基础与requests库

## Demo 1：基础 GET 请求与响应解析

```python
import requests

def demo_basic_get():
    """演示基础 GET 请求和响应对象的各个属性"""
    
    # 使用 httpbin.org 作为测试服务
    url = "https://httpbin.org/get"
    params = {"name": "Alice", "age": 25, "city": "北京"}
    
    print("=== 发送 GET 请求 ===")
    response = requests.get(url, params=params, timeout=10)
    
    # 响应基本信息
    print(f"状态码: {response.status_code}")
    print(f"响应头 Content-Type: {response.headers.get('Content-Type')}")
    print(f"最终请求 URL: {response.url}")
    print(f"响应时间: {response.elapsed.total_seconds():.3f} 秒")
    
    # 解析 JSON 响应
    data = response.json()
    print(f"\n服务器收到的 args 参数:")
    for key, value in data["args"].items():
        print(f"  {key}: {value}")
    
    print(f"\n请求来源 IP: {data['origin']}")

demo_basic_get()
```

```
# 预期输出：
=== 发送 GET 请求 ===
状态码: 200
响应头 Content-Type: application/json
最终请求 URL: https://httpbin.org/get?name=Alice&age=25&city=%E5%8C%97%E4%BA%AC
响应时间: 0.523 秒

服务器收到的 args 参数:
  age: 25
  city: 北京
  name: Alice

请求来源 IP: 203.xxx.xxx.xxx
```

---

## Demo 2：POST 请求与不同认证方式

```python
import requests
import json

def demo_post_and_auth():
    """演示 POST 请求 JSON 数据 和 Bearer Token 认证"""
    
    # --- POST JSON 数据 ---
    print("=== POST JSON 数据 ===")
    payload = {
        "title": "Python 学习笔记",
        "content": "今天学习了 requests 库",
        "tags": ["python", "http"],
        "published": True
    }
    
    response = requests.post(
        "https://httpbin.org/post",
        json=payload,
        timeout=10
    )
    
    data = response.json()
    # httpbin 会把我们发送的 JSON 原样返回
    received = json.loads(data["data"])
    print(f"服务器收到的 title: {received['title']}")
    print(f"服务器收到的 tags: {received['tags']}")
    print(f"请求的 Content-Type: {data['headers']['Content-Type']}")
    
    # --- Bearer Token 认证 ---
    print("\n=== Bearer Token 认证 ===")
    fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
    headers = {
        "Authorization": f"Bearer {fake_token}",
        "X-Request-ID": "req-001"
    }
    
    response = requests.get(
        "https://httpbin.org/headers",
        headers=headers,
        timeout=10
    )
    
    received_headers = response.json()["headers"]
    print(f"Authorization 头已发送: {received_headers.get('Authorization', '')[:30]}...")
    print(f"X-Request-ID: {received_headers.get('X-Request-Id')}")
    
    # --- Basic 认证 ---
    print("\n=== Basic 认证 ===")
    response = requests.get(
        "https://httpbin.org/basic-auth/admin/secret",
        auth=("admin", "secret"),
        timeout=10
    )
    print(f"Basic 认证状态码: {response.status_code}")
    print(f"认证结果: {response.json()}")

demo_post_and_auth()
```

```
# 预期输出：
=== POST JSON 数据 ===
服务器收到的 title: Python 学习笔记
服务器收到的 tags: ['python', 'http']
请求的 Content-Type: application/json

=== Bearer Token 认证 ===
Authorization 头已发送: Bearer eyJhbGciOiJIUzI1NiIsInR5...
X-Request-ID: req-001

=== Basic 认证 ===
Basic 认证状态码: 200
认证结果: {'authenticated': True, 'user': 'admin'}
```

---

## Demo 3：Session 会话保持与 Cookie 管理

```python
import requests

def demo_session():
    """演示 Session 复用 Headers/Cookies 和连接池"""
    
    print("=== Session 演示 ===")
    
    with requests.Session() as session:
        # 统一设置 Session 级别的 Headers
        session.headers.update({
            "User-Agent": "MyApp/1.0",
            "Accept": "application/json",
            "X-API-Version": "v2"
        })
        
        # 请求1：获取 cookies
        print("-- 请求1：设置 Cookie --")
        r1 = session.get(
            "https://httpbin.org/cookies/set",
            params={"session_id": "abc123", "user": "alice"},
            timeout=10,
            allow_redirects=True
        )
        print(f"当前 Session Cookies: {dict(session.cookies)}")
        
        # 请求2：验证 cookies 被自动携带
        print("\n-- 请求2：自动携带 Cookie --")
        r2 = session.get("https://httpbin.org/cookies", timeout=10)
        print(f"服务器收到的 Cookies: {r2.json()['cookies']}")
        
        # 请求3：验证 Headers 被复用
        print("\n-- 请求3：验证 Headers 复用 --")
        r3 = session.get("https://httpbin.org/headers", timeout=10)
        headers = r3.json()["headers"]
        print(f"User-Agent: {headers.get('User-Agent')}")
        print(f"X-Api-Version: {headers.get('X-Api-Version')}")

demo_session()
```

```
# 预期输出：
=== Session 演示 ===
-- 请求1：设置 Cookie --
当前 Session Cookies: {'session_id': 'abc123', 'user': 'alice'}

-- 请求2：自动携带 Cookie --
服务器收到的 Cookies: {'session_id': 'abc123', 'user': 'alice'}

-- 请求3：验证 Headers 复用 --
User-Agent: MyApp/1.0
X-Api-Version: v2
```

---

## Demo 4：超时与重试机制

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

def create_resilient_session(
    total_retries=3,
    backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504)
):
    """创建具有重试能力的 Session"""
    session = requests.Session()
    
    retry = Retry(
        total=total_retries,
        read=total_retries,
        connect=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        raise_on_status=False
    )
    
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def demo_timeout_and_retry():
    """演示超时捕获和重试策略"""
    
    # --- 超时演示 ---
    print("=== 超时处理演示 ===")
    try:
        # delay=5 让服务器延迟5秒响应，但我们只等2秒
        response = requests.get(
            "https://httpbin.org/delay/5",
            timeout=2
        )
    except requests.exceptions.Timeout:
        print("请求超时！（等待 2 秒后放弃）")
    except requests.exceptions.ConnectionError as e:
        print(f"连接失败（网络问题）: {e}")
    
    # --- 正常超时 ---
    print("\n=== 正常请求（足够超时时间）===")
    try:
        response = requests.get(
            "https://httpbin.org/delay/1",
            timeout=5
        )
        print(f"请求成功，状态码: {response.status_code}")
    except requests.exceptions.Timeout:
        print("超时了")
    
    # --- 重试 Session 演示 ---
    print("\n=== 重试 Session 演示 ===")
    session = create_resilient_session(total_retries=2)
    
    # 模拟请求（500状态码会自动重试）
    start = time.time()
    response = session.get(
        "https://httpbin.org/status/200",
        timeout=5
    )
    elapsed = time.time() - start
    print(f"状态码: {response.status_code}，耗时: {elapsed:.2f}s")
    
    session.close()

demo_timeout_and_retry()
```

```
# 预期输出：
=== 超时处理演示 ===
请求超时！（等待 2 秒后放弃）

=== 正常请求（足够超时时间）===
请求成功，状态码: 200

=== 重试 Session 演示 ===
状态码: 200，耗时: 0.45s
```

---

## Demo 5：完整的 API 客户端封装

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any

class APIClient:
    """封装 requests 的通用 API 客户端"""
    
    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.session = self._create_session(token)
    
    def _create_session(self, token: Optional[str]) -> requests.Session:
        session = requests.Session()
        
        # 默认 Headers
        session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        
        if token:
            session.headers["Authorization"] = f"Bearer {token}"
        
        # 重试策略
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    def get(self, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def post(self, path: str, data: Dict) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        response = self.session.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def close(self):
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


# 使用封装的客户端
def demo_api_client():
    print("=== 封装 API 客户端演示 ===")
    
    with APIClient("https://httpbin.org", token="my-secret-token") as client:
        # GET 请求
        result = client.get("/get", params={"user": "alice", "page": 1})
        print(f"GET 请求成功，收到参数: {result['args']}")
        
        # POST 请求
        result = client.post("/post", data={"action": "create", "name": "test"})
        import json
        body = json.loads(result["data"])
        print(f"POST 请求成功，发送数据: {body}")
        
        # 验证 Token 已注入
        print(f"Authorization: {result['headers']['Authorization'][:20]}...")

demo_api_client()
```

```
# 预期输出：
=== 封装 API 客户端演示 ===
GET 请求成功，收到参数: {'page': '1', 'user': 'alice'}
POST 请求成功，发送数据: {'action': 'create', 'name': 'test'}
Authorization: Bearer my-secret-token...
```
