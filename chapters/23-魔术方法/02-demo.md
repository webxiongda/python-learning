# 第23章：魔术方法 — Demo 演示

## Demo 1：__str__ 和 __repr__

```python
# demo1_str_repr.py

class Color:
    """RGB颜色类"""
    
    def __init__(self, r, g, b):
        if not all(0 <= v <= 255 for v in (r, g, b)):
            raise ValueError("RGB值必须在0-255之间")
        self.r = r
        self.g = g
        self.b = b
    
    def __repr__(self):
        """开发者视图：可重现对象"""
        return f"Color(r={self.r}, g={self.g}, b={self.b})"
    
    def __str__(self):
        """用户视图：友好展示"""
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"
    
    def to_hsv(self):
        """转换为HSV格式（简化版）"""
        r, g, b = self.r/255, self.g/255, self.b/255
        max_c = max(r, g, b)
        return f"HSV({max_c*360:.0f}°, {(max_c-min(r,g,b))/max_c if max_c else 0:.0%}, {max_c:.0%})"


# 创建颜色
red = Color(255, 0, 0)
green = Color(0, 255, 0)
blue = Color(0, 0, 255)
white = Color(255, 255, 255)

# __str__ 调用
print(red)           # #FF0000
print(green)         # #00FF00
print(f"蓝色：{blue}")  # 蓝色：#0000FF

# __repr__ 调用
print(repr(red))     # Color(r=255, g=0, b=0)

# 列表中的对象：使用 __repr__
colors = [red, green, blue]
print(colors)  # [Color(r=255, g=0, b=0), Color(r=0, g=255, b=0), Color(r=0, g=0, b=255)]

# 转换
print(f"\n{red} 的HSV：{red.to_hsv()}")

# 错误示例
try:
    invalid = Color(300, 0, 0)
except ValueError as e:
    print(f"错误：{e}")
```

```
# 预期输出：
#FF0000
#00FF00
蓝色：#0000FF
Color(r=255, g=0, b=0)
[Color(r=255, g=0, b=0), Color(r=0, g=255, b=0), Color(r=0, g=0, b=255)]

#FF0000 的HSV：HSV(360°, 100%, 100%)
错误：RGB值必须在0-255之间
```

---

## Demo 2：容器协议（__len__ / __getitem__ / __setitem__）

```python
# demo2_container.py

class Scoreboard:
    """记分板：支持索引访问和长度"""
    
    def __init__(self, title):
        self.title = title
        self._records = []  # [(name, score), ...]
    
    def add(self, name, score):
        self._records.append((name, score))
        # 保持降序排列
        self._records.sort(key=lambda x: x[1], reverse=True)
    
    def __len__(self):
        return len(self._records)
    
    def __getitem__(self, index):
        """支持 board[0] 和 board[0:3] 切片"""
        return self._records[index]
    
    def __setitem__(self, index, value):
        """支持 board[0] = ('新名字', 100)"""
        name, score = value
        self._records[index] = (name, score)
        self._records.sort(key=lambda x: x[1], reverse=True)
    
    def __contains__(self, name):
        """支持 'xxx' in board"""
        return any(n == name for n, _ in self._records)
    
    def __iter__(self):
        """支持 for item in board"""
        return iter(self._records)
    
    def __str__(self):
        lines = [f"=== {self.title} ==="]
        for i, (name, score) in enumerate(self._records, 1):
            lines.append(f"  #{i:2d}  {name:<10s}  {score:6d}")
        return "\n".join(lines)


board = Scoreboard("Python游戏排行榜")
board.add("张三", 9500)
board.add("李四", 12000)
board.add("王五", 8800)
board.add("赵六", 15000)
board.add("孙七", 11500)

print(board)
print(f"\n总人数：{len(board)}")  # __len__
print(f"第一名：{board[0]}")      # __getitem__
print(f"前三名：{board[0:3]}")    # 切片也用 __getitem__

# __contains__
print(f"\n张三是否在榜：{'张三' in board}")
print(f"钱八是否在榜：{'钱八' in board}")

# __iter__
print("\n高分玩家（>10000）：")
for name, score in board:
    if score > 10000:
        print(f"  {name}: {score}")
```

