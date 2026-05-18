# 第21章：面向对象入门 — Demo 演示

## Demo 1：最简单的类

```python
# demo1_basic_class.py
# 定义一个最基本的类

class Dog:
    """表示一只狗的类"""
    
    # 类属性：所有狗共享
    species = "犬科动物"
    
    def __init__(self, name, age, breed):
        # 实例属性：每只狗各自独有
        self.name = name
        self.age = age
        self.breed = breed
    
    def bark(self):
        """狗叫方法"""
        print(f"{self.name} 说：汪汪汪！")
    
    def introduce(self):
        """自我介绍"""
        print(f"我是{self.name}，{self.age}岁，品种：{self.breed}")
        print(f"我是{self.species}")


# 创建两个不同的狗实例
dog1 = Dog("旺财", 3, "柴犬")
dog2 = Dog("小白", 1, "拉布拉多")

dog1.introduce()
dog1.bark()
print()
dog2.introduce()
dog2.bark()

# 访问类属性
print(f"\n类属性（通过实例）：{dog1.species}")
print(f"类属性（通过类名）：{Dog.species}")

# 查看实例的属性字典
print(f"\ndog1的属性：{dog1.__dict__}")
print(f"dog2的属性：{dog2.__dict__}")
```

```
# 预期输出：
我是旺财，3岁，品种：柴犬
我是犬科动物
旺财 说：汪汪汪！

我是小白，1岁，品种：拉布拉多
我是犬科动物
小白 说：汪汪汪！

类属性（通过实例）：犬科动物
类属性（通过类名）：犬科动物

dog1的属性：{'name': '旺财', 'age': 3, 'breed': '柴犬'}
dog2的属性：{'name': '小白', 'age': 1, 'breed': '拉布拉多'}
```

---

## Demo 2：银行账户类

```python
# demo2_bank_account.py
# 模拟银行账户的存取款操作

class BankAccount:
    """银行账户类"""
    
    # 类属性：银行名称
    bank_name = "Python银行"
    # 类属性：账户计数器
    account_count = 0
    
    def __init__(self, owner, initial_balance=0):
        self.owner = owner
        self.balance = initial_balance
        # 每创建一个账户，计数器加1
        BankAccount.account_count += 1
        # 生成账户号码
        self.account_id = f"ACC{BankAccount.account_count:04d}"
    
    def deposit(self, amount):
        """存款"""
        if amount <= 0:
            print("存款金额必须大于0！")
            return False
        self.balance += amount
        print(f"[{self.account_id}] {self.owner} 存入 ¥{amount:.2f}，"
              f"当前余额：¥{self.balance:.2f}")
        return True
    
    def withdraw(self, amount):
        """取款"""
        if amount <= 0:
            print("取款金额必须大于0！")
            return False
        if amount > self.balance:
            print(f"余额不足！当前余额：¥{self.balance:.2f}，"
                  f"尝试取款：¥{amount:.2f}")
            return False
        self.balance -= amount
        print(f"[{self.account_id}] {self.owner} 取出 ¥{amount:.2f}，"
              f"当前余额：¥{self.balance:.2f}")
        return True
    
    def get_balance(self):
        """查询余额"""
        print(f"[{self.account_id}] {self.owner} 的余额：¥{self.balance:.2f}")
        return self.balance


# 创建账户
acc1 = BankAccount("张三", 1000)
acc2 = BankAccount("李四", 500)

print(f"=== {BankAccount.bank_name} ===")
print(f"当前账户总数：{BankAccount.account_count}\n")

# 操作账户
acc1.deposit(500)
acc1.withdraw(200)
acc1.get_balance()

print()
acc2.deposit(1000)
acc2.withdraw(2000)  # 余额不足
acc2.get_balance()

print(f"\n所有账户总数：{BankAccount.account_count}")
```

