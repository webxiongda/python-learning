# 第32章 Demo：多进程（multiprocessing）

## Demo 1：多进程 vs 多线程 CPU 性能对比

```python
import threading
import multiprocessing
import time
import math

def cpu_task(n):
    """CPU 密集型：计算 n 以内所有整数的平方根之和"""
    return sum(math.sqrt(i) for i in range(n))

TASKS = [5_000_000] * 4  # 4个相同的任务

if __name__ == "__main__":
    # 单线程顺序执行
    start = time.time()
    results = [cpu_task(n) for n in TASKS]
    print(f"单线程耗时: {time.time() - start:.2f}s")

    # 多线程（受GIL限制）
    start = time.time()
    threads = [threading.Thread(target=cpu_task, args=(n,)) for n in TASKS]
    for t in threads: t.start()
    for t in threads: t.join()
    print(f"多线程耗时: {time.time() - start:.2f}s  (基本无加速，GIL制约)")

    # 多进程（真并行）
    start = time.time()
    with multiprocessing.Pool(4) as pool:
        results = pool.map(cpu_task, TASKS)
    print(f"多进程耗时: {time.time() - start:.2f}s  (接近线性加速)")
```

```
# 预期输出（4核CPU上）：
单线程耗时: 4.20s
多线程耗时: 4.35s  (基本无加速，GIL制约)
多进程耗时: 1.15s  (接近线性加速)
```

---

## Demo 2：Pool.map 和 Pool.starmap

```python
from multiprocessing import Pool
import time

def analyze_text(text):
    """分析文本：统计字数、词数、句子数"""
    words = text.split()
    sentences = text.count('.') + text.count('!') + text.count('?')
    return {
        "chars": len(text),
        "words": len(words),
        "sentences": max(sentences, 1)
    }

def score_with_weight(text, weight):
    """带权重的文本评分"""
    stats = analyze_text(text)
    score = (stats["words"] * 2 + stats["sentences"] * 5) * weight
    return round(score, 2)

if __name__ == "__main__":
    articles = [
        "Python is great. It is easy to learn! Many people use it.",
        "Threading allows concurrent execution. GIL limits CPU parallelism.",
        "Multiprocessing bypasses GIL. It creates separate processes.",
        "Each process has its own memory. Communication needs serialization.",
    ]

    # Pool.map：单参数
    with Pool(4) as pool:
        stats_list = pool.map(analyze_text, articles)

    for i, stats in enumerate(stats_list):
        print(f"文章{i+1}: {stats}")

    print()

    # Pool.starmap：多参数
    weighted_tasks = [(art, w) for art, w in zip(articles, [1.0, 1.5, 2.0, 0.8])]
    with Pool(4) as pool:
        scores = pool.starmap(score_with_weight, weighted_tasks)

    print("加权评分:", scores)
```

```
# 预期输出：
文章1: {'chars': 56, 'words': 11, 'sentences': 3}
文章2: {'chars': 56, 'words': 8, 'sentences': 1}
文章3: {'chars': 52, 'words': 7, 'sentences': 2}
文章4: {'chars': 59, 'words': 8, 'sentences': 1}

加权评分: [37.0, 37.5, 48.0, 20.8]
```

---

## Demo 3：进程间通信——Queue

```python
from multiprocessing import Process, Queue
import time
import random

def image_processor(task_queue, result_queue, worker_id):
    """模拟图像处理工作进程"""
    while True:
        task = task_queue.get()
        if task is None:        # 退出信号
            break

        img_id, size = task
        # 模拟处理耗时（图像越大耗时越长）
        time.sleep(size / 1000)
        result = {
            "image_id": img_id,
            "worker": worker_id,
            "output": f"processed_{img_id}.jpg",
            "size_kb": size
        }
        result_queue.put(result)

if __name__ == "__main__":
    task_q = Queue()
    result_q = Queue()

    # 模拟10个图像任务
    tasks = [(f"img_{i:03d}", random.randint(100, 500)) for i in range(10)]

    # 启动3个工作进程
    workers = []
    for wid in range(3):
        p = Process(target=image_processor, args=(task_q, result_q, wid))
        p.start()
        workers.append(p)

    # 分发任务
    for task in tasks:
        task_q.put(task)

    # 发送退出信号
    for _ in workers:
        task_q.put(None)

    # 收集结果
    results = []
    for _ in range(len(tasks)):
        results.append(result_q.get())

    for p in workers:
        p.join()

    print(f"处理完成 {len(results)} 个图像:")
    for r in sorted(results, key=lambda x: x["image_id"]):
        print(f"  [{r['worker']}号进程] {r['image_id']} → {r['output']}")
```

