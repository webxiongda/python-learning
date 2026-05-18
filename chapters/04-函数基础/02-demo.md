# 第04章：函数基础 — Demo 篇

## Demo 1：参数类型全面演示

```python
# demo1_params.py
# 目标：对比位置参数、默认参数、关键字参数的用法

def order_coffee(size, coffee_type, milk="全脂奶", sugar=0, extra=None):
    """模拟咖啡订单"""
    order = f"{size} {coffee_type}"
    order += f" + {milk}"
    if sugar > 0:
        order += f" + {sugar}块糖"
    if extra:
        order += f" + {extra}"
    return order

print("=== 只传必填参数（使用默认值）===")
print(order_coffee("大杯", "拿铁"))

print("\n=== 覆盖默认参数 ===")
print(order_coffee("中杯", "美式", milk="燕麦奶", sugar=2))

print("\n=== 关键字参数（顺序无关）===")
print(order_coffee(coffee_type="卡布奇诺", size="小杯", extra="肉桂粉"))

print("\n=== 混合使用 ===")
print(order_coffee("大杯", "抹茶拿铁", sugar=1, extra="珍珠"))
```

```
# 预期输出：
=== 只传必填参数（使用默认值）===
大杯 拿铁 + 全脂奶

=== 覆盖默认参数 ===
中杯 美式 + 燕麦奶 + 2块糖

=== 关键字参数（顺序无关）===
小杯 卡布奇诺 + 全脂奶 + 肉桂粉

=== 混合使用 ===
大杯 抹茶拿铁 + 全脂奶 + 1块糖 + 珍珠
```

---

## Demo 2：*args 和 **kwargs 实战

```python
# demo2_args_kwargs.py
# 目标：理解可变参数的打包与解包

def stats(*numbers):
    """计算任意数量数字的统计信息"""
    if not numbers:
        return "没有输入任何数字"
    n = len(numbers)
    total = sum(numbers)
    return {
        "数量": n,
        "总和": total,
        "平均值": round(total / n, 2),
        "最大值": max(numbers),
        "最小值": min(numbers),
    }

print("=== *args：任意数量位置参数 ===")
result = stats(10, 25, 7, 42, 3, 18)
for k, v in result.items():
    print(f"  {k}: {v}")

print("\n=== **kwargs：任意数量关键字参数 ===")
def build_html_tag(tag, content, **attrs):
    """动态构建 HTML 标签"""
    attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
    if attr_str:
        return f"<{tag} {attr_str}>{content}</{tag}>"
    return f"<{tag}>{content}</{tag}>"

print(build_html_tag("p", "Hello World"))
print(build_html_tag("a", "点击这里", href="https://python.org", target="_blank"))
print(build_html_tag("img", "", src="photo.jpg", alt="照片", width="200"))

print("\n=== 解包运算符 * 和 ** ===")
def add(a, b, c):
    return a + b + c

nums = [1, 2, 3]
print(add(*nums))      # 列表解包为位置参数

params = {"a": 10, "b": 20, "c": 30}
print(add(**params))   # 字典解包为关键字参数
```

```
# 预期输出：
=== *args：任意数量位置参数 ===
  数量: 6
  总和: 105
  平均值: 17.5
  最大值: 42
  最小值: 3

=== **kwargs：任意数量关键字参数 ===
<p>Hello World</p>
<a href="https://python.org" target="_blank">点击这里</a>
<img src="photo.jpg" alt="照片" width="200"></img>

=== 解包运算符 * 和 ** ===
6
60
```

---

## Demo 3：作用域（LEGB）可视化

```python
# demo3_scope.py
# 目标：通过具体例子理解 LEGB 作用域规则

# G - 全局作用域
global_var = "我是全局变量"

def outer_func():
    # E - Enclosing 作用域
    enclosing_var = "我是外层函数变量"
    
    def inner_func():
        # L - 本地作用域
        local_var = "我是内层函数变量"
        
        print(f"L (本地): {local_var}")
        print(f"E (外层): {enclosing_var}")
        print(f"G (全局): {global_var}")
        print(f"B (内置): {len('Python')}")  # len 是内置函数
    
    inner_func()
    # 这里访问不到 local_var
    print(f"\n外层函数中 enclosing_var: {enclosing_var}")

outer_func()
print(f"\n全局作用域中 global_var: {global_var}")

print("\n=== global 关键字演示 ===")
counter = 0

def increment_global():
    global counter
    counter += 1
    print(f"  函数内 counter = {counter}")

increment_global()
increment_global()
print(f"全局 counter = {counter}")

print("\n=== nonlocal 关键字演示（计数器工厂）===")
def make_counter(start=0):
    count = start
    
    def increment(step=1):
        nonlocal count
        count += step
        return count
    
    return increment

counter1 = make_counter(0)
counter2 = make_counter(100)

print(f"counter1: {counter1()}, {counter1()}, {counter1(5)}")
print(f"counter2: {counter2()}, {counter2(10)}")
print(f"counter1 现在: {counter1()}")  # counter1 和 counter2 独立
```