```
# 预期输出：
=== Python银行 ===
当前账户总数：2

[ACC0001] 张三 存入 ¥500.00，当前余额：¥1500.00
[ACC0001] 张三 取出 ¥200.00，当前余额：¥1300.00
[ACC0001] 张三 的余额：¥1300.00

[ACC0002] 李四 存入 ¥1000.00，当前余额：¥1500.00
余额不足！当前余额：¥1500.00，尝试取款：¥2000.00
[ACC0002] 李四 的余额：¥1500.00

所有账户总数：2
```

---

## Demo 3：学生成绩管理

```python
# demo3_student.py
# 学生成绩管理类，展示实例方法的综合运用

class Student:
    """学生类"""
    
    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        self.scores = {}  # 科目 -> 分数
    
    def add_score(self, subject, score):
        """添加成绩"""
        if not (0 <= score <= 100):
            print(f"成绩 {score} 不合法，必须在0-100之间")
            return
        self.scores[subject] = score
        print(f"{self.name} 的{subject}成绩录入：{score}分")
    
    def get_average(self):
        """计算平均分"""
        if not self.scores:
            return 0
        return sum(self.scores.values()) / len(self.scores)
    
    def get_grade(self):
        """获取等级"""
        avg = self.get_average()
        if avg >= 90:
            return "优秀"
        elif avg >= 80:
            return "良好"
        elif avg >= 70:
            return "中等"
        elif avg >= 60:
            return "及格"
        else:
            return "不及格"
    
    def report(self):
        """打印成绩报告"""
        print(f"\n{'='*30}")
        print(f"学号：{self.student_id}  姓名：{self.name}")
        print(f"{'='*30}")
        if not self.scores:
            print("暂无成绩记录")
            return
        for subject, score in self.scores.items():
            bar = "█" * (score // 10) + "░" * (10 - score // 10)
            print(f"{subject:6s}  [{bar}]  {score:3d}分")
        print(f"{'─'*30}")
        print(f"平均分：{self.get_average():.1f}  综合评价：{self.get_grade()}")


# 创建学生
s1 = Student("20240001", "王小明")
s2 = Student("20240002", "李小红")

# 录入成绩
s1.add_score("语文", 85)
s1.add_score("数学", 92)
s1.add_score("英语", 78)
s1.add_score("物理", 101)  # 非法成绩

s2.add_score("语文", 95)
s2.add_score("数学", 88)
s2.add_score("英语", 91)

# 打印报告
s1.report()
s2.report()
```

```
# 预期输出：
王小明 的语文成绩录入：85分
王小明 的数学成绩录入：92分
王小明 的英语成绩录入：78分
成绩 101 不合法，必须在0-100之间
李小红 的语文成绩录入：95分
李小红 的数学成绩录入：88分
李小红 的英语成绩录入：91分

==============================
学号：20240001  姓名：王小明
==============================
语文    [████████░░]   85分
数学    [█████████░]   92分
英语    [███████░░░]   78分
──────────────────────────────
平均分：85.0  综合评价：良好

==============================
学号：20240002  姓名：李小红
==============================
语文    [█████████░]   95分
数学    [████████░░]   88分
英语    [█████████░]   91分
──────────────────────────────
平均分：91.3  综合评价：优秀
```

---

## Demo 4：类属性 vs 实例属性的陷阱

