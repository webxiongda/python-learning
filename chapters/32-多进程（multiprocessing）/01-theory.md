# 第32章：多进程（multiprocessing）

## 为什么需要多进程

Python 的 GIL 导致多线程无法实现真正的 CPU 并行。`multiprocessing` 模块通过**创建独立进程**绕过 GIL，每个进程有独立的 Python 解释器和内存空间，适合 **CPU 密集型任务**。

---

## Process vs Thread 对比

```
多线程（threading）：
┌─────────────── 单进程 ─────────────────┐
│  Thread-1  Thread-2  Thread-3          │
│     │          │         │             │
│     └──────[GIL]─────────┘             │
│         同一时刻只有1个执行              │
│         共享内存空间                    │
└─────────────────────────────────────────┘

多进程（multiprocessing）：
┌──────────┐  ┌──────────┐  ┌──────────┐
│  进程 1   │  │  进程 2   │  │  进程 3   │
│  (GIL-1) │  │  (GIL-2) │  │  (GIL-3) │
│  独立内存 │  │  独立内存 │  │  独立内存 │
└──────────┘  └──────────┘  └──────────┘
      │              │              │
      └──────── CPU核心并行执行 ──────┘
```

| 特性 | threading | multiprocessing |
|------|-----------|-----------------|
| 内存 | 共享 | 独立（需要序列化通信） |
| GIL 限制 | 受限 | 不受限 |
| 适合场景 | I/O 密集型 | CPU 密集型 |
| 创建开销 | 小（毫秒级） | 大（几十毫秒） |
| 通信方式 | 共享变量、Queue | Queue、Pipe、共享内存 |

---

## Process 基础用法

```python
from multiprocessing import Process
import os

def worker(name):
    print(f"子进程 {name}: PID={os.getpid()}, 父PID={os.getppid()}")

if __name__ == "__main__":          # Windows/macOS 必须有这个保护
    p = Process(target=worker, args=("Task-1",))
    p.start()
    p.join()    # 等待子进程结束
    print(f"主进程 PID={os.getpid()}")
```

> **重要**：multiprocessing 代码必须在 `if __name__ == "__main__":` 块中运行，防止子进程递归创建新进程（Windows 尤其重要）。

---

## Pool —— 进程池

进程池复用固定数量的进程，避免频繁创建/销毁的开销：

```
任务列表: [T0, T1, T2, T3, T4, T5, T6, T7]
                        │
                   Pool(4)
              ┌────┬────┬────┬────┐
              │ P0 │ P1 │ P2 │ P3 │
              └──┬─┴──┬─┴──┬─┴──┬─┘
                 │    │    │    │
                T0   T1   T2   T3   ← 第一批
                T4   T5   T6   T7   ← 第二批（等第一批完成后）
```

### Pool.map / Pool.starmap

```python
from multiprocessing import Pool
import math

def heavy_compute(n):
    """CPU 密集型计算"""
    return sum(math.sqrt(i) for i in range(n))

if __name__ == "__main__":
    data = [1000000, 2000000, 500000, 1500000]

    # map：单参数映射
    with Pool(processes=4) as pool:
        results = pool.map(heavy_compute, data)
    print(results)

    # starmap：多参数映射
    def power(base, exp):
        return base ** exp

    with Pool(4) as pool:
        results = pool.starmap(power, [(2, 10), (3, 5), (5, 3)])
    print(results)  # [1024, 243, 125]
```

### Pool.apply_async —— 异步提交

```python
from multiprocessing import Pool

def task(x):
    return x * x

if __name__ == "__main__":
    with Pool(4) as pool:
        # 提交任务，立即返回 AsyncResult 对象
        futures = [pool.apply_async(task, (i,)) for i in range(8)]
        # 获取结果（阻塞直到完成）
        results = [f.get() for f in futures]
    print(results)  # [0, 1, 4, 9, 16, 25, 36, 49]
```

---

## 进程间通信（IPC）

### Queue（多进程安全队列）

```python
from multiprocessing import Process, Queue

def producer(q):
    for i in range(5):
        q.put(f"数据-{i}")
    q.put(None)     # 结束信号

def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print(f"消费: {item}")

if __name__ == "__main__":
    q = Queue()
    p1 = Process(target=producer, args=(q,))
    p2 = Process(target=consumer, args=(q,))
    p1.start(); p2.start()
    p1.join(); p2.join()
```

### Pipe（双向管道）

```python
from multiprocessing import Process, Pipe

def sender(conn):
    conn.send({"type": "greeting", "data": "你好"})
    conn.close()

def receiver(conn):
    msg = conn.recv()
    print(f"收到消息: {msg}")
    conn.close()

if __name__ == "__main__":
    parent_conn, child_conn = Pipe()    # 创建管道两端
    p = Process(target=sender, args=(child_conn,))
    p.start()
    receiver(parent_conn)
    p.join()
```

```
Pipe 通信模型：
主进程 ←──parent_conn──── child_conn ──→ 子进程
       发送/接收             发送/接收
```

---

## 共享内存（Value / Array）

进程间直接共享数据，效率高但需要手动加锁：

```python
from multiprocessing import Process, Value, Array
import ctypes

def modify_shared(val, arr):
    val.value += 100           # 修改共享整数
    for i in range(len(arr)):
        arr[i] *= 2            # 修改共享数组

if __name__ == "__main__":
    shared_val = Value(ctypes.c_int, 0)      # 共享整数，初始值0
    shared_arr = Array(ctypes.c_double, [1.0, 2.0, 3.0])  # 共享浮点数组

    p = Process(target=modify_shared, args=(shared_val, shared_arr))
    p.start()
    p.join()

    print(f"共享整数: {shared_val.value}")          # 100
    print(f"共享数组: {list(shared_arr)}")          # [2.0, 4.0, 6.0]
```

> 注意：`Value` 和 `Array` 本身带有 `Lock`，可通过 `val.get_lock()` 访问。

---

## 选择通信方式

```
数据量小、结构简单  →  Value / Array（共享内存，最快）
生产者-消费者模式   →  Queue（线程安全，使用简单）
双向通信、单对单    →  Pipe（比Queue快，但不支持多对多）
大量数据、复杂对象  →  Manager().dict()/list()（通用但最慢）
```

---

## 小结

- **进程池（Pool）** 是处理 CPU 密集型批量任务的最佳选择
- **Queue/Pipe** 解决进程间数据传递，需要序列化（pickle）
- **Value/Array** 用于简单数据的高性能共享
- 所有 multiprocessing 代码务必放在 `if __name__ == "__main__":` 中
