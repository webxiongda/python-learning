# 第02章：Python 基础语法 — 理论篇

## 1. 变量与赋值

Python 的变量不需要声明类型，直接赋值即可使用。变量名本质上是对象的"标签"（引用），而不是存放值的盒子。

```
赋值的本质：
name = "Alice"

  内存中的对象        变量名（标签）
  ┌──────────┐
  │ "Alice"  │ ←──── name
  │ type:str │
  └──────────┘

重新赋值：
name = "Bob"

  ┌──────────┐
  │ "Alice"  │   （无引用，等待垃圾回收）
  └──────────┘
  ┌──────────┐
  │  "Bob"   │ ←──── name
  └──────────┘
```

### 变量命名规则

```python
# 合法的变量名
age = 25
user_name = "Alice"      # 下划线分隔（推荐 snake_case）
_private = "内部使用"
MAX_SIZE = 100           # 常量惯例用全大写

# 非法的变量名（会报 SyntaxError）
# 2fast = True           # 不能以数字开头
# my-name = "test"       # 不能含连字符
# class = "A"            # 不能使用关键字
```

Python 关键字（不能作变量名）：

```
False   None    True    and     as      assert
async   await   break   class   continue def
del     elif    else    except  finally  for
from    global  if      import  in       is
lambda  nonlocal not    or      pass     raise
return  try     while   with    yield
```

---

## 2. 基本数据类型

```
Python 内置数据类型层次

object
├── NoneType    → None（表示空值/缺失）
├── bool        → True / False
├── int         → 整数，无大小限制
├── float       → 浮点数（双精度）
├── str         → 字符串（Unicode）
├── list        → 列表（可变序列）
├── tuple       → 元组（不可变序列）
├── dict        → 字典（键值对）
└── set         → 集合（无序不重复）
```

### 2.1 整数（int）

```python
a = 42              # 十进制
b = 0b1010          # 二进制，值为 10
c = 0o17            # 八进制，值为 15
d = 0xFF            # 十六进制，值为 255
e = 1_000_000       # 下划线分隔，提高可读性，值为 1000000

print(type(a))      # <class 'int'>
print(a ** 100)     # Python 整数可以无限大，不会溢出
```

### 2.2 浮点数（float）

```python
pi = 3.14159
e = 2.718
科学计数 = 1.5e10   # 1.5 × 10^10 = 15000000000.0

# 浮点数精度问题（经典陷阱）
print(0.1 + 0.2)          # 0.30000000000000004
print(0.1 + 0.2 == 0.3)   # False！

# 正确比较浮点数的方式
import math
print(math.isclose(0.1 + 0.2, 0.3))  # True
```

### 2.3 字符串（str）

```python
s1 = 'hello'         # 单引号
s2 = "world"         # 双引号（功能相同）
s3 = '''多行
字符串'''             # 三引号

# 字符串不可变：无法修改某个字符，只能创建新字符串
name = "Alice"
# name[0] = "a"      # 报错：TypeError
name = "alice"       # 正确：创建新字符串

print(type(s1))      # <class 'str'>
```

### 2.4 布尔值（bool）

```python
is_adult = True
is_student = False

print(type(True))    # <class 'bool'>
print(True + 1)      # 2（bool 是 int 的子类）
print(int(True))     # 1
print(int(False))    # 0

# 以下值在布尔上下文中为 False（"假值"）
# False, None, 0, 0.0, "", [], {}, set()
```

### 2.5 None 类型

```python
result = None        # 表示"没有值"或"空"

print(type(None))    # <class 'NoneType'>
print(result is None)  # True（推荐用 is 而不是 ==）

# 函数没有 return 语句时，默认返回 None
def do_nothing():
    pass

print(do_nothing())  # None
```

---

## 3. 动态类型与类型检查

Python 是**动态类型**语言：变量的类型由其当前指向的对象决定，可以随时改变。

```python
x = 42          # x 是 int
print(type(x))  # <class 'int'>

x = "hello"     # x 现在是 str
print(type(x))  # <class 'str'>

x = [1, 2, 3]  # x 现在是 list
print(type(x))  # <class 'list'>
```

```
静态类型 vs 动态类型
┌─────────────┬────────────────────────┐
│ 静态类型     │ 动态类型               │
│ (Java/C++)  │ (Python)              │
├─────────────┼────────────────────────┤
│ 编译时检查  │ 运行时检查             │
│ 需要声明类型 │ 无需声明，自动推断     │
│ 性能更好    │ 灵活性更强             │
│ int x = 5; │ x = 5                 │
└─────────────┴────────────────────────┘
```

### 类型转换

```python
# 显式类型转换
int("42")        # 42
float("3.14")    # 3.14
str(100)         # "100"
bool(0)          # False
bool("hello")    # True
list("abc")      # ['a', 'b', 'c']
```

---

## 4. 运算符

### 4.1 算术运算符

```python
a, b = 17, 5

print(a + b)    # 22  加法
print(a - b)    # 12  减法
print(a * b)    # 85  乘法
print(a / b)    # 3.4 真除法（结果始终为 float）
print(a // b)   # 3   整除（向下取整）
print(a % b)    # 2   取余（模运算）
print(a ** b)   # 1419857  幂运算
```

### 4.2 比较运算符

```python
print(3 == 3)    # True   等于
print(3 != 4)    # True   不等于
print(5 > 3)     # True   大于
print(5 < 3)     # False  小于
print(5 >= 5)    # True   大于等于
print(3 <= 5)    # True   小于等于

# Python 支持链式比较（其他语言少见）
x = 5
print(1 < x < 10)   # True（等价于 1 < x and x < 10）
```

### 4.3 逻辑运算符

```python
print(True and False)   # False  逻辑与
print(True or False)    # True   逻辑或
print(not True)         # False  逻辑非

# 短路求值
# and：左边为 False，右边不再求值
# or：左边为 True，右边不再求值
print(0 and 1/0)    # 0（不会触发除零错误）
print(1 or 1/0)     # 1（不会触发除零错误）
```

### 4.4 赋值运算符

```python
x = 10
x += 3    # 等价于 x = x + 3，x = 13
x -= 2    # x = 11
x *= 2    # x = 22
x //= 4   # x = 5
x **= 2   # x = 25
x %= 7    # x = 4
```

### 4.5 身份与成员运算符

```python
a = [1, 2, 3]
b = a            # b 和 a 指向同一对象
c = [1, 2, 3]   # c 是内容相同但不同的对象

print(a is b)    # True（同一对象）
print(a is c)    # False（不同对象）
print(a == c)    # True（内容相同）

# in 运算符
print(2 in a)    # True
print(5 in a)    # False
print(5 not in a)  # True
```

---

## 5. 注释规范

```python
# 单行注释：以 # 开头

"""
多行注释（实际上是字符串字面量，不赋值给任何变量）
常用作模块、类、函数的文档字符串（docstring）
"""

# 内联注释（与代码同行，前面空两格）
result = x * 2  # 计算两倍值
```

---

## 小结

```
本章核心概念速查
├── 变量      → 对象的标签，无需声明类型
├── int       → 任意精度整数
├── float     → 双精度浮点，注意精度问题
├── str       → 不可变 Unicode 字符串
├── bool      → True/False，是 int 子类
├── None      → 空值，用 is 比较
├── 动态类型  → 变量类型运行时确定
└── 运算符    → 算术/比较/逻辑/赋值/身份/成员
```
