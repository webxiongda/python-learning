# 第22章：继承与多态

## 继承的概念

继承是面向对象编程的核心特性之一，允许一个类（子类/派生类）复用另一个类（父类/基类）的属性和方法，并在此基础上进行扩展或修改。

```
继承关系示意：
           Animal（父类/基类）
           ├── name
           ├── age
           └── speak()
                │
        ┌───────┴───────┐
        │               │
      Dog（子类）     Cat（子类）
      ├── breed       ├── color
      └── fetch()     └── purr()
```

## 单继承

```python
class Animal:
    """动物基类"""
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def speak(self):
        print(f"{self.name} 发出声音")
    
    def info(self):
        print(f"名字：{self.name}，年龄：{self.age}岁")


class Dog(Animal):  # Dog 继承自 Animal
    """狗类，继承自 Animal"""
    def __init__(self, name, age, breed):
        super().__init__(name, age)  # 调用父类构造方法
        self.breed = breed           # 子类新增属性
    
    def speak(self):  # 方法重写（Override）
        print(f"{self.name} 说：汪汪！")
    
    def fetch(self):  # 子类新增方法
        print(f"{self.name} 去捡球了！")


dog = Dog("旺财", 3, "柴犬")
dog.info()   # 继承自 Animal
dog.speak()  # Dog 的重写方法
dog.fetch()  # Dog 自己的方法
```

## super() 函数

`super()` 用于调用父类的方法，避免硬编码父类名称：

```python
class Animal:
    def __init__(self, name):
        self.name = name
        print(f"Animal.__init__ 被调用，name={name}")

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)   # 等价于 Animal.__init__(self, name)
        self.breed = breed
        print(f"Dog.__init__ 被调用，breed={breed}")

class GoldenRetriever(Dog):
    def __init__(self, name, color):
        super().__init__(name, "金毛")  # 调用 Dog.__init__
        self.color = color
        print(f"GoldenRetriever.__init__ 被调用，color={color}")

g = GoldenRetriever("贝贝", "金色")
```

输出顺序说明 `super()` 的调用链：
```
Animal.__init__ 被调用，name=贝贝
Dog.__init__ 被调用，breed=金毛
GoldenRetriever.__init__ 被调用，color=金色
```

## 多继承

Python 支持一个类继承多个父类：

```python
class Flyable:
    def fly(self):
        print(f"{self.name} 在飞翔")

class Swimmable:
    def swim(self):
        print(f"{self.name} 在游泳")

class Duck(Animal, Flyable, Swimmable):
    """鸭子：既会飞又会游泳"""
    def speak(self):
        print(f"{self.name} 说：嘎嘎！")

donald = Duck("唐老鸭", 5)
donald.speak()
donald.fly()   # 来自 Flyable
donald.swim()  # 来自 Swimmable
```

多继承结构图：
```
    Animal    Flyable    Swimmable
      │           │           │
      └───────────┴───────────┘
                  │
                Duck
```

## MRO — 方法解析顺序

MRO（Method Resolution Order）决定了多继承时方法的查找顺序。Python 使用 **C3 线性化算法**。

```python
class A:
    def hello(self):
        print("A.hello")

class B(A):
    def hello(self):
        print("B.hello")

class C(A):
    def hello(self):
        print("C.hello")

class D(B, C):
    pass

d = D()
d.hello()  # 打印 "B.hello"

# 查看 MRO
print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)
```

MRO 查找顺序可视化：
```
  D 的 MRO 链：
  D → B → C → A → object

  钻石继承问题：
        A
       / \
      B   C
       \ /
        D

  C3 算法保证：
  1. 子类在父类前面
  2. 多个父类按声明顺序排列
  3. A 只出现一次（最终）
```

C3 线性化计算过程（了解即可）：
```
L[D] = D + merge(L[B], L[C], [B, C])
     = D + merge([B,A,object], [C,A,object], [B,C])
     = D + B + merge([A,object], [C,A,object], [C])
     = D + B + C + merge([A,object], [A,object])
     = D + B + C + A + object
```

## 方法重写（Override）

子类可以重写父类的方法以实现不同的行为：

```python
class Shape:
    def area(self):
        return 0
    
    def describe(self):
        print(f"这是一个形状，面积为 {self.area():.2f}")

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):  # 重写父类方法
        import math
        return math.pi * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):  # 重写父类方法
        return self.width * self.height

# 多态：同一方法名，不同行为
shapes = [Circle(5), Rectangle(4, 6), Shape()]
for shape in shapes:
    shape.describe()  # 每个对象调用自己的 area()
```

## 多态（Polymorphism）

多态的核心：**同一接口，不同实现**。

```
多态示意：
                  speak()
                    │
          ┌─────────┼─────────┐
          │         │         │
        Dog       Cat       Duck
       "汪汪"     "喵喵"    "嘎嘎"

调用方不需要知道具体类型，只需调用 speak()
```

Python 的多态是"鸭子类型"（Duck Typing）：
> "如果它走起来像鸭子，叫起来像鸭子，那它就是鸭子。"

```python
def make_sound(animal):
    """不关心具体类型，只要有 speak 方法就行"""
    animal.speak()

class Robot:
    """不是 Animal 的子类，但有 speak 方法"""
    def speak(self):
        print("我是机器人，哔哔哔！")

# 都可以传入 make_sound，无需继承同一父类
make_sound(Dog("旺财", 3, "柴犬"))
make_sound(Robot())
```

## isinstance 和 issubclass

```python
dog = Dog("旺财", 3, "柴犬")

# isinstance：判断对象是否是某个类（或其子类）的实例
print(isinstance(dog, Dog))     # True
print(isinstance(dog, Animal))  # True（Dog 是 Animal 的子类）
print(isinstance(dog, Cat))     # False

# issubclass：判断类之间的继承关系
print(issubclass(Dog, Animal))  # True
print(issubclass(Animal, Dog))  # False
print(issubclass(Dog, object))  # True（所有类都继承自 object）
```

## 继承体系图示

```
                    object
                      │
                    Animal
                 ┌────┴────┐
               Dog        Cat
            ┌───┴───┐
        Poodle   GoldenRetriever

查找 GoldenRetriever 的 speak()：
  GoldenRetriever → Dog → Animal → object

所有类最终都继承自 object，object 提供了基础方法：
  __str__、__repr__、__eq__、__hash__ 等
```

## 总结

| 概念 | 作用 | 示例 |
|------|------|------|
| 单继承 | 继承一个父类 | `class Dog(Animal):` |
| 多继承 | 继承多个父类 | `class Duck(Animal, Flyable):` |
| super() | 调用父类方法 | `super().__init__(name)` |
| MRO | 多继承查找顺序 | `Dog.__mro__` |
| 方法重写 | 子类覆盖父类方法 | 子类重新定义同名方法 |
| 多态 | 同接口不同实现 | 鸭子类型 |
| isinstance | 检查实例类型 | `isinstance(obj, Class)` |
| issubclass | 检查继承关系 | `issubclass(Sub, Base)` |
