# 第03章：控制流程 — Demo 篇

## Demo 1：成绩等级分类系统

```python
# demo1_grade_system.py
# 目标：用 if/elif/else 实现多级条件分支

scores = [95, 82, 71, 65, 55, 100, 0]

print(f"{'分数':<8} {'等级':<6} {'评语'}")
print("-" * 30)

for score in scores:
    if not (0 <= score <= 100):
        print(f"{score:<8} {'无效':<6} 分数超出范围")
        continue

    if score >= 90:
        grade, comment = "A", "优秀！继续保持"
    elif score >= 80:
        grade, comment = "B", "良好，还有提升空间"
    elif score >= 70:
        grade, comment = "C", "中等，需要努力"
    elif score >= 60:
        grade, comment = "D", "及格，勉强过关"
    else:
        grade, comment = "F", "不及格，需要补考"

    print(f"{score:<8} {grade:<6} {comment}")
```

```
# 预期输出：
分数     等级   评语
------------------------------
95       A      优秀！继续保持
82       B      良好，还有提升空间
71       C      中等，需要努力
65       D      及格，勉强过关
55       F      不及格，需要补考
100      A      优秀！继续保持
0        F      不及格，需要补考
```

---

## Demo 2：range() 的各种用法

```python
# demo2_range_demo.py
# 目标：掌握 range() 的三种参数形式

print("=== range(stop) ===")
print(list(range(6)))     # [0, 1, 2, 3, 4, 5]

print("\n=== range(start, stop) ===")
print(list(range(3, 8)))  # [3, 4, 5, 6, 7]

print("\n=== range(start, stop, step) 正步长 ===")
print(list(range(0, 20, 3)))  # [0, 3, 6, 9, 12, 15, 18]

print("\n=== range(start, stop, step) 负步长（倒序）===")
print(list(range(10, 0, -1)))  # [10, 9, 8, ..., 1]

print("\n=== 实际应用：打印星形三角 ===")
for i in range(1, 6):
    print("★" * i)

print("\n=== 实际应用：累加求和 ===")
total = 0
for i in range(1, 101):
    total += i
print(f"1 + 2 + ... + 100 = {total}")

print("\n=== 实际应用：找出 100 以内所有 3 和 5 的公倍数 ===")
result = []
for i in range(1, 101):
    if i % 15 == 0:
        result.append(i)
print(result)
```

```
# 预期输出：
=== range(stop) ===
[0, 1, 2, 3, 4, 5]

=== range(start, stop) ===
[3, 4, 5, 6, 7]

=== range(start, stop, step) 正步长 ===
[0, 3, 6, 9, 12, 15, 18]

=== range(start, stop, step) 负步长（倒序）===
[10, 9, 8, 7, 6, 5, 4, 3, 2, 1]

=== 实际应用：打印星形三角 ===
★
★★
★★★
★★★★
★★★★★

=== 实际应用：累加求和 ===
1 + 2 + ... + 100 = 5050

=== 实际应用：找出 100 以内所有 3 和 5 的公倍数 ===
[15, 30, 45, 60, 75, 90]
```

---

## Demo 3：break 和 continue 对比实验

```python
# demo3_break_continue.py
# 目标：通过对比直观理解 break 和 continue 的区别

data = [3, 7, 2, 8, 1, 9, 4, 6, 5]

print("=== 原始数据 ===")
print(data)

print("\n=== 找到第一个大于5的数（break）===")
for num in data:
    print(f"  检查 {num}...", end="")
    if num > 5:
        print(f" ← 找到了！")
        break
    print()

print("\n=== 跳过所有偶数（continue）===")
print("奇数列表：", end="")
for num in data:
    if num % 2 == 0:
        continue
    print(num, end=" ")
print()

print("\n=== while + break：模拟菜单 ===")
menu_shown = False
choices = ["1", "2", "q"]  # 模拟用户依次输入
for choice in choices:
    if not menu_shown:
        print("\n菜单：1.查询  2.添加  q.退出")
        menu_shown = True
    print(f"[模拟输入] 你的选择：{choice}")
    if choice == "q":
        print("再见！")
        break
    elif choice == "1":
        print("  → 执行查询操作")
    elif choice == "2":
        print("  → 执行添加操作")
    else:
        print("  → 无效选项，请重新输入")
```

