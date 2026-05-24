# 第46章：数据库基础 — Demo 篇

## Demo 1：SQLite 参数化查询和事务提交

### 目标

用一个最小、可运行、可修改的例子验证本章核心能力。

### 示例代码

```python
import sqlite3
from pathlib import Path

DB_PATH = Path("learning.db")

def connect():
    return sqlite3.connect(DB_PATH)

def init_db(conn):
    conn.execute(
        "create table if not exists progress("
        "chapter_no integer primary key, title text not null, done integer not null)"
    )
    conn.commit()

def save_progress(conn, chapter_no, title, done=False):
    conn.execute(
        "insert into progress(chapter_no, title, done) values (?, ?, ?) "
        "on conflict(chapter_no) do update set title=excluded.title, done=excluded.done",
        (chapter_no, title, int(done)),
    )
    conn.commit()

def list_progress(conn):
    return conn.execute(
        "select chapter_no, title, done from progress order by chapter_no"
    ).fetchall()
```

### 运行方式

```bash
python demo_46.py
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
projects/chapter-46/
├── README.md
├── src/
│   └── main.py
└── tests/
    └── test_main.py
```

## 常见错误

- 字符串拼接 SQL
- 忘记事务提交
- 没有唯一约束导致重复数据

## 复盘问题

1. 本章 Demo 里哪个函数最值得写测试？
2. 如果把它接到 FastAPI 路由，路由层应该只做什么？
3. 如果后续要支持 AI 应用场景，哪些输入输出需要记录？
