from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_FILES = [
    "01-theory.md",
    "02-demo.md",
    "03-check.md",
    "04-project-task.md",
    "review.md",
]


def parse_chapters() -> list[dict[str, str]]:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    chapters: list[dict[str, str]] = []
    pattern = re.compile(
        r"\|\s*(\d{2})\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(L\d[^|]+?)\s*\|\s*([^|]+?)\s*\|"
    )
    for line in readme.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        no, title, topic, priority, duration = [group.strip() for group in match.groups()]
        chapters.append(
            {
                "no": no,
                "title": title,
                "topic": topic,
                "priority": priority,
                "duration": duration,
            }
        )
    return chapters


def slug(title: str) -> str:
    return (
        title.replace("：", "")
        .replace(":", "")
        .replace("/", "_")
        .replace("、", "")
        .replace(" ", "-")
    )


def chapter_dir(chapter: dict[str, str]) -> Path:
    chapters_root = ROOT / "chapters"
    existing = sorted(chapters_root.glob(f"{chapter['no']}-*"))
    if existing:
        return existing[0]
    return chapters_root / f"{chapter['no']}-{slug(chapter['title'])}"


def key_points(topic: str) -> list[str]:
    parts = re.split(r"[、,，/]+", topic)
    return [part.strip() for part in parts if part.strip()]


def code_example(chapter: dict[str, str]) -> str:
    no = chapter["no"]
    title = chapter["title"]
    examples = {
        "05": '''text = "  Python 全栈工程师  "
print(text.strip())
print(text.lower())
print(text.replace("全栈", "后端"))

name = "Alice"
score = 96.5
print(f"{name} 本次得分：{score:.1f}")''',
        "06": '''tasks = ["写需求", "写代码", "自测"]
tasks.append("提交")
print(tasks[1:3])

point = (120.5, 30.2)
x, y = point
print(f"坐标：{x}, {y}")''',
        "07": '''user = {"name": "Alice", "role": "admin"}
user["active"] = True
print(user.get("email", "未填写"))

tags = {"python", "api", "python"}
print(tags)''',
        "08": '''from pathlib import Path

path = Path("notes.txt")
path.write_text("第一行\\n第二行\\n", encoding="utf-8")

for line in path.read_text(encoding="utf-8").splitlines():
    print(line)''',
        "09": '''def parse_age(raw):
    try:
        age = int(raw)
    except ValueError as exc:
        raise ValueError("年龄必须是数字") from exc
    if age < 0:
        raise ValueError("年龄不能为负数")
    return age''',
        "15": '''# project/
#   app/
#     __init__.py
#     services.py

from app.services import create_order

order = create_order(user_id=1, amount=99)
print(order)''',
        "16": '''import re

pattern = re.compile(r"(?P<name>[\\w.-]+)@(?P<domain>[\\w.-]+)")
text = "联系 alice@example.com 或 bob@test.dev"

for match in pattern.finditer(text):
    print(match.group("name"), match.group("domain"))''',
        "17": '''from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)
deadline = now + timedelta(days=7)
print(now.isoformat())
print(deadline.strftime("%Y-%m-%d %H:%M"))''',
        "19": '''from typing import Iterable

def average(values: Iterable[float]) -> float:
    numbers = list(values)
    if not numbers:
        raise ValueError("values 不能为空")
    return sum(numbers) / len(numbers)''',
        "25": '''class User:
    count = 0

    def __init__(self, name):
        self.name = name
        User.count += 1

    @classmethod
    def from_email(cls, email):
        return cls(email.split("@")[0])

    @staticmethod
    def is_valid_email(email):
        return "@" in email''',
        "27": '''from dataclasses import dataclass
from enum import Enum

class OrderStatus(Enum):
    CREATED = "created"
    PAID = "paid"

@dataclass(frozen=True)
class Order:
    id: int
    amount: float
    status: OrderStatus = OrderStatus.CREATED''',
        "29": '''def add(a, b):
    return a + b

def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0''',
        "39": '''import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_user(username):
    logger.info("creating user", extra={"username": username})
    return {"username": username}''',
        "46": '''import sqlite3

conn = sqlite3.connect("app.db")
conn.execute("create table if not exists users(id integer primary key, name text)")
conn.execute("insert into users(name) values (?)", ("Alice",))
conn.commit()

for row in conn.execute("select id, name from users"):
    print(row)''',
        "51": '''python -m venv .venv
source .venv/bin/activate
python -m pip install requests
python -m pip freeze > requirements.txt''',
    }
    if no in examples:
        return examples[no]
    if "FastAPI" in title:
        return '''from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.post("/items")
def create_item(item: Item):
    return {"message": "created", "item": item}'''
    if "Flask" in title:
        return '''from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify(status="ok")'''
    if "Docker" in title or "CI/CD" in title:
        return '''FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]'''
    if "Redis" in title:
        return '''import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
r.setex("user:1", 60, "Alice")
print(r.get("user:1"))'''
    if "SQLAlchemy" in title:
        return '''from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///app.db")
with engine.begin() as conn:
    conn.execute(text("select 1"))'''
    if "数据分析" in title:
        return '''import pandas as pd

df = pd.DataFrame({"city": ["北京", "上海"], "sales": [120, 180]})
print(df.groupby("city")["sales"].sum())'''
    if "数据可视化" in title:
        return '''import matplotlib.pyplot as plt

plt.bar(["Mon", "Tue", "Wed"], [3, 5, 4])
plt.title("Daily Tasks")
plt.show()'''
    return f'''def main():
    """第{no}章：{title} 的最小可运行示例。"""
    topic = "{chapter['topic']}"
    print(f"开始练习：{{topic}}")

if __name__ == "__main__":
    main()'''


