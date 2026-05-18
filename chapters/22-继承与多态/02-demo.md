# 第22章：继承与多态 — Demo 演示

## Demo 1：单继承与 super()

```python
# demo1_single_inheritance.py

class Vehicle:
    """交通工具基类"""
    
    def __init__(self, brand, speed):
        self.brand = brand
        self.speed = speed
        self.is_running = False
    
    def start(self):
        self.is_running = True
        print(f"{self.brand} 启动了！最高速度 {self.speed} km/h")
    
    def stop(self):
        self.is_running = False
        print(f"{self.brand} 停止了")
    
    def status(self):
        state = "行驶中" if self.is_running else "停止"
        print(f"{self.brand}：{state}")


class Car(Vehicle):
    """汽车，继承 Vehicle"""
    
    def __init__(self, brand, speed, doors):
        super().__init__(brand, speed)  # 调用父类构造
        self.doors = doors
    
    def honk(self):
        print(f"{self.brand} 鸣笛：嘀嘀！")


class ElectricCar(Car):
    """电动汽车，继承 Car"""
    
    def __init__(self, brand, speed, doors, battery):
        super().__init__(brand, speed, doors)  # 调用 Car 构造
        self.battery = battery  # 电池容量(kWh)
        self.charge_level = 100  # 电量百分比
    
    def start(self):
        if self.charge_level == 0:
            print(f"{self.brand} 没电了，无法启动！")
            return
        super().start()  # 调用父类 start
        print(f"  当前电量：{self.charge_level}%，续航约 {self.battery * self.charge_level // 100 * 5} km")
    
    def charge(self, hours):
        added = min(hours * 20, 100 - self.charge_level)
        self.charge_level += added
        print(f"{self.brand} 充电 {hours} 小时，电量：{self.charge_level}%")


# 使用继承链
tesla = ElectricCar("Tesla Model 3", 250, 4, 75)
byd = ElectricCar("BYD 海豹", 240, 4, 82)

tesla.start()
tesla.honk()       # 继承自 Car
tesla.status()     # 继承自 Vehicle
print()

tesla.charge_level = 0
tesla.start()      # 没电无法启动
tesla.charge(3)
tesla.start()
```

```
# 预期输出：
Tesla Model 3 启动了！最高速度 250 km/h
  当前电量：100%，续航约 375 km
Tesla Model 3 鸣笛：嘀嘀！
Tesla Model 3：行驶中

Tesla Model 3 没电了，无法启动！
Tesla Model 3 充电 3 小时，电量：60%
Tesla Model 3 启动了！最高速度 250 km/h
  当前电量：60%，续航约 225 km
```

---

## Demo 2：多继承与 MRO

```python
# demo2_multiple_inheritance_mro.py

class Logger:
    """日志混入类"""
    
    def log(self, message):
        print(f"[LOG] {message}")


class Serializable:
    """序列化混入类"""
    
    def to_dict(self):
        return self.__dict__.copy()
    
    def from_dict(self, data):
        for key, value in data.items():
            setattr(self, key, value)


class Validatable:
    """验证混入类"""
    
    def validate(self):
        """子类应重写此方法"""
        return True


class User(Logger, Serializable, Validatable):
    """用户类，使用多个混入"""
    
    def __init__(self, username, email, age):
        self.username = username
        self.email = email
        self.age = age
    
    def validate(self):
        """重写验证方法"""
        if not self.username:
            return False
        if "@" not in self.email:
            return False
        if not (0 < self.age < 150):
            return False
        return True
    
    def save(self):
        if self.validate():
            data = self.to_dict()
            self.log(f"用户 {self.username} 数据保存成功：{data}")
        else:
            self.log(f"用户数据验证失败")


# 查看 MRO
print("User 的 MRO：")
for i, cls in enumerate(User.__mro__):
    print(f"  {i+1}. {cls.__name__}")

print()

# 使用多继承功能
u1 = User("张三", "zhangsan@example.com", 25)
u1.save()

u2 = User("", "invalid-email", 200)
u2.save()

# 序列化功能
data = u1.to_dict()
print(f"\n序列化结果：{data}")
```

```
# 预期输出：
User 的 MRO：
  1. User
  2. Logger
  3. Serializable
  4. Validatable
  5. object

[LOG] 用户 张三 数据保存成功：{'username': '张三', 'email': 'zhangsan@example.com', 'age': 25}
[LOG] 用户数据验证失败

序列化结果：{'username': '张三', 'email': 'zhangsan@example.com', 'age': 25}
```

---

## Demo 3：多态实战——图形面积计算器

