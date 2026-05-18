# 第12章：推导式与迭代器 — Demo 示例

## Demo 1：列表推导式实战

```python
# 各种列表推导式用法

# 1. 基础：过滤和转换
原始数据 = ["  Python  ", " Java ", "Go", "  Rust  ", "C++"]
清理后 = [s.strip().upper() for s in 原始数据 if len(s.strip()) > 2]
print("清理后:", 清理后)

# 2. 嵌套推导式：生成乘法表
乘法表 = [f"{i}×{j}={i*j}" for i in range(1, 4) for j in range(1, 4)]
for item in 乘法表:
    print(f"  {item}")

# 3. 扁平化嵌套列表
嵌套列表 = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
扁平化 = [x for sublist in 嵌套列表 for x in sublist]
print("扁平化:", 扁平化)

# 4. 条件表达式（三元）在推导式中
数字 = range(-5, 6)
符号 = ["正" if x > 0 else "负" if x < 0 else "零" for x in 数字]
print("符号:", 符号)
```

```
# 预期输出：
清理后: ['PYTHON', 'JAVA', 'RUST', 'C++']
  1×1=1
  1×2=2
  1×3=3
  2×1=2
  2×2=4
  2×3=6
  3×1=3
  3×2=6
  3×3=9
扁平化: [1, 2, 3, 4, 5, 6, 7, 8, 9]
符号: ['负', '负', '负', '负', '负', '零', '正', '正', '正', '正', '正']
```

---

## Demo 2：字典推导式与集合推导式

```python
# 字典和集合推导式的实用场景

# 1. 快速构建索引（字典推导式）
学生成绩 = [
    ("张三", 85), ("李四", 92), ("王五", 78),
    ("赵六", 95), ("钱七", 61)
]
成绩字典 = {name: score for name, score in 学生成绩}
print("成绩字典:", 成绩字典)

# 2. 数据分级（条件字典推导式）
分级 = {
    name: "优秀" if score >= 90 else "良好" if score >= 75 else "及格"
    for name, score in 学生成绩
}
print("分级:", 分级)

# 3. 集合推导式：提取唯一值
文章 = "the quick brown fox jumps over the lazy dog"
唯一字母 = {char for char in 文章 if char.isalpha()}
print(f"唯一字母数量: {len(唯一字母)}")
print(f"字母集合: {sorted(唯一字母)}")

# 4. 找出两个列表共有的元素（集合推导式优化）
列表A = [1, 2, 3, 4, 5, 2, 3]
列表B = [3, 4, 5, 6, 7, 4, 5]
集合A = {x for x in 列表A}
集合B = {x for x in 列表B}
共有 = 集合A & 集合B
print("共有元素:", 共有)
```

```
# 预期输出：
成绩字典: {'张三': 85, '李四': 92, '王五': 78, '赵六': 95, '钱七': 61}
分级: {'张三': '良好', '李四': '优秀', '王五': '良好', '赵六': '优秀', '钱七': '及格'}
唯一字母数量: 26
字母集合: ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
共有元素: {3, 4, 5}
```

---

## Demo 3：生成器表达式内存对比

```python
import sys
import time

# 对比列表推导式和生成器表达式的内存使用

N = 1_000_000

# 内存对比
列表 = [x**2 for x in range(N)]
生成器 = (x**2 for x in range(N))

print(f"列表内存占用:    {sys.getsizeof(列表):,} 字节 ({sys.getsizeof(列表)//1024} KB)")
print(f"生成器内存占用:  {sys.getsizeof(生成器):,} 字节")
print(f"内存比例: 列表是生成器的 {sys.getsizeof(列表)//sys.getsizeof(生成器)} 倍")

# 时间对比（求和）
start = time.perf_counter()
total1 = sum([x**2 for x in range(N)])  # 列表
t1 = time.perf_counter() - start

start = time.perf_counter()
total2 = sum(x**2 for x in range(N))   # 生成器
t2 = time.perf_counter() - start

print(f"\n列表求和时间:   {t1:.3f} 秒")
print(f"生成器求和时间: {t2:.3f} 秒")
print(f"结果相同: {total1 == total2}")

# 生成器只能遍历一次
gen = (x for x in range(5))
print("\n第一次遍历:", list(gen))
print("第二次遍历:", list(gen))  # 空！
```

```
# 预期输出（数值因机器而异）：
列表内存占用:    8,697,464 字节 (8494 KB)
生成器内存占用:  104 字节
内存比例: 列表是生成器的 83,629 倍

列表求和时间:   0.087 秒
生成器求和时间: 0.061 秒
结果相同: True

第一次遍历: [0, 1, 2, 3, 4]
第二次遍历: []
```

---

## Demo 4：手动实现迭代器

```python
# 实现一个自定义迭代器：斐波那契数列

class 斐波那契迭代器:
    """生成斐波那契数列的迭代器"""

    def __init__(self, 最大值):
        self.最大值 = 最大值
        self.a = 0
        self.b = 1

    def __iter__(self):
        return self  # 迭代器本身就是可迭代对象

    def __next__(self):
        if self.a > self.最大值:
            raise StopIteration  # 发出停止信号
        当前值 = self.a
        self.a, self.b = self.b, self.a + self.b
        return 当前值

# 使用 for 循环（内部自动处理 StopIteration）
print("100以内的斐波那契数列:")
for n in 斐波那契迭代器(100):
    print(n, end=" ")
print()

# 手动使用 iter() 和 next()
it = 斐波那契迭代器(20)
print("\n手动迭代:")
while True:
    value = next(it, None)  # 使用默认值避免异常
    if value is None:
        break
    print(f"  获取: {value}")
```

```
# 预期输出：
100以内的斐波那契数列:
0 1 1 2 3 5 8 13 21 34 55 89 

手动迭代:
  获取: 0
  获取: 1
  获取: 1
  获取: 2
  获取: 3
  获取: 5
  获取: 8
  获取: 13
```

---

## Demo 5：推导式性能分析

```python
import timeit

# 对比不同写法处理大量数据的性能

数据 = list(range(10000))

# 测试1：筛选偶数并求平方
def 循环写法():
    result = []
    for x in 数据:
        if x % 2 == 0:
            result.append(x**2)
    return result

def 推导式写法():
    return [x**2 for x in 数据 if x % 2 == 0]

def map_filter写法():
    return list(map(lambda x: x**2, filter(lambda x: x % 2 == 0, 数据)))

# 运行1000次，取平均
次数 = 1000
t1 = timeit.timeit(循环写法, number=次数)
t2 = timeit.timeit(推导式写法, number=次数)
t3 = timeit.timeit(map_filter写法, number=次数)

print(f"循环写法:     {t1:.3f} 秒 ({t1/次数*1000:.3f} ms/次)")
print(f"推导式写法:   {t2:.3f} 秒 ({t2/次数*1000:.3f} ms/次)")
print(f"map/filter:  {t3:.3f} 秒 ({t3/次数*1000:.3f} ms/次)")

最快 = min(t1, t2, t3)
print(f"\n推导式比循环快 {t1/t2:.1f} 倍")

# 验证结果一致性
assert 循环写法() == 推导式写法() == map_filter写法()
print("三种方法结果完全一致 ✓")
```

```
# 预期输出（数值因机器而异）：
循环写法:     0.521 秒 (0.521 ms/次)
推导式写法:   0.332 秒 (0.332 ms/次)
map/filter:  0.421 秒 (0.421 ms/次)

推导式比循环快 1.6 倍
三种方法结果完全一致 ✓
```