def theory(chapter: dict[str, str]) -> str:
    points = key_points(chapter["topic"])
    point_lines = "\n".join(f"- **{point}**：理解概念、掌握语法、能在真实代码中判断适用场景。" for point in points)
    mistake_lines = "\n".join(f"- 把 `{point}` 当成孤立语法背诵，而没有结合输入、输出和边界情况练习。" for point in points[:4])
    return f'''# 第{chapter["no"]}章：{chapter["title"]} — 理论篇

## 1. 本章目标

本章要把 **{chapter["topic"]}** 学到能解释、能运行、能在项目中使用的程度。

- 优先级：{chapter["priority"]}
- 建议投入：{chapter["duration"]}
- 学完后应能：独立写出示例代码，解释关键概念，并在小项目中正确使用。

---

## 2. 核心概念

{point_lines}

可以用下面的问题检查自己是否真的理解：

1. 这个能力解决了什么重复劳动或工程问题？
2. 它的输入、输出和副作用分别是什么？
3. 常见错误发生在哪些边界条件上？
4. 如果放到真实项目里，代码应该放在哪一层？

---

## 3. 使用场景

- **日常开发**：把本章知识用于更清晰的数据处理、业务封装和错误控制。
- **项目实战**：在 CLI 工具、Web API、数据处理脚本或自动化任务中落地。
- **代码评审**：判断一段代码是否过度复杂、是否隐藏副作用、是否容易测试。
- **面试表达**：用“问题 → 机制 → 示例 → 坑点”的顺序回答，而不是只背定义。

---

## 4. 工作原理

学习本章时建议按这条链路理解：

```text
需求场景
  ↓
选择合适的语言特性或库
  ↓
设计清晰的输入和输出
  ↓
处理异常、边界和可测试性
  ↓
沉淀为可复用代码
```

核心判断标准：代码是否让调用者更容易使用，让维护者更容易定位问题。

---

## 5. 常见问题

{mistake_lines}
- 只写“能跑”的 demo，没有补充异常路径、空值、重复数据或性能影响。
- 把所有逻辑写在一个函数或一个文件里，导致后续无法测试和复用。

---

## 6. 面试高频问题

1. 请解释 `{points[0] if points else chapter["title"]}` 的典型使用场景。
2. 本章内容在真实项目中最容易踩的坑是什么？
3. 如何给相关代码设计单元测试？
4. 如果输入数据异常，应该在哪里处理，如何向调用者反馈？
5. 什么时候应该避免使用本章能力，改用更简单的写法？
'''


def demo(chapter: dict[str, str]) -> str:
    return f'''# 第{chapter["no"]}章：{chapter["title"]} — Demo 篇

## Demo 1：最小可运行示例

### 实操目标

用最短代码跑通 **{chapter["topic"]}** 的核心路径，先建立可执行反馈。

```python
{code_example(chapter)}
```

### 运行建议

1. 新建独立文件，例如 `demo_{chapter["no"]}.py`。
2. 先原样运行，确认无语法错误。
3. 修改输入数据，观察输出是否符合预期。
4. 故意传入异常数据，记录报错信息。

---

## Demo 2：函数化与边界

```python
def validate_input(value):
    if value is None:
        raise ValueError("value 不能为空")
    return value


def run_case(value):
    checked = validate_input(value)
    return {{"input": checked, "ok": True}}


if __name__ == "__main__":
    print(run_case("sample"))
```

### 练习要求

- 给函数补充类型注解。
- 增加 2 个正常用例和 2 个异常用例。
- 把打印输出改成返回结构化数据。

---

## Demo 3：接近真实业务的小流程

```python
def load_items():
    return [
        {{"id": 1, "name": "Alice", "active": True}},
        {{"id": 2, "name": "Bob", "active": False}},
    ]


def filter_active(items):
    return [item for item in items if item.get("active")]


def main():
    items = load_items()
    active_items = filter_active(items)
    print(active_items)


main()
```

### 思考

- 哪些逻辑应该拆函数？
- 哪些错误应该提前校验？
- 如果数据来自文件、数据库或 HTTP 接口，代码需要怎么调整？
'''