```
# 预期输出：
=== 原始数据 ===
[3, 7, 2, 8, 1, 9, 4, 6, 5]

=== 找到第一个大于5的数（break）===
  检查 3...
  检查 7... ← 找到了！

=== 跳过所有偶数（continue）===
奇数列表：3 7 1 9 5

=== while + break：模拟菜单 ===

菜单：1.查询  2.添加  q.退出
[模拟输入] 你的选择：1
  → 执行查询操作
[模拟输入] 你的选择：2
  → 执行添加操作
[模拟输入] 你的选择：q
再见！
```

---

## Demo 4：嵌套循环 — 九九乘法表

```python
# demo4_multiplication_table.py
# 目标：用嵌套 for 循环实现经典的九九乘法表

print("=== 九九乘法表 ===\n")
for i in range(1, 10):
    for j in range(1, i + 1):  # j 只到 i，形成下三角
        result = i * j
        print(f"{j}×{i}={result:<3}", end=" ")
    print()  # 每行结束换行

print("\n=== 用嵌套循环打印菱形 ===")
n = 5  # 菱形半高
# 上半部分（含中间行）
for i in range(1, n + 1):
    spaces = " " * (n - i)
    stars = "* " * i
    print(spaces + stars)
# 下半部分
for i in range(n - 1, 0, -1):
    spaces = " " * (n - i)
    stars = "* " * i
    print(spaces + stars)
```

```
# 预期输出：
=== 九九乘法表 ===

1×1=1
1×2=2   2×2=4
1×3=3   2×3=6   3×3=9
1×4=4   2×4=8   3×4=12  4×4=16
1×5=5   2×5=10  3×5=15  4×5=20  5×5=25
1×6=6   2×6=12  3×6=18  4×6=24  5×6=30  6×6=36
1×7=7   2×7=14  3×7=21  4×7=28  5×7=35  6×7=42  7×7=49
1×8=8   2×8=16  3×8=24  4×8=32  5×8=40  6×8=48  7×8=56  8×8=64
1×9=9   2×9=18  3×9=27  4×9=36  5×9=45  6×9=54  7×9=63  8×9=72  9×9=81

=== 用嵌套循环打印菱形 ===
    *
   * *
  * * *
 * * * *
* * * * *
 * * * *
  * * *
   * *
    *
```

---

## Demo 5：while 循环 — 猜数字游戏

```python
# demo5_guess_game.py
# 目标：用 while 循环实现一个完整的猜数字游戏

import random

# 生成 1-100 之间的随机整数
secret = random.randint(1, 100)
attempts = 0
max_attempts = 7

print("=" * 35)
print("  猜数字游戏（1-100）")
print(f"  你有 {max_attempts} 次机会")
print("=" * 35)

while attempts < max_attempts:
    attempts += 1
    remaining = max_attempts - attempts

    try:
        guess = int(input(f"\n第{attempts}次猜测（还剩{remaining}次）："))
    except ValueError:
        print("请输入整数！")
        attempts -= 1  # 无效输入不计次数
        continue

    if guess < 1 or guess > 100:
        print("请输入 1-100 之间的数！")
        attempts -= 1
        continue

    if guess == secret:
        print(f"\n🎉 恭喜！猜对了！答案是 {secret}，共猜了 {attempts} 次。")
        break
    elif guess < secret:
        hint = "太小了" if secret - guess > 10 else "再大一点点"
        print(f"  {hint}，往大猜！")
    else:
        hint = "太大了" if guess - secret > 10 else "再小一点点"
        print(f"  {hint}，往小猜！")
else:
    # while 循环正常结束（用完次数），else 分支执行
    print(f"\n😢 次数用完！正确答案是 {secret}，下次加油！")
```

```
# 预期输出（示例，随机数不同每次不同）：
===================================
  猜数字游戏（1-100）
  你有 7 次机会
===================================

第1次猜测（还剩6次）：50
  太小了，往大猜！

第2次猜测（还剩5次）：75
  再小一点点，往小猜！

第3次猜测（还剩4次）：68

🎉 恭喜！猜对了！答案是 68，共猜了 3 次。
```