```
# 预期输出：
=== Python游戏排行榜 ===
  # 1  赵六         15000
  # 2  李四         12000
  # 3  孙七         11500
  # 4  张三          9500
  # 5  王五          8800

总人数：5
第一名：('赵六', 15000)
前三名：[('赵六', 15000), ('李四', 12000), ('孙七', 11500)]

张三是否在榜：True
钱八是否在榜：False

高分玩家（>10000）：
  赵六: 15000
  李四: 12000
  孙七: 11500
```

---

## Demo 3：比较运算符 __eq__ / __lt__

```python
# demo3_comparison.py
from functools import total_ordering

@total_ordering
class Version:
    """软件版本号比较"""
    
    def __init__(self, version_str):
        self.version_str = version_str
        parts = version_str.split(".")
        self.major = int(parts[0])
        self.minor = int(parts[1]) if len(parts) > 1 else 0
        self.patch = int(parts[2]) if len(parts) > 2 else 0
    
    @property
    def _tuple(self):
        return (self.major, self.minor, self.patch)
    
    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._tuple == other._tuple
    
    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._tuple < other._tuple
    
    def __repr__(self):
        return f"Version('{self.version_str}')"
    
    def __str__(self):
        return self.version_str
    
    def __hash__(self):
        return hash(self._tuple)


# 测试版本比较
v1 = Version("1.0.0")
v2 = Version("1.2.3")
v3 = Version("2.0.0")
v4 = Version("1.2.3")

print(f"{v2} == {v4}: {v2 == v4}")   # True
print(f"{v1} < {v2}:  {v1 < v2}")    # True
print(f"{v3} > {v2}:  {v3 > v2}")    # True（@total_ordering自动生成）
print(f"{v1} >= {v1}: {v1 >= v1}")   # True（自动生成）

# 排序（利用比较方法）
versions = [Version("2.1.0"), Version("1.0.5"), Version("1.2.3"), Version("3.0.0")]
versions.sort()
print(f"\n排序结果：{versions}")

# 找最新版本
latest = max(versions)
print(f"最新版本：{latest}")

# 用在集合中（需要__hash__）
version_set = {v1, v2, v4}  # v2 和 v4 相等，集合去重
print(f"版本集合大小：{len(version_set)}")
```

```
# 预期输出：
1.2.3 == 1.2.3: True
1.0.0 < 1.2.3:  True
2.0.0 > 1.2.3:  True
1.0.0 >= 1.0.0: True

排序结果：[Version('1.0.5'), Version('1.2.3'), Version('2.1.0'), Version('3.0.0')]
最新版本：3.0.0
版本集合大小：2
```

---

## Demo 4：上下文管理器 __enter__ / __exit__

```python
# demo4_context_manager.py

class Timer:
    """计时器上下文管理器"""
    import time
    
    def __init__(self, name=""):
        self.name = name
        self.elapsed = 0
    
    def __enter__(self):
        import time
        self._start = time.perf_counter()
        print(f"⏱ 开始计时：{self.name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.elapsed = time.perf_counter() - self._start
        print(f"⏱ 结束：{self.name}，耗时 {self.elapsed:.4f} 秒")
        return False  # 不压制异常


class DatabaseConnection:
    """模拟数据库连接"""
    
    def __init__(self, host, db):
        self.host = host
        self.db = db
        self.connected = False
        self.queries = []
    
    def __enter__(self):
        self.connected = True
        print(f"[DB] 连接到 {self.host}/{self.db}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"[DB] 发生错误，回滚事务：{exc_val}")
            self.queries.clear()
        else:
            print(f"[DB] 提交 {len(self.queries)} 条查询")
        self.connected = False
        print(f"[DB] 断开连接")
        return False
    
    def execute(self, sql):
        if not self.connected:
            raise RuntimeError("未连接数据库")
        self.queries.append(sql)
        print(f"[DB] 执行：{sql}")


# 使用计时器
with Timer("列表排序") as t:
    data = list(range(10000, 0, -1))
    data.sort()
print(f"排序完成，共 {len(data)} 个元素\n")

# 使用数据库连接（正常流程）
with DatabaseConnection("localhost", "mydb") as db:
    db.execute("SELECT * FROM users")
    db.execute("UPDATE users SET active=1 WHERE id=5")

print()

# 使用数据库连接（异常流程）
try:
    with DatabaseConnection("localhost", "mydb") as db:
        db.execute("INSERT INTO orders VALUES (1, 'test')")
        raise ValueError("业务逻辑错误！")  # 模拟异常
        db.execute("UPDATE inventory SET qty=qty-1")  # 不会执行
except ValueError:
    print("外层捕获异常")
```

