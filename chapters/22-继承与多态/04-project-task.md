# 第22章项目任务：动物园管理系统

## 业务背景

某城市动物园需要一套简单的动物档案管理系统，用于记录各类动物的信息和行为特征。动物园有多种动物，它们有共同的属性，但也有各自独特的技能。

## 技术要求

### 继承结构设计

```
Animal（基类）
├── name, age, weight
├── eat()、sleep()、info()
│
├── Mammal（哺乳动物）
│   ├── fur_color
│   ├── feed_young()
│   ├── Lion(Mammal)  —— roar(), hunt()
│   └── Dolphin(Mammal) —— swim(), echolocation()
│
└── Bird（鸟类）
    ├── wingspan
    ├── lay_eggs()
    ├── Eagle(Bird) —— fly(), hunt()
    └── Penguin(Bird) —— swim(), waddle()（不会飞）
```

### 要求实现

1. **Animal 基类**：`name`、`age`、`weight`，方法 `eat(food)`、`sleep(hours)`、`info()`
2. **Mammal 子类**：继承 Animal，新增 `fur_color`，新增 `feed_young()`，重写 `info()`
3. **Bird 子类**：继承 Animal，新增 `wingspan`，新增 `lay_eggs()`，重写 `info()`
4. **四个具体动物类**：Lion、Dolphin、Eagle、Penguin，各有独特方法
5. **多态展示函数** `morning_routine(animals)`：遍历所有动物，调用 `eat()`、`info()`

### 验收标准

- [ ] 正确使用 `super().__init__()` 传递参数
- [ ] 每个具体类有至少2个独特方法
- [ ] `morning_routine()` 函数体现多态（不判断类型，直接调用共有方法）
- [ ] `isinstance` 用于某处类型检查（如统计哺乳动物数量）
- [ ] 打印 `Lion.__mro__` 验证继承链

## 示例输出

```
=== 早间例行活动 ===
[狮子-辛巴] 正在吃 牛肉
  名字：辛巴 | 类型：Lion | 年龄：4岁 | 毛色：黄色
[海豚-波波] 正在吃 鱼
  名字：波波 | 类型：Dolphin | 年龄：6岁 | 毛色：灰色
...

=== 动物园统计 ===
哺乳动物：2只
鸟类：2只

Lion 的继承链：Lion → Mammal → Animal → object
```

## 扩展挑战（可选）

- 添加 `Aquatic`（水生）Mixin，让 `Dolphin` 和 `Penguin` 共享 `swim()` 方法
- 实现 `Zoo` 容器类，管理所有动物，支持按类型筛选
