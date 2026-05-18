# 第22章：继承与多态 — 自测题

## 题目1：MRO 顺序判断

给出以下类定义，写出 `D.__mro__` 的顺序：

```python
class A:
    pass

class B(A):
    pass

class C(A):
    pass

class D(B, C):
    pass
```

`D.__mro__` 是什么？调用 `D().method()` 时，如果 `B` 和 `C` 都有 `method`，哪个会被调用？

### 参考答案

```
D.__mro__ = (D, B, C, A, object)
```

**顺序推导（C3线性化）：**
```
L[D] = D + merge(L[B], L[C], [B,C])
     = D + merge([B,A,object], [C,A,object], [B,C])
     = D + B + merge([A,object], [C,A,object], [C])
     = D + B + C + merge([A,object], [A,object])
     = D + B + C + A + object
```

`D` 没有 `method`，会按 MRO 顺序查找，`B` 在 `C` 前面，所以 **`B.method()` 会被调用**。

---

## 题目2：代码输出预测

预测以下代码的输出：

```python
class Base:
    def __init__(self):
        print("Base init")
        self.value = 10
    
    def show(self):
        print(f"Base.show: {self.value}")

class Child(Base):
    def __init__(self):
        super().__init__()
        print("Child init")
        self.value = 20
    
    def show(self):
        super().show()
        print(f"Child.show: {self.value}")

class GrandChild(Child):
    def __init__(self):
        super().__init__()
        print("GrandChild init")
    
    def show(self):
        super().show()
        print(f"GrandChild.show: {self.value}")

gc = GrandChild()
print("---")
gc.show()
```

### 参考答案

```
Base init
Child init
GrandChild init
---
Base.show: 20
Child.show: 20
GrandChild.show: 20
```

**分析：**
1. 构造顺序：`GrandChild.__init__` → `super().__init__()` → `Child.__init__` → `super().__init__()` → `Base.__init__`，然后按栈顺序打印。
2. `self.value` 最终是 20（Child 中赋值）。
3. `gc.show()` 调用 `GrandChild.show`，内部调 `super().show()` → `Child.show`，Child 内再调 `super().show()` → `Base.show`。
4. `Base.show` 中 `self.value` 是 `gc` 的 `value = 20`（self 始终指向 gc）。

---

## 题目3：多继承顺序填空

以下代码涉及多继承，填写执行结果：

```python
class A:
    def greet(self):
        return "Hello from A"

class B(A):
    def greet(self):
        return "Hello from B, " + super().greet()

class C(A):
    def greet(self):
        return "Hello from C, " + super().greet()

class D(B, C):
    def greet(self):
        return "Hello from D, " + super().greet()

d = D()
print(d.greet())
print(D.__mro__)
```

写出 `d.greet()` 的完整返回值。

### 参考答案

```
Hello from D, Hello from B, Hello from C, Hello from A
(<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)
```

**调用链追踪（MRO: D→B→C→A）：**
1. `D.greet()` → `"Hello from D, "` + `super().greet()`（super 指 B）
2. `B.greet()` → `"Hello from B, "` + `super().greet()`（super 指 C，按 MRO）
3. `C.greet()` → `"Hello from C, "` + `super().greet()`（super 指 A）
4. `A.greet()` → `"Hello from A"`

拼接：`"Hello from D, Hello from B, Hello from C, Hello from A"`

---

## 题目4：实现继承体系

设计一个简单的员工继承体系：

1. `Employee` 基类：`name`、`salary` 属性，`get_salary()` 方法返回薪资
2. `Manager(Employee)` 子类：新增 `team_size` 属性，工资 = 底薪 + 500 × 团队人数
3. `Salesperson(Employee)` 子类：新增 `sales_amount` 属性，工资 = 底薪 + 销售额 × 0.05

编写代码，并用多态方式打印所有人员工资。

### 参考答案

```python
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
    
    def get_salary(self):
        return self.salary
    
    def info(self):
        print(f"{self.name}（{self.__class__.__name__}）：¥{self.get_salary():.2f}")


class Manager(Employee):
    def __init__(self, name, salary, team_size):
        super().__init__(name, salary)
        self.team_size = team_size
    
    def get_salary(self):
        return self.salary + 500 * self.team_size


class Salesperson(Employee):
    def __init__(self, name, salary, sales_amount):
        super().__init__(name, salary)
        self.sales_amount = sales_amount
    
    def get_salary(self):
        return self.salary + self.sales_amount * 0.05


# 多态测试
staff = [
    Employee("普通员工", 5000),
    Manager("张经理", 8000, 5),
    Salesperson("李销售", 4000, 100000),
]

for person in staff:
    person.info()
# 普通员工（Employee）：¥5000.00
# 张经理（Manager）：¥10500.00
# 李销售（Salesperson）：¥9000.00
```

---

## 题目5：综合题

以下代码有设计问题，请找出并改进：

```python
class Bird:
    def __init__(self, name):
        self.name = name
    
    def fly(self):
        print(f"{self.name} 在飞翔")
    
    def swim(self):
        print(f"{self.name} 在游泳")
    
    def run(self):
        print(f"{self.name} 在奔跑")

class Eagle(Bird):
    pass  # 鹰：会飞，不会游泳，会跑

class Penguin(Bird):
    def fly(self):
        raise Exception("企鹅不会飞！")  # 重写为异常
```

**问题在哪里？如何使用多继承重构？**

### 参考答案

**问题分析：**
1. `Bird` 包含了所有行为（飞、游、跑），但不是所有鸟都具备所有能力。
2. `Penguin` 继承了 `fly()` 却抛出异常，违反了**里氏替换原则**（子类应能替换父类）。
3. 这是典型的"胖接口"设计问题。

**改进方案（使用 Mixin 多继承）：**

```python
class Bird:
    """鸟的基类，只包含共有特征"""
    def __init__(self, name):
        self.name = name
    
    def breathe(self):
        print(f"{self.name} 呼吸")


class FlyMixin:
    def fly(self):
        print(f"{self.name} 在飞翔")


class SwimMixin:
    def swim(self):
        print(f"{self.name} 在游泳")


class RunMixin:
    def run(self):
        print(f"{self.name} 在奔跑")


# 按能力组合
class Eagle(Bird, FlyMixin, RunMixin):
    """鹰：飞 + 跑"""
    pass

class Penguin(Bird, SwimMixin, RunMixin):
    """企鹅：游 + 跑（不会飞！）"""
    pass

class Duck(Bird, FlyMixin, SwimMixin, RunMixin):
    """鸭子：飞 + 游 + 跑"""
    pass


eagle = Eagle("老鹰")
penguin = Penguin("企鹅")
duck = Duck("鸭子")

eagle.fly()
eagle.run()
# eagle.swim()  # AttributeError，正确！鹰不该有游泳方法

penguin.swim()
penguin.run()
# penguin.fly() 不存在，不会误用

duck.fly()
duck.swim()
duck.run()
```
