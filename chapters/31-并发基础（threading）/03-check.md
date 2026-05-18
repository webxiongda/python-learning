# 第31章 自测题：并发基础（threading）

## 题目1：GIL 理解

以下说法中，哪些是正确的？（多选）

A. GIL 保证了同一时刻只有一个线程执行 Python 字节码  
B. 使用多线程可以突破 GIL 限制，实现真正的 CPU 并行  
C. 对于 I/O 密集型任务，多线程能提升整体效率  
D. GIL 在执行 C 扩展时（如 numpy 计算）可能被释放  
E. 多线程适合矩阵乘法等 CPU 密集型计算加速  

### 参考答案

**正确答案：A、C、D**

- A 正确：GIL 是 CPython 的核心机制，同一时刻只有一个线程持有 GIL 并执行。
- B 错误：多线程无法突破 GIL，真正的 CPU 并行需要使用 `multiprocessing`。
- C 正确：线程在等待 I/O 时会释放 GIL，其他线程可趁机执行，提高整体吞吐量。
- D 正确：很多 C 扩展（如 numpy、PIL 的底层操作）会主动释放 GIL，支持真并行。
- E 错误：CPU 密集型计算受 GIL 制约，多线程反而因锁竞争更慢。

---

## 题目2：代码分析

下面的代码有什么问题？如何修复？

```python
import threading

total = 0

def add_numbers():
    global total
    for i in range(1000):
        total += i

threads = [threading.Thread(target=add_numbers) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"结果: {total}")  # 期望: 49950 * 10 = 499500
```

### 参考答案

**问题：竞态条件（Race Condition）**

`total += i` 实际上是三步操作：读取 `total`、计算 `total + i`、写回 `total`。多线程并发执行时，这三步可能被其他线程打断，导致写入丢失，最终结果小于期望值。

**修复方案：使用 Lock**

```python
import threading

total = 0
lock = threading.Lock()

def add_numbers():
    global total
    for i in range(1000):
        with lock:       # 加锁保护临界区
            total += i

threads = [threading.Thread(target=add_numbers) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"结果: {total}")  # 499500
```

---

## 题目3：Lock vs RLock

什么情况下必须使用 `RLock` 而不能用普通 `Lock`？请写出一个会因使用 `Lock` 而死锁的示例，并用 `RLock` 修复。

### 参考答案

当**同一个线程需要多次获取同一把锁**时，必须用 `RLock`（可重入锁）。普通 `Lock` 不支持重入，同一线程第二次获取同一锁会永久等待，造成死锁。

**死锁示例（使用 Lock）：**

```python
import threading
lock = threading.Lock()

def outer():
    with lock:          # 第1次获取
        print("outer 执行")
        inner()         # 调用 inner，但 inner 也要获取同一把锁

def inner():
    with lock:          # 第2次获取同一把锁 → 永久等待，死锁！
        print("inner 执行")

t = threading.Thread(target=outer)
t.start()
t.join(timeout=2)
print("超时，发生死锁")
```

**修复（使用 RLock）：**

```python
import threading
rlock = threading.RLock()   # 替换为 RLock

def outer():
    with rlock:
        print("outer 执行")
        inner()         # 同一线程再次获取 rlock，不会阻塞

def inner():
    with rlock:         # 可重入，成功获取
        print("inner 执行")

t = threading.Thread(target=outer)
t.start()
t.join()
# 输出: outer 执行 → inner 执行
```

---

## 题目4：Queue 实现

请用 `queue.Queue` 实现一个线程池模式：主线程提交10个任务到队列，3个工作线程并发消费，全部处理完后主线程打印"完成"。

### 参考答案

```python
import threading
import queue
import time

NUM_WORKERS = 3
task_q = queue.Queue()

def worker(worker_id):
    while True:
        task = task_q.get()
        if task is None:            # 哨兵值，退出信号
            task_q.task_done()
            break
        print(f"Worker-{worker_id} 处理: {task}")
        time.sleep(0.1)             # 模拟处理耗时
        task_q.task_done()

# 启动工作线程
workers = []
for i in range(NUM_WORKERS):
    t = threading.Thread(target=worker, args=(i,), daemon=True)
    t.start()
    workers.append(t)

# 提交任务
for j in range(10):
    task_q.put(f"任务-{j}")

# 为每个工作线程发送退出信号
for _ in range(NUM_WORKERS):
    task_q.put(None)

# 等待所有任务完成
task_q.join()
print("完成")
```

关键点：
- 使用 `None` 作为哨兵值通知线程退出
- `task_q.join()` 会阻塞直到队列中所有 `task_done()` 都被调用
- 守护线程（`daemon=True`）确保主程序退出时线程自动销毁

---

## 题目5：综合设计

设计一个下载管理器，要求：
1. 最多同时下载3个文件（用 Semaphore 限制）
2. 每个下载任务完成后记录到共享列表（用 Lock 保护）
3. 所有下载完成后打印成功列表

### 参考答案

```python
import threading
import time
import random

semaphore = threading.Semaphore(3)   # 最大并发数
lock = threading.Lock()
completed = []

def download(url):
    with semaphore:                  # 限制并发
        print(f"开始下载: {url}")
        time.sleep(random.uniform(0.5, 2.0))  # 模拟下载耗时
        print(f"完成下载: {url}")
        with lock:                   # 保护共享列表
            completed.append(url)

urls = [f"https://example.com/file{i}.zip" for i in range(10)]
threads = [threading.Thread(target=download, args=(url,)) for url in urls]

for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"\n成功下载 {len(completed)} 个文件:")
for f in sorted(completed):
    print(f"  ✓ {f}")
```
