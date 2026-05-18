# 第03章：控制流程 — 自测题

---

## 题目 1：代码追踪题

手动追踪以下代码，写出所有输出行：

```python
for i in range(4):
    if i == 2:
        continue
    if i == 3:
        break
    print(f"i = {i}")
else:
    print("循环正常结束")

print("程序结束")
```

### 参考答案

```
i = 0
i = 1
程序结束
```

解析：
- `i=0`：无特殊条件，打印 `i = 0`
- `i=1`：无特殊条件，打印 `i = 1`
- `i=2`：触发 `continue`，跳过本次，不打印
- `i=3`：触发 `break`，退出循环
- `else` 块：由于循环被 `break` 中断，`else` **不执行**
- 最后打印 `程序结束`

---

## 题目 2：代码改错题

以下代码意图打印 1-20 中所有不能被 3 整除的数，但有 2 处逻辑错误，请找出并修正：

```python
for i in range(1, 20):   # 错误1
    if i % 3 == 0:       # 错误2
        print(i)
```

### 参考答案

**错误1**：`range(1, 20)` 不包含 20，应改为 `range(1, 21)`

**错误2**：`i % 3 == 0` 表示"能被3整除"，应改为 `i % 3 != 0`（不能被3整除）

修正后的代码：
```python
for i in range(1, 21):   # 包含 20
    if i % 3 != 0:       # 不能被 3 整除
        print(i, end=" ")
```

输出：`1 2 4 5 7 8 10 11 13 14 16 17 19 20`

---

## 题目 3：输出预测题

以下代码会输出什么？

```python
count = 0
i = 1
while i <= 10:
    if i % 2 == 0 and i % 3 == 0:
        count += i
    i += 1
print(f"count = {count}")
```

### 参考答案

```
count = 6
```

解析：找出 1-10 中既能被 2 整除又能被 3 整除的数（即被 6 整除）：只有 6。所以 `count = 6`。

---

## 题目 4：编程题

用 for 循环和条件判断，打印以下图案（n=5 行）：

```
*
**
***
****
*****
****
***
**
*
```

要求：不允许硬编码每行内容，必须通过循环计算每行星号数量。

### 参考答案

```python
n = 5

# 上半部分（含第5行）
for i in range(1, n + 1):
    print("*" * i)

# 下半部分（从第4行到第1行）
for i in range(n - 1, 0, -1):
    print("*" * i)
```

另一种更简洁的写法：
```python
n = 5
for i in list(range(1, n + 1)) + list(range(n - 1, 0, -1)):
    print("*" * i)
```

---

## 题目 5：综合应用题

实现一个"FizzBuzz"程序：打印 1 到 50 的数字，但：
- 3 的倍数打印 "Fizz"
- 5 的倍数打印 "Buzz"
- 既是 3 又是 5 的倍数打印 "FizzBuzz"
- 其他数字正常打印

输出格式：每行 5 个，用制表符分隔。

### 参考答案

```python
results = []
for i in range(1, 51):
    if i % 15 == 0:       # 先判断 15 的倍数（必须最先判断）
        results.append("FizzBuzz")
    elif i % 3 == 0:
        results.append("Fizz")
    elif i % 5 == 0:
        results.append("Buzz")
    else:
        results.append(str(i))

# 每行输出 5 个
for i, val in enumerate(results):
    print(f"{val:<9}", end="")
    if (i + 1) % 5 == 0:
        print()
```

预期输出（前两行）：
```
1        2        Fizz     4        Buzz
6        7        8        Fizz     10
```

关键点：必须先判断 `i % 15 == 0`（FizzBuzz），如果先判断 `i % 3 == 0` 则 15 会被错误匹配为 "Fizz"。
