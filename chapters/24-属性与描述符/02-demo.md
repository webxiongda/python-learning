# 第24章：属性与描述符 — Demo 演示

## Demo 1：@property 基础用法

```python
# demo1_property_basic.py

class Temperature:
    """温度类，摄氏度存储，支持多单位读取"""
    
    def __init__(self, celsius=0):
        self.celsius = celsius  # 触发 setter
    
    @property
    def celsius(self):
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError(f"温度不能低于绝对零度（-273.15°C），得到 {value}")
        self._celsius = float(value)
    
    @property
    def fahrenheit(self):
        """只读：华氏度"""
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        """通过华氏度设置温度"""
        self.celsius = (value - 32) * 5/9
    
    @property
    def kelvin(self):
        """只读：开尔文"""
        return self._celsius + 273.15
    
    def __str__(self):
        return f"{self._celsius:.1f}°C / {self.fahrenheit:.1f}°F / {self.kelvin:.2f}K"


# 正常使用
t = Temperature(100)
print(t)                      # 100.0°C / 212.0°F / 373.15K

t.celsius = 0
print(t)                      # 0.0°C / 32.0°F / 273.15K

# 通过华氏度设置
t.fahrenheit = 98.6
print(f"体温：{t}")            # 体温：37.0°C / 98.6°F / 310.15K

# 验证：绝对零度
try:
    t.celsius = -300
except ValueError as e:
    print(f"错误：{e}")

# 只读属性
try:
    t.kelvin = 300
except AttributeError as e:
    print(f"只读属性：{e}")

print(f"\n当前温度：{t.celsius:.1f}°C")
```

```
# 预期输出：
100.0°C / 212.0°F / 373.15K
0.0°C / 32.0°F / 273.15K
体温：37.0°C / 98.6°F / 310.15K
错误：温度不能低于绝对零度（-273.15°C），得到 -300
只读属性：can't set attribute 'kelvin'

当前温度：37.0°C
```

---

## Demo 2：property 用于数据验证

```python
# demo2_property_validation.py

class UserProfile:
    """用户信息类，所有属性均有验证"""
    
    def __init__(self, username, email, age, bio=""):
        self.username = username
        self.email = email
        self.age = age
        self.bio = bio
    
    @property
    def username(self):
        return self._username
    
    @username.setter
    def username(self, value):
        if not isinstance(value, str):
            raise TypeError("用户名必须是字符串")
        value = value.strip()
        if len(value) < 3:
            raise ValueError("用户名至少3个字符")
        if len(value) > 20:
            raise ValueError("用户名最多20个字符")
        if not value.replace("_", "").isalnum():
            raise ValueError("用户名只能包含字母、数字和下划线")
        self._username = value
    
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, value):
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError(f"无效邮箱地址：{value}")
        self._email = value.lower()
    
    @property
    def age(self):
        return self._age
    
    @age.setter
    def age(self, value):
        if not isinstance(value, int) or not (1 <= value <= 150):
            raise ValueError(f"年龄必须在1-150之间，得到：{value}")
        self._age = value
    
    @property
    def bio(self):
        return self._bio
    
    @bio.setter
    def bio(self, value):
        if len(value) > 200:
            raise ValueError("简介不能超过200字符")
        self._bio = value
    
    @property
    def display_name(self):
        """只读：显示名（截取邮箱前缀作为默认）"""
        return self._username or self._email.split("@")[0]
    
    def __repr__(self):
        return f"UserProfile({self._username!r}, {self._email!r}, age={self._age})"


# 正常创建
u = UserProfile("zhang_san", "zhangsan@example.com", 25, "Python爱好者")
print(u)
print(f"显示名：{u.display_name}")

# 测试各种验证
test_cases = [
    ("用户名太短", lambda: setattr(u, "username", "ab")),
    ("用户名含特殊字符", lambda: setattr(u, "username", "zhang@san")),
    ("邮箱格式错误", lambda: setattr(u, "email", "not-an-email")),
    ("年龄无效", lambda: setattr(u, "age", -5)),
    ("年龄非整数", lambda: setattr(u, "age", "二十五")),
]

print("\n验证测试：")
for desc, test in test_cases:
    try:
        test()
        print(f"  {desc}：未触发错误（异常！）")
    except (ValueError, TypeError) as e:
        print(f"  {desc}：正确拦截 → {e}")

# 合法修改
u.age = 26
u.bio = "热爱编程的程序员"
print(f"\n更新后：{u}")
```

```
# 预期输出：
UserProfile('zhang_san', 'zhangsan@example.com', age=25)
显示名：zhang_san

验证测试：
  用户名太短：正确拦截 → 用户名至少3个字符
  用户名含特殊字符：正确拦截 → 用户名只能包含字母、数字和下划线
  邮箱格式错误：正确拦截 → 无效邮箱地址：not-an-email
  年龄无效：正确拦截 → 年龄必须在1-150之间，得到：-5
  年龄非整数：正确拦截 → 年龄必须在1-150之间，得到：二十五

更新后：UserProfile('zhang_san', 'zhangsan@example.com', age=26)
```

---

## Demo 3：描述符协议实战

