# 第13章：生成器与协议

## 学习目标
- 理解 yield 关键字的工作原理
- 区分生成器函数与生成器表达式
- 掌握 send()、yield from 的高级用法
- 深入理解迭代器协议

---

## 1. yield 关键字

### 1.1 yield vs return

```
return:  函数执行到此处，返回值并终止
yield:   函数执行到此处，返回值并【暂停】，下次调用从此处继续
```

```
生成器函数执行流程：

调用 gen = my_generator()   → 创建生成器对象（不执行任何代码！）
调用 next(gen)              → 执行到第一个 yield，暂停，返回值
调用 next(gen)              → 从上次 yield 之后继续，执行到下一个 yield
调用 next(gen)              → 执行到函数结束，抛出 StopIteration
```

```python
def 简单生成器():
    print("第1步")
    yield 1         # 暂停，返回 1
    print("第2步")
    yield 2         # 暂停，返回 2
    print("第3步")
    yield 3         # 暂停，返回 3
    print("结束")   # 函数体执行完毕

gen = 简单生成器()  # 不打印任何内容！
print(next(gen))    # 打印"第1步"，返回 1
print(next(gen))    # 打印"第2步"，返回 2
print(next(gen))    # 打印"第3步"，返回 3
# next(gen)         # 打印"结束"，然后抛出 StopIteration
```

### 1.2 生成器的状态

```
┌─────────────────────────────────────────────────┐
│                生成器的生命周期                   │
│                                                 │
│  Created  →  Suspended  →  Closed               │
│    │              ↑  ↓        ↑                 │
│    │           next()      StopIteration        │
│    └──────────────────────────────────────────→ │
│              第一次 next() 激活                  │
└─────────────────────────────────────────────────┘
```

---

## 2. 生成器函数 vs 生成器表达式

```python
# 生成器函数：含 yield 的普通函数
def 偶数生成器(最大值):
    n = 0
    while n <= 最大值:
        yield n
        n += 2

# 生成器表达式：类似列表推导式，但用 ()
偶数表达式 = (x for x in range(0, 101, 2))

# 两者功能相同，但生成器函数更灵活
gen1 = 偶数生成器(10)
gen2 = (x for x in range(0, 11, 2))

print(list(gen1))  # [0, 2, 4, 6, 8, 10]
print(list(gen2))  # [0, 2, 4, 6, 8, 10]
```

**选择建议：**
- 逻辑简单：用生成器表达式（一行即可）
- 逻辑复杂（循环、条件、多个 yield）：用生成器函数

---

## 3. send() 方法 — 双向通信

`send()` 不仅能驱动生成器，还能**向生成器发送数据**。

```
普通 next():   外部 ←── yield值 ── 生成器
send():        外部 ←── yield值 ── 生成器
                     ──发送值──→
```

```python
def 累加器():
    total = 0
    while True:
        值 = yield total    # yield 表达式：既输出 total，也接收 send() 的值
        if 值 is None:
            break
        total += 值

gen = 累加器()
print(next(gen))        # 启动生成器，输出初始值 0
print(gen.send(10))     # 发送 10，输出 10
print(gen.send(20))     # 发送 20，输出 30
print(gen.send(5))      # 发送 5，输出 35
```

**关键规则：**
1. 第一次必须用 `next()` 或 `send(None)` 启动生成器
2. `send(值)` 把值送入 `yield 表达式`，返回下一个 `yield` 的值

---

## 4. yield from — 委托生成器

`yield from` 让一个生成器**委托**给另一个生成器（或任何可迭代对象）。

### 4.1 基本用法

```python
# 不用 yield from：需要手动循环
def 合并生成器_v1(*iterables):
    for iterable in iterables:
        for item in iterable:
            yield item

# 用 yield from：更简洁
def 合并生成器_v2(*iterables):
    for iterable in iterables:
        yield from iterable

# 两者等价
gen1 = 合并生成器_v1([1, 2], [3, 4], [5, 6])
gen2 = 合并生成器_v2([1, 2], [3, 4], [5, 6])

print(list(gen1))  # [1, 2, 3, 4, 5, 6]
print(list(gen2))  # [1, 2, 3, 4, 5, 6]
```

### 4.2 yield from 的通道作用

```
┌─────────────────────────────────────────────────────┐
│              yield from 建立的通道                   │
│                                                     │
│  调用方  ←── 值 ── 委托生成器(yield from) ←── 子生成器 │
│  调用方  ──send()──→  委托生成器  ──send()──→ 子生成器  │
│                                                     │
│  send() 和异常直接穿透到子生成器                     │
└─────────────────────────────────────────────────────┘
```

```python
def 子生成器(n):
    for i in range(n):
        yield i

def 委托生成器(n):
    result = yield from 子生成器(n)   # yield from 接收子生成器的 return 值
    print(f"子生成器返回: {result}")
    yield "完成"

for val in 委托生成器(4):
    print(val)
```

---

## 5. 迭代器协议详解

任何实现了以下两个方法的对象都是迭代器：

```
__iter__()   → 返回迭代器自身（通常 return self）
__next__()   → 返回下一个值，耗尽时抛出 StopIteration
```

```python
class 范围迭代器:
    """实现类似 range() 的自定义迭代器"""

    def __init__(self, start, stop, step=1):
        self.current = start
        self.stop = stop
        self.step = step

    def __iter__(self):
        return self  # 迭代器返回自身

    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration  # 告知外界迭代结束
        value = self.current
        self.current += self.step
        return value

# 使用
for n in 范围迭代器(1, 10, 2):
    print(n, end=" ")  # 1 3 5 7 9
```

**可迭代对象 vs 迭代器：**

```
可迭代对象（Iterable）：有 __iter__，每次调用返回新迭代器
迭代器（Iterator）：有 __iter__ 和 __next__，有内部状态

list  → 可迭代对象（不是迭代器）
iter(list) → 迭代器
生成器 → 既是可迭代对象，也是迭代器
```

---

## 总结

```
┌──────────────────────────────────────────────────────┐
│                   本章知识点总结                      │
├───────────────────┬──────────────────────────────────┤
│  yield            │  暂停并返回值，下次从此继续        │
│  生成器函数        │  含 yield 的函数，返回生成器对象  │
│  生成器表达式      │  (expr for x in it)，简洁版       │
│  send()           │  向生成器发送值                   │
│  yield from       │  委托给另一个可迭代对象            │
│  __iter__         │  返回迭代器自身                   │
│  __next__         │  返回下一个值或抛出 StopIteration │
└───────────────────┴──────────────────────────────────┘
```
