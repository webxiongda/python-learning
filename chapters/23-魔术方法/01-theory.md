# 第23章：魔术方法

## 什么是魔术方法

魔术方法（Magic Methods / Dunder Methods）是 Python 中以双下划线开头和结尾的特殊方法（如 `__init__`、`__str__`）。它们让自定义类与 Python 的内置操作协同工作，实现运算符重载、内置函数支持等功能。

```
魔术方法分类图：
┌─────────────────────────────────────────────────┐
│                   魔术方法                       │
│                                                  │
│  字符串表示      容器协议        比较运算          │
│  __str__        __len__         __eq__           │
│  __repr__       __getitem__     __lt__           │
│                 __setitem__     __le__           │
│                 __contains__    __gt__           │
│                                                  │
│  上下文管理器    可调用对象       算术运算          │
│  __enter__      __call__        __add__          │
│  __exit__                       __mul__          │
└─────────────────────────────────────────────────┘
```

## __str__ 和 __repr__

### __str__：面向用户的字符串

`__str__` 定义 `str(obj)` 和 `print(obj)` 的输出，目的是可读性：

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"Point({self.x}, {self.y})"

p = Point(3, 4)
print(p)         # Point(3, 4)  ← 调用 __str__
print(str(p))    # Point(3, 4)
```

### __repr__：面向开发者的字符串

`__repr__` 定义对象的官方字符串表示，目的是无歧义，理想情况下可用于重建对象：

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"
    
    def __str__(self):
        return f"({self.x}, {self.y})"

p = Point(3, 4)
print(p)       # (3, 4)          ← __str__
print(repr(p)) # Point(x=3, y=4) ← __repr__
```

**选择规则：**
```
str() / print()  ──→ __str__
repr() / 调试     ──→ __repr__
未定义 __str__   ──→ 回退到 __repr__
```

## __len__ 和 __getitem__ / __setitem__

### __len__

让对象支持 `len()` 函数：

```python
class Playlist:
    def __init__(self, name):
        self.name = name
        self.songs = []
    
    def add(self, song):
        self.songs.append(song)
    
    def __len__(self):
        return len(self.songs)

pl = Playlist("我的歌单")
pl.add("周杰伦 - 晴天")
pl.add("林俊杰 - 江南")
print(len(pl))  # 2
```

### __getitem__ 和 __setitem__

让对象支持索引访问（`obj[key]`）和赋值（`obj[key] = value`）：

```python
class Matrix:
    """简单的2D矩阵"""
    def __init__(self, rows, cols, fill=0):
        self.data = [[fill] * cols for _ in range(rows)]
        self.rows = rows
        self.cols = cols
    
    def __getitem__(self, pos):
        row, col = pos
        return self.data[row][col]
    
    def __setitem__(self, pos, value):
        row, col = pos
        self.data[row][col] = value
    
    def __len__(self):
        return self.rows * self.cols

m = Matrix(3, 3)
m[0, 0] = 1   # 调用 __setitem__
m[1, 1] = 5
m[2, 2] = 9
print(m[1, 1])  # 5  ← 调用 __getitem__
```

## __eq__ 和 __lt__

### 比较运算符重载

```python
class Student:
    def __init__(self, name, gpa):
        self.name = name
        self.gpa = gpa
    
    def __eq__(self, other):
        """== 运算符"""
        if not isinstance(other, Student):
            return NotImplemented
        return self.gpa == other.gpa
    
    def __lt__(self, other):
        """< 运算符"""
        if not isinstance(other, Student):
            return NotImplemented
        return self.gpa < other.gpa
    
    def __repr__(self):
        return f"Student({self.name!r}, {self.gpa})"

s1 = Student("张三", 3.8)
s2 = Student("李四", 3.5)
s3 = Student("王五", 3.8)

print(s1 == s3)  # True（GPA相同）
print(s1 > s2)   # True（需要 __gt__ 或 __lt__）
```

### functools.total_ordering

只需实现 `__eq__` 和一个比较方法，自动生成其余比较方法：

```python
from functools import total_ordering

@total_ordering
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius
    
    def __eq__(self, other):
        return self.celsius == other.celsius
    
    def __lt__(self, other):
        return self.celsius < other.celsius
    # 自动生成：__le__、__gt__、__ge__

t1 = Temperature(100)
t2 = Temperature(50)
print(t1 > t2)   # True（自动生成）
print(t1 >= t2)  # True（自动生成）
```

比较魔术方法对应表：

```
运算符  魔术方法
==      __eq__
!=      __ne__
<       __lt__
<=      __le__
>       __gt__
>=      __ge__
```

## __enter__ 和 __exit__（上下文管理器）

实现 `with` 语句支持：

```python
class FileManager:
    """自定义文件管理器"""
    
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        """with 块开始时调用"""
        print(f"打开文件：{self.filename}")
        self.file = open(self.filename, self.mode, encoding="utf-8")
        return self.file  # as 子句得到的值
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """with 块结束时调用（无论是否异常）"""
        if self.file:
            self.file.close()
        print(f"关闭文件：{self.filename}")
        if exc_type:
            print(f"发生异常：{exc_type.__name__}: {exc_val}")
        return False  # False = 不压制异常

# 使用
with FileManager("test.txt", "w") as f:
    f.write("Hello, World!")
# 自动关闭文件
```

`__exit__` 参数说明：
```
__exit__(self, exc_type, exc_val, exc_tb)
                │           │        │
                │           │        └── traceback 对象
                │           └────────── 异常实例
                └────────────────────── 异常类型
                                       （无异常时均为 None）

返回值：
  True  → 压制异常（with块内的异常不会传播）
  False → 不压制异常（异常继续传播）
```

## __call__

让对象像函数一样被调用：

```python
class Multiplier:
    """乘法器工厂"""
    
    def __init__(self, factor):
        self.factor = factor
    
    def __call__(self, value):
        return value * self.factor

double = Multiplier(2)   # 创建对象
triple = Multiplier(3)

print(double(10))  # 20  ← 调用 __call__
print(triple(10))  # 30

# 也可以用 callable() 检查
print(callable(double))  # True
print(callable(42))      # False
```

`__call__` 常用于：
- 函数式风格的对象
- 带状态的"函数"（如闭包替代）
- 装饰器类

## 魔术方法调用时机总结

```
操作                调用的魔术方法
────────────────────────────────────────
print(obj)          __str__（或__repr__）
repr(obj)           __repr__
len(obj)            __len__
obj[key]            __getitem__
obj[key] = val      __setitem__
del obj[key]        __delitem__
obj == other        __eq__
obj < other         __lt__
with obj as x       __enter__ / __exit__
obj(args)           __call__
iter(obj)           __iter__
next(obj)           __next__
```

## 总结建议

1. **始终实现 `__repr__`**：调试时非常有用
2. **`__str__` 用于展示给用户**：可读性优先
3. **`__eq__` 和 `__hash__` 通常成对实现**：定义了 `__eq__` 后，默认 `__hash__` 会失效
4. **上下文管理器保证资源释放**：数据库连接、文件、锁等场景必备
