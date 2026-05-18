# 第11章：函数进阶 — 自测题

## 题目1：*args 与 **kwargs

以下代码的输出是什么？

```python
def func(a, b=2, *args, **kwargs):
    print(a, b, args, kwargs)

func(1, 3, 4, 5, x=10)
```

A. `1 2 (3, 4, 5) {'x': 10}`
B. `1 3 (4, 5) {'x': 10}`
C. `1 3 (4, 5, 'x', 10) {}`
D. 报错

### 参考答案

**B**

解析：
- `a=1`（第一个位置参数）
- `b=3`（第二个位置参数，覆盖默认值2）
- `args=(4, 5)`（剩余位置参数打包为元组）
- `kwargs={'x': 10}`（关键字参数打包为字典）

---

## 题目2：默认参数陷阱

下面哪段代码存在默认参数陷阱，并说明原因及修复方式。

```python
# 代码A
def append_to(element, to=None):
    if to is None:
        to = []
    to.append(element)
    return to

# 代码B
def append_to2(element, to=[]):
    to.append(element)
    return to
```

### 参考答案

**代码B 存在默认参数陷阱。**

原因：Python 在函数**定义**时就计算并创建默认值 `[]`，这个列表对象只创建一次。每次调用 `append_to2` 时，如果不传 `to` 参数，所有调用共享同一个列表对象，导致历史数据累积。

验证：
```python
print(append_to2(1))  # [1]
print(append_to2(2))  # [1, 2]  ← 不是 [2]！
```

修复：使用 `None` 作为哨兵值（代码A 的写法），在函数体内创建新列表。

---

## 题目3：闭包与 nonlocal

补全以下代码，使输出结果为 `1 2 3 2 1`：

```python
def 创建双向计数器():
    count = 0

    def 增加():
        # 补全这里
        count += 1
        return count

    def 减少():
        # 补全这里
        count -= 1
        return count

    return 增加, 减少

inc, dec = 创建双向计数器()
print(inc(), inc(), inc(), dec(), dec())
```

### 参考答案

```python
def 创建双向计数器():
    count = 0

    def 增加():
        nonlocal count    # 关键：声明修改外层变量
        count += 1
        return count

    def 减少():
        nonlocal count    # 关键：声明修改外层变量
        count -= 1
        return count

    return 增加, 减少

inc, dec = 创建双向计数器()
print(inc(), inc(), inc(), dec(), dec())
# 输出：1 2 3 2 1
```

关键点：如果不加 `nonlocal count`，`count += 1` 会被解释为局部变量赋值，Python 会抛出 `UnboundLocalError`，因为局部变量 `count` 在赋值前被引用。

---

## 题目4：map 与 filter

使用 `map` 和 `filter` 完成以下任务：给定字符串列表 `["hello", "WORLD", "Python", "123", "ai"]`，筛选出长度大于3的字符串，然后将它们全部转为大写。

### 参考答案

```python
words = ["hello", "WORLD", "Python", "123", "ai"]

# 方法1：链式使用 map 和 filter
result = list(map(str.upper, filter(lambda w: len(w) > 3, words)))
print(result)  # ['HELLO', 'WORLD', 'PYTHON']

# 方法2：分步处理
长词 = filter(lambda w: len(w) > 3, words)
大写 = map(str.upper, 长词)
print(list(大写))  # ['HELLO', 'WORLD', 'PYTHON']

# 方法3：列表推导式（更 Pythonic）
result2 = [w.upper() for w in words if len(w) > 3]
print(result2)  # ['HELLO', 'WORLD', 'PYTHON']
```

注意：`"123"` 长度为3，不满足"大于3"的条件，所以被过滤掉。

---

## 题目5：综合应用

编写一个 `make_power` 函数，它接收一个整数 `n`，返回一个函数，该函数计算输入值的 `n` 次方。然后使用 `map` 和这些函数，分别计算列表 `[1, 2, 3, 4, 5]` 的平方和立方。

### 参考答案

```python
def make_power(n):
    """函数工厂：返回计算 n 次方的函数"""
    def power(x):
        return x ** n
    return power

# 创建专用函数
square = make_power(2)
cube = make_power(3)

numbers = [1, 2, 3, 4, 5]

# 使用 map 计算
平方列表 = list(map(square, numbers))
立方列表 = list(map(cube, numbers))

print("平方:", 平方列表)  # [1, 4, 9, 16, 25]
print("立方:", 立方列表)  # [1, 8, 27, 64, 125]

# 验证函数工厂的原理
print(f"square 记住了 n={square.__code__.co_freevars}")  # ('n',)

# 更简洁的 lambda 版本
make_power2 = lambda n: lambda x: x ** n
print(list(map(make_power2(4), numbers)))  # [1, 16, 81, 256, 625]
```

关键点：`make_power` 是一个函数工厂，利用闭包让返回的 `power` 函数"记住"了 `n` 的值。每次调用 `make_power` 都创建一个独立的闭包，`square` 和 `cube` 各自持有自己的 `n`。
