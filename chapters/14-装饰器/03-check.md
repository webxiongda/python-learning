# 第14章：装饰器 — 自测题

## 题目1：装饰器基础

以下代码输出什么？

```python
def decorator(func):
    print("装饰中...")
    def wrapper():
        print("before")
        func()
        print("after")
    return wrapper

print("定义前")

@decorator
def hello():
    print("hello")

print("定义后")
hello()
```

### 参考答案

```
定义前
装饰中...
定义后
before
hello
after
```

关键点：`@decorator` 在**模块导入/函数定义时**立即执行，而不是在调用时。所以"装饰中..."在"定义后"之前打印。

---

## 题目2：functools.wraps

以下代码有什么问题？如何修复？

```python
def log(func):
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log
def calculate(x, y):
    """计算两数之和"""
    return x + y

print(calculate.__name__)
print(calculate.__doc__)
help(calculate)
```

### 参考答案

问题：没有使用 `functools.wraps`，导致 `calculate.__name__` 返回 `'wrapper'`，`__doc__` 返回 `None`，`help()` 显示的是 wrapper 的信息而非原函数。

修复：

```python
from functools import wraps

def log(func):
    @wraps(func)  # 添加这一行
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log
def calculate(x, y):
    """计算两数之和"""
    return x + y

print(calculate.__name__)  # calculate（正确）
print(calculate.__doc__)   # 计算两数之和（正确）
```

---

## 题目3：带参数的装饰器

实现一个 `限速(每秒最多N次)` 装饰器，当调用过于频繁时打印警告并返回 `None`。

```python
# 期望行为：
@限速(每秒最多=2)
def api调用(参数):
    return f"结果: {参数}"
```

### 参考答案

```python
import time
from functools import wraps

def 限速(每秒最多):
    def decorator(func):
        调用时间记录 = []

        @wraps(func)
        def wrapper(*args, **kwargs):
            现在 = time.time()
            # 清理1秒前的记录
            while 调用时间记录 and 现在 - 调用时间记录[0] > 1.0:
                调用时间记录.pop(0)

            if len(调用时间记录) >= 每秒最多:
                print(f"警告：{func.__name__} 调用过于频繁，已限速！")
                return None

            调用时间记录.append(现在)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@限速(每秒最多=2)
def api调用(参数):
    return f"结果: {参数}"

# 快速调用3次
print(api调用("A"))   # 结果: A
print(api调用("B"))   # 结果: B
print(api调用("C"))   # 警告：...  None
```

---

## 题目4：叠加装饰器

以下代码执行后，输出的第一行是什么？

```python
from functools import wraps

def upper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper() if isinstance(result, str) else result
    return wrapper

def exclaim(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result + "!!!" if isinstance(result, str) else result
    return wrapper

@upper
@exclaim
def greet(name):
    return f"hello {name}"

print(greet("world"))
```

### 参考答案

```
HELLO WORLD!!!
```

执行顺序分析：
1. 装饰时：`greet = upper(exclaim(greet))`
2. 调用时：`upper` 的 wrapper 先执行
3. `upper` 调用 `exclaim` 的 wrapper
4. `exclaim` 调用原始 `greet`，得到 `"hello world"`
5. `exclaim` 的 wrapper 添加 `!!!`，返回 `"hello world!!!"`
6. `upper` 的 wrapper 转大写，返回 `"HELLO WORLD!!!"`

---

## 题目5：综合实践

实现一个 `验证参数` 装饰器工厂，根据传入的类型规格验证函数参数：

```python
@验证参数(name=str, age=int, score=float)
def 创建用户(name, age, score):
    return f"{name}, {age}岁, 得分{score}"

创建用户("张三", 25, 95.5)    # 正常
创建用户("李四", "25", 95.5)  # 应抛出 TypeError
```

### 参考答案

```python
from functools import wraps
import inspect

def 验证参数(**类型规格):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取函数的参数名列表
            参数名列表 = list(inspect.signature(func).parameters.keys())
            # 将位置参数与参数名对应
            所有参数 = dict(zip(参数名列表, args))
            所有参数.update(kwargs)

            for 参数名, 期望类型 in 类型规格.items():
                if 参数名 in 所有参数:
                    实际值 = 所有参数[参数名]
                    if not isinstance(实际值, 期望类型):
                        raise TypeError(
                            f"参数 '{参数名}' 期望类型 {期望类型.__name__}，"
                            f"但收到 {type(实际值).__name__}（值：{实际值!r}）"
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@验证参数(name=str, age=int, score=float)
def 创建用户(name, age, score):
    return f"{name}, {age}岁, 得分{score}"

print(创建用户("张三", 25, 95.5))

try:
    创建用户("李四", "25", 95.5)
except TypeError as e:
    print(f"类型错误: {e}")
# 输出：类型错误: 参数 'age' 期望类型 int，但收到 str（值：'25'）
```
