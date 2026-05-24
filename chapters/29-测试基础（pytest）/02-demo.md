# 第29章：测试基础（pytest） — Demo 篇

## Demo 1：参数化测试和临时目录 fixture

### 目标

用一个最小、可运行、可修改的例子验证本章核心能力。

### 示例代码

```python
def normalize_text(value):
    if value is None:
        raise ValueError("value 不能为空")
    text = str(value).strip()
    if not text:
        raise ValueError("value 不能是空字符串")
    return text

def build_record(raw_value, tags=None):
    tags = tags or []
    clean_tags = sorted({normalize_text(tag).lower() for tag in tags if str(tag).strip()})
    return {"title": normalize_text(raw_value), "tags": clean_tags, "source": "测试基础（pytest）"}

print(build_record("参数化测试和临时目录 fixture", ["Python", " api ", "Python"]))
```

### 运行方式

```bash
python demo_29.py
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
        print(case, "=>", build_record(case, ["Python", "AI", "python"]))
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
projects/chapter-29/
├── README.md
├── src/
│   └── main.py
└── tests/
    └── test_main.py
```

## 常见错误

- 只测一条成功路径
- 过度 mock 自己的代码
- 测试名不能说明行为

## 复盘问题

1. 本章 Demo 里哪个函数最值得写测试？
2. 如果把它接到 FastAPI 路由，路由层应该只做什么？
3. 如果后续要支持 AI 应用场景，哪些输入输出需要记录？
