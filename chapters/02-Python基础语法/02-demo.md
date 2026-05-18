# 第02章：Python 基础语法 — Demo 篇

## Demo 1：数据类型识别器

```python
# demo1_type_inspector.py
# 目标：直观感受各数据类型的表示和 type() 函数用法

values = [
    42,
    -7,
    3.14,
    2.0,
    "hello",
    '',
    True,
    False,
    None,
]

print(f"{'值':<15} {'类型':<20} {'布尔值'}")
print("-" * 45)
for val in values:
    print(f"{repr(val):<15} {str(type(val)):<20} {bool(val)}")
```

```
# 预期输出：
值               类型                 布尔值
---------------------------------------------
42              <class 'int'>        True
-7              <class 'int'>        True
3.14            <class 'float'>      True
2.0             <class 'float'>      True
'hello'         <class 'str'>        True
''              <class 'str'>        False
True            <class 'bool'>       True
False           <class 'bool'>       False
None            <class 'NoneType'>   False
```

---

## Demo 2：运算符全面演示

```python
# demo2_operators.py
# 目标：掌握 Python 所有常用运算符的行为

a, b = 17, 5

print("=== 算术运算符 ===")
print(f"{a} + {b} = {a + b}")
print(f"{a} - {b} = {a - b}")
print(f"{a} * {b} = {a * b}")
print(f"{a} / {b} = {a / b}   ← 真除法，结果为 float")
print(f"{a} // {b} = {a // b}   ← 整除，向下取整")
print(f"{a} % {b} = {a % b}   ← 取余")
print(f"{a} ** {b} = {a ** b}  ← 幂运算")

print("\n=== 比较运算符 ===")
print(f"3 == 3: {3 == 3}")
print(f"3 != 5: {3 != 5}")
print(f"1 < 5 < 10: {1 < 5 < 10}  ← 链式比较，Python 特有")

print("\n=== 逻辑运算符（短路求值）===")
x = 5
print(f"x > 0 and x < 10: {x > 0 and x < 10}")
print(f"x < 0 or x > 3: {x < 0 or x > 3}")
print(f"not (x == 5): {not (x == 5)}")

print("\n=== 身份运算符 ===")
lst1 = [1, 2]
lst2 = lst1
lst3 = [1, 2]
print(f"lst1 is lst2: {lst1 is lst2}  ← 同一对象")
print(f"lst1 is lst3: {lst1 is lst3}  ← 不同对象")
print(f"lst1 == lst3: {lst1 == lst3}  ← 内容相同")
```

```
# 预期输出：
=== 算术运算符 ===
17 + 5 = 22
17 - 5 = 12
17 * 5 = 85
17 / 5 = 3.4   ← 真除法，结果为 float
17 // 5 = 3   ← 整除，向下取整
17 % 5 = 2   ← 取余
17 ** 5 = 1419857  ← 幂运算

=== 比较运算符 ===
3 == 3: True
3 != 5: True
1 < 5 < 10: True  ← 链式比较，Python 特有

=== 逻辑运算符（短路求值）===
x > 0 and x < 10: True
x < 0 or x > 3: True
not (x == 5): False

=== 身份运算符 ===
lst1 is lst2: True  ← 同一对象
lst1 is lst3: False  ← 不同对象
lst1 == lst3: True  ← 内容相同
```

---

## Demo 3：浮点数精度问题与解决方案

```python
# demo3_float_precision.py
# 目标：理解浮点数精度问题，学习正确的处理方式

import math
from decimal import Decimal

print("=== 浮点数精度问题 ===")
print(f"0.1 + 0.2 = {0.1 + 0.2}")
print(f"0.1 + 0.2 == 0.3: {0.1 + 0.2 == 0.3}")

print("\n=== 解决方案 1：round() 函数 ===")
result = round(0.1 + 0.2, 10)  # 保留10位小数
print(f"round(0.1 + 0.2, 10) = {result}")
print(f"round(0.1 + 0.2, 2) = {round(0.1 + 0.2, 2)}")

print("\n=== 解决方案 2：math.isclose() ===")
print(f"math.isclose(0.1+0.2, 0.3): {math.isclose(0.1 + 0.2, 0.3)}")

print("\n=== 解决方案 3：Decimal 精确计算（财务场景）===")
a = Decimal("0.1")
b = Decimal("0.2")
c = Decimal("0.3")
print(f"Decimal('0.1') + Decimal('0.2') = {a + b}")
print(f"Decimal 结果 == 0.3: {a + b == c}")
```

