# 第34章 Demo：异步进阶（aiohttp）

## Demo 1：aiohttp 基础请求

```python
import aiohttp
import asyncio
import json

async def get_json(session, url):
    """发起GET请求，返回JSON数据"""
    async with session.get(url) as response:
        response.raise_for_status()         # 非2xx状态码抛出异常
        return await response.json()

async def post_data(session, url, payload):
    """发起POST请求"""
    headers = {"Content-Type": "application/json"}
    async with session.post(url, json=payload, headers=headers) as response:
        print(f"状态码: {response.status}")
        result = await response.json()
        return result

async def main():
    async with aiohttp.ClientSession() as session:
        # GET 请求
        data = await get_json(session, "https://httpbin.org/get")
        print("GET 响应 headers:", dict(list(data.get("headers", {}).items())[:3]))

        # POST 请求
        payload = {"username": "alice", "action": "login"}
        result = await post_data(session, "https://httpbin.org/post", payload)
        print("POST 响应 json:", result.get("json"))

asyncio.run(main())
```

```
# 预期输出：
GET 响应 headers: {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'Host': 'httpbin.org'}
状态码: 200
POST 响应 json: {'username': 'alice', 'action': 'login'}
```

---

## Demo 2：并发请求与限速

```python
import aiohttp
import asyncio
import time

async def fetch_url(session, url, semaphore):
    """带信号量限速的请求"""
    async with semaphore:           # 限制并发数
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                content = await resp.text()
                return {
                    "url": url,
                    "status": resp.status,
                    "length": len(content)
                }
        except aiohttp.ClientError as e:
            return {"url": url, "status": "error", "error": str(e)}
        except asyncio.TimeoutError:
            return {"url": url, "status": "timeout"}

async def main():
    # 模拟30个URL
    urls = [f"https://httpbin.org/delay/{i%3}" for i in range(15)]

    # 不限速
    connector = aiohttp.TCPConnector(limit=100)
    semaphore = asyncio.Semaphore(5)    # 同时最多5个请求

    start = time.time()
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_url(session, url, semaphore) for url in urls]
        results = await asyncio.gather(*tasks)

    elapsed = time.time() - start
    success = [r for r in results if r.get("status") == 200]
    print(f"完成 {len(urls)} 个请求 | 成功: {len(success)} | 耗时: {elapsed:.2f}s")
    for r in results[:3]:
        print(f"  {r['url'][-20:]} → {r['status']} ({r.get('length', 0)} bytes)")

asyncio.run(main())
```

```
# 预期输出：
完成 15 个请求 | 成功: 15 | 耗时: 6.23s
  httpbin.org/delay/0 → 200 (290 bytes)
  httpbin.org/delay/1 → 200 (290 bytes)
  httpbin.org/delay/2 → 200 (290 bytes)
```

---

## Demo 3：自定义异步上下文管理器

```python
import asyncio
from contextlib import asynccontextmanager

class AsyncHTTPPool:
    """异步HTTP连接池上下文管理器"""

    def __init__(self, base_url, max_connections=10):
        self.base_url = base_url
        self.max_connections = max_connections
        self._session = None
        self._request_count = 0

    async def __aenter__(self):
        import aiohttp
        connector = aiohttp.TCPConnector(limit=self.max_connections)
        self._session = aiohttp.ClientSession(
            base_url=self.base_url,
            connector=connector
        )
        print(f"连接池已创建: {self.base_url} (最大{self.max_connections}连接)")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
            print(f"连接池已关闭 | 共发出 {self._request_count} 次请求")
        return False    # 不抑制异常

    async def get(self, path, **kwargs):
        self._request_count += 1
        async with self._session.get(path, **kwargs) as resp:
            return {"status": resp.status, "data": await resp.text()}

# 使用 @asynccontextmanager 装饰器写法
@asynccontextmanager
async def timer(label):
    import time
    start = time.time()
    print(f"[{label}] 开始")
    try:
        yield
    finally:
        print(f"[{label}] 耗时: {time.time()-start:.2f}s")

async def main():
    async with timer("HTTP请求"):
        async with AsyncHTTPPool("https://httpbin.org", max_connections=5) as pool:
            results = await asyncio.gather(
                pool.get("/status/200"),
                pool.get("/status/201"),
                pool.get("/status/404"),
            )
            for r in results:
                print(f"  状态: {r['status']}")

asyncio.run(main())
```

