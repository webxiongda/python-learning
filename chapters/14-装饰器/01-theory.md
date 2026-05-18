# 第14章：装饰器

## 学习目标
- 理解装饰器的本质与工作原理
- 掌握带参数的装饰器写法
- 学会使用 functools.wraps 保留元信息
- 理解类装饰器与叠加装饰器

---

## 1. 装饰器的本质

装饰器本质上是一个**接收函数、返回函数的函数**，它在不修改原函数代码的情况下，为函数添加额外功能。

### 1.1 手动装饰（理解原理）

```python
# 假设我们有一个函数
def 打招呼():
    print("你好！")

# 我们想在调用前后添加日志
def 添加日志(func):
    def 包装器():
        print(f"调用 {func.__name__} 之前")
        func()
        print(f"调用 {func.__name__} 之后")
    return 包装器

# 手动装饰
打招呼 = 添加日志(打招呼)
打招呼()
```

### 1.2 @ 语法糖

`@装饰器` 就是 `函数 = 装饰器(函数)` 的简写：

```
@decorator
def func():
    ...

等价于：

def func():
    ...
func = decorator(func)
```

```python
def 添加日志(func):
    def 包装器(*args, **kwargs):
        print(f"调用 {func.__name__}")
        结果 = func(*args, **kwargs)
        print(f"{func.__name__} 返回: {结果}")
        return 结果
    return 包装器

@添加日志  # 相当于：add = 添加日志(add)
def add(a, b):
    return a + b

add(3, 4)
```

---

## 2. 装饰器的执行流程

```
┌─────────────────────────────────────────────────────┐
│                装饰器执行时序图                       │
│                                                     │
│  定义阶段（import 时）：                             │
│  ┌──────────────────────────────────────────────┐   │
│  │  @decorator                                  │   │
│  │  def func():  →  func = decorator(func)      │   │
│  │                   └── 返回 wrapper           │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  调用阶段（运行时）：                                │
│  ┌──────────────────────────────────────────────┐   │
│  │  func(args)  →  wrapper(args)                │   │
│  │                  ├── 前置逻辑                │   │
│  │                  ├── 原始 func(args)          │   │
│  │                  └── 后置逻辑                │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## 3. functools.wraps

不使用 `wraps` 时，被装饰函数的元信息（`__name__`、`__doc__`）会丢失：

```python
from functools import wraps

# ❌ 不使用 wraps
def 装饰器_v1(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@装饰器_v1
def 我的函数():
    """这是文档字符串"""
    pass

print(我的函数.__name__)  # 'wrapper'  ← 错误！
print(我的函数.__doc__)   # None       ← 文档丢失！

# ✅ 使用 wraps
def 装饰器_v2(func):
    @wraps(func)  # 保留原函数的元信息
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@装饰器_v2
def 我的函数():
    """这是文档字符串"""
    pass

print(我的函数.__name__)  # '我的函数'  ← 正确！
print(我的函数.__doc__)   # '这是文档字符串'
```

---

## 4. 带参数的装饰器

需要给装饰器传参数时，要多包一层：

```
┌─────────────────────────────────────────────────────┐
│              带参数装饰器的三层结构                   │
│                                                     │
│  第1层：接收装饰器参数 → 返回真正的装饰器             │
│  ┌────────────────────────────────────────────┐     │
│  │  def 装饰器工厂(参数1, 参数2):             │     │
│  │                                            │     │
│  │    第2层：接收被装饰的函数 → 返回包装器     │     │
│  │    ┌────────────────────────────────────┐  │     │
│  │    │  def 装饰器(func):                │  │     │
│  │    │                                   │  │     │
│  │    │    第3层：实际调用时执行           │  │     │
│  │    │    ┌─────────────────────────┐    │  │     │
│  │    │    │  def wrapper(*a, **kw)  │    │  │     │
│  │    │    │      ...               │    │  │     │
│  │    │    └─────────────────────────┘    │  │     │
│  │    │    return wrapper                 │  │     │
│  │    └────────────────────────────────────┘  │     │
│  │  return 装饰器                             │     │
│  └────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────┘
```

```python
from functools import wraps

def 重试(最大次数=3, 延迟=0):
    """重试装饰器：失败时自动重试"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            for 尝试 in range(最大次数):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if 尝试 == 最大次数 - 1:
                        raise  # 最后一次失败，重新抛出
                    print(f"第{尝试+1}次失败: {e}，{延迟}秒后重试...")
                    if 延迟:
                        time.sleep(延迟)
        return wrapper
    return decorator

@重试(最大次数=3, 延迟=0)
def 不稳定的函数():
    import random
    if random.random() < 0.7:
        raise ConnectionError("连接失败")
    return "成功"
```

---

## 5. 类装饰器

类也可以作为装饰器，需要实现 `__call__` 方法：

```python
from functools import wraps

class 计时器:
    """计时装饰器（类实现）"""

    def __init__(self, func):
        wraps(func)(self)  # 保留元信息
        self.func = func
        self.调用次数 = 0
        self.总耗时 = 0

    def __call__(self, *args, **kwargs):
        import time
        start = time.perf_counter()
        结果 = self.func(*args, **kwargs)
        耗时 = time.perf_counter() - start
        self.调用次数 += 1
        self.总耗时 += 耗时
        print(f"{self.func.__name__} 耗时: {耗时:.4f}s")
        return 结果

    @property
    def 平均耗时(self):
        if self.调用次数 == 0:
            return 0
        return self.总耗时 / self.调用次数

@计时器
def 排序(数据):
    return sorted(数据)
```

---

## 6. 叠加装饰器

多个装饰器叠加时，**从下往上**依次执行：

```
@A
@B
@C
def func():
    ...

等价于：func = A(B(C(func)))

执行顺序：
  调用时：A的前置 → B的前置 → C的前置 → func → C的后置 → B的后置 → A的后置
```

```python
def 装饰A(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("A 前")
        result = func(*args, **kwargs)
        print("A 后")
        return result
    return wrapper

def 装饰B(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("B 前")
        result = func(*args, **kwargs)
        print("B 后")
        return result
    return wrapper

@装饰A
@装饰B
def 目标函数():
    print("执行目标函数")

目标函数()
# 输出：A前 → B前 → 执行 → B后 → A后
```

---

## 总结

```
┌──────────────────────────────────────────────────────┐
│                   本章知识点总结                      │
├───────────────────────┬──────────────────────────────┤
│  装饰器本质            │  接收函数、返回函数的函数     │
│  @语法糖              │  func = decorator(func)的简写 │
│  functools.wraps      │  保留被装饰函数的元信息        │
│  带参数的装饰器        │  三层嵌套函数结构             │
│  类装饰器             │  实现 __call__ 方法           │
│  叠加顺序             │  从下往上包装，从外往内执行    │
└───────────────────────┴──────────────────────────────┘
```
