# 第60章：总结与进阶路线 — Demo 篇

## Demo 1：简历项目描述和后续路线规划

### 目标

用一个最小、可运行、可修改的例子验证本章核心能力。

### 示例代码

```python
def describe_project():
    return {
        "name": "Python FastAPI AI Learning Workbench",
        "problem": "把学习路线、强验收、复习和 AI 面试训练集中到一个系统",
        "backend": ["FastAPI", "SQLAlchemy", "SQLite", "JWT"],
        "ai_ready": ["streaming", "RAG boundary", "interview scoring service"],
        "evidence": ["tests passing", "local demo", "README", "screenshots"],
    }

print(describe_project())
```

### 运行方式

```bash
python demo_60.py
```

如果本章示例是配置文件或 workflow，把代码保存为对应文件后按文档命令运行。

### 观察点

- 输出是否是结构化结果，而不是散乱打印。
- 输入为空、重复或非法时是否能得到清晰反馈。
- 哪些部分可以拆成函数并单独测试。

## Demo 2：加入边界条件

把 Demo 1 改造成下面的调用方式：

```python
cases = [
    "normal input",
    "  input with spaces  ",
    "",
    None,
]

for case in cases:
    try:
        print(case, "=>", "把这里替换成 Demo 1 的核心函数调用")
    except Exception as exc:
        print(case, "=> ERROR:", exc)
```

要求你能解释：

- 哪些输入应该被接受。
- 哪些输入应该抛错。
- 错误信息是否能帮助定位问题。

## Demo 3：接近项目的分层

把代码拆成三层：

- `load_*`：读取输入，可以来自文件、HTTP 请求或数据库。
- `process_*`：纯业务处理，尽量只接收参数并返回结构化结果。
- `save_*` 或 `render_*`：保存或展示结果。

建议目录：

```text
projects/chapter-60/
├── README.md
├── src/
│   └── main.py
└── tests/
    └── test_main.py
```

## 常见错误

- 只列技术栈不列成果
- 没有可运行链接或截图
- 进阶路线没有优先级

## 复盘问题

1. 本章 Demo 里哪个函数最值得写测试？
2. 如果把它接到 FastAPI 路由，路由层应该只做什么？
3. 如果后续要支持 AI 应用场景，哪些输入输出需要记录？
