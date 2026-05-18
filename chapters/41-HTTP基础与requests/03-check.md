# 第41章 自测题：HTTP基础与requests库

## 题目1：HTTP 方法辨析

**问题：** 下列场景应使用哪种 HTTP 方法？请说明理由。

1. 查询用户列表（不修改数据）
2. 用户注册（创建新用户）
3. 修改用户头像（只更新部分字段）
4. 删除一篇博客文章
5. 完整替换某商品的全部信息

### 参考答案

1. **GET** — 读取操作，不改变服务器状态，且是幂等的
2. **POST** — 创建资源，每次请求可能产生新用户，不是幂等的
3. **PATCH** — 部分更新，只发送需要修改的字段（如只发 `avatar_url`）
4. **DELETE** — 删除资源，幂等（多次删除同一资源结果相同——资源不存在）
5. **PUT** — 完整替换，需要发送资源的完整表示，是幂等的

**补充区分 PUT vs PATCH：**
- `PUT /users/1` + `{"name":"Alice","email":"a@b.com","age":25}` → 完整替换
- `PATCH /users/1` + `{"age":26}` → 只更新 age 字段

---

## 题目2：状态码判断

**问题：** 以下情况服务器应返回什么状态码？

1. 用户请求的文章 ID 不存在
2. 用户未登录就访问需要认证的接口
3. 用户已登录但权限不足（普通用户访问管理员接口）
4. 成功创建了一篇新文章
5. 成功删除了一条评论（不需要返回任何内容）

### 参考答案

1. **404 Not Found** — 资源不存在
2. **401 Unauthorized** — 未认证，需要提供身份凭据（如 Token）
3. **403 Forbidden** — 已认证但没有操作权限
4. **201 Created** — 成功创建，通常响应体包含新创建的资源
5. **204 No Content** — 成功删除，但没有内容需要返回（响应体为空）

---

## 题目3：代码填空

**问题：** 补全以下代码，使其能正确发送带 Bearer Token 的 POST 请求：

```python
import requests

token = "abc123"
data = {"title": "测试", "body": "内容"}

response = requests.post(
    "https://api.example.com/posts",
    ___________,      # 填空1：发送 JSON 数据
    ___________,      # 填空2：设置认证 Header
    timeout=10
)

if response.status_code == ___________:  # 填空3：成功创建的状态码
    print("创建成功:", response.json())
```

### 参考答案

```python
import requests

token = "abc123"
data = {"title": "测试", "body": "内容"}

response = requests.post(
    "https://api.example.com/posts",
    json=data,                                          # 填空1
    headers={"Authorization": f"Bearer {token}"},      # 填空2
    timeout=10
)

if response.status_code == 201:  # 填空3
    print("创建成功:", response.json())
```

**关键点：**
- 使用 `json=data` 而不是 `data=data`，前者自动设置 `Content-Type: application/json`
- 使用 `headers={"Authorization": f"Bearer {token}"}` 设置认证头
- 创建成功状态码是 `201`，不是 `200`

---

## 题目4：Session 使用场景

**问题：** 有以下两段代码，哪段更好？为什么？

**代码 A：**
```python
import requests

token = "mytoken"
for user_id in range(1, 6):
    response = requests.get(
        f"https://api.example.com/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5
    )
    print(response.json())
```

**代码 B：**
```python
import requests

token = "mytoken"
with requests.Session() as s:
    s.headers["Authorization"] = f"Bearer {token}"
    for user_id in range(1, 6):
        response = s.get(
            f"https://api.example.com/users/{user_id}",
            timeout=5
        )
        print(response.json())
```

### 参考答案

**代码 B 更好**，原因如下：

1. **TCP 连接复用**：Session 内部维护连接池，对同一主机的多次请求会复用 TCP 连接（Keep-Alive），减少握手开销，代码 A 每次都建立新连接
2. **避免重复代码**：Headers、auth 等配置只需设置一次，不用每次请求都重复写
3. **Cookie 自动管理**：如果服务器返回 Cookie，Session 会自动存储并在后续请求中携带
4. **with 语句保证资源释放**：`with` 语句确保循环结束后连接池被正确关闭，避免资源泄漏

---

## 题目5：错误处理

**问题：** 以下代码有什么问题？请修复它：

```python
import requests

response = requests.get("https://api.example.com/data")
data = response.json()  # 直接解析
print(data["result"])   # 直接访问
```

### 参考答案

原代码存在以下问题：
1. 没有设置 `timeout`，如果服务器不响应会永久阻塞
2. 没有处理网络错误（ConnectionError、Timeout）
3. 没有检查 HTTP 状态码（4xx/5xx 也会执行 `.json()`）
4. 没有处理 `KeyError`（`result` 键可能不存在）

**修复后的代码：**

```python
import requests
from requests.exceptions import Timeout, ConnectionError, HTTPError, RequestException

try:
    response = requests.get(
        "https://api.example.com/data",
        timeout=10  # 修复1：设置超时
    )
    response.raise_for_status()  # 修复2：自动抛出 4xx/5xx 异常
    
    data = response.json()
    result = data.get("result", "默认值")  # 修复3：使用 .get() 避免 KeyError
    print(result)

except Timeout:
    print("请求超时，请稍后重试")
except ConnectionError:
    print("网络连接失败，请检查网络")
except HTTPError as e:
    print(f"服务器错误：{e.response.status_code} - {e.response.text}")
except RequestException as e:
    print(f"请求失败：{e}")
except ValueError:
    print("响应体不是有效的 JSON 格式")
```