```
# 预期输出：
[HTTP请求] 开始
连接池已创建: https://httpbin.org (最大5连接)
  状态: 200
  状态: 201
  状态: 404
连接池已关闭 | 共发出 3 次请求
[HTTP请求] 耗时: 0.87s
```

---

## Demo 4：异步生成器实现数据流

```python
import asyncio
import random

async def stream_events(source_name, count):
    """异步生成器：模拟事件流"""
    for i in range(count):
        await asyncio.sleep(random.uniform(0.1, 0.5))  # 模拟事件间隔
        yield {
            "source": source_name,
            "event_id": f"{source_name}-{i:03d}",
            "value": random.randint(1, 100)
        }

async def merge_streams(*async_gens):
    """合并多个异步生成器（使用任务并发）"""
    queue = asyncio.Queue()

    async def drain(gen):
        async for item in gen:
            await queue.put(item)
        await queue.put(None)   # 完成标记

    # 并发消费所有生成器
    tasks = [asyncio.create_task(drain(gen)) for gen in async_gens]

    finished = 0
    while finished < len(tasks):
        item = await queue.get()
        if item is None:
            finished += 1
        else:
            yield item

async def main():
    # 独立消费单个异步生成器
    print("=== 单流消费 ===")
    async for event in stream_events("传感器A", 5):
        print(f"  {event['event_id']}: {event['value']}")

    print("\n=== 合并多流 ===")
    sources = [
        stream_events("传感器X", 3),
        stream_events("传感器Y", 3),
        stream_events("传感器Z", 3),
    ]
    count = 0
    async for event in merge_streams(*sources):
        print(f"  [{event['source']}] {event['event_id']}: {event['value']}")
        count += 1
    print(f"共收到 {count} 个事件")

asyncio.run(main())
```

```
# 预期输出（顺序可能不同）：
=== 单流消费 ===
  传感器A-000: 42
  传感器A-001: 87
  传感器A-002: 15
  传感器A-003: 63
  传感器A-004: 29

=== 合并多流 ===
  [传感器X] 传感器X-000: 71
  [传感器Y] 传感器Y-000: 34
  [传感器Z] 传感器Z-000: 58
  ...（交替出现）
共收到 9 个事件
```

---

## Demo 5：anyio 兼容示例

```python
# pip install anyio
import anyio
import time

async def fetch_mock(url, delay):
    """模拟HTTP请求"""
    await anyio.sleep(delay)
    return {"url": url, "status": 200, "delay": delay}

async def main():
    print("使用 anyio 任务组并发请求:")
    start = time.time()

    urls = [
        ("https://api.example.com/users", 0.5),
        ("https://api.example.com/orders", 0.8),
        ("https://api.example.com/products", 0.3),
    ]

    results = []

    async with anyio.create_task_group() as tg:
        async def do_fetch(url, delay):
            result = await fetch_mock(url, delay)
            results.append(result)

        for url, delay in urls:
            tg.start_soon(do_fetch, url, delay)

    print(f"耗时: {time.time()-start:.2f}s（所有任务完成后才继续）")
    for r in sorted(results, key=lambda x: x["delay"]):
        print(f"  {r['url'].split('/')[-1]:10s} delay={r['delay']}s")

    # 超时控制
    print("\n超时控制测试:")
    try:
        with anyio.fail_after(0.3):         # 0.3秒内必须完成
            await fetch_mock("slow_api", 1.0)
    except TimeoutError:
        print("  请求超时（超过0.3秒）")

# anyio 可选择后端
anyio.run(main, backend="asyncio")
# anyio.run(main, backend="trio")  # 切换到trio后端
```

```
# 预期输出：
使用 anyio 任务组并发请求:
耗时: 0.81s（所有任务完成后才继续）
  products   delay=0.3s
  users      delay=0.5s
  orders     delay=0.8s

超时控制测试:
  请求超时（超过0.3秒）
```
