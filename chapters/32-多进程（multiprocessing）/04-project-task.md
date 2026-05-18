# 第32章 项目任务：并行图像批处理工具

## 业务背景

某电商平台有数千张商品图片需要批量处理（缩放、转格式、加水印），这是典型的 CPU 密集型任务。需要利用多进程充分利用多核 CPU，并提供进度监控和错误汇报。

---

## 技术要求

### 核心功能

1. **进程池处理**：使用 `Pool(cpu_count())` 创建最优进程数的进程池
2. **任务分批**：将图片列表均匀分配，使用 `Pool.starmap` 传递多参数（文件名、缩放比例、质量）
3. **进度回调**：通过 `apply_async` 的 `callback` 参数实时更新进度计数
4. **错误处理**：收集失败的图片，最终生成错误报告
5. **性能对比**：打印单进程 vs 多进程的耗时对比

### 代码框架

```python
# parallel_image_processor.py
from multiprocessing import Pool, cpu_count, Value, Lock
import ctypes
import time
import random
import os

def process_image(task):
    """
    模拟图像处理：接收 (filename, scale, quality) 元组
    返回 (filename, success, output_path, elapsed)
    """
    filename, scale, quality = task
    # 模拟处理耗时（CPU密集型）
    time.sleep(random.uniform(0.05, 0.3))

    # 模拟偶发失败（5%概率）
    if random.random() < 0.05:
        raise ValueError(f"处理 {filename} 失败：格式不支持")

    output = filename.replace(".jpg", f"_s{int(scale*100)}q{quality}.jpg")
    return filename, True, output

class ImageBatchProcessor:
    def __init__(self, num_workers=None):
        self.num_workers = num_workers or cpu_count()
        self.completed = 0
        self.errors = []

    def process_batch(self, tasks):
        """
        并行处理图片任务
        tasks: List[(filename, scale, quality)]
        """
        # TODO: 实现以下功能：
        # 1. 使用 Pool(self.num_workers) 创建进程池
        # 2. 用 apply_async 提交所有任务
        # 3. 用 callback 函数统计进度
        # 4. 用 error_callback 收集错误
        # 5. 收集所有结果并返回
        pass

    def generate_report(self, results):
        """生成处理报告"""
        # TODO: 统计成功/失败数量，打印报告
        pass

if __name__ == "__main__":
    # 生成模拟任务（100张图片）
    tasks = [
        (f"product_{i:04d}.jpg", random.choice([0.5, 0.75, 1.0]), random.choice([60, 80, 95]))
        for i in range(100)
    ]

    processor = ImageBatchProcessor()

    # 单进程基准测试
    start = time.time()
    for task in tasks:
        process_image(task)
    single_time = time.time() - start
    print(f"单进程耗时: {single_time:.2f}s")

    # 多进程处理
    start = time.time()
    results = processor.process_batch(tasks)
    multi_time = time.time() - start
    print(f"多进程耗时: {multi_time:.2f}s | 加速比: {single_time/multi_time:.1f}x")

    processor.generate_report(results)
```

---

## 验收标准

| 验收项 | 要求 |
|--------|------|
| 并行效率 | 多进程比单进程快 2x 以上（4核机器） |
| 错误隔离 | 某张图片失败不影响其他图片处理 |
| 进度输出 | 每完成10%打印一次进度 |
| 报告完整 | 最终打印成功数、失败数、失败文件名 |
| 代码规范 | 有 `if __name__ == "__main__":` 保护 |

### 预期输出示例

```
单进程耗时: 12.45s
启动 8 个工作进程...
进度: 10/100 (10%)
进度: 20/100 (20%)
...
进度: 100/100 (100%)
多进程耗时: 1.82s | 加速比: 6.8x

============ 处理报告 ============
总任务数: 100
成功: 95
失败: 5
失败文件:
  - product_0012.jpg: 格式不支持
  - product_0047.jpg: 格式不支持
  ...
==================================
```

### 加分项

- 使用 `Manager().list()` 在进程间共享错误列表
- 支持断点续传（已处理的文件跳过）
- 实现任务优先级队列（大图优先处理）
