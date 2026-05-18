# 第33章 Demo：异步编程基础（asyncio）

## Demo 1：协程基础与事件循环

```python
import asyncio
import time

async def greet(name, delay):
    """一个简单的协程：等待delay秒后打招呼"""
    print(f"[{time.strftime('%H:%M:%S')}] {name}: 开始等待 {delay}s")
    await asyncio.sleep(delay)
    print(f"[{time.strftime('%H:%M:%S')}] {name}: 你好！")
    return f"{name} 已问候"

async def main():
    print("=== 顺序执行 ===")
    start = time.time()
    r1 = await greet("Alice", 2)
    r2 = await greet("Bob", 1)
    print(f"顺序结果: {[r1, r2]}, 耗时: {time.time()-start:.1f}s\n")

    print("=== 并发执行 ===")
    start = time.time()
    results = await asyncio.gather(
        greet("Alice", 2),
        greet("Bob", 1),
        greet("Charlie", 1.5),
    )
    print(f"并发结果: {results}, 耗时: {time.time()-start:.1f}s")

asyncio.run(main())
```

```
# 预期输出：
=== 顺序执行 ===
[10:00:00] Alice: 开始等待 2s
[10:00:02] Alice: 你好！
[10:00:02] Bob: 开始等待 1s
[10:00:03] Bob: 你好！
顺序结果: ['Alice 已问候', 'Bob 已问候'], 耗时: 3.0s

=== 并发执行 ===
[10:00:03] Alice: 开始等待 2s
[10:00:03] Bob: 开始等待 1s
[10:00:03] Charlie: 开始等待 1.5s
[10:00:04] Bob: 你好！
[10:00:04] Charlie: 你好！
[10:00:05] Alice: 你好！
并发结果: ['Alice 已问候', 'Bob 已问候', 'Charlie 已问候'], 耗时: 2.0s
```

---

## Demo 2：create_task 与任务取消

```python
import asyncio

async def long_running(task_id, duration):
    try:
        print(f"任务 {task_id} 开始，预计 {duration}s")
        await asyncio.sleep(duration)
        print(f"任务 {task_id} 完成")
        return f"结果-{task_id}"
    except asyncio.CancelledError:
        print(f"任务 {task_id} 被取消！")
        raise  # 必须重新抛出 CancelledError

async def main():
    # 创建任务
    task1 = asyncio.create_task(long_running(1, 3), name="task-1")
    task2 = asyncio.create_task(long_running(2, 1), name="task-2")
    task3 = asyncio.create_task(long_running(3, 5), name="task-3")

    # 等待1.5秒后取消 task3
    await asyncio.sleep(1.5)
    print(f"\n取消任务3（task3.done()={task3.done()}）")
    task3.cancel()

    # 等待剩余任务
    results = await asyncio.gather(task1, task2, task3, return_exceptions=True)
    for i, r in enumerate(results, 1):
        if isinstance(r, asyncio.CancelledError):
            print(f"任务{i}: 已取消")
        elif isinstance(r, Exception):
            print(f"任务{i}: 异常 {r}")
        else:
            print(f"任务{i}: {r}")

asyncio.run(main())
```

```
# 预期输出：
任务 1 开始，预计 3s
任务 2 开始，预计 1s
任务 3 开始，预计 5s
任务 2 完成

取消任务3（task3.done()=False）
任务 3 被取消！
任务 1 完成
任务1: 结果-1
任务2: 结果-2
任务3: 已取消
```

---

## Demo 3：asyncio.wait 与超时控制

```python
import asyncio
import random

async def api_call(endpoint, max_wait=3):
    """模拟API调用，随机延迟"""
    delay = random.uniform(0.5, 4.0)
    print(f"  → 请求 {endpoint}（预计 {delay:.1f}s）")
    await asyncio.sleep(delay)
    return {"endpoint": endpoint, "status": 200}

async def main():
    endpoints = ["/users", "/orders", "/products", "/inventory"]

    # 方法1：wait 等待第一个完成
    print("【先到先得模式】")
    tasks = {asyncio.create_task(api_call(ep)): ep for ep in endpoints[:3]}
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    for task in done:
        print(f"  最快完成: {task.result()['endpoint']}")
    for task in pending:
        task.cancel()   # 取消剩余任务
        await asyncio.gather(task, return_exceptions=True)

    # 方法2：带超时的 wait_for
    print("\n【超时控制】")
    try:
        result = await asyncio.wait_for(
            api_call("/slow-service"),
            timeout=1.5     # 超时1.5秒
        )
        print(f"  请求成功: {result}")
    except asyncio.TimeoutError:
        print("  请求超时！使用缓存数据")

asyncio.run(main())
```

