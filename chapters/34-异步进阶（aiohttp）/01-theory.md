# 第34章：异步进阶（aiohttp）

## aiohttp 简介

`aiohttp` 是基于 asyncio 的异步 HTTP 客户端/服务器库，是异步爬虫和微服务开发的首选。它相比 `requests` 的最大优势是**非阻塞**——发出请求后不锁住事件循环，可同时并发处理数千个请求。

```
requests（同步）：
发请求 ──[等待响应2s]──[收到]── 发请求 ──[等待响应1s]──[收到]──
总耗时: 3s，其中2s在等待

aiohttp（异步）：
发请求A ──────────────────────[收到A]──
发请求B ──────[收到B]──
总耗时: 2s（B完成时A仍在等待，但不阻塞）
```

---

## aiohttp.ClientSession

`ClientSession` 是 aiohttp 的核心类，**一个应用应只创建一个 Session 实例**，它内部管理连接池和 TCP 复用：

```python
import aiohttp
import asyncio

async def fetch(session, url):
    async with session.get(url) as response:
        # session.get() 返回一个异步上下文管理器
        status = response.status
        text = await response.text()
        return {"status": status, "length": len(text)}

async def main():
    # Session 必须在 async with 块内使用
    async with aiohttp.ClientSession() as session:
        result = await fetch(session, "https://httpbin.org/get")
        print(result)

asyncio.run(main())
```

**常用请求方法：**

```python
async with session.get(url, params={"q": "python"}) as resp: ...
async with session.post(url, json={"key": "value"}) as resp: ...
async with session.put(url, data=b"binary") as resp: ...
async with session.delete(url) as resp: ...
async with session.request("PATCH", url, headers={"X-Token": "abc"}) as resp: ...
```

---

## 响应处理

```python
async with session.get(url) as response:
    # 状态码
    print(response.status)          # 200
    print(response.reason)          # "OK"

    # 响应头
    print(response.headers)         # CIMultiDictProxy

    # 响应体（三选一）
    text = await response.text()           # 字符串
    data = await response.json()           # 解析JSON
    raw = await response.read()            # bytes

    # 流式读取（大文件）
    async for chunk in response.content.iter_chunked(1024):
        process(chunk)
```

---

## 并发请求与连接限制

```
不限速并发（危险！）：
1000个请求同时发出 → 服务器可能封禁IP

使用 TCPConnector 限速：
         ┌─────────────────────────────┐
请求队列  │ limit=100 TCPConnector       │
[req1]   │  ┌───┬───┬───┬── 最多100个 ─┐│
[req2]   │  │连接│连接│连接│...          ││
...      │  └───┴───┴───┴─────────────┘│
[req999] └─────────────────────────────┘
```

```python
import aiohttp
import asyncio

async def main():
    # 限制最多50个并发连接
    connector = aiohttp.TCPConnector(
        limit=50,               # 总连接数上限
        limit_per_host=10,      # 每个主机连接数上限
        ssl=False               # 禁用SSL验证（测试用）
    )
    timeout = aiohttp.ClientTimeout(total=30, connect=5)

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout
    ) as session:
        urls = [f"https://httpbin.org/delay/1" for _ in range(20)]
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
```

---

## 异步上下文管理器（__aenter__ / __aexit__）

asyncio 中资源管理的标准方式，实现 `async with` 语法：

```python
class AsyncResource:
    """自定义异步上下文管理器"""

    async def __aenter__(self):
        # 异步初始化（建立连接、打开文件等）
        await asyncio.sleep(0.01)  # 模拟异步开销
        print("资源已开启")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # 异步清理（关闭连接、刷新缓冲等）
        await asyncio.sleep(0.01)
        print("资源已关闭")
        # 返回 True 抑制异常，False 传播异常
        return False

# 使用
async with AsyncResource() as res:
    print("使用资源中...")
```

也可以用 `@asynccontextmanager` 装饰器（更简洁）：

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_connection(url):
    conn = await open_connection(url)
    try:
        yield conn          # yield 前 = __aenter__，yield 后 = __aexit__
    finally:
        await conn.close()

async with managed_connection("redis://localhost") as conn:
    await conn.set("key", "value")
```

---

## 异步生成器

```python
import aiohttp
import asyncio

async def paginated_fetch(session, base_url, max_pages=5):
    """异步生成器：逐页获取数据"""
    page = 1
    while page <= max_pages:
        url = f"{base_url}?page={page}&per_page=10"
        async with session.get(url) as resp:
            if resp.status != 200:
                return
            data = await resp.json()
            if not data:
                return
            yield data          # 产出当前页数据
            page += 1

async def main():
    async with aiohttp.ClientSession() as session:
        # 使用异步 for 循环消费
        async for page_data in paginated_fetch(session, "https://api.example.com/items"):
            print(f"处理第 {page_data.get('page')} 页，{len(page_data.get('items', []))} 条")

        # 或者收集所有页
        all_data = [
            page async for page in paginated_fetch(session, "https://api.example.com/items")
        ]
```

---

## anyio 简介

`anyio` 是多后端异步库，支持 asyncio 和 trio，提供统一 API：

```python
import anyio

async def main():
    # 替代 asyncio.sleep
    await anyio.sleep(1)

    # 任务组（替代 asyncio.gather）
    async with anyio.create_task_group() as tg:
        tg.start_soon(task1)
        tg.start_soon(task2)
    # 所有任务完成后继续

    # 超时（替代 asyncio.wait_for）
    with anyio.fail_after(5):   # 5秒超时
        await long_operation()

# 运行（自动选择后端）
anyio.run(main)
```

anyio 的优势：代码可以在 asyncio 和 trio 后端之间无缝切换，适合编写可移植的异步库。

---

## 小结

| 功能 | aiohttp API |
|------|-------------|
| 发起GET请求 | `session.get(url)` |
| 发起POST请求 | `session.post(url, json=data)` |
| 限制并发连接 | `TCPConnector(limit=N)` |
| 设置超时 | `ClientTimeout(total=N)` |
| 流式读取 | `response.content.iter_chunked(N)` |
| 异步上下文 | `async with ... as ...: ...` |
| 异步生成器 | `async def gen(): yield ...` |
