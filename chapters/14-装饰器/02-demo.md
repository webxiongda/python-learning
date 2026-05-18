# 第14章：装饰器 — Demo 示例

## Demo 1：计时装饰器

```python
import time
from functools import wraps

def 计时(func):
    """测量函数执行时间的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[计时] {func.__name__} 执行耗时: {elapsed:.6f} 秒")
        return result
    return wrapper

@计时
def 冒泡排序(arr):
    arr = arr.copy()
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

@计时
def 内置排序(arr):
    return sorted(arr)

import random
data = [random.randint(1, 1000) for _ in range(2000)]

结果1 = 冒泡排序(data)
结果2 = 内置排序(data)
print(f"结果一致: {结果1 == 结果2}")
print(f"函数名称: {冒泡排序.__name__}")  # 保留了原名
```

```
# 预期输出：
[计时] 冒泡排序 执行耗时: 1.234567 秒
[计时] 内置排序 执行耗时: 0.000234 秒
结果一致: True
函数名称: 冒泡排序
```

---

## Demo 2：带参数装饰器——权限控制

```python
from functools import wraps

# 模拟用户系统
当前用户 = {"name": "张三", "roles": ["user", "editor"]}

def 需要权限(*required_roles):
    """权限控制装饰器，支持多角色"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            用户角色 = set(当前用户.get("roles", []))
            需要角色 = set(required_roles)

            if not 需要角色.intersection(用户角色):
                raise PermissionError(
                    f"用户 '{当前用户['name']}' 无权限访问 {func.__name__}。"
                    f"需要角色：{required_roles}，当前角色：{list(用户角色)}"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@需要权限("user")
def 查看文章(文章id):
    return f"显示文章 #{文章id}"

@需要权限("editor", "admin")
def 编辑文章(文章id, 内容):
    return f"编辑文章 #{文章id}"

@需要权限("admin")
def 删除文章(文章id):
    return f"删除文章 #{文章id}"

# 测试权限
print("=== 权限测试 ===")

print(查看文章(1))   # 有 user 角色，成功
print(编辑文章(1, "新内容"))  # 有 editor 角色，成功

try:
    删除文章(1)   # 没有 admin 角色，失败
except PermissionError as e:
    print(f"权限错误: {e}")
```

```
# 预期输出：
=== 权限测试 ===
显示文章 #1
编辑文章 #1
权限错误: 用户 '张三' 无权限访问 删除文章。需要角色：('admin',)，当前角色：['user', 'editor']
```

---

## Demo 3：缓存装饰器（LRU Cache 原理）

```python
from functools import wraps

def 简单缓存(func):
    """简单的记忆化装饰器"""
    缓存 = {}

    @wraps(func)
    def wrapper(*args):
        if args not in 缓存:
            缓存[args] = func(*args)
        return 缓存[args]

    wrapper.缓存 = 缓存  # 暴露缓存供调试
    wrapper.清除缓存 = lambda: 缓存.clear()
    return wrapper

@简单缓存
def 斐波那契(n):
    if n <= 1:
        return n
    return 斐波那契(n - 1) + 斐波那契(n - 2)

# 不用缓存时，fib(35) 需要约 29M 次计算
# 用了缓存后，只需 35 次
import time

start = time.perf_counter()
结果 = 斐波那契(40)
elapsed = time.perf_counter() - start

print(f"fib(40) = {结果}")
print(f"耗时: {elapsed:.6f} 秒")
print(f"缓存条目数: {len(斐波那契.缓存)}")

# 对比 Python 内置 lru_cache
from functools import lru_cache

@lru_cache(maxsize=128)
def 斐波那契_lru(n):
    if n <= 1:
        return n
    return 斐波那契_lru(n - 1) + 斐波那契_lru(n - 2)

print(f"\nlru_cache fib(40) = {斐波那契_lru(40)}")
print(f"缓存信息: {斐波那契_lru.cache_info()}")
```

```
# 预期输出：
fib(40) = 102334155
耗时: 0.000021 秒
缓存条目数: 41

lru_cache fib(40) = 102334155
缓存信息: CacheInfo(hits=38, misses=41, maxsize=128, currsize=41)
```

---

## Demo 4：叠加装饰器执行顺序

```python
from functools import wraps

def 装饰器(名称):
    """通用装饰器工厂，用于演示执行顺序"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"[{名称}] 进入")
            result = func(*args, **kwargs)
            print(f"[{名称}] 退出")
            return result
        return wrapper
    return decorator

@装饰器("A")  # 最外层
@装饰器("B")  # 中间层
@装饰器("C")  # 最内层（最先包装原函数）
def 目标函数():
    print("  执行目标函数")
    return 42

print("=== 叠加装饰器执行顺序 ===")
result = 目标函数()
print(f"返回值: {result}")

# 验证等价关系
print("\n=== 手动等价写法 ===")
def 原始函数():
    print("  执行原始函数")
    return 42

等价 = 装饰器("A")(装饰器("B")(装饰器("C")(原始函数)))
等价()
```

```
# 预期输出：
=== 叠加装饰器执行顺序 ===
[A] 进入
[B] 进入
[C] 进入
  执行目标函数
[C] 退出
[B] 退出
[A] 退出
返回值: 42

=== 手动等价写法 ===
[A] 进入
[B] 进入
[C] 进入
  执行原始函数
[C] 退出
[B] 退出
[A] 退出
```

---

## Demo 5：类装饰器——调用统计

```python
from functools import wraps, update_wrapper

class 调用统计:
    """统计函数调用次数和参数的类装饰器"""

    def __init__(self, func):
        update_wrapper(self, func)  # 保留元信息
        self.func = func
        self.调用次数 = 0
        self.调用历史 = []

    def __call__(self, *args, **kwargs):
        self.调用次数 += 1
        self.调用历史.append({
            "第N次": self.调用次数,
            "args": args,
            "kwargs": kwargs,
        })
        return self.func(*args, **kwargs)

    def 报告(self):
        print(f"\n=== {self.func.__name__} 调用统计 ===")
        print(f"总调用次数: {self.调用次数}")
        for 记录 in self.调用历史:
            print(f"  第{记录['第N次']}次: args={记录['args']}, kwargs={记录['kwargs']}")

@调用统计
def 发送消息(收件人, 内容, 优先级="普通"):
    return f"消息已发送给 {收件人}"

# 调用函数
发送消息("张三", "你好")
发送消息("李四", "开会通知", 优先级="紧急")
发送消息("张三", "下午三点会议室")

# 查看统计
发送消息.报告()
print(f"\n函数名: {发送消息.__name__}")
```

```
# 预期输出：
=== 发送消息 调用统计 ===
总调用次数: 3
  第1次: args=('张三', '你好'), kwargs={}
  第2次: args=('李四', '开会通知'), kwargs={'优先级': '紧急'}
  第3次: args=('张三', '下午三点会议室'), kwargs={}

函数名: 发送消息
```