```python
# demo3_polymorphism.py
import math

class Shape:
    """图形基类"""
    
    def area(self):
        raise NotImplementedError("子类必须实现 area() 方法")
    
    def perimeter(self):
        raise NotImplementedError("子类必须实现 perimeter() 方法")
    
    def describe(self):
        print(f"{self.__class__.__name__}: 面积={self.area():.4f}, 周长={self.perimeter():.4f}")


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return math.pi * self.radius ** 2
    
    def perimeter(self):
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)


class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c
    
    def area(self):
        # 海伦公式
        s = (self.a + self.b + self.c) / 2
        return math.sqrt(s * (s-self.a) * (s-self.b) * (s-self.c))
    
    def perimeter(self):
        return self.a + self.b + self.c


# 多态：统一处理不同形状
def total_area(shapes):
    """计算所有形状的总面积"""
    return sum(s.area() for s in shapes)

def largest_shape(shapes):
    """找出面积最大的形状"""
    return max(shapes, key=lambda s: s.area())


shapes = [
    Circle(5),
    Rectangle(4, 6),
    Triangle(3, 4, 5),
    Circle(3),
    Rectangle(10, 2),
]

print("=== 所有形状 ===")
for shape in shapes:
    shape.describe()

print(f"\n总面积：{total_area(shapes):.4f}")
biggest = largest_shape(shapes)
print(f"最大形状：{biggest.__class__.__name__}，面积：{biggest.area():.4f}")

# isinstance 检查
print("\n=== 类型检查 ===")
for shape in shapes:
    if isinstance(shape, Circle):
        print(f"圆形：半径={shape.radius}")
    elif isinstance(shape, Rectangle):
        print(f"矩形：{shape.width}×{shape.height}")
    elif isinstance(shape, Triangle):
        print(f"三角形：{shape.a},{shape.b},{shape.c}")
```

```
# 预期输出：
=== 所有形状 ===
Circle: 面积=78.5398, 周长=31.4159
Rectangle: 面积=24.0000, 周长=20.0000
Triangle: 面积=6.0000, 周长=12.0000
Circle: 面积=28.2743, 周长=18.8496
Rectangle: 面积=20.0000, 周长=24.0000

总面积：156.8141
最大形状：Circle，面积：78.5398

=== 类型检查 ===
圆形：半径=5
矩形：4×6
三角形：3,4,5
圆形：半径=3
矩形：10×2
```

---

## Demo 4：issubclass 和 isinstance 深入

```python
# demo4_isinstance_issubclass.py

class Animal:
    pass

class Mammal(Animal):
    pass

class Dog(Mammal):
    pass

class Cat(Mammal):
    pass

class Robot:  # 不属于 Animal 体系
    pass


dog = Dog()
cat = Cat()
robot = Robot()

print("=== isinstance 测试 ===")
print(f"isinstance(dog, Dog)    = {isinstance(dog, Dog)}")      # True
print(f"isinstance(dog, Mammal) = {isinstance(dog, Mammal)}")   # True
print(f"isinstance(dog, Animal) = {isinstance(dog, Animal)}")   # True
print(f"isinstance(dog, Cat)    = {isinstance(dog, Cat)}")      # False
print(f"isinstance(dog, object) = {isinstance(dog, object)}")   # True（万物皆对象）

# isinstance 接受元组
print(f"\nisinstance(dog, (Cat, Dog)) = {isinstance(dog, (Cat, Dog))}")  # True

print("\n=== issubclass 测试 ===")
print(f"issubclass(Dog, Mammal)   = {issubclass(Dog, Mammal)}")    # True
print(f"issubclass(Dog, Animal)   = {issubclass(Dog, Animal)}")    # True
print(f"issubclass(Mammal, Dog)   = {issubclass(Mammal, Dog)}")    # False
print(f"issubclass(Dog, object)   = {issubclass(Dog, object)}")    # True
print(f"issubclass(Robot, Animal) = {issubclass(Robot, Animal)}")  # False

print("\n=== 实际应用：安全类型处理 ===")
animals = [Dog(), Cat(), Robot(), Mammal()]

for obj in animals:
    if isinstance(obj, Dog):
        print(f"这是一只狗")
    elif isinstance(obj, Cat):
        print(f"这是一只猫")
    elif isinstance(obj, Mammal):
        print(f"这是一种哺乳动物（非狗非猫）")
    else:
        print(f"这不是动物：{type(obj).__name__}")
```

```
# 预期输出：
=== isinstance 测试 ===
isinstance(dog, Dog)    = True
isinstance(dog, Mammal) = True
isinstance(dog, Animal) = True
isinstance(dog, Cat)    = False
isinstance(dog, object) = True

isinstance(dog, (Cat, Dog)) = True

=== issubclass 测试 ===
issubclass(Dog, Mammal)   = True
issubclass(Dog, Animal)   = True
issubclass(Mammal, Dog)   = False
issubclass(Dog, object)   = True
issubclass(Robot, Animal) = False

=== 实际应用：安全类型处理 ===
这是一只狗
这是一只猫
这不是动物：Robot
这是一种哺乳动物（非狗非猫）
```
