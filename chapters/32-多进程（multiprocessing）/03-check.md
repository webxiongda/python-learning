# 第32章 自测题：多进程（multiprocessing）

## 题目1：场景判断

下列哪些场景适合用多进程而非多线程？（多选）

A. 爬取1000个网页（主要等待网络响应）  
B. 对100万张图片做压缩（纯CPU计算）  
C. 聊天服务器同时处理100个连接（等待消息）  
D. 训练机器学习模型的多折交叉验证（每折独立计算）  
E. 读取大量文件内容并存入数据库（磁盘I/O）  

### 参考答案

**正确答案：B、D**

- A 错误：网络爬取是 I/O 密集型，用多线程（或 asyncio）更合适，进程开销反而浪费。
- B 正确：图片压缩是 CPU 密集型，多进程可利用多核真并行，显著加速。
- C 错误：聊天服务器是 I/O 密集型，适合多线程或异步 I/O，不需要多进程。
- D 正确：每折交叉验证是独立的 CPU 密集型任务，非常适合 Pool.map 并行。
- E 错误：磁盘 I/O 是 I/O 密集型，多线程即可，多进程的序列化开销不合算。

---

## 题目2：代码改错

以下代码在 Windows 上运行会出现什么问题？如何修复？

```python
from multiprocessing import Pool

def square(x):
    return x * x

pool = Pool(4)
results = pool.map(square, range(10))
print(results)
pool.close()
```

### 参考答案

**问题：缺少 `if __name__ == "__main__":` 保护**

在 Windows 上，`multiprocessing` 使用 `spawn` 方式创建子进程，子进程会重新导入主模块。如果没有 `if __name__ == "__main__":` 保护，子进程导入模块时会再次执行 `Pool(4)` 创建新的子进程，导致无限递归，抛出 `RuntimeError`。

macOS/Linux 默认使用 `fork`，问题不明显，但 Python 3.8+ macOS 也改用 `spawn`，同样会出现此问题。

**修复方案：**

```python
from multiprocessing import Pool

def square(x):
    return x * x

if __name__ == "__main__":          # 必须加此保护
    with Pool(4) as pool:           # 推荐用上下文管理器自动关闭
        results = pool.map(square, range(10))
    print(results)
    # 输出: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

---

## 题目3：Queue vs Pipe

解释 `multiprocessing.Queue` 和 `multiprocessing.Pipe` 的区别，并说明各自适用的场景。

### 参考答案

**Queue（队列）：**
- 基于 `Pipe` + `Lock` 实现，线程/进程安全
- 支持多个进程同时读写（多生产者，多消费者）
- 适合：任务分发、结果收集、生产者-消费者模式
- 缺点：有额外的锁开销，比 Pipe 稍慢

**Pipe（管道）：**
- 底层是操作系统管道，由两个 `Connection` 对象组成
- 只支持两端通信（一端发送，另一端接收）
- 适合：两个进程之间的双向通信
- 优点：比 Queue 快，无需加锁
- 缺点：不支持多对多，多个进程同时读写同一端会导致数据损坏

**选择建议：**
- 一对一通信 → Pipe（更快）
- 多对多/多对一 → Queue（更安全）
- 需要优先级队列 → `queue.PriorityQueue`（单进程内）

---

## 题目4：共享内存

```python
from multiprocessing import Process, Value
import ctypes

counter = Value(ctypes.c_int, 0)

def increment(n):
    for _ in range(n):
        counter.value += 1

if __name__ == "__main__":
    processes = [Process(target=increment, args=(10000,)) for _ in range(4)]
    for p in processes: p.start()
    for p in processes: p.join()
    print(counter.value)  # 期望40000，实际可能小于40000
```

为什么结果不是40000？如何修复？

### 参考答案

**原因：Value 的加法操作不是原子的**

`counter.value += 1` 展开为：
1. 读取 `counter.value`（比如读到 100）
2. 计算 `100 + 1 = 101`
3. 写回 `counter.value = 101`

多进程并发时，进程 A 读到 100，进程 B 也读到 100，各自计算出 101，先后写回都是 101，期望是 102，丢失了一次递增。

**修复：使用 `get_lock()` 加锁**

```python
from multiprocessing import Process, Value, Lock
import ctypes

counter = Value(ctypes.c_int, 0)

def increment(n, lock):
    for _ in range(n):
        with lock:               # 加锁保护
            counter.value += 1

if __name__ == "__main__":
    lock = Lock()
    processes = [Process(target=increment, args=(10000, lock)) for _ in range(4)]
    for p in processes: p.start()
    for p in processes: p.join()
    print(counter.value)         # 40000
```

也可以用 `Value` 内置的锁：`with counter.get_lock(): counter.value += 1`

---

## 题目5：综合实现

用 `Pool.map` 实现一个并行素数筛选器：给定列表 `[2, 3, 10, 17, 25, 97, 100, 101]`，返回其中所有素数。

### 参考答案

```python
from multiprocessing import Pool
import math

def is_prime(n):
    """判断一个数是否为素数"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

if __name__ == "__main__":
    numbers = [2, 3, 10, 17, 25, 97, 100, 101]

    with Pool(4) as pool:
        is_prime_flags = pool.map(is_prime, numbers)

    primes = [n for n, flag in zip(numbers, is_prime_flags) if flag]
    print(f"素数列表: {primes}")
    # 输出: 素数列表: [2, 3, 17, 97, 101]
```

**更简洁的写法（使用 filter 等价）：**

```python
if __name__ == "__main__":
    numbers = [2, 3, 10, 17, 25, 97, 100, 101]
    with Pool(4) as pool:
        primes = [n for n, ok in zip(numbers, pool.map(is_prime, numbers)) if ok]
    print(primes)  # [2, 3, 17, 97, 101]
```
