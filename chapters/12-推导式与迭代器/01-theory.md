# 第12章：推导式与迭代器

## 学习目标
- 掌握列表、字典、集合推导式的语法与性能
- 理解生成器表达式与列表推导式的区别
- 掌握 iter() 和 next() 的使用
- 理解 StopIteration 异常的角色

---

## 1. 列表推导式（List Comprehension）

### 1.1 基本语法

```
[表达式 for 变量 in 可迭代对象 if 条件]
    ↑          ↑              ↑
  输出值    循环变量       过滤条件（可选）
```

```python
# 普通 for 循环写法
squares = []
for x in range(10):
    if x % 2 == 0:
        squares.append(x ** 2)

# 等价的推导式写法（更简洁）
squares = [x**2 for x in range(10) if x % 2 == 0]
print(squares)  # [0, 4, 16, 36, 64]
```

### 1.2 嵌套推导式

```
[[表达式 for j in 内层] for i in 外层]
```

```python
# 矩阵转置
matrix = [[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]]

转置 = [[row[i] for row in matrix] for i in range(3)]
# [[1,4,7], [2,5,8], [3,6,9]]
```

### 1.3 推导式 vs 普通循环

```
性能对比（创建1000个元素的列表）：

列表推导式:  ████████░░  0.05ms  ← 最快
for 循环:   ████████████ 0.08ms
map():      █████████░░ 0.06ms
```

---

## 2. 字典推导式（Dict Comprehension）

```python
# 语法：{键表达式: 值表达式 for 变量 in 可迭代对象 if 条件}

单词 = ["apple", "banana", "cherry"]
字长 = {word: len(word) for word in 单词}
print(字长)  # {'apple': 5, 'banana': 6, 'cherry': 6}

# 键值互换
原字典 = {"a": 1, "b": 2, "c": 3}
反转字典 = {v: k for k, v in 原字典.items()}
print(反转字典)  # {1: 'a', 2: 'b', 3: 'c'}

# 条件过滤
成绩 = {"张三": 85, "李四": 62, "王五": 91, "赵六": 54}
及格 = {k: v for k, v in 成绩.items() if v >= 60}
print(及格)  # {'张三': 85, '李四': 62, '王五': 91}
```

---

## 3. 集合推导式（Set Comprehension）

```python
# 语法：{表达式 for 变量 in 可迭代对象}
# 与列表推导式的区别：使用 {} 而不是 []，结果自动去重

数字 = [1, 2, 2, 3, 3, 3, 4]
唯一平方 = {x**2 for x in 数字}
print(唯一平方)  # {1, 4, 9, 16}（无重复，无序）

# 提取所有出现的字母（自动去重）
句子 = "hello world"
字母集合 = {c for c in 句子 if c.isalpha()}
print(字母集合)  # {'h', 'e', 'l', 'o', 'w', 'r', 'd'}
```

---

## 4. 生成器表达式（Generator Expression）

### 4.1 语法对比

```
列表推导式：[x**2 for x in range(1000)]  ← 立即创建所有元素
生成器表达式：(x**2 for x in range(1000)) ← 按需计算，不占内存
```

### 4.2 内存对比

```
列表推导式：
┌──────────────────────────────────┐
│ [0, 1, 4, 9, 16, 25, ... 998001] │  全部存在内存中
└──────────────────────────────────┘  内存占用：大

生成器表达式：
┌──────────┐
│ generator │  只存储当前状态
└──────────┘  内存占用：极小
     ↓ 每次 next() 时才计算下一个值
```

```python
import sys

# 内存对比
列表 = [x**2 for x in range(10000)]
生成器 = (x**2 for x in range(10000))

print(f"列表占用内存: {sys.getsizeof(列表)} 字节")     # ~85k 字节
print(f"生成器占用内存: {sys.getsizeof(生成器)} 字节")  # ~104 字节
```

### 4.3 使用生成器表达式的场景

```python
# 适合用生成器的场景：数据量大，只需遍历一次
总和 = sum(x**2 for x in range(1000000))  # 不需要 []
最大值 = max(len(line) for line in open("大文件.txt"))

# 不适合的场景：需要多次遍历、需要索引访问
gen = (x**2 for x in range(10))
print(list(gen))   # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
print(list(gen))   # []  ← 生成器耗尽后无法重用！
```

---

## 5. 迭代器协议：iter() 与 next()

### 5.1 可迭代对象 vs 迭代器

```
┌────────────────────────────────────────────────────┐
│                   可迭代对象                        │
│  list, tuple, str, dict, set, range, file...       │
│                                                    │
│  特征：实现了 __iter__() 方法                       │
│  调用 iter() 返回一个迭代器                         │
└───────────────────────┬────────────────────────────┘
                        │ iter()
                        ↓
┌────────────────────────────────────────────────────┐
│                    迭代器                           │
│                                                    │
│  特征：实现了 __iter__() 和 __next__() 方法         │
│  调用 next() 返回下一个值                           │
│  耗尽时抛出 StopIteration                          │
└────────────────────────────────────────────────────┘
```

```python
# 手动使用迭代器
my_list = [10, 20, 30]
it = iter(my_list)        # 创建迭代器

print(next(it))  # 10
print(next(it))  # 20
print(next(it))  # 30
# print(next(it))  # 抛出 StopIteration！
```

### 5.2 StopIteration

`StopIteration` 是迭代结束的信号，`for` 循环内部自动处理它。

```python
# for 循环的内部实现原理
def 模拟for循环(iterable):
    it = iter(iterable)
    while True:
        try:
            value = next(it)
            print(value)        # 循环体
        except StopIteration:
            break               # 循环结束

模拟for循环([1, 2, 3])
```

### 5.3 next() 的默认值

```python
it = iter([1, 2, 3])
print(next(it, "已耗尽"))  # 1
print(next(it, "已耗尽"))  # 2
print(next(it, "已耗尽"))  # 3
print(next(it, "已耗尽"))  # 已耗尽（不抛异常）
```

---

## 总结

```
┌─────────────────────────────────────────────────────────┐
│               本章知识点总结                             │
├──────────────────────┬──────────────────────────────────┤
│  列表推导式           │  [expr for x in it if cond]      │
│  字典推导式           │  {k: v for x in it}              │
│  集合推导式           │  {expr for x in it}              │
│  生成器表达式         │  (expr for x in it) 惰性求值      │
│  iter()              │  将可迭代对象转为迭代器            │
│  next()              │  获取下一个值                     │
│  StopIteration       │  迭代结束的信号                   │
└──────────────────────┴──────────────────────────────────┘
```
