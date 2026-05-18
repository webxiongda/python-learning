# 第31章 项目任务：多线程文件批量处理工具

## 业务背景

某数据处理平台需要对一批文本文件进行预处理（统计词频、过滤停用词、输出报告）。文件数量多（模拟50个），每个文件处理耗时不等，需要利用多线程提高吞吐量，并保证结果汇总的线程安全。

---

## 技术要求

### 核心功能

1. **任务队列调度**：使用 `queue.Queue` 将文件路径分发给工作线程
2. **并发处理**：启动 5 个工作线程，从队列消费任务并处理
3. **限速控制**：使用 `Semaphore(5)` 限制同时处理的文件数
4. **结果汇总**：用 `Lock` 保护共享字典，记录每个文件的词频统计结果
5. **进度报告**：主线程每秒打印一次已完成/总任务数

### 代码结构

```python
# file_processor.py

import threading
import queue
import time
import random
import string
from collections import Counter

def generate_fake_content():
    """生成模拟文件内容"""
    words = ["python", "thread", "lock", "queue", "data", "file", "process"]
    return " ".join(random.choices(words, k=random.randint(50, 200)))

def process_file(filename, content):
    """处理单个文件，返回词频统计"""
    time.sleep(random.uniform(0.1, 0.5))  # 模拟处理耗时
    words = content.lower().split()
    return Counter(words)

# 请实现以下内容：
# 1. FileProcessor 类，包含 worker() 方法
# 2. 主程序：创建50个模拟任务，启动5个线程处理
# 3. 进度监控线程：每秒打印进度
# 4. 结果汇总：打印出现次数最多的前5个词
```

### 关键实现点

- 使用 `threading.Thread(daemon=True)` 创建工作线程
- 使用 `queue.Queue` 的 `task_done()` + `join()` 等待所有任务完成
- 使用 `threading.Lock` 保护结果字典的写入
- 进度监控线程通过 `threading.Event` 控制停止

---

## 验收标准

| 验收项 | 要求 |
|--------|------|
| 线程安全 | 结果字典不出现数据丢失或覆盖 |
| 并发效果 | 5线程处理比单线程快3倍以上 |
| 进度监控 | 每秒打印 `进度: X/50` |
| 结果正确 | 最终汇总词频与单线程结果一致 |
| 代码健壮 | 异常任务不影响其他线程继续工作 |

### 预期输出示例

```
启动5个工作线程...
进度: 5/50
进度: 12/50
进度: 21/50
...
进度: 50/50
所有文件处理完成！耗时: 3.2s

词频统计 Top 5:
  python: 1423次
  thread: 1187次
  data:   1056次
  queue:  998次
  lock:   876次
```

### 加分项

- 处理异常：当某个"文件"处理失败时，记录错误并继续
- 支持命令行参数：`--workers N` 指定线程数
- 使用 `logging` 模块替代 `print` 记录日志
