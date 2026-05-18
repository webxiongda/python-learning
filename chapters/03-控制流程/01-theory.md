# 第03章：控制流程 — 理论篇

## 1. 什么是控制流程？

程序默认从上到下顺序执行。**控制流程**语句允许我们根据条件决定是否执行某段代码（分支），或反复执行某段代码（循环）。

```
程序执行模式
┌──────────────────────────────────┐
│ 顺序执行  A → B → C → D         │
├──────────────────────────────────┤
│ 条件分支  条件True → A           │
│          条件False → B           │
├──────────────────────────────────┤
│ 循环      重复执行 A，直到条件满足 │
└──────────────────────────────────┘
```

---

## 2. if / elif / else — 条件分支

### 基本语法

```python
if 条件:
    # 条件为 True 时执行
    代码块
elif 另一个条件:
    # 第一个条件 False，第二个为 True 时执行
    代码块
else:
    # 所有条件都为 False 时执行
    代码块
```

Python 使用**缩进**（通常 4 个空格）来表示代码块，这是强制要求，不是风格建议。

### 完整示例

```python
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"成绩：{score}，等级：{grade}")
# 输出：成绩：85，等级：B
```

### 条件分支流程图

```
         score = 85
              │
         score >= 90?
         /           \
       True          False
        │              │
      grade="A"   score >= 80?
                  /          \
                True         False
                 │             │
               grade="B"   score >= 70?
                            ......
```

### 单行条件表达式（三元运算符）

```python
# 语法：值_if_true if 条件 else 值_if_false
age = 20
status = "成年" if age >= 18 else "未成年"
print(status)  # 成年

# 等价于：
if age >= 18:
    status = "成年"
else:
    status = "未成年"
```

---

## 3. for 循环

`for` 循环用于**遍历可迭代对象**（列表、字符串、range 等）中的每个元素。

```python
# 遍历列表
fruits = ["苹果", "香蕉", "橙子"]
for fruit in fruits:
    print(f"水果：{fruit}")

# 遍历字符串
for char in "Python":
    print(char, end=" ")
print()  # 换行
# 输出：P y t h o n
```

### range() 函数

`range()` 生成整数序列，是 for 循环最常见的搭档：

```
range() 参数说明
range(stop)          → 0, 1, 2, ..., stop-1
range(start, stop)   → start, start+1, ..., stop-1
range(start, stop, step) → start, start+step, ..., < stop

示例：
range(5)        → 0 1 2 3 4
range(2, 7)     → 2 3 4 5 6
range(0, 10, 2) → 0 2 4 6 8
range(10, 0, -1)→ 10 9 8 7 6 5 4 3 2 1
```

```python
# 打印 1 到 10 的平方
for i in range(1, 11):
    print(f"{i}² = {i**2}")

# 倒计时
for i in range(5, 0, -1):
    print(i, end=" ")
print("发射！")
# 输出：5 4 3 2 1 发射！
```

---

## 4. while 循环

`while` 循环在**条件为 True 时持续执行**，适合不知道具体迭代次数的场景。

```python
# 基本结构
count = 0
while count < 5:
    print(f"第 {count + 1} 次循环")
    count += 1   # 必须有修改条件的语句，否则死循环！

# 常见模式：用户输入验证
while True:                         # 无限循环
    password = input("请输入密码：")
    if password == "secret":
        print("密码正确！")
        break                       # 满足条件后退出
    print("密码错误，请重试...")
```

```
while 循环执行流程
┌─────────────────────────────┐
│  检查条件                    │
│    │                        │
│  True? ──→ 执行循环体 ──┐    │
│    │                   │    │
│  False? ──→ 退出循环    │    │
│             ↑           │    │
│             └───────────┘    │
└─────────────────────────────┘
```

---

## 5. break、continue、pass

这三个关键字用于在循环中精细控制执行流程。

### break：立即退出循环

```python
# 在列表中查找第一个偶数，找到即停止
numbers = [1, 3, 5, 4, 7, 9]
for n in numbers:
    if n % 2 == 0:
        print(f"找到第一个偶数：{n}")
        break   # 退出整个 for 循环
```

### continue：跳过本次迭代

```python
# 打印 1-10 中所有奇数
for i in range(1, 11):
    if i % 2 == 0:
        continue   # 跳过偶数，直接进入下一次循环
    print(i, end=" ")
# 输出：1 3 5 7 9
```

### pass：占位符（什么都不做）

```python
# 用于语法上需要代码块但逻辑尚未实现的场合
for i in range(5):
    pass   # 之后再补充逻辑

if True:
    pass   # 空的 if 块，语法合法

def todo_function():
    pass   # 函数体待实现
```

### 三者对比

```
break    → 打破循环，完全退出
continue → 跳过当次，进入下一轮
pass     → 什么都不做，继续执行

for i in range(5):   i = 0 1 2 3 4
    if i == 2:
        break        → 循环在 i=2 时终止，输出 0 1
        continue     → 跳过 i=2，输出 0 1 3 4
        pass         → 不影响，输出 0 1 2 3 4
```

---

## 6. 循环的 else 子句

Python 的循环支持 `else` 块，**当循环正常结束（未被 break 中断）时执行**：

```python
# 查找素数
def is_prime(n):
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            print(f"{n} 不是素数，可被 {i} 整除")
            break
    else:
        # 循环完整跑完（没有触发 break），说明没有因子
        print(f"{n} 是素数")

is_prime(7)   # 7 是素数
is_prime(9)   # 9 不是素数，可被 3 整除
```

---

## 7. 嵌套循环

循环可以嵌套，常用于处理二维数据（矩阵、表格等）：

```python
# 打印乘法表
for i in range(1, 4):
    for j in range(1, 4):
        print(f"{i}×{j}={i*j}", end="  ")
    print()  # 外层循环换行

# 输出：
# 1×1=1  1×2=2  1×3=3
# 2×1=2  2×2=4  2×3=6
# 3×1=3  3×2=6  3×3=9
```

---

## 小结

```
控制流程关键字速查
├── if / elif / else → 条件分支
├── for ... in ...   → 遍历可迭代对象
├── while 条件:      → 条件为真时循环
├── range(n)         → 生成整数序列
├── break            → 退出循环
├── continue         → 跳过本次迭代
├── pass             → 占位，什么都不做
└── for/while...else → 循环正常结束时执行
```
