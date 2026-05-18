# 第13章：生成器与协议 — 自测题

## 题目1：yield 基础

以下代码的输出是什么？

```python
def gen():
    yield 1
    yield 2
    return "完成"
    yield 3  # 这行会执行吗？

g = gen()
print(next(g))
print(next(g))
try:
    next(g)
except StopIteration as e:
    print(f"停止，值为: {e.value}")
```

### 参考答案

```
1
2
停止，值为: 完成
```

解析：
- `yield 3` 永远不会执行，因为 `return` 在它之前
- 生成器函数中的 `return 值` 会在 `StopIteration` 异常中携带该返回值
- `StopIteration.value` 可以获取生成器的返回值

---

## 题目2：send() 用法

补全以下代码，使其能接收外部值并输出累积乘积：

```python
def 累积乘积():
    product = 1
    while True:
        value = yield ___  # 补全
        if value is None:
            return
        product *= value

gen = 累积乘积()
next(gen)  # 启动
print(gen.send(2))   # 2
print(gen.send(3))   # 6
print(gen.send(4))   # 24
```

### 参考答案

```python
def 累积乘积():
    product = 1
    while True:
        value = yield product   # 输出当前乘积，接收新值
        if value is None:
            return
        product *= value

gen = 累积乘积()
next(gen)            # 启动生成器，执行到第一个 yield
print(gen.send(2))   # product = 1*2 = 2，输出 2
print(gen.send(3))   # product = 2*3 = 6，输出 6
print(gen.send(4))   # product = 6*4 = 24，输出 24
```

关键：`yield product` 这行既输出 `product` 的当前值，也等待接收 `send()` 传入的新值。

---

## 题目3：yield from

以下两段代码的输出是否相同？为什么？

```python
# 代码A
def gen_a():
    for x in [[1, 2], [3, 4], [5, 6]]:
        for item in x:
            yield item

# 代码B
def gen_b():
    for x in [[1, 2], [3, 4], [5, 6]]:
        yield from x

print(list(gen_a()))
print(list(gen_b()))
```

### 参考答案

两段代码输出完全相同：
```
[1, 2, 3, 4, 5, 6]
[1, 2, 3, 4, 5, 6]
```

解析：`yield from 可迭代对象` 等价于 `for item in 可迭代对象: yield item`。

区别在于复杂场景下 `yield from` 的额外功能：
1. `send()` 值会透传到子生成器
2. 子生成器的 `return` 值会成为 `yield from` 表达式的值
3. 异常也会透传

对于简单的展开操作，两者完全等价，但 `yield from` 更简洁。

---

## 题目4：迭代器协议

实现一个 `循环迭代器` 类，使其对任意可迭代对象**无限循环**迭代（类似 `itertools.cycle`）。

```python
# 期望行为：
it = 循环迭代器([1, 2, 3])
for _ in range(7):
    print(next(it), end=" ")
# 输出：1 2 3 1 2 3 1
```

### 参考答案

```python
class 循环迭代器:
    def __init__(self, iterable):
        self.数据 = list(iterable)  # 保存原始数据
        self.索引 = 0

    def __iter__(self):
        return self

    def __next__(self):
        if not self.数据:
            raise StopIteration
        值 = self.数据[self.索引]
        self.索引 = (self.索引 + 1) % len(self.数据)  # 取模实现循环
        return 值

it = 循环迭代器([1, 2, 3])
for _ in range(7):
    print(next(it), end=" ")
# 输出：1 2 3 1 2 3 1

# 等价的生成器版本
def 循环生成器(iterable):
    数据 = list(iterable)
    while True:
        yield from 数据
```

---

## 题目5：综合应用

编写一个 `分块生成器(iterable, n)` 函数，将可迭代对象每 `n` 个元素分为一组，使用 `yield` 返回每组（元组形式）。

```python
# 期望：
list(分块生成器(range(10), 3))
# [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]
```

### 参考答案

```python
def 分块生成器(iterable, n):
    """将可迭代对象按 n 个一组分块"""
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == n:
            yield tuple(chunk)
            chunk = []
    if chunk:  # 处理最后不满 n 个的情况
        yield tuple(chunk)

# 测试
print(list(分块生成器(range(10), 3)))
# [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]

print(list(分块生成器("abcdefg", 2)))
# [('a', 'b'), ('c', 'd'), ('e', 'f'), ('g',)]

# 进阶版本：使用 iter 和 zip
def 分块生成器_v2(iterable, n):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            break
        yield chunk

import itertools
print(list(分块生成器_v2(range(10), 3)))
# [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]
```