```
# 预期输出：
L (本地): 我是内层函数变量
E (外层): 我是外层函数变量
G (全局): 我是全局变量
B (内置): 6

外层函数中 enclosing_var: 我是外层函数变量

全局作用域中 global_var: 我是全局变量

=== global 关键字演示 ===
  函数内 counter = 1
  函数内 counter = 2
全局 counter = 2

=== nonlocal 关键字演示（计数器工厂）===
counter1: 1, 2, 7
counter2: 101, 111
counter1 现在: 8
```

---

## Demo 4：函数作为一等对象

```python
# demo4_first_class.py
# 目标：函数可以作为参数传递、存入变量、从函数返回

def apply_twice(func, value):
    """将函数应用两次"""
    return func(func(value))

def double(x):
    return x * 2

def add_exclamation(s):
    return s + "!"

print("=== 函数作为参数 ===")
print(apply_twice(double, 3))              # 12（3→6→12）
print(apply_twice(add_exclamation, "hi"))  # hi!!

print("\n=== 函数存入列表（管道处理）===")
def strip_spaces(s):    return s.strip()
def to_upper(s):        return s.upper()
def add_greeting(s):    return "你好，" + s

pipeline = [strip_spaces, to_upper, add_greeting]
text = "  alice  "

for step in pipeline:
    text = step(text)
    print(f"  → {repr(text)}")

print(f"\n最终结果：{text}")

print("\n=== map() 和 filter() 内置函数 ===")
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# map：对每个元素应用函数
squared = list(map(lambda x: x**2, numbers))
print(f"平方：{squared}")

# filter：保留满足条件的元素
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(f"偶数：{evens}")
```

```
# 预期输出：
=== 函数作为参数 ===
12
hi!!

=== 函数存入列表（管道处理）===
  → '  alice  '
  → 'ALICE'
  → '你好，ALICE'

最终结果：你好，ALICE

=== map() 和 filter() 内置函数 ===
平方：[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
偶数：[2, 4, 6, 8, 10]
```

---

## Demo 5：带完整 docstring 的实用函数库

```python
# demo5_utils.py
# 目标：编写规范的实用函数，含 docstring 和类型提示

def celsius_to_fahrenheit(celsius: float) -> float:
    """将摄氏度转换为华氏度。

    公式：F = C × 9/5 + 32

    参数：
        celsius: 摄氏度温度值

    返回：
        对应的华氏度值，保留2位小数
    
    示例：
        >>> celsius_to_fahrenheit(100)
        212.0
        >>> celsius_to_fahrenheit(0)
        32.0
    """
    return round(celsius * 9 / 5 + 32, 2)


def is_palindrome(text: str) -> bool:
    """判断字符串是否为回文（忽略大小写和空格）。

    参数：
        text: 要检测的字符串

    返回：
        如果是回文返回 True，否则返回 False

    示例：
        >>> is_palindrome("racecar")
        True
        >>> is_palindrome("A man a plan a canal Panama")
        True
    """
    cleaned = text.lower().replace(" ", "")
    return cleaned == cleaned[::-1]


def clamp(value: float, min_val: float, max_val: float) -> float:
    """将值限制在指定范围内。

    参数：
        value: 输入值
        min_val: 范围最小值
        max_val: 范围最大值

    返回：
        如果 value 在范围内返回 value；
        如果小于 min_val 返回 min_val；
        如果大于 max_val 返回 max_val。
    """
    return max(min_val, min(max_val, value))


# 测试所有函数
print("=== 温度转换 ===")
for temp in [0, 20, 37, 100]:
    print(f"  {temp}°C = {celsius_to_fahrenheit(temp)}°F")

print("\n=== 回文检测 ===")
words = ["racecar", "hello", "A man a plan a canal Panama", "上海自来水来自海上"]
for w in words:
    print(f"  '{w}': {is_palindrome(w)}")

print("\n=== 值限制 ===")
for v in [-10, 0, 50, 100, 150]:
    print(f"  clamp({v}, 0, 100) = {clamp(v, 0, 100)}")
```

```
# 预期输出：
=== 温度转换 ===
  0°C = 32.0°F
  20°C = 68.0°F
  37°C = 98.6°F
  100°C = 212.0°F

=== 回文检测 ===
  'racecar': True
  'hello': False
  'A man a plan a canal Panama': True
  '上海自来水来自海上': True

=== 值限制 ===
  clamp(-10, 0, 100) = 0
  clamp(0, 0, 100) = 0
  clamp(50, 0, 100) = 50
  clamp(100, 0, 100) = 100
  clamp(150, 0, 100) = 100
```
