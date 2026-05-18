# 第04章：函数基础 — 自测题

---

## 题目 1：选择题

以下代码的输出是什么？

```python
def mystery(a, b=10, *args):
    return a + b + sum(args)

print(mystery(1))
print(mystery(1, 2))
print(mystery(1, 2, 3, 4))
```

A. 11 / 3 / 10
B. 11 / 3 / 11  
C. 报错 / 3 / 10
D. 11 / 3 / 报错

### 参考答案

**A**

解析：
- `mystery(1)`：a=1, b=10（默认），args=()，结果 1+10+0=11
- `mystery(1, 2)`：a=1, b=2，args=()，结果 1+2+0=3
- `mystery(1, 2, 3, 4)`：a=1, b=2，args=(3, 4)，sum(args)=7，结果 1+2+7=10

---

## 题目 2：作用域分析题

分析以下代码，预测每个 `print` 的输出，并解释原因：

```python
x = 1

def foo():
    x = 2
    def bar():
        x = 3
        print(f"bar 中 x = {x}")
    bar()
    print(f"foo 中 x = {x}")

foo()
print(f"全局 x = {x}")
```

### 参考答案

```
bar 中 x = 3
foo 中 x = 2
全局 x = 1
```

解析：这是 LEGB 规则的经典示例。每个函数内部的 `x = ...` 创建了一个新的**本地变量**，不会影响外层作用域的 `x`。查找顺序：bar 先找 Local（找到 x=3）；foo 先找 Local（找到 x=2）；全局找到 x=1。三个 x 是完全独立的变量。

---

## 题目 3：函数改写题

将以下重复代码重构为一个函数：

```python
# 原始重复代码
total1 = 0
for i in range(1, 6):
    total1 += i
print(f"1到5的和：{total1}")

total2 = 0
for i in range(1, 11):
    total2 += i
print(f"1到10的和：{total2}")

total3 = 0
for i in range(1, 101):
    total3 += i
print(f"1到100的和：{total3}")
```

要求：编写一个函数，接受起始值（默认1）和结束值（必填），返回范围内所有整数之和，并附上 docstring。

### 参考答案

```python
def sum_range(end: int, start: int = 1) -> int:
    """计算从 start 到 end（含）的所有整数之和。

    参数：
        end: 范围结束值（包含）
        start: 范围起始值（默认为 1）

    返回：
        范围内所有整数的总和

    示例：
        >>> sum_range(5)
        15
        >>> sum_range(10, 1)
        55
    """
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


# 使用重构后的函数
print(f"1到5的和：{sum_range(5)}")
print(f"1到10的和：{sum_range(10)}")
print(f"1到100的和：{sum_range(100)}")
```

---

## 题目 4：代码输出预测题

```python
def outer(n):
    results = []
    for i in range(n):
        def inner(x):
            return x * i    # 注意：i 是闭包变量
        results.append(inner)
    return results

funcs = outer(3)
for f in funcs:
    print(f(10))
```

预测输出，并解释为什么（这是一个经典的"闭包陷阱"）。

### 参考答案

输出：
```
20
20
20
```

解析（经典闭包陷阱）：`inner` 函数捕获的是变量 `i` 的**引用**，而不是其当时的值。当 `outer(3)` 执行完毕后，`i` 的值为 2（最后一次循环结束时的值）。所以所有 `inner` 函数调用时 `i` 都是 2，结果都是 `10 * 2 = 20`。

修复方式（将 i 作为默认参数固定）：
```python
def inner(x, i=i):   # 默认参数在定义时求值
    return x * i
```

修复后输出：`0 / 10 / 20`

---

## 题目 5：综合编程题

编写一个函数 `describe_list`，满足以下要求：

1. 接受一个列表参数和一个可选的 `label` 参数（默认值 `"列表"`）
2. 函数返回一个字典，包含以下统计信息：
   - `label`：传入的标签
   - `length`：列表长度
   - `sum`：所有数字的总和（非数字元素忽略）
   - `avg`：平均值（只考虑数字，无数字时返回 None）
   - `types`：列表中各类型的数量（字典形式）
3. 附上完整的 docstring

### 参考答案

```python
def describe_list(data: list, label: str = "列表") -> dict:
    """统计并描述一个列表的基本信息。

    参数：
        data: 要分析的列表
        label: 列表的标签名称，默认为 "列表"

    返回：
        包含 label, length, sum, avg, types 的字典

    示例：
        >>> describe_list([1, 2, "a", 3.5, True])
        {'label': '列表', 'length': 5, 'sum': 7.5, 'avg': 2.5, 'types': {...}}
    """
    numbers = [x for x in data if isinstance(x, (int, float)) and not isinstance(x, bool)]
    total = sum(numbers)
    avg = total / len(numbers) if numbers else None

    type_count = {}
    for item in data:
        type_name = type(item).__name__
        type_count[type_name] = type_count.get(type_name, 0) + 1

    return {
        "label": label,
        "length": len(data),
        "sum": total,
        "avg": avg,
        "types": type_count,
    }


# 测试
result = describe_list([1, 2, "hello", 3.5, None, True], label="混合数据")
for k, v in result.items():
    print(f"  {k}: {v}")
```

预期输出：
```
  label: 混合数据
  length: 6
  sum: 6.5
  avg: 2.1666666666666665
  types: {'int': 2, 'str': 1, 'float': 1, 'NoneType': 1, 'bool': 1}
```
