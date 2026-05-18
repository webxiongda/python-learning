# 第10章：里程碑：Python SE小项目 — 项目任务

## 项目名称

学生成绩管理系统（CLI）

## 目标

把前 1-9 章的基础能力整合成一个可运行、可测试的命令行程序。重点不是界面复杂度，而是输入校验、数据结构、文件读写、异常处理和函数拆分。

## 交付目录

在 `projects/chapter-10/` 下完成：

```text
projects/chapter-10/
├── README.md
├── student_scores/
│   ├── __init__.py
│   ├── models.py
│   ├── storage.py
│   ├── services.py
│   └── cli.py
├── tests/
│   ├── test_services.py
│   └── test_storage.py
└── data/
    └── students.json
```

## 功能要求

- 学生信息：新增、查询、删除学生，字段至少包含 `id`、`name`、`scores`。
- 成绩管理：为学生添加课程成绩，成绩范围为 0-100。
- 统计能力：计算单个学生平均分、班级平均分、最高分、最低分。
- 排名能力：按平均分输出排名，分数相同时按姓名排序。
- 持久化：使用 JSON 文件保存和读取数据。
- CLI 命令：至少支持 `add-student`、`add-score`、`list`、`rank`、`stats`。

## 设计约束

- 业务函数不能直接 `print`，必须返回结构化结果。
- 文件读写集中在 `storage.py`，业务规则集中在 `services.py`。
- CLI 只负责解析参数和展示结果。
- 所有用户输入都要校验，错误信息必须说明哪个字段错了。

## 测试要求

- `pytest` 至少覆盖 12 个用例。
- 必测场景：空学生列表、重复学号、非法成绩、删除不存在学生、JSON 文件不存在、排名并列。
- 文件读写测试使用临时目录，不污染真实 `data/`。

## 运行命令

```bash
python -m student_scores.cli add-student --id 1 --name Alice
python -m student_scores.cli add-score --id 1 --course math --score 95
python -m student_scores.cli list
python -m student_scores.cli rank
python -m pytest
```

## 阶段拆分

1. **最小可运行版**：先实现内存版新增学生、添加成绩、列表展示，不接文件。
2. **持久化版**：加入 JSON 读取和保存，处理文件不存在、空文件、损坏 JSON。
3. **统计版**：加入平均分、最高分、最低分和排名，确保空数据不会崩溃。
4. **测试版**：把服务函数和存储函数分别测试，不通过 CLI 断言业务结果。
5. **整理版**：补 README、示例数据、错误记录和项目复盘。

## 完成定义

这个项目完成时，你应该能解释清楚：

- 为什么业务函数不应该直接打印结果。
- 为什么文件路径不应该散落在多个函数中。
- JSON 数据结构如何设计，后续如果换成数据库要改哪一层。
- 异常应该在哪里抛出，CLI 层应该如何转成用户能看懂的消息。
- 测试为什么要覆盖“空数据、重复数据、非法数据、文件不存在”。

## 验收清单

- [ ] CLI 命令能从空数据文件开始运行。
- [ ] 数据能保存到 JSON，并能再次读取。
- [ ] 核心业务逻辑有单元测试。
- [ ] 异常路径有明确错误信息。
- [ ] README 写清运行方式、数据格式和设计取舍。
- [ ] 至少记录 1 个真实踩坑到根目录 `mistakes.md`。