```python
# demo3_descriptor.py

class TypedField:
    """类型检查描述符"""
    
    def __init__(self, expected_type, min_val=None, max_val=None):
        self.expected_type = expected_type
        self.min_val = min_val
        self.max_val = max_val
    
    def __set_name__(self, owner, name):
        self.name = name
        self.storage = f"_{name}"
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.storage, None)
    
    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} 期望类型 {self.expected_type.__name__}，"
                f"得到 {type(value).__name__}"
            )
        if self.min_val is not None and value < self.min_val:
            raise ValueError(f"{self.name} 不能小于 {self.min_val}")
        if self.max_val is not None and value > self.max_val:
            raise ValueError(f"{self.name} 不能大于 {self.max_val}")
        setattr(obj, self.storage, value)


class StringField(TypedField):
    """字符串描述符，含长度验证"""
    
    def __init__(self, min_len=0, max_len=None):
        super().__init__(str)
        self.min_len = min_len
        self.max_len = max_len
    
    def __set__(self, obj, value):
        super().__set__(obj, value)  # 先做类型检查
        if len(value) < self.min_len:
            raise ValueError(f"{self.name} 长度不能小于 {self.min_len}")
        if self.max_len and len(value) > self.max_len:
            raise ValueError(f"{self.name} 长度不能超过 {self.max_len}")
        setattr(obj, self.storage, value)


# 使用描述符定义模型类
class Employee:
    name = StringField(min_len=2, max_len=50)
    age = TypedField(int, min_val=18, max_val=65)
    salary = TypedField(float, min_val=0)
    
    def __init__(self, name, age, salary):
        self.name = name
        self.age = age
        self.salary = salary
    
    def __repr__(self):
        return f"Employee({self.name!r}, age={self.age}, salary={self.salary})"


class Student:
    """复用相同描述符"""
    name = StringField(min_len=2, max_len=50)
    age = TypedField(int, min_val=6, max_val=30)
    gpa = TypedField(float, min_val=0.0, max_val=4.0)
    
    def __init__(self, name, age, gpa):
        self.name = name
        self.age = age
        self.gpa = gpa
    
    def __repr__(self):
        return f"Student({self.name!r}, age={self.age}, gpa={self.gpa})"


# 测试 Employee
print("=== Employee ===")
e = Employee("张三", 30, 8500.0)
print(e)

try:
    Employee("李", 30, 8500.0)  # 名字太短
except ValueError as e:
    print(f"名字验证：{e}")

try:
    Employee("王五", 17, 5000.0)  # 年龄太小
except ValueError as e:
    print(f"年龄验证：{e}")

# 测试 Student
print("\n=== Student ===")
s = Student("李小红", 20, 3.8)
print(s)

try:
    Student("王明", 25, 4.5)  # GPA超出范围
except ValueError as e:
    print(f"GPA验证：{e}")

# 通过类访问描述符本身
print(f"\n通过类访问：{Employee.name}")
print(f"描述符类型：{type(Employee.name).__name__}")
```

```
# 预期输出：
=== Employee ===
Employee('张三', age=30, salary=8500.0)
名字验证：name 长度不能小于 2
年龄验证：age 不能小于 18

=== Student ===
Student('李小红', age=20, gpa=3.8)
GPA验证：gpa 不能大于 4.0

通过类访问：<__main__.StringField object at 0x...>
描述符类型：StringField
```

---

## Demo 4：__slots__ 内存优化

```python
# demo4_slots.py
import sys

class PointNormal:
    """普通类（有__dict__）"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

class PointSlots:
    """使用 __slots__ 的类"""
    __slots__ = ('x', 'y')
    
    def __init__(self, x, y):
        self.x = x
        self.y = y


# 单个对象内存比较
p_normal = PointNormal(1, 2)
p_slots = PointSlots(1, 2)

print("=== 单个对象 ===")
print(f"普通对象大小：{sys.getsizeof(p_normal)} 字节")
print(f"Slots对象大小：{sys.getsizeof(p_slots)} 字节")

# 普通对象有 __dict__
print(f"\n普通对象 __dict__：{p_normal.__dict__}")
try:
    print(p_slots.__dict__)
except AttributeError:
    print("Slots对象没有 __dict__")

# 动态添加属性
p_normal.z = 3   # 允许
print(f"普通对象可动态添加属性：p_normal.z = {p_normal.z}")

try:
    p_slots.z = 3
except AttributeError as e:
    print(f"Slots对象不允许动态添加：{e}")

# 大规模对象内存对比
print("\n=== 大规模内存测试（10万个对象）===")
import tracemalloc

tracemalloc.start()
normal_list = [PointNormal(i, i) for i in range(100_000)]
current, peak = tracemalloc.get_traced_memory()
print(f"普通类：当前内存 {current/1024:.1f} KB，峰值 {peak/1024:.1f} KB")
tracemalloc.reset_peak()

del normal_list
slots_list = [PointSlots(i, i) for i in range(100_000)]
current, peak = tracemalloc.get_traced_memory()
print(f"Slots类：当前内存 {current/1024:.1f} KB，峰值 {peak/1024:.1f} KB")
tracemalloc.stop()
```

```
# 预期输出（实际数值可能因Python版本略有差异）：
=== 单个对象 ===
普通对象大小：48 字节
Slots对象大小：56 字节

普通对象 __dict__：{'x': 1, 'y': 2}
Slots对象没有 __dict__

普通对象可动态添加属性：p_normal.z = 3
Slots对象不允许动态添加：'PointSlots' object has no attribute 'z'

=== 大规模内存测试（10万个对象）===
普通类：当前内存 8400.0 KB，峰值 8400.0 KB
Slots类：当前内存 3200.0 KB，峰值 3200.0 KB
```
