# 第21章：面向对象入门 — 自测题

## 题目1：判断题

下列关于类和实例的说法，哪些是正确的？（多选）

A. 类属性可以通过 `类名.属性名` 访问  
B. 实例属性存储在实例的 `__dict__` 中  
C. 修改实例的类属性一定会影响该类的其他实例  
D. `__init__` 方法在每次创建实例时自动被调用  
E. `self` 必须命名为 `self`，不能使用其他名称  

### 参考答案

**正确答案：A、B、D**

- **A 正确**：类属性可以通过 `类名.属性名` 直接访问，也可以通过实例访问。
- **B 正确**：每个实例的属性都保存在其 `__dict__` 字典中。
- **C 错误**：若类属性是不可变对象（如整数、字符串），通过实例赋值会创建实例属性，而不是修改类属性，不会影响其他实例。若类属性是可变对象（如列表），通过实例的引用直接修改（如 `append`）才会影响其他实例。
- **D 正确**：`__init__` 是构造方法，实例化时自动调用。
- **E 错误**：`self` 只是约定俗成的名称，Python 不强制要求，但强烈建议遵循惯例。

---

## 题目2：代码改错

下面的代码有多处错误，请找出并修正：

```python
class Rectangle:
    def init(width, height):
        width = width
        height = height
    
    def area():
        return width * height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

r = Rectangle(5, 3)
print(r.area())
```

### 参考答案

**错误分析与修正：**

```python
class Rectangle:
    # 错误1：构造方法名应为 __init__（双下划线）
    # 错误2：缺少 self 参数
    def __init__(self, width, height):  # 修正：加双下划线，加 self
        # 错误3：缺少 self.，只是局部变量赋值给同名局部变量
        self.width = width    # 修正：加 self.
        self.height = height  # 修正：加 self.
    
    # 错误4：实例方法缺少 self 参数
    def area(self):  # 修正：加 self
        # 错误5：未通过 self 访问实例属性
        return self.width * self.height  # 修正：加 self.
    
    def perimeter(self):
        return 2 * (self.width + self.height)

r = Rectangle(5, 3)
print(r.area())       # 15
print(r.perimeter())  # 16
```

---

## 题目3：填空题

补全以下代码，实现一个 `Circle` 类：

```python
import math

class Circle:
    # 类属性：圆周率
    pi = math.pi
    
    def __init__(self, ______):
        ______ = radius  # 实例属性
    
    def area(self):
        """返回面积"""
        return ______ * self.radius ** 2
    
    def circumference(self):
        """返回周长"""
        return 2 * ______ * ______
    
    def describe(self):
        print(f"半径为{self.radius}的圆，面积={self.area():.2f}，周长={self.circumference():.2f}")

c = Circle(5)
c.describe()
# 输出：半径为5的圆，面积=78.54，周长=31.42
```

### 参考答案

```python
import math

class Circle:
    pi = math.pi
    
    def __init__(self, radius):   # 填空1：参数名 radius
        self.radius = radius      # 填空2：self.radius
    
    def area(self):
        return self.pi * self.radius ** 2     # 填空3：self.pi
    
    def circumference(self):
        return 2 * self.pi * self.radius      # 填空4：self.pi，填空5：self.radius
    
    def describe(self):
        print(f"半径为{self.radius}的圆，面积={self.area():.2f}，周长={self.circumference():.2f}")

c = Circle(5)
c.describe()
```

---

## 题目4：代码阅读题

阅读以下代码，写出程序的输出结果：

```python
class Counter:
    count = 0
    instances = []
    
    def __init__(self, name):
        self.name = name
        Counter.count += 1
        Counter.instances.append(self.name)
    
    def reset(self):
        self.count = 0  # 注意这里
    
    @classmethod
    def total(cls):
        return cls.count

c1 = Counter("A")
c2 = Counter("B")
c3 = Counter("C")

print(Counter.count)
print(Counter.instances)
c1.reset()
print(Counter.count)
print(c1.count)
print(Counter.total())
```

### 参考答案

```
3
['A', 'B', 'C']
3
0
3
```

**分析：**
- 创建3个实例，每次 `Counter.count += 1`，最终类属性 `count = 3`。
- `instances` 是可变列表，三次 `append` 后包含所有名字。
- `c1.reset()` 中 `self.count = 0` 是给 `c1` 创建了一个**实例属性** `count = 0`，类属性 `Counter.count` 仍为 3。
- `c1.count` 优先返回实例属性，所以是 0。
- `Counter.total()` 返回类属性 `cls.count = 3`。

---

## 题目5：综合编程题

设计一个 `温度转换` 类 `Temperature`，要求：

1. 构造方法接受摄氏度值和温度名称（可选，默认"未命名"）
2. 实例方法 `to_fahrenheit()` 返回华氏度（公式：F = C × 9/5 + 32）
3. 实例方法 `to_kelvin()` 返回开尔文（公式：K = C + 273.15）
4. 类属性 `unit = "摄氏度"`
5. 实例方法 `describe()` 打印格式：`{名称}：{摄氏度}°C = {华氏度:.2f}°F = {开尔文:.2f}K`

示例输出：
```
沸点：100°C = 212.00°F = 373.15K
冰点：0°C = 32.00°F = 273.15K
体温：37°C = 98.60°F = 310.15K
```

### 参考答案

```python
class Temperature:
    unit = "摄氏度"
    
    def __init__(self, celsius, name="未命名"):
        self.celsius = celsius
        self.name = name
    
    def to_fahrenheit(self):
        return self.celsius * 9 / 5 + 32
    
    def to_kelvin(self):
        return self.celsius + 273.15
    
    def describe(self):
        f = self.to_fahrenheit()
        k = self.to_kelvin()
        print(f"{self.name}：{self.celsius}°C = {f:.2f}°F = {k:.2f}K")


# 测试
t1 = Temperature(100, "沸点")
t2 = Temperature(0, "冰点")
t3 = Temperature(37, "体温")

t1.describe()
t2.describe()
t3.describe()

# 验证类属性
print(f"\n温度单位：{Temperature.unit}")
```