```
# 预期输出：
⏱ 开始计时：列表排序
⏱ 结束：列表排序，耗时 0.0012 秒
排序完成，共 10000 个元素

[DB] 连接到 localhost/mydb
[DB] 执行：SELECT * FROM users
[DB] 执行：UPDATE users SET active=1 WHERE id=5
[DB] 提交 2 条查询
[DB] 断开连接

[DB] 连接到 localhost/mydb
[DB] 执行：INSERT INTO orders VALUES (1, 'test')
[DB] 发生错误，回滚事务：业务逻辑错误！
[DB] 断开连接
外层捕获异常
```

---

## Demo 5：__call__ 实战

```python
# demo5_call.py

class RateLimiter:
    """调用频率限制器（模拟）"""
    import time
    
    def __init__(self, max_calls, per_seconds):
        self.max_calls = max_calls
        self.per_seconds = per_seconds
        self.call_times = []
    
    def __call__(self, func):
        """作为装饰器使用"""
        import time
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # 清理过期记录
            self.call_times = [t for t in self.call_times 
                              if now - t < self.per_seconds]
            
            if len(self.call_times) >= self.max_calls:
                print(f"[限流] {func.__name__} 调用过于频繁，已阻止")
                return None
            
            self.call_times.append(now)
            return func(*args, **kwargs)
        
        return wrapper
    
    def __repr__(self):
        return f"RateLimiter({self.max_calls}次/{self.per_seconds}秒)"


class Validator:
    """可调用的验证器"""
    
    def __init__(self, min_len=1, max_len=100, allow_digits=True):
        self.min_len = min_len
        self.max_len = max_len
        self.allow_digits = allow_digits
        self.errors = []
    
    def __call__(self, text):
        """调用验证器：validate(text)"""
        self.errors = []
        
        if len(text) < self.min_len:
            self.errors.append(f"长度不足（最少{self.min_len}字符）")
        if len(text) > self.max_len:
            self.errors.append(f"长度超限（最多{self.max_len}字符）")
        if not self.allow_digits and any(c.isdigit() for c in text):
            self.errors.append("不允许包含数字")
        
        return len(self.errors) == 0
    
    def __repr__(self):
        return f"Validator(min={self.min_len}, max={self.max_len})"


# 使用验证器
username_validator = Validator(min_len=3, max_len=20, allow_digits=False)
password_validator = Validator(min_len=8, max_len=50)

test_usernames = ["ab", "zhangsan", "user123", "a" * 25]

print("=== 用户名验证 ===")
for name in test_usernames:
    result = username_validator(name)  # 调用 __call__
    status = "✓ 通过" if result else f"✗ 失败：{username_validator.errors}"
    print(f"  '{name}': {status}")

print("\n=== 密码验证 ===")
test_passwords = ["short", "validpass123", "another_valid_pass!"]
for pwd in test_passwords:
    result = password_validator(pwd)
    status = "✓ 通过" if result else f"✗ 失败：{password_validator.errors}"
    print(f"  '{pwd}': {status}")

print(f"\n验证器：{username_validator}")
print(f"callable(username_validator) = {callable(username_validator)}")
```

```
# 预期输出：
=== 用户名验证 ===
  'ab': ✗ 失败：['长度不足（最少3字符）']
  'zhangsan': ✓ 通过
  'user123': ✗ 失败：['不允许包含数字']
  'aaaaaaaaaaaaaaaaaaaaaaaaa': ✗ 失败：['长度超限（最多20字符）']

=== 密码验证 ===
  'short': ✗ 失败：['长度不足（最少8字符）']
  'validpass123': ✓ 通过
  'another_valid_pass!': ✓ 通过

验证器：Validator(min=3, max=20)
callable(username_validator) = True
```
