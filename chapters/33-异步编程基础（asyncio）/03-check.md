# 第33章 自测题：异步编程基础（asyncio）

## 题目1：概念判断

以下关于 asyncio 的说法，哪些正确？（多选）

A. `async def` 定义的函数调用后会立即开始执行  
B. `await` 关键字只能在 `async def` 函数内部使用  
C. `asyncio.gather()` 中的协程是真正的并行（利用多核）  
D. 在协程中调用 `time.sleep(1)` 会阻塞整个事件循环  
E. `asyncio.create_task()` 创建的任务会立即被调度（但不立即执行）  

### 参考答案

**正确答案：B、D、E**

- A 错误：`async def` 函数调用返回的是协程对象，不会立即执行，需要 `await` 或 `asyncio.run()` 才会运行。
- B 正确：`await` 是协程的挂起机制，只能在 `async def` 内部使用，在普通函数中使用会报 `SyntaxError`。
- C 错误：asyncio 是单线程并发，不是并行。`gather` 只是在单线程内交替执行，等待I/O时切换，不利用多核。
- D 正确：`time.sleep` 是同步阻塞调用，会直接阻塞当前线程（即事件循环所在线程），应使用 `await asyncio.sleep()`。
- E 正确：`create_task` 将协程封装为 Task 并加入事件循环的调度队列，但要等当前协程 `await` 让出控制权后才会真正开始执行。

---

## 题目2：代码改错

找出以下代码中的所有问题并修复：

```python
import asyncio
import time

async def fetch(url):
    time.sleep(2)           # 问题1
    return f"data from {url}"

async def main():
    results = []
    for url in ["a.com", "b.com", "c.com"]:
        result = fetch(url)  # 问题2
        results.append(result)
    return results

result = main()              # 问题3
print(result)
```

### 参考答案

**问题1**：`time.sleep(2)` 是同步阻塞，应改为 `await asyncio.sleep(2)`

**问题2**：`fetch(url)` 没有 `await`，只是创建了协程对象而未执行，应改为 `result = await fetch(url)`

**问题3**：`main()` 只是创建协程对象，必须用 `asyncio.run()` 来运行

**修复后的代码：**

```python
import asyncio

async def fetch(url):
    await asyncio.sleep(2)          # 修复1：改为异步睡眠
    return f"data from {url}"

async def main():
    results = []
    for url in ["a.com", "b.com", "c.com"]:
        result = await fetch(url)   # 修复2：添加 await
        results.append(result)
    return results

# 修复3：使用 asyncio.run() 运行
result = asyncio.run(main())
print(result)
# ['data from a.com', 'data from b.com', 'data from c.com']

# 进一步优化：并发执行
async def main_concurrent():
    return await asyncio.gather(
        fetch("a.com"),
        fetch("b.com"),
        fetch("c.com"),
    )
```

---

## 题目3：gather vs wait

解释 `asyncio.gather()` 和 `asyncio.wait()` 的区别，各在什么场景下使用？

### 参考答案

**asyncio.gather()：**
- 接受可变参数（协程或任务）
- 按照**输入顺序**返回结果列表
- 默认：任意一个异常会立即取消其他任务并抛出
- `return_exceptions=True`：将异常作为普通结果返回
- 适合：需要所有任务都完成，结果有序的场景

```python
results = await asyncio.gather(coro1(), coro2(), coro3())
# 返回 [result1, result2, result3]，顺序固定
```

**asyncio.wait()：**
- 接受任务/协程的可迭代对象
- 返回 `(done, pending)` 两个集合
- 支持 `return_when` 控制等待策略：
  - `ALL_COMPLETED`（默认）：全部完成
  - `FIRST_COMPLETED`：第一个完成时返回
  - `FIRST_EXCEPTION`：第一个异常时返回
- 适合：需要处理"先完成先处理"、或想取消剩余任务的场景

```python
done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
```

**选择建议：**
- 需要所有结果，顺序重要 → `gather`
- 需要最先完成的那个结果 → `wait(FIRST_COMPLETED)`
- 需要细粒度控制各任务状态 → `wait`

---

## 题目4：异步上下文管理器

实现一个异步上下文管理器 `AsyncDBConnection`，模拟数据库连接：
- `__aenter__`：等待0.1秒"建立连接"，打印"连接已建立"，返回 `self`
- `__aexit__`：等待0.05秒"关闭连接"，打印"连接已关闭"
- 有 `query(sql)` 方法：等待0.1秒返回模拟结果

### 参考答案

```python
import asyncio

class AsyncDBConnection:
    def __init__(self, db_url):
        self.db_url = db_url
        self.connected = False

    async def __aenter__(self):
        await asyncio.sleep(0.1)    # 模拟连接建立
        self.connected = True
        print(f"连接已建立: {self.db_url}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await asyncio.sleep(0.05)   # 模拟关闭连接
        self.connected = False
        print(f"连接已关闭: {self.db_url}")
        return False                # 不抑制异常

    async def query(self, sql):
        if not self.connected:
            raise RuntimeError("未连接到数据库")
        await asyncio.sleep(0.1)    # 模拟查询
        return [{"id": 1, "sql": sql}]

async def main():
    async with AsyncDBConnection("postgresql://localhost/mydb") as db:
        result = await db.query("SELECT * FROM users")
        print(f"查询结果: {result}")

asyncio.run(main())
# 输出:
# 连接已建立: postgresql://localhost/mydb
# 查询结果: [{'id': 1, 'sql': 'SELECT * FROM users'}]
# 连接已关闭: postgresql://localhost/mydb
```

---

## 题目5：超时与重试

实现 `retry_async` 函数：对一个可能失败的协程函数最多重试 N 次，每次重试前等待 `delay` 秒，全部失败后抛出最后一次异常。

### 参考答案

```python
import asyncio
import random

async def retry_async(coro_func, *args, retries=3, delay=1.0, **kwargs):
    """
    重试包装器
    :param coro_func: 异步函数
    :param retries: 最大重试次数
    :param delay: 重试间隔（秒）
    """
    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            result = await coro_func(*args, **kwargs)
            print(f"第{attempt}次尝试成功")
            return result
        except Exception as e:
            last_exception = e
            print(f"第{attempt}次尝试失败: {e}")
            if attempt < retries:
                print(f"  {delay}秒后重试...")
                await asyncio.sleep(delay)
    raise last_exception    # 所有重试耗尽，抛出最后一次异常

# 测试
async def flaky_api():
    """模拟不稳定的API：70%概率失败"""
    if random.random() < 0.7:
        raise ConnectionError("网络错误")
    return {"status": "ok", "data": [1, 2, 3]}

async def main():
    try:
        result = await retry_async(flaky_api, retries=5, delay=0.5)
        print(f"最终结果: {result}")
    except Exception as e:
        print(f"全部失败: {e}")

asyncio.run(main())
```