```
# 预期输出：
【先到先得模式】
  → 请求 /users（预计 1.2s）
  → 请求 /orders（预计 2.8s）
  → 请求 /products（预计 0.7s）
  最快完成: /products

【超时控制】
  → 请求 /slow-service（预计 3.1s）
  请求超时！使用缓存数据
```

---

## Demo 4：异步上下文管理器与生成器

```python
import asyncio

class AsyncTimer:
    """异步上下文管理器：计时器"""

    def __init__(self, name):
        self.name = name
        self._start = None

    async def __aenter__(self):
        import time
        self._start = time.time()
        print(f"[{self.name}] 开始计时")
        return self          # 返回给 as 子句

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        import time
        elapsed = time.time() - self._start
        print(f"[{self.name}] 耗时: {elapsed:.2f}s")
        return False         # 不抑制异常

async def async_number_gen(n):
    """异步生成器：逐个产出数字"""
    for i in range(n):
        await asyncio.sleep(0.1)  # 模拟异步获取
        yield i * i               # 产出平方值

async def main():
    # 使用异步上下文管理器
    async with AsyncTimer("计算任务"):
        await asyncio.sleep(0.5)
        print("  任务执行中...")

    print()

    # 使用异步生成器
    print("异步生成平方数:")
    async for value in async_number_gen(5):
        print(f"  {value}", end=" ")
    print()

    # 使用列表推导式收集异步生成器结果
    squares = [v async for v in async_number_gen(5)]
    print(f"列表推导: {squares}")

asyncio.run(main())
```

```
# 预期输出：
[计算任务] 开始计时
  任务执行中...
[计算任务] 耗时: 0.50s

异步生成平方数:
  0 1 4 9 16
列表推导: [0, 1, 4, 9, 16]
```

---

## Demo 5：run_in_executor 运行阻塞代码

```python
import asyncio
import time
import concurrent.futures

def blocking_io(filename):
    """同步阻塞的文件操作（模拟）"""
    time.sleep(0.5)  # 模拟慢速I/O
    return f"内容来自 {filename}（{len(filename)} 字节）"

def blocking_cpu(n):
    """同步CPU密集型计算"""
    return sum(i * i for i in range(n))

async def main():
    loop = asyncio.get_event_loop()

    # 在默认线程池中运行阻塞I/O
    print("并发读取文件（使用线程池执行器）:")
    start = time.time()
    tasks = [
        loop.run_in_executor(None, blocking_io, f"file_{i}.txt")
        for i in range(5)
    ]
    results = await asyncio.gather(*tasks)
    print(f"  耗时: {time.time()-start:.2f}s（5个文件并发读取）")
    for r in results:
        print(f"  {r}")

    # 在进程池中运行CPU密集型任务（绕过GIL）
    print("\nCPU密集型任务（使用进程池执行器）:")
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        start = time.time()
        cpu_tasks = [
            loop.run_in_executor(executor, blocking_cpu, 1_000_000)
            for _ in range(4)
        ]
        cpu_results = await asyncio.gather(*cpu_tasks)
        print(f"  耗时: {time.time()-start:.2f}s, 结果: {cpu_results[0]}")

asyncio.run(main())
```

```
# 预期输出：
并发读取文件（使用线程池执行器）:
  耗时: 0.51s（5个文件并发读取）
  内容来自 file_0.txt（10 字节）
  内容来自 file_1.txt（10 字节）
  ...

CPU密集型任务（使用进程池执行器）:
  耗时: 0.35s, 结果: 333332833333500000
```