```python
# demo4_class_vs_instance_attr.py
# 深入理解类属性和实例属性的区别与陷阱

class Config:
    """配置类，演示属性陷阱"""
    
    # 类属性
    debug = False
    tags = []         # 危险！可变类属性
    settings = {}     # 危险！可变类属性
    
    def __init__(self, name):
        self.name = name


print("=== 不可变类属性 ===")
c1 = Config("服务1")
c2 = Config("服务2")

# 通过实例"修改"不可变类属性，实际上创建了实例属性
c1.debug = True
print(f"c1.debug = {c1.debug}")        # True（实例属性）
print(f"c2.debug = {c2.debug}")        # False（仍是类属性）
print(f"Config.debug = {Config.debug}")  # False（类属性未变）

print("\n=== 可变类属性的陷阱 ===")
c3 = Config("服务3")
c4 = Config("服务4")

# 修改可变类属性，会影响所有实例！
c3.tags.append("重要")  # 这是修改类属性，不是创建实例属性
c4.tags.append("紧急")

print(f"c3.tags = {c3.tags}")    # ['重要', '紧急']  ← 意外！
print(f"c4.tags = {c4.tags}")    # ['重要', '紧急']  ← 意外！
print(f"Config.tags = {Config.tags}")  # ['重要', '紧急']

print("\n=== 正确做法：在__init__中初始化可变属性 ===")

class SafeConfig:
    debug = False
    
    def __init__(self, name):
        self.name = name
        self.tags = []     # 每个实例独立的列表
        self.settings = {} # 每个实例独立的字典

sc1 = SafeConfig("服务A")
sc2 = SafeConfig("服务B")

sc1.tags.append("重要")
sc2.tags.append("测试")

print(f"sc1.tags = {sc1.tags}")   # ['重要']
print(f"sc2.tags = {sc2.tags}")   # ['测试']  ← 互不影响
```

```
# 预期输出：
=== 不可变类属性 ===
c1.debug = True
c2.debug = False
Config.debug = False

=== 可变类属性的陷阱 ===
c3.tags = ['重要', '紧急']
c4.tags = ['重要', '紧急']
Config.tags = ['重要', '紧急']

=== 正确做法：在__init__中初始化可变属性 ===
sc1.tags = ['重要']
sc2.tags = ['测试']
```

---

## Demo 5：完整的图书类

```python
# demo5_book.py
# 综合运用类定义、__init__、实例属性、类属性和实例方法

class Book:
    """图书类"""
    
    # 类属性
    total_books = 0
    
    def __init__(self, title, author, price, isbn):
        self.title = title
        self.author = author
        self.price = price
        self.isbn = isbn
        self.is_available = True  # 是否可借
        self.borrow_count = 0     # 被借次数
        Book.total_books += 1
    
    def borrow(self, reader_name):
        """借出图书"""
        if not self.is_available:
            print(f"《{self.title}》已被借出，暂不可借")
            return False
        self.is_available = False
        self.borrow_count += 1
        print(f"{reader_name} 成功借出《{self.title}》（第{self.borrow_count}次被借）")
        return True
    
    def return_book(self, reader_name):
        """归还图书"""
        if self.is_available:
            print(f"《{self.title}》未被借出，无需归还")
            return False
        self.is_available = True
        print(f"{reader_name} 归还了《{self.title}》")
        return True
    
    def info(self):
        """显示图书信息"""
        status = "可借" if self.is_available else "已借出"
        print(f"书名：《{self.title}》 | 作者：{self.author} | "
              f"价格：¥{self.price} | 状态：{status} | 借阅次数：{self.borrow_count}")


# 创建图书
b1 = Book("Python编程", "Guido", 89.0, "978-7-111-1")
b2 = Book("算法导论", "Cormen", 128.0, "978-7-111-2")
b3 = Book("设计模式", "GoF", 79.0, "978-7-111-3")

print(f"图书馆共有 {Book.total_books} 本书\n")

b1.info()
b2.info()
b3.info()

print()
b1.borrow("张三")
b1.borrow("李四")  # 已被借出
b1.return_book("张三")
b1.borrow("李四")  # 现在可以借了

print()
b1.info()
```

```
# 预期输出：
图书馆共有 3 本书

书名：《Python编程》 | 作者：Guido | 价格：¥89.0 | 状态：可借 | 借阅次数：0
书名：《算法导论》 | 作者：Cormen | 价格：¥128.0 | 状态：可借 | 借阅次数：0
书名：《设计模式》 | 作者：GoF | 价格：¥79.0 | 状态：可借 | 借阅次数：0

张三 成功借出《Python编程》（第1次被借）
《Python编程》已被借出，暂不可借
张三 归还了《Python编程》
李四 成功借出《Python编程》（第2次被借）

书名：《Python编程》 | 作者：Guido | 价格：¥89.0 | 状态：已借出 | 借阅次数：2
```
