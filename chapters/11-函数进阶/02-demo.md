# 第11章：函数进阶 — Demo 示例

## Demo 1：可变参数综合应用

```python
# 演示 *args 和 **kwargs 的综合用法

def 构建SQL查询(表名, *字段, **条件):
    """动态构建 SQL 查询语句"""
    if 字段:
        字段列表 = ", ".join(字段)
    else:
        字段列表 = "*"

    sql = f"SELECT {字段列表} FROM {表名}"

    if 条件:
        条件列表 = " AND ".join(f"{k}='{v}'" for k, v in 条件.items())
        sql += f" WHERE {条件列表}"

    return sql

# 测试不同组合
print(构建SQL查询("用户表"))
print(构建SQL查询("用户表", "姓名", "年龄"))
print(构建SQL查询("用户表", "姓名", "年龄", 城市="北京"))
print(构建SQL查询("用户表", 城市="上海", 状态="活跃"))

# 使用解包传参
fields = ("姓名", "邮箱")
filters = {"部门": "技术", "状态": "在职"}
print(构建SQL查询("员工表", *fields, **filters))
```

```
# 预期输出：
SELECT * FROM 用户表
SELECT 姓名, 年龄 FROM 用户表
SELECT 姓名, 年龄 FROM 用户表 WHERE 城市='北京'
SELECT * FROM 用户表 WHERE 城市='上海' AND 状态='活跃'
SELECT 姓名, 邮箱 FROM 员工表 WHERE 部门='技术' AND 状态='在职'
```

---

## Demo 2：默认参数陷阱与修复

```python
# 演示默认参数陷阱及正确写法

import datetime

# ❌ 错误示范：可变默认参数
def 错误的记录日志(消息, 日志列表=[]):
    日志列表.append(消息)
    return 日志列表

# ✅ 正确写法1：使用 None
def 正确的记录日志_v1(消息, 日志列表=None):
    if 日志列表 is None:
        日志列表 = []
    日志列表.append(消息)
    return 日志列表

# ✅ 正确写法2：使用 None 并处理时间戳
def 正确的记录日志_v2(消息, 时间=None, 日志列表=None):
    if 时间 is None:
        时间 = datetime.datetime.now().strftime("%H:%M:%S")
    if 日志列表 is None:
        日志列表 = []
    日志列表.append(f"[{时间}] {消息}")
    return 日志列表

# 演示错误
print("=== 错误示范 ===")
log1 = 错误的记录日志("启动系统")
log2 = 错误的记录日志("用户登录")  # 会包含上一条！
print(f"log1: {log1}")
print(f"log2: {log2}")
print(f"log1 is log2: {log1 is log2}")  # True，同一个对象！

print("\n=== 正确写法 ===")
log3 = 正确的记录日志_v1("启动系统")
log4 = 正确的记录日志_v1("用户登录")
print(f"log3: {log3}")
print(f"log4: {log4}")
print(f"log3 is log4: {log3 is log4}")  # False，独立对象
```

```
# 预期输出：
=== 错误示范 ===
log1: ['启动系统', '用户登录']
log2: ['启动系统', '用户登录']
log1 is log2: True

=== 正确写法 ===
log3: ['启动系统']
log4: ['用户登录']
log3 is log4: False
```

---

## Demo 3：闭包实战 — 计数器与缓存

```python
# 使用闭包实现计数器和简单缓存

def 创建计数器(初始值=0, 步长=1):
    """返回一个计数器函数"""
    count = 初始值

    def 计数(重置=False):
        nonlocal count
        if 重置:
            count = 初始值
            return count
        count += 步长
        return count

    return 计数

# 创建不同步长的计数器
counter1 = 创建计数器()          # 从0开始，步长1
counter2 = 创建计数器(100, 10)   # 从100开始，步长10

print("计数器1:", counter1(), counter1(), counter1())
print("计数器2:", counter2(), counter2(), counter2())
print("计数器1重置:", counter1(重置=True))
print("计数器1重置后:", counter1(), counter1())

# 闭包实现简单缓存
def 创建缓存函数(func):
    """给任意函数添加缓存能力"""
    缓存 = {}
    调用次数 = [0]  # 用列表是为了在闭包中可修改

    def 带缓存的函数(*args):
        调用次数[0] += 1
        if args not in 缓存:
            缓存[args] = func(*args)
            print(f"  [计算] {func.__name__}{args} = {缓存[args]}")
        else:
            print(f"  [缓存] {func.__name__}{args} = {缓存[args]}")
        return 缓存[args]

    def 获取统计():
        return f"总调用次数: {调用次数[0]}, 缓存条目: {len(缓存)}"

    带缓存的函数.统计 = 获取统计
    return 带缓存的函数

def 斐波那契(n):
    if n <= 1:
        return n
    return n  # 简化版，仅演示缓存效果

cached_fib = 创建缓存函数(斐波那契)
print("\n=== 缓存演示 ===")
cached_fib(5)
cached_fib(10)
cached_fib(5)   # 这次从缓存取
cached_fib(10)  # 这次从缓存取
print(cached_fib.统计())
```