```
# 预期输出：
处理完成 10 个图像:
  [0号进程] img_000 → processed_img_000.jpg
  [1号进程] img_001 → processed_img_001.jpg
  [2号进程] img_002 → processed_img_002.jpg
  ...（分配给各进程）
```

---

## Demo 4：共享内存 Value 与 Array

```python
from multiprocessing import Process, Value, Array, Lock
import ctypes
import time

def accumulate(shared_sum, lock, numbers):
    """将 numbers 中的数字累加到共享变量"""
    for n in numbers:
        with lock:
            shared_sum.value += n
        time.sleep(0.001)

def fill_array(shared_arr, start_val):
    """填充共享数组"""
    for i in range(len(shared_arr)):
        shared_arr[i] = start_val + i * 10

if __name__ == "__main__":
    # 共享整数求和
    shared_sum = Value(ctypes.c_int, 0)
    lock = Lock()

    # 将1-100拆成两半，分配给两个进程
    p1 = Process(target=accumulate, args=(shared_sum, lock, range(1, 51)))
    p2 = Process(target=accumulate, args=(shared_sum, lock, range(51, 101)))
    p1.start(); p2.start()
    p1.join(); p2.join()
    print(f"1+2+...+100 = {shared_sum.value}")  # 5050

    # 共享数组
    shared_arr = Array(ctypes.c_int, 5)   # 5个整数，初始为0
    p = Process(target=fill_array, args=(shared_arr, 100))
    p.start()
    p.join()
    print(f"共享数组: {list(shared_arr)}")  # [100, 110, 120, 130, 140]
```

```
# 预期输出：
1+2+...+100 = 5050
共享数组: [100, 110, 120, 130, 140]
```

---

## Demo 5：apply_async 异步任务池

```python
from multiprocessing import Pool
import time

def fetch_and_parse(url_id):
    """模拟异步HTTP请求+解析"""
    import random
    time.sleep(random.uniform(0.5, 2.0))  # 模拟网络延迟
    return {
        "url_id": url_id,
        "status": 200,
        "data_size": random.randint(1024, 10240)
    }

def on_success(result):
    print(f"  完成 URL-{result['url_id']:02d}: {result['data_size']} bytes")

def on_error(exc):
    print(f"  错误: {exc}")

if __name__ == "__main__":
    url_ids = list(range(1, 13))   # 模拟12个URL
    start = time.time()

    with Pool(processes=4) as pool:
        # 提交所有任务，不等待
        futures = []
        for uid in url_ids:
            f = pool.apply_async(
                fetch_and_parse,
                args=(uid,),
                callback=on_success,
                error_callback=on_error
            )
            futures.append(f)

        print(f"已提交 {len(futures)} 个任务，等待完成...")
        # 等待所有结果
        results = [f.get() for f in futures]

    elapsed = time.time() - start
    total_size = sum(r["data_size"] for r in results)
    print(f"\n全部完成！耗时: {elapsed:.1f}s | 总数据: {total_size/1024:.1f} KB")
```

```
# 预期输出：
已提交 12 个任务，等待完成...
  完成 URL-03: 4521 bytes
  完成 URL-07: 2048 bytes
  完成 URL-01: 8192 bytes
  ...（完成顺序不定）

全部完成！耗时: 2.1s | 总数据: 62.4 KB
```
