# 第31章 Demo：并发基础（threading）

## Demo 1：基本线程创建与 join

```python
import threading
import time

def download_file(filename, duration):
    """模拟下载文件"""
    print(f"开始下载: {filename}")
    time.sleep(duration)  # 模拟 I/O 等待
    print(f"下载完成: {filename}")

# 顺序执行
start = time.time()
download_file("文件A.zip", 2)
download_file("文件B.zip", 1)
download_file("文件C.zip", 1.5)
print(f"顺序耗时: {time.time() - start:.1f}s\n")

# 并发执行
start = time.time()
threads = [
    threading.Thread(target=download_file, args=("文件A.zip", 2)),
    threading.Thread(target=download_file, args=("文件B.zip", 1)),
    threading.Thread(target=download_file, args=("文件C.zip", 1.5)),
]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"并发耗时: {time.time() - start:.1f}s")
```

```
# 预期输出：
开始下载: 文件A.zip
开始下载: 文件B.zip
开始下载: 文件C.zip
下载完成: 文件B.zip
下载完成: 文件C.zip
下载完成: 文件A.zip
顺序耗时: 4.5s（实际并发顺序可能不同）

并发耗时: 2.0s
```

---

## Demo 2：Lock 防止竞态条件

```python
import threading

# ---- 无锁版本（会产生竞态条件）----
counter_unsafe = 0

def unsafe_increment():
    global counter_unsafe
    for _ in range(100000):
        counter_unsafe += 1  # 非原子操作！

threads = [threading.Thread(target=unsafe_increment) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"无锁计数（期望500000）: {counter_unsafe}")  # 通常小于500000

# ---- 有锁版本 ----
counter_safe = 0
lock = threading.Lock()

def safe_increment():
    global counter_safe
    for _ in range(100000):
        with lock:
            counter_safe += 1

threads = [threading.Thread(target=safe_increment) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"有锁计数（期望500000）: {counter_safe}")
```

```
# 预期输出：
无锁计数（期望500000）: 347821   # 每次运行结果不同
有锁计数（期望500000）: 500000
```

---

## Demo 3：Semaphore 限制并发连接数

```python
import threading
import time
import random

# 模拟数据库连接池，最多同时3个连接
db_pool = threading.Semaphore(3)
active_connections = 0
lock = threading.Lock()

def query_database(thread_id):
    global active_connections
    print(f"线程 {thread_id} 等待数据库连接...")
    with db_pool:
        with lock:
            active_connections += 1
            print(f"线程 {thread_id} 获得连接 | 当前连接数: {active_connections}")

        # 模拟查询
        time.sleep(random.uniform(0.5, 1.5))

        with lock:
            active_connections -= 1
            print(f"线程 {thread_id} 释放连接 | 当前连接数: {active_connections}")

# 启动10个线程，但同时最多3个访问数据库
threads = [threading.Thread(target=query_database, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("所有查询完成")
```

```
# 预期输出（顺序可能不同，但当前连接数始终≤3）：
线程 0 等待数据库连接...
线程 1 等待数据库连接...
线程 2 等待数据库连接...
线程 0 获得连接 | 当前连接数: 1
线程 1 获得连接 | 当前连接数: 2
线程 2 获得连接 | 当前连接数: 3
线程 3 等待数据库连接...   ← 被信号量阻塞
...
所有查询完成
```

---

## Demo 4：生产者-消费者模式（Queue）

```python
import threading
import time
import queue
import random

def producer(q, num_items):
    """生产者：生成任务"""
    for i in range(num_items):
        item = f"任务-{i:03d}"
        q.put(item)
        print(f"[生产] {item} | 队列大小: {q.qsize()}")
        time.sleep(random.uniform(0.1, 0.3))
    # 发送结束信号（每个消费者一个）
    q.put(None)
    q.put(None)
    print("[生产] 已发出结束信号")

def consumer(q, consumer_id):
    """消费者：处理任务"""
    while True:
        item = q.get()
        if item is None:
            print(f"[消费者{consumer_id}] 收到结束信号，退出")
            q.task_done()
            break
        # 模拟处理耗时
        time.sleep(random.uniform(0.2, 0.5))
        print(f"[消费者{consumer_id}] 处理完成: {item}")
        q.task_done()

task_queue = queue.Queue(maxsize=5)

prod = threading.Thread(target=producer, args=(task_queue, 8))
cons1 = threading.Thread(target=consumer, args=(task_queue, 1))
cons2 = threading.Thread(target=consumer, args=(task_queue, 2))

cons1.start()
cons2.start()
prod.start()

prod.join()
cons1.join()
cons2.join()
print("所有任务处理完毕")
```

```
# 预期输出（顺序可能不同）：
[生产] 任务-000 | 队列大小: 1
[消费者1] 处理完成: 任务-000
[生产] 任务-001 | 队列大小: 1
[生产] 任务-002 | 队列大小: 2
[消费者2] 处理完成: 任务-001
...
[生产] 已发出结束信号
[消费者1] 收到结束信号，退出
[消费者2] 收到结束信号，退出
所有任务处理完毕
```

---

## Demo 5：threading.local() 线程局部变量

```python
import threading

# 线程局部存储，每个线程有独立副本
local_storage = threading.local()

def process_request(user_id, request_data):
    """模拟 Web 请求处理，每个线程独立存储当前用户"""
    # 存入线程本地数据
    local_storage.user_id = user_id
    local_storage.request = request_data

    # 调用其他函数时可以直接访问，无需传参
    result = handle_logic()
    print(f"[线程{threading.current_thread().name}] 用户{user_id}: {result}")

def handle_logic():
    """从线程本地存储读取用户信息"""
    uid = getattr(local_storage, 'user_id', '未知')
    req = getattr(local_storage, 'request', '')
    return f"处理请求 '{req}' (uid={uid})"

# 模拟多个并发请求
requests = [
    ("user_001", "查询订单"),
    ("user_002", "添加商品"),
    ("user_003", "提交支付"),
]
threads = [
    threading.Thread(target=process_request, args=(uid, req), name=f"T{i}")
    for i, (uid, req) in enumerate(requests)
]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

```
# 预期输出（顺序可能不同）：
[线程T0] 用户user_001: 处理请求 '查询订单' (uid=user_001)
[线程T1] 用户user_002: 处理请求 '添加商品' (uid=user_002)
[线程T2] 用户user_003: 处理请求 '提交支付' (uid=user_003)
```
