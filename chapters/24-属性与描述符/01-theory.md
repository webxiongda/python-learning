# 第24章：属性与描述符

## @property 装饰器

`@property` 让方法像属性一样访问，是 Python 实现"受控属性"的标准方式。它解决了一个核心问题：**在不改变接口的情况下，为属性访问添加逻辑**。

### 基本用法

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius   # 约定 _ 前缀表示内部属性
    
    @property
    def radius(self):
        """获取半径"""
        return self._radius
    
    @radius.setter
    def radius(self, value):
        """设置半径（带验证）"""
        if value < 0:
            raise ValueError("半径不能为负数")
        self._radius = value
    
    @radius.deleter
    def radius(self):
        """删除半径"""
        del self._radius

c = Circle(5)
print(c.radius)    # 5     ← 像属性一样访问，实际调用 getter
c.radius = 10      # 调用 setter
# c.radius = -1    # 抛出 ValueError
del c.radius       # 调用 deleter
```

### property 的三个装饰器

```
@property          ← 定义 getter（读取）
@属性名.setter     ← 定义 setter（写入）
@属性名.deleter    ← 定义 deleter（删除）
```

工作原理：
```
c.radius          ─→  Circle.radius.fget(c)     (getter)
c.radius = 10     ─→  Circle.radius.fset(c, 10) (setter)
del c.radius      ─→  Circle.radius.fdel(c)     (deleter)
```

### 只读属性

只定义 `@property`，不定义 `@setter`，即为只读属性：

```python
import math

class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        return self._radius
    
    @property
    def area(self):
        """只读的计算属性"""
        return math.pi * self._radius ** 2
    
    @property
    def circumference(self):
        return 2 * math.pi * self._radius

c = Circle(5)
print(c.area)           # 78.53...
# c.area = 100          # AttributeError: can't set attribute
```

### 属性验证示例

```python
class Person:
    def __init__(self, name, age):
        self.name = name   # 触发 setter
        self.age = age     # 触发 setter
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("姓名必须是非空字符串")
        self._name = value.strip()
    
    @property
    def age(self):
        return self._age
    
    @age.setter
    def age(self, value):
        if not isinstance(value, int) or not (0 <= value <= 150):
            raise ValueError("年龄必须是0-150之间的整数")
        self._age = value
```

## 描述符协议

描述符是实现了特定魔术方法（`__get__`、`__set__`、`__delete__`）的对象。`@property` 本质上就是一个描述符。

```
描述符分类：
┌──────────────────────────────────────────┐
│              描述符                       │
│                                          │
│  ┌──────────────────┐  ┌──────────────┐ │
│  │   数据描述符      │  │  非数据描述符 │ │
│  │ __get__ + __set__ │  │  只有__get__ │ │
│  │ 或 __delete__     │  │             │ │
│  └──────────────────┘  └──────────────┘ │
│  优先级高于实例属性      优先级低于实例属性│
└──────────────────────────────────────────┘
```

### 实现描述符

```python
class Validator:
    """通用验证描述符"""
    
    def __set_name__(self, owner, name):
        """当描述符被赋给类属性时调用"""
        self.name = name
        self.storage_name = f"_{name}"  # 存储用的内部属性名
    
    def __get__(self, obj, objtype=None):
        """获取属性值"""
        if obj is None:
            return self  # 通过类访问时返回描述符本身
        return getattr(obj, self.storage_name, None)
    
    def __set__(self, obj, value):
        """设置属性值"""
        self._validate(value)
        setattr(obj, self.storage_name, value)
    
    def __delete__(self, obj):
        """删除属性"""
        delattr(obj, self.storage_name)
    
    def _validate(self, value):
        """子类重写验证逻辑"""
        pass


class IntValidator(Validator):
    def __init__(self, min_val=None, max_val=None):
        self.min_val = min_val
        self.max_val = max_val
    
    def _validate(self, value):
        if not isinstance(value, int):
            raise TypeError(f"{self.name} 必须是整数，得到 {type(value).__name__}")
        if self.min_val is not None and value < self.min_val:
            raise ValueError(f"{self.name} 不能小于 {self.min_val}")
        if self.max_val is not None and value > self.max_val:
            raise ValueError(f"{self.name} 不能大于 {self.max_val}")


class Product:
    price = IntValidator(min_val=0)       # 使用描述符
    quantity = IntValidator(min_val=0, max_val=9999)
    
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price       # 触发 IntValidator.__set__
        self.quantity = quantity
```

### 描述符的查找顺序

```
obj.attr 的查找顺序：

1. type(obj).__mro__ 中查找数据描述符（有__set__的）
   找到 → 调用 descriptor.__get__(obj, type(obj))

2. obj.__dict__ 中查找实例属性
   找到 → 直接返回

3. type(obj).__mro__ 中查找非数据描述符（只有__get__的）
   找到 → 调用 descriptor.__get__(obj, type(obj))

4. 抛出 AttributeError
```

## __slots__

`__slots__` 限制实例只能有指定的属性，节省内存并提高访问速度：

```python
class Point:
    __slots__ = ('x', 'y')  # 只允许 x 和 y 属性
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
print(p.x, p.y)   # 正常
# p.z = 3         # AttributeError
# p.__dict__      # AttributeError（slots 对象无 __dict__）
```

内存对比：

```
普通类实例：
  对象头 + __dict__（字典开销）
  每个实例约 200+ 字节

使用 __slots__ 的实例：
  对象头 + 固定槽位数组
  每个实例约 80-100 字节

100万个实例时，内存差距可达数百MB
```

### __slots__ 的注意事项

```python
# 1. 继承时子类需要重新定义 __slots__
class Point3D(Point):
    __slots__ = ('z',)   # 只需声明新增的属性
    
    def __init__(self, x, y, z):
        super().__init__(x, y)
        self.z = z

# 2. 与 __dict__ 共用（留空 __slots__）
class FlexiblePoint:
    __slots__ = ('x', 'y', '__dict__')  # 保留 __dict__
    def __init__(self, x, y):
        self.x = x
        self.y = y

fp = FlexiblePoint(1, 2)
fp.extra = "额外属性"  # 允许，因为有 __dict__
```

## property vs 描述符的选择

```
应用场景：
                                    
  单个属性需要验证/计算  →  @property（简单直接）
  
  多个类需要相同的验证逻辑  →  描述符（可复用）
  
  大量实例，内存敏感  →  __slots__
  
  框架/ORM/表单验证  →  描述符（如 Django 的 Field）
```

## 总结

| 特性 | 用途 | 优先选择场景 |
|------|------|-------------|
| `@property` | 为单属性添加逻辑 | 单个类的特定属性 |
| `@setter` | 写入时验证/转换 | 需要输入校验 |
| `@deleter` | 删除时清理资源 | 需要清理副作用 |
| 描述符 | 可复用的属性逻辑 | 多类共用相同逻辑 |
| `__slots__` | 内存优化 | 海量小对象 |
