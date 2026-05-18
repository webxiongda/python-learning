# 第13章：生成器与协议 — Demo 示例

## Demo 1：生成器函数基础

```python
# 演示生成器函数的基本行为

def 倒计时(n):
    """倒计时生成器"""
    print(f"开始倒计时，从 {n} 开始")
    while n > 0:
        print(f"  准备 yield {n}")
        yield n
        print(f"  yield {n} 之后恢复")
        n -= 1
    print("倒计时结束！")

print("=== 创建生成器（不执行任何代码）===")
gen = 倒计时(3)
print(f"生成器对象: {gen}")

print("\n=== 开始驱动生成器 ===")
print(f"获取: {next(gen)}")
print(f"获取: {next(gen)}")
print(f"获取: {next(gen)}")

print("\n=== 尝试再次获取 ===")
try:
    next(gen)
except StopIteration:
    print("StopIteration 被捕获：生成器已耗尽")
```

```
# 预期输出：
=== 创建生成器（不执行任何代码）===
生成器对象: <generator object 倒计时 at 0x...>

=== 开始驱动生成器 ===
开始倒计时，从 3 开始
  准备 yield 3
获取: 3
  yield 3 之后恢复
  准备 yield 2
获取: 2
  yield 2 之后恢复
  准备 yield 1
获取: 1
  yield 1 之后恢复
倒计时结束！

=== 尝试再次获取 ===
StopIteration 被捕获：生成器已耗尽
```

---

## Demo 2：无限生成器与 itertools.islice

```python
# 生成器可以产生无限序列，配合切片使用

import itertools

def 自然数():
    """无限自然数生成器"""
    n = 1
    while True:
        yield n
        n += 1

def 素数():
    """无限素数生成器（埃拉托斯特尼筛法简化版）"""
    def 是素数(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    n = 2
    while True:
        if 是素数(n):
            yield n
        n += 1

# 取前10个自然数
前10自然数 = list(itertools.islice(自然数(), 10))
print("前10个自然数:", 前10自然数)

# 取前15个素数
前15素数 = list(itertools.islice(素数(), 15))
print("前15个素数:", 前15素数)

# 使用 takewhile 取小于50的素数
小于50素数 = list(itertools.takewhile(lambda x: x < 50, 素数()))
print("50以内素数:", 小于50素数)
```

```
# 预期输出：
前10个自然数: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
前15个素数: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
50以内素数: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
```

---

## Demo 3：send() 实现协程风格

```python
# 使用 send() 实现双向通信——运动数据统计器

def 运动统计器():
    """接收运动数据，实时统计"""
    总距离 = 0
    总时间 = 0
    最高速度 = 0
    圈数 = 0

    while True:
        # yield 左边接收 send() 传来的值，右边输出当前统计
        数据 = yield {
            "圈数": 圈数,
            "总距离km": round(总距离, 2),
            "总时间min": round(总时间, 2),
            "平均速度km/h": round(总距离 / 总时间 * 60, 1) if 总时间 > 0 else 0,
            "最高速度km/h": round(最高速度, 1),
        }

        if 数据 is None:
            break

        距离, 时间 = 数据  # 解包：(距离km, 时间min)
        总距离 += 距离
        总时间 += 时间
        圈数 += 1
        当前速度 = 距离 / 时间 * 60  # km/h
        if 当前速度 > 最高速度:
            最高速度 = 当前速度

# 启动统计器
stats = 运动统计器()
初始状态 = next(stats)  # 必须先 next() 激活
print(f"初始状态: {初始状态}")

# 模拟每圈的数据 (距离km, 时间min)
圈数据 = [(0.4, 2.5), (0.4, 2.3), (0.4, 2.1), (0.4, 2.4)]

for i, (距离, 时间) in enumerate(圈数据, 1):
    结果 = stats.send((距离, 时间))
    print(f"第{i}圈后: 总距离={结果['总距离km']}km, "
          f"平均速度={结果['平均速度km/h']}km/h, "
          f"最高速度={结果['最高速度km/h']}km/h")
```

```
# 预期输出：
初始状态: {'圈数': 0, '总距离km': 0, '总时间min': 0, '平均速度km/h': 0, '最高速度km/h': 0}
第1圈后: 总距离=0.4km, 平均速度=9.6km/h, 最高速度=9.6km/h
第2圈后: 总距离=0.8km, 平均速度=10.0km/h, 最高速度=10.4km/h
第3圈后: 总距离=1.2km, 平均速度=10.5km/h, 最高速度=11.4km/h
第4圈后: 总距离=1.6km, 平均速度=10.4km/h, 最高速度=11.4km/h
```

---

## Demo 4：yield from 树结构遍历

```python
# yield from 非常适合递归遍历树结构

# 定义树节点
class 节点:
    def __init__(self, 值, *子节点):
        self.值 = 值
        self.子节点 = list(子节点)

    def __repr__(self):
        return f"节点({self.值})"

def 深度优先遍历(节点对象):
    """使用 yield from 递归遍历树"""
    yield 节点对象.值
    for 子节点 in 节点对象.子节点:
        yield from 深度优先遍历(子节点)  # 递归委托

def 广度优先遍历(根节点):
    """广度优先遍历（使用队列）"""
    from collections import deque
    队列 = deque([根节点])
    while 队列:
        当前 = 队列.popleft()
        yield 当前.值
        队列.extend(当前.子节点)

# 构建树：
#       1
#      / \
#     2   3
#    / \   \
#   4   5   6
#  /
# 7

树 = 节点(1,
    节点(2,
        节点(4,
            节点(7)
        ),
        节点(5)
    ),
    节点(3,
        节点(6)
    )
)

print("深度优先:", list(深度优先遍历(树)))
print("广度优先:", list(广度优先遍历(树)))
```

```
# 预期输出：
深度优先: [1, 2, 4, 7, 5, 3, 6]
广度优先: [1, 2, 3, 4, 5, 6, 7]
```

---

## Demo 5：自定义迭代器类

```python
# 实现一个分页迭代器

class 分页迭代器:
    """
    将大列表分页返回
    用法：for page in 分页迭代器(data, page_size=3)
    """

    def __init__(self, 数据, 页大小=10):
        self.数据 = list(数据)
        self.页大小 = 页大小
        self.当前索引 = 0
        self.总页数 = (len(self.数据) + 页大小 - 1) // 页大小

    def __iter__(self):
        return self

    def __next__(self):
        if self.当前索引 >= len(self.数据):
            raise StopIteration

        页码 = self.当前索引 // self.页大小 + 1
        页数据 = self.数据[self.当前索引: self.当前索引 + self.页大小]
        self.当前索引 += self.页大小

        return {"页码": 页码, "数据": 页数据, "总页数": self.总页数}

    def __len__(self):
        return self.总页数

# 测试
用户列表 = [f"用户{i}" for i in range(1, 12)]

print(f"总用户数: {len(用户列表)}, 每页3条")
for 页 in 分页迭代器(用户列表, 页大小=3):
    print(f"  第{页['页码']}/{页['总页数']}页: {页['数据']}")
```

```
# 预期输出：
总用户数: 11, 每页3条
  第1/4页: ['用户1', '用户2', '用户3']
  第2/4页: ['用户4', '用户5', '用户6']
  第3/4页: ['用户7', '用户8', '用户9']
  第4/4页: ['用户10', '用户11']
```
