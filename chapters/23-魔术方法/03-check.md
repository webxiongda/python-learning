# 第23章：魔术方法 — 自测题

## 题目1：选择正确的魔术方法

将左列的操作与右列的魔术方法对应连线：

| 操作 | 魔术方法 |
|------|----------|
| `print(obj)` | A. `__call__` |
| `len(obj)` | B. `__repr__` |
| `obj[3]` | C. `__str__` |
| `repr(obj)` | D. `__len__` |
| `obj(args)` | E. `__getitem__` |
| `with obj as x` | F. `__enter__` / `__exit__` |
| `obj1 == obj2` | G. `__eq__` |

### 参考答案

| 操作 | 对应 |
|------|------|
| `print(obj)` | C. `__str__` |
| `len(obj)` | D. `__len__` |
| `obj[3]` | E. `__getitem__` |
| `repr(obj)` | B. `__repr__` |
| `obj(args)` | A. `__call__` |
| `with obj as x` | F. `__enter__` / `__exit__` |
| `obj1 == obj2` | G. `__eq__` |

---

## 题目2：代码补全

补全以下 `Vector` 类，使其支持向量加法、长度计算和美观输出：

```python
import math

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        # 补全：返回 "Vector(x=3, y=4)" 格式
        ______
    
    def __str__(self):
        # 补全：返回 "(3, 4)" 格式
        ______
    
    def __add__(self, other):
        # 补全：返回两个向量相加的新 Vector
        ______
    
    def __len__(self):
        # 补全：返回向量的整数长度（magnitude）
        ______
    
    def __eq__(self, other):
        # 补全：两个向量相等当且仅当x和y都相等
        ______

v1 = Vector(3, 4)
v2 = Vector(1, 2)
print(v1)             # (3, 4)
print(repr(v1))       # Vector(x=3, y=4)
print(v1 + v2)        # (4, 6)
print(len(v1))        # 5
print(v1 == Vector(3, 4))  # True
```

### 参考答案

```python
import math

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Vector(x={self.x}, y={self.y})"
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __len__(self):
        return int(math.sqrt(self.x**2 + self.y**2))
    
    def __eq__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y
```

---

## 题目3：上下文管理器输出预测

阅读以下代码，写出完整输出：

```python
class Managed:
    def __init__(self, name):
        self.name = name
    
    def __enter__(self):
        print(f"进入：{self.name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"退出：{self.name}，有异常={exc_type is not None}")
        return True  # 注意这里是 True

print("开始")
with Managed("A") as a:
    print(f"  使用 {a.name}")
    raise ValueError("测试错误")
    print("  这行不会执行")
print("结束")
```

预测输出并解释 `return True` 的作用。

### 参考答案

**输出：**
```
开始
进入：A
  使用 A
退出：A，有异常=True
结束
```

**解释：**
- `__exit__` 返回 `True` 表示**压制（吞掉）异常**。
- 尽管 `with` 块内抛出了 `ValueError`，但由于 `__exit__` 返回 `True`，异常不会传播到外部。
- 因此 `print("结束")` 正常执行。
- 如果返回 `False`（或 `None`），异常会继续向上传播，`print("结束")` 就不会执行。

---

## 题目4：__call__ 应用

使用 `__call__` 实现一个"记忆化"装饰器类 `Memoize`，使函数的计算结果被缓存，相同参数不重复计算：

要求：
- `Memoize` 类接受一个函数作为参数
- 实现 `__call__` 方法，第一次计算时缓存结果，之后直接返回缓存
- 需要打印是否命中缓存

### 参考答案

```python
class Memoize:
    """记忆化缓存装饰器"""
    
    def __init__(self, func):
        self.func = func
        self.cache = {}
        self.__name__ = func.__name__
    
    def __call__(self, *args):
        if args in self.cache:
            print(f"[缓存命中] {self.__name__}{args}")
            return self.cache[args]
        
        print(f"[计算中] {self.__name__}{args}")
        result = self.func(*args)
        self.cache[args] = result
        return result
    
    def __repr__(self):
        return f"Memoize({self.func.__name__}, 缓存{len(self.cache)}条)"


@Memoize
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)


# 测试
print(fibonacci(5))
print(fibonacci(3))  # 已缓存
print(fibonacci(6))
```

---

## 题目5：综合实现

实现一个 `Money` 类，支持货币运算：

```python
# 要求：
m1 = Money(100, "CNY")
m2 = Money(50, "CNY")
m3 = Money(20, "USD")

print(m1)           # ¥100.00
print(repr(m1))     # Money(100, 'CNY')
print(m1 + m2)      # ¥150.00
print(m1 - m2)      # ¥50.00
print(m1 > m2)      # True
print(m1 == Money(100, "CNY"))  # True

# 不同货币不能相加
try:
    m1 + m3
except TypeError as e:
    print(e)        # 货币类型不匹配：CNY vs USD
```

### 参考答案

```python
from functools import total_ordering

@total_ordering
class Money:
    SYMBOLS = {"CNY": "¥", "USD": "$", "EUR": "€"}
    
    def __init__(self, amount, currency="CNY"):
        self.amount = amount
        self.currency = currency
    
    def __repr__(self):
        return f"Money({self.amount!r}, {self.currency!r})"
    
    def __str__(self):
        symbol = self.SYMBOLS.get(self.currency, self.currency)
        return f"{symbol}{self.amount:.2f}"
    
    def _check_currency(self, other):
        if self.currency != other.currency:
            raise TypeError(f"货币类型不匹配：{self.currency} vs {other.currency}")
    
    def __add__(self, other):
        self._check_currency(other)
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other):
        self._check_currency(other)
        return Money(self.amount - other.amount, self.currency)
    
    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return self.currency == other.currency and self.amount == other.amount
    
    def __lt__(self, other):
        self._check_currency(other)
        return self.amount < other.amount
    
    def __hash__(self):
        return hash((self.amount, self.currency))
```
