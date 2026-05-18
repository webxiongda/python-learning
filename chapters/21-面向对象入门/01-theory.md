# 第21章：面向对象入门

## 什么是面向对象编程

面向对象编程（Object-Oriented Programming，OOP）是一种将程序组织为"对象"集合的编程范式。每个对象包含数据（属性）和行为（方法）。

与面向过程编程的对比：

```
面向过程编程：
  数据 ──→ 函数1 ──→ 函数2 ──→ 结果

面向对象编程：
  ┌─────────────┐
  │   对象       │
  │  ┌────────┐ │
  │  │ 属性   │ │   ←── 数据封装在对象内部
  │  └────────┘ │
  │  ┌────────┐ │
  │  │ 方法   │ │   ←── 操作数据的函数
  │  └────────┘ │
  └─────────────┘
```

## class 定义

使用 `class` 关键字定义一个类，类名通常采用大驼峰命名法（PascalCase）：

```python
class Dog:
    """这是一个狗的类"""
    pass  # 空类，什么都不做
```

## __init__ 方法

`__init__` 是类的构造方法，在创建对象时自动调用。它负责初始化对象的属性：

```python
class Dog:
    def __init__(self, name, age):
        self.name = name   # 实例属性
        self.age = age     # 实例属性

# 创建对象（实例化）
my_dog = Dog("旺财", 3)
```

`__init__` 的作用示意：

```
Dog("旺财", 3)
       │
       ▼
  __init__(self, "旺财", 3)
       │
       ▼
  self.name = "旺财"
  self.age  = 3
       │
       ▼
  返回已初始化的对象
```

## self 参数

`self` 是指向当前对象自身的引用。每个实例方法的第一个参数必须是 `self`（名字可以不同，但约定俗成用 `self`）：

```python
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def bark(self):
        # self 让方法知道在操作哪个对象
        print(f"{self.name} 说：汪汪！")

dog1 = Dog("旺财", 3)
dog2 = Dog("小白", 2)

dog1.bark()  # 旺财 说：汪汪！
dog2.bark()  # 小白 说：汪汪！
```

调用链示意：

```
dog1.bark()
    │
    ▼
Dog.bark(dog1)   ← Python自动将dog1作为self传入
    │
    ▼
self.name == "旺财"
```

## 实例属性 vs 类属性

### 实例属性

每个实例独有的属性，通常在 `__init__` 中用 `self.属性名` 定义：

```python
class Dog:
    def __init__(self, name):
        self.name = name  # 实例属性，每只狗各自独立
```

### 类属性

所有实例共享的属性，定义在类体内、方法外：

```python
class Dog:
    species = "犬科"  # 类属性，所有狗共享

    def __init__(self, name):
        self.name = name  # 实例属性

dog1 = Dog("旺财")
dog2 = Dog("小白")

print(dog1.species)  # 犬科
print(dog2.species)  # 犬科
print(Dog.species)   # 犬科（通过类名访问）
```

内存结构对比：

```
类属性：
  Dog类
  ┌────────────┐
  │ species    │  ← 存储在类对象中
  │ = "犬科"  │
  └────────────┘
       ↑   ↑
  dog1 │   │ dog2   ← 两个实例共享同一份

实例属性：
  dog1对象          dog2对象
  ┌──────────┐      ┌──────────┐
  │ name     │      │ name     │
  │ = "旺财" │      │ = "小白" │
  └──────────┘      └──────────┘
  （各自独立的内存空间）
```

### 修改类属性的陷阱

```python
class Counter:
    count = 0  # 类属性

c1 = Counter()
c2 = Counter()

Counter.count = 10  # 通过类修改，影响所有实例
print(c1.count)  # 10
print(c2.count)  # 10

c1.count = 99    # 通过实例"修改"，实际上创建了c1的实例属性
print(c1.count)  # 99（访问实例属性）
print(c2.count)  # 10（仍访问类属性）
print(Counter.count)  # 10（类属性未变）
```

## 实例方法

实例方法是定义在类中，第一个参数为 `self` 的函数：

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        """存款"""
        if amount > 0:
            self.balance += amount
            print(f"{self.owner} 存入 {amount} 元，余额：{self.balance} 元")

    def withdraw(self, amount):
        """取款"""
        if amount > self.balance:
            print("余额不足！")
        else:
            self.balance -= amount
            print(f"{self.owner} 取出 {amount} 元，余额：{self.balance} 元")

    def get_balance(self):
        """查询余额"""
        return self.balance
```

## 属性访问机制（查找顺序）

当访问 `obj.attr` 时，Python 的查找顺序：

```
obj.attr
   │
   ▼
1. 查找 obj.__dict__（实例属性）
   │ 找到 → 返回
   │ 没找到 ↓
   ▼
2. 查找 type(obj).__dict__（类属性）
   │ 找到 → 返回
   │ 没找到 ↓
   ▼
3. 查找父类（继承链）
   │ 找到 → 返回
   │ 没找到 ↓
   ▼
4. 抛出 AttributeError
```

## 对象的内置属性

```python
class Person:
    def __init__(self, name):
        self.name = name

p = Person("张三")

print(p.__dict__)        # {'name': '张三'}  实例的属性字典
print(type(p))           # <class '__main__.Person'>
print(p.__class__)       # <class '__main__.Person'>
print(Person.__name__)   # Person  类名
```

## 总结

| 概念 | 说明 | 示例 |
|------|------|------|
| class | 定义类 | `class Dog:` |
| __init__ | 构造方法，初始化属性 | `def __init__(self, name):` |
| self | 指向当前实例 | `self.name = name` |
| 实例属性 | 每个对象独有 | `self.name` |
| 类属性 | 所有对象共享 | `Dog.species` |
| 实例方法 | 操作对象的函数 | `def bark(self):` |

面向对象编程的三大核心概念——封装、继承、多态——将在后续章节逐步展开。