```
# 预期输出：
计数器1: 1 2 3
计数器2: 110 120 130
计数器1重置: 0
计数器1重置后: 1 2

=== 缓存演示 ===
  [计算] 斐波那契(5,) = 5
  [计算] 斐波那契(10,) = 10
  [缓存] 斐波那契(5,) = 5
  [缓存] 斐波那契(10,) = 10
总调用次数: 4, 缓存条目: 2
```

---

## Demo 4：高阶函数 map/filter 实战

```python
# map 和 filter 的实际应用场景

# 场景：处理用户数据
用户数据 = [
    {"姓名": "张三", "年龄": 28, "薪资": 15000, "部门": "技术"},
    {"姓名": "李四", "年龄": 35, "薪资": 22000, "部门": "产品"},
    {"姓名": "王五", "年龄": 24, "薪资": 8000,  "部门": "技术"},
    {"姓名": "赵六", "年龄": 42, "薪资": 35000, "部门": "管理"},
    {"姓名": "钱七", "年龄": 29, "薪资": 18000, "部门": "产品"},
]

# 1. 使用 map 提取姓名列表
姓名列表 = list(map(lambda u: u["姓名"], 用户数据))
print("所有姓名:", 姓名列表)

# 2. 使用 map 计算税后薪资（扣除20%税）
税后薪资 = list(map(lambda u: {**u, "税后薪资": int(u["薪资"] * 0.8)}, 用户数据))
for u in 税后薪资:
    print(f"  {u['姓名']}: {u['薪资']} → {u['税后薪资']}")

# 3. 使用 filter 筛选高薪员工（薪资 > 15000）
高薪员工 = list(filter(lambda u: u["薪资"] > 15000, 用户数据))
print("\n高薪员工:")
for u in 高薪员工:
    print(f"  {u['姓名']} - {u['薪资']}")

# 4. 链式组合：技术部的税后薪资
技术部税后 = list(map(
    lambda u: f"{u['姓名']}: {int(u['薪资'] * 0.8)}",
    filter(lambda u: u["部门"] == "技术", 用户数据)
))
print("\n技术部税后薪资:", 技术部税后)
```

```
# 预期输出：
所有姓名: ['张三', '李四', '王五', '赵六', '钱七']
  张三: 15000 → 12000
  李四: 22000 → 17600
  王五: 8000 → 6400
  赵六: 35000 → 28000
  钱七: 18000 → 14400

高薪员工:
  李四 - 22000
  赵六 - 35000
  钱七 - 18000

技术部税后薪资: ['张三: 12000', '王五: 6400']
```

---

## Demo 5：函数工厂模式

```python
# 使用闭包创建函数工厂，生成各种专用函数

def 创建验证器(最小值=None, 最大值=None, 允许为空=False):
    """创建一个数值范围验证函数"""
    def 验证(值, 字段名="值"):
        if 值 is None:
            if 允许为空:
                return True, ""
            return False, f"{字段名}不能为空"

        if not isinstance(值, (int, float)):
            return False, f"{字段名}必须是数字"

        if 最小值 is not None and 值 < 最小值:
            return False, f"{字段名}不能小于{最小值}"

        if 最大值 is not None and 值 > 最大值:
            return False, f"{字段名}不能大于{最大值}"

        return True, "验证通过"
    return 验证

# 创建专用验证器
验证年龄 = 创建验证器(0, 150)
验证分数 = 创建验证器(0, 100)
验证可空薪资 = 创建验证器(0, 最大值=None, 允许为空=True)

# 测试
测试数据 = [
    ("年龄", 验证年龄, 25),
    ("年龄", 验证年龄, -5),
    ("年龄", 验证年龄, 200),
    ("分数", 验证分数, 95),
    ("分数", 验证分数, 101),
    ("薪资", 验证可空薪资, None),
    ("薪资", 验证可空薪资, 5000),
]

for 字段, 验证器, 测试值 in 测试数据:
    通过, 消息 = 验证器(测试值, 字段)
    状态 = "✓" if 通过 else "✗"
    print(f"  {状态} {字段}={测试值}: {消息}")
```

```
# 预期输出：
  ✓ 年龄=25: 验证通过
  ✗ 年龄=-5: 年龄不能小于0
  ✗ 年龄=200: 年龄不能大于150
  ✓ 分数=95: 验证通过
  ✗ 分数=101: 分数不能大于100
  ✓ 薪资=None: 
  ✓ 薪资=5000: 验证通过
```
