# 第33章：异步编程基础（asyncio）

## 并发的三种模型对比

```
多线程（抢占式）：
OS 调度切换，线程可被随时打断
Thread-1: ──[运行]──[被打断]──── 等待 ──[恢复]──
Thread-2: ────────[运行]────[被打断][恢复]────────

多进程（并行）：
真正的并行，各自独立运行
Process-1: ──[运行]──[运行]──[运行]──
Process-2: ──[运行]──[运行]──[运行]──  （不同CPU核）

协程（协作式）：
主动让出控制权，单线程内并发
Coroutine-1: ──[run]──[await让出]──────────[恢复run]──
Coroutine-2: ──────────────[run]──[await让出]──[run]──
              事件循环负责调度，零切换开销
```

---

## 事件循环（Event Loop）

asyncio 的核心是事件循环，它是一个无限循环，负责调度所有协程：

```
事件循环工作流程：

┌─────────────────────────────────────────┐
│              Event Loop                  │
│                                         │
│  就绪队列: [协程A, 协程C]                 │
│                    │                    │
│         取出协程A 执行                   │
│                    │                    │
│    协程A 遇到 await → 挂起               │
│                    │                    │
│  I/O 监听: {协程A等待socket, 协程B等待文件}│
│                    │                    │
│    I/O 完成 → 将协程移回就绪队列           │
└─────────────────────────────────────────┘
```

---

## async def 和 await

```python
import asyncio

# async def 定义协程函数
async def fetch_data(url):
    print(f"开始请求: {url}")
    await asyncio.sleep(1)      # await 暂停协程，让出事件循环
    print(f"请求完成: {url}")
    return {"url": url, "data": "..."}

# 协程函数调用返回协程对象（并不立即执行）
coro = fetch_data("http://example.com")
print(type(coro))    # <class 'coroutine'>

# 必须通过 asyncio.run() 或 await 来执行
result = asyncio.run(fetch_data("http://example.com"))
```

**await 关键字只能用在 async def 函数内部**，它可以等待：
- 另一个协程（`await other_coro()`）
- `asyncio.Future` 对象
- 实现了 `__await__` 的对象

---

## asyncio.create_task —— 并发运行

`create_task` 将协程包装为 Task，立即安排执行（不等待完成）：

```python
import asyncio
import time

async def download(name, delay):
    print(f"开始下载 {name}")
    await asyncio.sleep(delay)  # 模拟 I/O 等待
    print(f"完成下载 {name}")
    return name

async def main():
    start = time.time()

    # 顺序执行（总耗时 = 各任务之和）
    await download("A", 2)
    await download("B", 1)
    print(f"顺序耗时: {time.time()-start:.1f}s\n")

    start = time.time()
    # 并发执行（总耗时 = 最长任务）
    task_a = asyncio.create_task(download("C", 2))
    task_b = asyncio.create_task(download("D", 1))
    await task_a    # 等待任务完成
    await task_b
    print(f"并发耗时: {time.time()-start:.1f}s")

asyncio.run(main())
```

---

## asyncio.gather —— 等待多个任务

`gather` 是并发运行多个协程的最常用方式：

```python
import asyncio

async def task(name, delay):
    await asyncio.sleep(delay)
    return f"{name} 完成"

async def main():
    # 并发执行3个任务，按顺序返回结果
    results = await asyncio.gather(
        task("任务A", 3),
        task("任务B", 1),
        task("任务C", 2),
    )
    print(results)
    # ['任务A 完成', '任务B 完成', '任务C 完成']
    # 总耗时约3秒，而非6秒

    # return_exceptions=True：不因单个异常停止
    results = await asyncio.gather(
        task("成功", 1),
        asyncio.sleep(-1),      # 会抛出异常
        task("也成功", 2),
        return_exceptions=True  # 异常作为结果返回，不抛出
    )
    for r in results:
        if isinstance(r, Exception):
            print(f"异常: {r}")
        else:
            print(f"结果: {r}")

asyncio.run(main())
```

---

## 协程 vs 线程

```
协程优势：
┌────────────────────────────────────┐
│  单线程内运行，无需锁（无共享状态竞争）│
│  切换开销极小（函数调用级别）         │
│  可轻松创建数千个协程                │
│  代码执行流程清晰（主动让出控制权）   │
└────────────────────────────────────┘

线程优势：
┌────────────────────────────────────┐
│  可利用阻塞型第三方库（无需async版本）│
│  OS 调度，单个任务不会阻塞整个程序   │
│  适合已有同步代码的改造场景          │
└────────────────────────────────────┘

协程劣势：
┌────────────────────────────────────┐
│  必须全链路 async（"async 传染性"）  │
│  同步阻塞调用会卡住整个事件循环      │
│  调试和错误堆栈比线程更复杂          │
└────────────────────────────────────┘
```

---

## 避免阻塞事件循环

在 async 代码中绝对不能调用同步阻塞函数（如 `time.sleep`、同步文件读取），否则整个事件循环会被挂起：

```python
import asyncio

# 错误：time.sleep 是同步阻塞，会冻结事件循环
async def bad_example():
    import time
    time.sleep(1)       # 整个事件循环阻塞1秒！

# 正确：await asyncio.sleep
async def good_example():
    await asyncio.sleep(1)  # 只暂停此协程，事件循环继续运行

# 正确：在线程池中运行阻塞代码
async def run_blocking():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, blocking_function, arg)
```

---

## 小结

| 概念 | 说明 |
|------|------|
| `async def` | 定义协程函数 |
| `await` | 挂起协程，等待异步操作完成 |
| `asyncio.run()` | 运行顶层协程，创建/关闭事件循环 |
| `asyncio.create_task()` | 创建任务，立即调度执行 |
| `asyncio.gather()` | 并发等待多个协程，返回结果列表 |
| `asyncio.sleep()` | 异步睡眠，不阻塞事件循环 |
