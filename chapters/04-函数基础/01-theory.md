# 第04章：函数基础 — 理论篇

## 1. 为什么需要函数？

函数是将一段**可复用代码**封装起来并命名的机制。它解决了两个核心问题：

```
没有函数的问题
┌─────────────────────────────────┐
│  代码重复：同样的计算逻辑复制3遍 │
│  难以维护：修改需要改3个地方     │
│  难以测试：无法单独测试某段逻辑  │
└─────────────────────────────────┘

使用函数后
┌─────────────────────────────────┐
│  def calculate_tax(income):     │
│      return income * 0.2        │
│                                 │
│  tax1 = calculate_tax(50000)    │  ← 复用
│  tax2 = calculate_tax(80000)    │  ← 复用
│  tax3 = calculate_tax(120000)   │  ← 复用
└─────────────────────────────────┘
```

函数的核心价值：**DRY 原则**（Don't Repeat Yourself）

---

## 2. 定义与调用函数

### 基本语法

```python
def 函数名(参数1, 参数2, ...):
    """文档字符串（可选）"""
    # 函数体
    return 返回值

# 调用
结果 = 函数名(实参1, 实参2)
```

### 完整示例

```python
def greet(name):
    """生成问候语。
    
    参数：
        name: 被问候人的姓名
    返回：
        包含问候信息的字符串
    """
    message = f"你好，{name}！欢迎学习 Python。"
    return message

# 调用函数
result = greet("Alice")
print(result)  # 你好，Alice！欢迎学习 Python。
```

---

## 3. 参数类型详解

### 3.1 位置参数

按照**定义顺序**传入的参数：

```python
def describe_person(name, age, city):
    return f"{name}，{age}岁，来自{city}"

# 调用时必须按顺序传入
print(describe_person("张三", 25, "北京"))
# 输出：张三，25岁，来自北京
```

### 3.2 默认参数

为参数提供默认值，调用时可以省略：

```python
def power(base, exponent=2):   # exponent 有默认值
    return base ** exponent

print(power(3))      # 9（exponent 用默认值 2）
print(power(3, 3))   # 27（exponent 用传入的 3）
print(power(2, 10))  # 1024
```

**重要规则**：有默认值的参数必须放在无默认值参数的**后面**。

```python
# 错误：def f(a=1, b)   ← SyntaxError
# 正确：def f(b, a=1)
```

### 3.3 关键字参数

调用时通过**参数名**指定值，顺序可以不同：

```python
def create_user(username, email, role="user"):
    return f"用户: {username}, 邮箱: {email}, 角色: {role}"

# 关键字参数调用，顺序无关
result = create_user(email="alice@example.com", username="alice")
print(result)
# 输出：用户: alice, 邮箱: alice@example.com, 角色: user
```

### 3.4 可变位置参数 *args

接收任意数量的位置参数，打包为元组：

```python
def sum_all(*numbers):
    """计算任意数量数字的总和"""
    total = 0
    for n in numbers:
        total += n
    return total

print(sum_all(1, 2, 3))        # 6
print(sum_all(10, 20, 30, 40)) # 100
```

### 3.5 可变关键字参数 **kwargs

接收任意数量的关键字参数，打包为字典：

```python
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"  {key}: {value}")

print_info(name="Alice", age=25, city="北京")
# 输出：
#   name: Alice
#   age: 25
#   city: 北京
```

### 参数顺序规则

```
函数参数的正确顺序（从左到右）：
┌──────────────────────────────────────────────────────┐
│ 位置参数 → 默认参数 → *args → 关键字专用参数 → **kwargs │
│  (a, b)  →  (c=1)  →  (*d)  →      (*, e)   →  (**f) │
└──────────────────────────────────────────────────────┘
```

---

## 4. return 语句

```python
# 返回单个值
def square(x):
    return x ** 2

# 返回多个值（实际上是返回元组）
def min_max(numbers):
    return min(numbers), max(numbers)

low, high = min_max([3, 1, 4, 1, 5, 9, 2])
print(f"最小值：{low}，最大值：{high}")
# 输出：最小值：1，最大值：9

# 没有 return 或 return 无值，函数返回 None
def do_print(msg):
    print(msg)
    # 隐式 return None

result = do_print("hello")
print(result is None)  # True
```

---

## 5. 作用域：LEGB 规则

Python 查找变量名时，按照 **LEGB** 顺序依次查找：

```
LEGB 作用域查找顺序
┌──────────────────────────────────────────┐
│  L - Local（本地作用域）                  │
│      当前函数内部定义的变量               │
│         ↓ 找不到，往上找                 │
│  E - Enclosing（闭包/嵌套函数作用域）    │
│      外层函数的变量（嵌套函数时存在）     │
│         ↓ 找不到，往上找                 │
│  G - Global（全局作用域）                │
│      模块级别定义的变量                  │
│         ↓ 找不到，往上找                 │
│  B - Built-in（内置作用域）              │
│      Python 内置函数和常量              │
└──────────────────────────────────────────┘
```

```python
x = "全局 x"          # Global 作用域

def outer():
    x = "外层 x"      # Enclosing 作用域（对 inner 来说）
    
    def inner():
        x = "内层 x"  # Local 作用域
        print(x)      # 找到 Local，打印"内层 x"
    
    inner()
    print(x)          # 找到 Enclosing，打印"外层 x"

outer()
print(x)              # 找到 Global，打印"全局 x"
```

### global 和 nonlocal 关键字

```python
count = 0   # 全局变量

def increment():
    global count   # 声明要修改全局变量
    count += 1

increment()
increment()
print(count)  # 2

# nonlocal 用于修改闭包中的变量
def make_counter():
    n = 0
    def counter():
        nonlocal n   # 修改外层函数的变量
        n += 1
        return n
    return counter

c = make_counter()
print(c(), c(), c())  # 1 2 3
```

---

## 6. docstring（文档字符串）

好的文档字符串是专业代码的标志：

```python
def calculate_bmi(weight_kg, height_m):
    """计算 BMI 体重指数。

    BMI = 体重(kg) / 身高(m)²

    参数：
        weight_kg (float): 体重，单位千克
        height_m (float): 身高，单位米

    返回：
        float: BMI 值，保留 2 位小数

    示例：
        >>> calculate_bmi(70, 1.75)
        22.86
    """
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)

# 查看文档字符串
help(calculate_bmi)
print(calculate_bmi.__doc__)
```

---

## 7. 函数是一等对象

Python 中函数是"一等公民"，可以像普通对象一样传递：

```python
def double(x):
    return x * 2

def triple(x):
    return x * 3

def apply(func, value):
    """将函数应用到值上"""
    return func(value)

print(apply(double, 5))   # 10
print(apply(triple, 5))   # 15

# 函数可以存入列表
operations = [double, triple]
for op in operations:
    print(op(4))   # 8, 12
```

---

## 小结

```
函数核心概念速查
├── def 函数名(参数):    → 函数定义
├── return 值            → 返回值（可多值）
├── 位置参数             → 按顺序传入
├── 默认参数 param=val  → 可省略
├── *args               → 可变位置参数，打包为元组
├── **kwargs            → 可变关键字参数，打包为字典
├── LEGB                → 作用域查找顺序
├── global/nonlocal     → 修改非本地作用域变量
└── docstring           → 三引号文档说明，放函数体第一行
```
