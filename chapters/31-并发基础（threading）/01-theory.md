# 第31章：并发基础（threading）

## 核心概念

并发（Concurrency）是指程序在同一时间段内处理多个任务的能力。Python 的 `threading` 模块提供了线程级别的并发支持，适合处理 I/O 密集型任务。

---

## 进程 vs 线程

```
┌─────────────────────────────────────────┐
│              操作系统进程                  │
│                                         │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │  线程 1   │  │  线程 2   │  │ 线程 3 ││
│  │ (栈/寄存器)│  │ (栈/寄存器)│  │        ││
│  └──────────┘  └──────────┘  └────────┘│
│                                         │
│        共享内存区（堆、全局变量）            │
└─────────────────────────────────────────┘
```

- **进程**：独立内存空间，重量级，创建开销大
- **线程**：共享进程内存，轻量级，创建开销小
- **协程**：用户态调度，比线程更轻量（第33章介绍）

---

## GIL —— 全局解释器锁

Python（CPython）的 GIL（Global Interpreter Lock）是一把全局锁，**同一时刻只允许一个线程执行 Python 字节码**。

```
时间轴:
Thread-1: ───[获得GIL]───[执行]───[释放GIL]─── 等待 ─────────────────
Thread-2: ─── 等待 ─────────────────────────[获得GIL]─[执行]─[释放]──
Thread-3: ─── 等待 ────────────────────────────────── 等待 ──────────
```

**GIL 的影响：**
| 任务类型 | 线程效果 | 原因 |
|----------|----------|------|
| CPU 密集型（计算） | 无加速，甚至更慢 | GIL 竞争开销 |
| I/O 密集型（网络/文件）| 有效加速 | I/O 等待时释放 GIL |

> 结论：Python 线程适合 I/O 密集型，CPU 密集型请用 `multiprocessing`。

---

## Thread 创建与启动

```python
import threading

# 方式1：函数式创建
def worker(name, count):
    for i in range(count):
        print(f"[{name}] 步骤 {i+1}")

t = threading.Thread(target=worker, args=("Alice", 3), daemon=True)
t.start()   # 启动线程
t.join()    # 等待线程结束

# 方式2：继承 Thread 类
class MyThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def run(self):
        print(f"线程 {self.name} 正在运行")

mt = MyThread("Bob")
mt.start()
mt.join()
```

**关键参数：**
- `target`：线程执行的函数
- `args`/`kwargs`：传给函数的参数
- `daemon=True`：守护线程，主线程结束时自动终止

---

## 线程同步：Lock 与 RLock

多线程共享数据时需要同步，否则会产生**竞态条件**（Race Condition）：

```
无锁时的问题：
Thread-1 读取 counter=5
Thread-2 读取 counter=5
Thread-1 写入 counter=6  （counter+1）
Thread-2 写入 counter=6  （counter+1，期望是7！）

有锁时：
Thread-1 [锁] 读取=5 写入=6 [解锁]
Thread-2         等待 →   [锁] 读取=6 写入=7 [解锁]
```

```python
import threading

lock = threading.Lock()
counter = 0

def increment():
    global counter
    with lock:          # 上下文管理器自动获取/释放锁
        temp = counter
        counter = temp + 1

# RLock（可重入锁）：同一线程可多次获取
rlock = threading.RLock()

def outer():
    with rlock:
        inner()     # 同一线程内再次获取 rlock，不会死锁

def inner():
    with rlock:     # 普通 Lock 在这里会死锁
        print("inner 执行")
```

---

## Semaphore —— 信号量

Semaphore 控制同时访问某资源的线程数量，适合**限流**场景：

```
Semaphore(3) 示意：
     许可证池 [●●●]
线程1 → 取走 ● → [●●]
线程2 → 取走 ● → [●]
线程3 → 取走 ● → []
线程4 → 等待... (池空)
线程1 → 归还 ● → [●] → 线程4 拿到许可证
```

```python
semaphore = threading.Semaphore(3)  # 最多3个线程同时执行

def limited_task(tid):
    with semaphore:
        print(f"线程 {tid} 开始")
        time.sleep(1)
        print(f"线程 {tid} 结束")
```

---

## threading.Queue —— 线程安全队列

`Queue` 是线程间通信的首选方式，内置锁机制，无需手动同步：

```
生产者-消费者模型：

生产者线程 ──put()──▶ [任务队列] ──get()──▶ 消费者线程
生产者线程 ──put()──▶ [任务队列] ──get()──▶ 消费者线程
```

```python
from queue import Queue

q = Queue(maxsize=10)   # 最大容量10

# 生产者
def producer():
    for i in range(5):
        q.put(f"任务{i}")
    q.put(None)         # 发送结束信号

# 消费者
def consumer():
    while True:
        item = q.get()
        if item is None:
            break
        print(f"处理: {item}")
        q.task_done()   # 通知队列任务已完成
```

---

## 线程安全最佳实践

1. **优先使用 Queue** 而非共享变量进行线程间通信
2. **最小化锁的粒度**：只在必要时加锁，减少锁持有时间
3. **避免嵌套锁**：多把锁按固定顺序获取，防止死锁
4. **使用 `with` 语句**管理锁，确保异常时也能释放
5. **线程局部存储** `threading.local()` 避免共享状态

```python
# threading.local() 示例
local_data = threading.local()

def set_user(user_id):
    local_data.user_id = user_id    # 每个线程有独立副本

def get_user():
    return getattr(local_data, 'user_id', None)
```

---

## 小结

| 概念 | 作用 |
|------|------|
| `Thread` | 创建并运行线程 |
| `Lock` | 互斥锁，防止竞态 |
| `RLock` | 可重入锁，同线程可多次获取 |
| `Semaphore` | 限制并发数量 |
| `Queue` | 线程安全的任务队列 |
| `threading.local()` | 线程局部变量 |
