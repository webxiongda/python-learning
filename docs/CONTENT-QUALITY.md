# Content Quality Standard

## 目标

学习文档必须服务于掌握能力，而不是堆文字。每个章节都要能推动一次“理解、运行、验收、复盘”闭环。

## 章节标准

每章固定包含 5 个文件：

- `01-theory.md`：讲清概念、场景、常见坑和验收口径。
- `02-demo.md`：给出可运行或可手动推演的示例。
- `03-check.md`：包含概念题、代码改造题、项目应用题和费曼输出题。
- `04-project-task.md`：说明项目目录、功能、测试和验收。
- `review.md`：记录复习、错题、费曼输出和下一步。

## 合格内容

- 章节标题、核心主题和任务目标一致。
- Demo 不只打印固定字符串，至少能体现输入、处理和输出。
- 验收题必须要求解释边界条件或改造代码。
- 项目任务必须落到 `projects/chapter-xx/`。
- 错题和复习必须能回流到根目录文件。

## 不合格内容

- 只有概念解释，没有运行或验收。
- 多章复用同一段泛化文案。
- 项目任务只说“实现几个函数”，没有功能、测试和验收。
- 业务函数只 `print`，没有结构化返回值。
- 没有异常路径、空输入、非法输入或重复数据测试。

## 自动检查

运行：

```bash
make all
```

等价于：

```bash
python3 -m py_compile tools/check_learning_repo.py tools/generate_missing_chapters.py tools/refresh_generic_chapters.py
python3 tools/check_learning_repo.py
```

如果发现模板化内容：

```bash
make refresh-generic
make all
```

## 人工抽查

每次大批量改动后，至少抽查：

- 一个基础章节，例如第 05 章。
- 一个 Web 章节，例如第 44 或 50 章。
- 一个工程化章节，例如第 52 或 53 章。
- 一个扩展章节，例如第 57 或 60 章。