def check(chapter: dict[str, str]) -> str:
    points = key_points(chapter["topic"])
    qs = "\n".join(f"{idx}. 请用自己的话解释 `{point}`，并写一个最小例子。" for idx, point in enumerate(points[:5], 1))
    return f'''# 第{chapter["no"]}章：{chapter["title"]} — 验收题

## 1. 概念自测

{qs or "1. 请用自己的话解释本章核心概念，并写一个最小例子。"}

## 2. 代码判断题

下面代码能运行，但不适合进入项目。请改造成可测试、可复用的版本：

```python
def process(data):
    result = []
    for item in data:
        if item:
            result.append(item)
    print(result)
```

要求：

- 说明输入为空、类型不匹配、数据量较大时会发生什么。
- 把 `print` 改成返回值。
- 给出至少 3 个测试用例。

## 3. 费曼输出题

不用查资料，向一个刚学 Python 的人讲清楚：

- 本章知识解决的实际问题是什么？
- 为什么不能只背语法？
- 项目中最容易写错的地方是什么？
- 你会如何验证自己写对了？

## 4. 达标标准

- 能独立写出一个可运行 demo。
- 能解释关键概念和边界条件。
- 能把本章知识用于一个小业务流程。
- 能通过测试或手动用例证明代码正确。
'''


def project_task(chapter: dict[str, str]) -> str:
    return f'''# 第{chapter["no"]}章：{chapter["title"]} — 项目任务

## 项目名称

{chapter["title"]}专项练习

## 背景

把 **{chapter["topic"]}** 转成真实代码产出。重点不是堆功能，而是写出结构清晰、可运行、可解释、可测试的代码。

## 任务目标

1. 新建一个独立练习目录，例如 `projects/chapter-{chapter["no"]}/`。
2. 实现至少 3 个函数或 1 个小模块，覆盖本章核心概念。
3. 提供命令行运行入口或清晰的示例调用。
4. 处理至少 3 类边界情况。
5. 写一份 `README.md`，说明运行方式、核心设计和踩坑点。

## 功能要求

- 输入：准备一组正常数据和异常数据。
- 处理：使用本章知识完成转换、校验、封装或集成。
- 输出：返回结构化结果，不把业务结果只写死在 `print` 里。
- 错误处理：异常信息要能帮助定位问题。
- 可测试性：核心逻辑应能被单独调用。

## 验收清单

- [ ] 代码能从零运行。
- [ ] 至少包含 3 个正常用例。
- [ ] 至少包含 3 个异常或边界用例。
- [ ] 函数命名能表达业务含义。
- [ ] README 写清楚“为什么这样设计”。
- [ ] 能口头解释本章知识在项目中的作用。

## 加分项

- 为核心函数补充类型注解。
- 使用 `pytest` 写自动化测试。
- 把配置、业务逻辑、入口文件分开。
- 记录一个你实际踩到的坑到根目录 `mistakes.md`。
'''


def review(chapter: dict[str, str]) -> str:
    return f'''# 第{chapter["no"]}章：{chapter["title"]} — 复习记录

## 本章掌握状态

| 项目 | 状态 | 说明 |
|------|------|------|
| 理论 | 未开始 | |
| Demo | 未开始 | |
| 验收题 | 未开始 | |
| 项目任务 | 未开始 | |
| 错题复盘 | 未开始 | |

## 复习安排

| 节点 | 日期 | 结果 | 备注 |
|------|------|------|------|
| 首次完成 | | | |
| +3 天 | | | |
| +7 天 | | | |
| +30 天 | | | |

## 费曼输出

用 5-8 句话讲清楚本章知识：

1. 这个章节解决什么问题？
2. 最小可运行示例是什么？
3. 最容易写错的边界是什么？
4. 在真实项目中应该放在哪一层？
5. 如何用测试或手动用例证明自己写对了？

## 错题与卡点

| 日期 | 问题 | 原因 | 修正 |
|------|------|------|------|
| | | | |

## 下一步

- [ ] 把本章最重要的一个知识点用于 `projects/` 或后续章节。
- [ ] 把复习结果同步到根目录 `review-plan.md`。
- [ ] 如果出现真实错误，同步记录到根目录 `mistakes.md`。
'''


GENERATORS = {
    "01-theory.md": theory,
    "02-demo.md": demo,
    "03-check.md": check,
    "04-project-task.md": project_task,
    "review.md": review,
}


def main() -> None:
    """Fill missing chapter files with starter templates.

    This script is for structural recovery only. Generated files still need a
    chapter-specific rewrite before they should be treated as learning material.
    Run tools/check_learning_repo.py afterwards to find generic content.
    """
    created: list[Path] = []
    for chapter in parse_chapters():
        directory = chapter_dir(chapter)
        directory.mkdir(parents=True, exist_ok=True)
        for filename in EXPECTED_FILES:
            path = directory / filename
            if path.exists() and path.stat().st_size > 0:
                continue
            path.write_text(GENERATORS[filename](chapter), encoding="utf-8")
            created.append(path.relative_to(ROOT))

    print(f"created {len(created)} files")
    for path in created:
        print(path)
    print("next: run python3 tools/check_learning_repo.py and rewrite generic files")


if __name__ == "__main__":
    main()