```
# 预期输出：
=== 浮点数精度问题 ===
0.1 + 0.2 = 0.30000000000000004
0.1 + 0.2 == 0.3: False

=== 解决方案 1：round() 函数 ===
round(0.1 + 0.2, 10) = 0.3
round(0.1 + 0.2, 2) = 0.3

=== 解决方案 2：math.isclose() ===
math.isclose(0.1+0.2, 0.3): True

=== 解决方案 3：Decimal 精确计算（财务场景）===
Decimal('0.1') + Decimal('0.2') = 0.3
Decimal 结果 == 0.3: True
```

---

## Demo 4：类型转换实战

```python
# demo4_type_conversion.py
# 目标：掌握常见类型转换，处理用户输入

# 模拟从用户输入获取的字符串数据
raw_age = "25"
raw_score = "98.5"
raw_flag = "1"

print("=== 字符串转数字 ===")
age = int(raw_age)
score = float(raw_score)
is_active = bool(int(raw_flag))

print(f"年龄：{age}，类型：{type(age).__name__}")
print(f"分数：{score}，类型：{type(score).__name__}")
print(f"是否活跃：{is_active}")

print("\n=== 数字转字符串 ===")
pi = 3.14159
msg = "圆周率约等于 " + str(pi)
print(msg)

print("\n=== 进制转换 ===")
num = 255
print(f"十进制：{num}")
print(f"二进制：{bin(num)}")   # 0b11111111
print(f"八进制：{oct(num)}")   # 0o377
print(f"十六进制：{hex(num)}") # 0xff

print("\n=== 类型转换失败示例 ===")
try:
    int("abc")   # 无法转换非数字字符串
except ValueError as e:
    print(f"转换失败：{e}")
```

```
# 预期输出：
=== 字符串转数字 ===
年龄：25，类型：int
分数：98.5，类型：float
是否活跃：True

=== 数字转字符串 ===
圆周率约等于 3.14159

=== 进制转换 ===
十进制：255
二进制：0b11111111
八进制：0o377
十六进制：0xff

=== 类型转换失败示例 ===
转换失败：invalid literal for int() with base 10: 'abc'
```

---

## Demo 5：变量交换与多重赋值

```python
# demo5_assignment_tricks.py
# 目标：掌握 Python 独特的赋值语法

print("=== 传统方式交换变量（需要临时变量）===")
a = 10
b = 20
temp = a
a = b
b = temp
print(f"交换后：a={a}, b={b}")

print("\n=== Python 优雅方式：元组解包 ===")
x = 100
y = 200
x, y = y, x   # 右边先打包成元组 (200, 100)，再解包赋值
print(f"交换后：x={x}, y={y}")

print("\n=== 多重赋值 ===")
m = n = p = 0
print(f"m={m}, n={n}, p={p}")

a, b, c = 1, 2, 3
print(f"a={a}, b={b}, c={c}")

first, *rest = [1, 2, 3, 4, 5]
print(f"first={first}, rest={rest}")

*head, last = [1, 2, 3, 4, 5]
print(f"head={head}, last={last}")

print("\n=== 增强赋值运算符 ===")
score = 100
score += 10   # 答题加分
print(f"加分后：{score}")
score *= 1.1  # 奖励系数
print(f"奖励后：{score}")
```

```
# 预期输出：
=== 传统方式交换变量（需要临时变量）===
交换后：a=20, b=10

=== Python 优雅方式：元组解包 ===
交换后：x=200, y=100

=== 多重赋值 ===
m=0, n=0, p=0
a=1, b=2, c=3
first=1, rest=[2, 3, 4, 5]
head=[1, 2, 3, 4], last=5

=== 增强赋值运算符 ===
加分后：110
奖励后：121.00000000000001
```
