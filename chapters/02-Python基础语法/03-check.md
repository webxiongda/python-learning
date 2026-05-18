# 第02章：Python 基础语法 — 自测题

---

## 题目 1：选择题

以下代码的输出是什么？

```python
x = 5
print(type(x))
x = "hello"
print(type(x))
print(x * 2)
```

A. `<class 'int'>` / `<class 'str'>` / `hellohello`
B. `int` / `str` / `hellohello`
C. 报错，x 不能从 int 改为 str
D. `<class 'int'>` / `<class 'str'>` / `10`

### 参考答案

**A**

解析：Python 是动态类型语言，变量可以随时指向不同类型的对象。`type()` 返回的是 `<class 'xxx'>` 格式。字符串乘以整数表示重复，`"hello" * 2` 结果为 `"hellohello"`。

---

## 题目 2：代码纠错题

以下代码有 3 个错误，请找出并修正：

```python
2score = 95          # 错误1
name = "Alice"
age = 25
print("姓名：" + name + "，年龄：" + age)   # 错误2
print(0.1 + 0.2 == 0.3)   # 错误3（逻辑错误，不是语法错误）
```

### 参考答案

**错误1**：变量名不能以数字开头
```python
score = 95   # 或 score_2, score2 等合法命名
```

**错误2**：字符串不能与整数直接用 `+` 拼接，需要类型转换
```python
print("姓名：" + name + "，年龄：" + str(age))
# 更好的写法（f-string）：
print(f"姓名：{name}，年龄：{age}")
```

**错误3**：浮点数精度问题导致结果为 `False`，应使用 `math.isclose()`
```python
import math
print(math.isclose(0.1 + 0.2, 0.3))  # True
```

---

## 题目 3：输出预测题

预测以下每行代码的输出（直接写结果，不要写 `<class xxx>`）：

```python
print(True + True)
print(True * 5)
print(bool(""))
print(bool(0.001))
print(10 // 3)
print(-10 // 3)
print(10 % 3)
print(2 ** 8)
print(1 < 2 < 3 < 4)
```

### 参考答案

```
2
5
False
True
3
-4
1
256
True
```

重点解析：
- `True + True`：bool 是 int 子类，True=1，所以 1+1=2
- `bool("")`：空字符串是假值，返回 False
- `bool(0.001)`：非零浮点数是真值，返回 True
- `-10 // 3`：整除向下取整，-10/3=-3.33...，向下取整为 -4（注意不是 -3！）
- `2 ** 8`：2 的 8 次方 = 256
- `1 < 2 < 3 < 4`：链式比较，等价于 True and True and True

---

## 题目 4：填空题

完成以下代码，使其输出指定结果：

```python
# 要求输出：姓名:张三, 年龄:22, 成绩:95.50
name = "张三"
age = 22
score = 95.5

# 方式1：f-string（填写横线处）
print(f"姓名:{____}, 年龄:{____}, 成绩:{score:.2f}")

# 方式2：str() 拼接（填写横线处）
print("姓名:" + ____ + ", 年龄:" + ____ + ", 成绩:" + ____)

# 变量交换：交换 a 和 b 的值，不使用临时变量
a, b = 10, 20
____, ____ = b, a
print(a, b)   # 应输出 20 10
```

### 参考答案

```python
# f-string 方式
print(f"姓名:{name}, 年龄:{age}, 成绩:{score:.2f}")

# str() 拼接方式
print("姓名:" + name + ", 年龄:" + str(age) + ", 成绩:" + str(score))

# 变量交换
a, b = b, a
```

注意：`{score:.2f}` 表示将 score 格式化为保留 2 位小数的浮点数，输出 `95.50`。

---

## 题目 5：综合应用题

编写一段代码，完成以下需求：

1. 定义变量：商品名称 `item="苹果"`，单价 `price=3.5`，数量 `qty=6`
2. 计算总价（单价 × 数量）
3. 计算打折后价格（9折）
4. 判断折后价格是否超过 20 元
5. 打印一张格式化的"购物小票"

### 参考答案

```python
# 定义变量
item = "苹果"
price = 3.5
qty = 6

# 计算
total = price * qty
discount = 0.9
discounted = total * discount

# 判断
is_over_20 = discounted > 20

# 打印小票
print("=" * 25)
print("       购物小票")
print("=" * 25)
print(f"商品：{item}")
print(f"单价：{price:.2f} 元")
print(f"数量：{qty} 件")
print(f"原价：{total:.2f} 元")
print(f"折扣：{int(discount * 10)} 折")
print(f"折后：{discounted:.2f} 元")
print(f"超过20元：{is_over_20}")
print("=" * 25)
```

预期输出：
```
=========================
       购物小票
=========================
商品：苹果
单价：3.50 元
数量：6 件
原价：21.00 元
折扣：9 折
折后：18.90 元
超过20元：False
=========================
```
