from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "chapters"

TEMPLATE_PHRASES = (
    "本章围绕",
    "Demo 2：封装成可复用函数",
    "业务练习模块",
    "你正在维护一个 Python 全栈项目",
    "阅读下面代码，指出它的问题",
)


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


def chapter_dir(chapter: dict[str, str]) -> Path:
    matches = sorted(CHAPTERS.glob(f"{chapter['no']}-*"))
    if not matches:
        raise FileNotFoundError(f"missing chapter directory for {chapter['no']}")
    return matches[0]


def points(topic: str) -> list[str]:
    return [part.strip() for part in re.split(r"[、,，/]+", topic) if part.strip()]


def has_template_phrase(path: Path) -> bool:
    content = path.read_text(encoding="utf-8")
    return any(phrase in content for phrase in TEMPLATE_PHRASES)


def bullet_points(items: list[str]) -> str:
    return "\n".join(f"- `{item}`：说清它解决的问题、输入输出、常见边界和项目落点。" for item in items)


def theory(chapter: dict[str, str]) -> str:
    ps = points(chapter["topic"])
    core = bullet_points(ps)
    first = ps[0] if ps else chapter["title"]
    return f"""# 第{chapter["no"]}章：{chapter["title"]} — 理论篇

## 学习目标

本章要把 **{chapter["topic"]}** 学到能解释、能运行、能在项目中使用的程度。

- 优先级：{chapter["priority"]}
- 建议投入：{chapter["duration"]}
- 产出要求：一个可运行 Demo、一组验收答案、一个小项目任务记录。

## 核心知识

{core}

## 学习路径

1. 先用最小代码跑通 `{first}`。
2. 再把代码拆成函数或模块，明确输入、输出和异常。
3. 补充边界用例，至少覆盖空值、非法类型和重复数据。
4. 把本章能力用于 `projects/` 或章节项目任务。

## 项目落点

- CLI 工具：用于参数校验、文件处理、结果展示。
- Web API：用于请求解析、业务封装、错误响应。
- 数据处理：用于清洗、转换、统计和报告。
- 测试代码：用于构造输入、验证边界和保护重构。

## 常见误区

- 只背概念，不写能运行的代码。
- 只覆盖正常路径，忽略空输入、非法输入和异常分支。
- 把演示代码直接搬进项目，没有拆分业务逻辑和入口层。
- 遇到报错只修表象，没有记录到根目录 `mistakes.md`。

## 验收口径

- 能用自己的话解释本章 3 个核心概念。
- 能写出一个不依赖复制粘贴的最小示例。
- 能说明至少 2 个真实项目场景。
- 能设计至少 3 个测试或手动验收用例。
"""


def demo(chapter: dict[str, str]) -> str:
    ps = points(chapter["topic"])
    first = ps[0] if ps else chapter["title"]
    return f"""# 第{chapter["no"]}章：{chapter["title"]} — Demo 篇

## Demo 1：最小反馈

目标：用最短路径验证 `{first}` 的基本行为。

```python
def run_demo():
    topic = "{chapter["topic"]}"
    result = {{"topic": topic, "status": "ok"}}
    return result


if __name__ == "__main__":
    print(run_demo())
```

运行后先确认输出结构，再替换输入数据观察变化。

## Demo 2：函数化与边界

目标：把演示代码改成可测试函数。

```python
def normalize_items(items):
    if items is None:
        raise ValueError("items 不能为空")
    return [str(item).strip() for item in items if str(item).strip()]


def summarize(items):
    normalized = normalize_items(items)
    return {{"count": len(normalized), "items": normalized}}
```

建议至少手动验证：

- 正常列表
- 空列表
- `None`
- 包含空字符串或重复元素的数据

## Demo 3：接近项目的流程

目标：把输入、处理、输出分层。

```python
def load_sample_data():
    return [" Alice ", "Bob", "", "Alice"]


def process_data(raw_items):
    items = normalize_items(raw_items)
    unique_items = sorted(set(items))
    return {{"total": len(items), "unique": unique_items}}


def main():
    data = load_sample_data()
    report = process_data(data)
    print(report)


if __name__ == "__main__":
    main()
```

复盘问题：

- 哪些函数可以单独测试？
- 哪些错误应该提前校验？
- 如果输入来自文件、HTTP 或数据库，哪一层需要调整？
"""


def check(chapter: dict[str, str]) -> str:
    ps = points(chapter["topic"])
    concept_questions = "\n".join(
        f"{idx}. 用自己的话解释 `{point}`，并写一个最小例子。"
        for idx, point in enumerate(ps[:5], 1)
    )
    if not concept_questions:
        concept_questions = "1. 用自己的话解释本章标题对应的核心能力，并写一个最小例子。"

    return f"""# 第{chapter["no"]}章：{chapter["title"]} — 验收题

## 1. 概念自测

{concept_questions}

## 2. 代码改造题

下面代码能运行，但不适合进入项目。请改造成可测试、可复用的版本。

```python
def process(data):
    result = []
    for item in data:
        if item:
            result.append(item)
    print(result)
```

要求：

- 明确函数输入和返回值。
- 处理 `None`、空列表、非预期类型。
- 不在业务函数中直接打印。
- 写出至少 3 个测试或手动验收用例。

## 3. 项目应用题

假设你要在 `projects/chapter-{chapter["no"]}/` 中使用本章知识，请说明：

- 模块如何命名？
- 哪些函数属于核心业务？
- 哪些输入需要校验？
- 出错时向调用者返回什么信息？

## 4. 费曼输出题

不用查资料，向刚学 Python 的人讲清楚：

- 本章解决的实际问题。
- 最小示例如何运行。
- 项目中最常见的坑。
- 你会如何验证自己真的掌握了。

## 5. 达标标准

- 能独立写出一个可运行 Demo。
- 能解释关键概念和边界条件。
- 能把本章知识用于一个小业务流程。
- 能通过测试或手动用例证明代码正确。
"""


def project_task(chapter: dict[str, str]) -> str:
    ps = points(chapter["topic"])
    core = "、".join(ps[:3]) if ps else chapter["title"]
    return f"""# 第{chapter["no"]}章：{chapter["title"]} — 项目任务

## 项目名称

`chapter-{chapter["no"]}` {chapter["title"]}专项练习

## 目标

在 `projects/chapter-{chapter["no"]}/` 中完成一个小型可运行模块，把 **{chapter["topic"]}** 转成真实代码产出。重点是明确输入输出、处理边界、留下测试和复盘记录。

## 建议目录

```text
projects/chapter-{chapter["no"]}/
├── README.md
├── src/
│   └── main.py
└── tests/
    └── test_main.py
```

## 功能要求

- 围绕 `{core}` 设计 2-4 个核心函数。
- 准备一组正常数据、一组空数据、一组非法数据。
- 核心函数返回结构化结果，不直接打印业务结果。
- 入口文件只负责调用和展示。
- README 写清运行方式、设计思路和踩坑记录。

## 测试要求

- 至少 5 个测试或手动验收用例。
- 覆盖正常路径、空输入、非法输入和边界值。
- 如果使用第三方库，说明安装命令和版本。

## 阶段拆分

1. 写 README 中的目标和样例输入输出。
2. 实现最小核心函数。
3. 加入边界处理和错误信息。
4. 补测试或手动验收记录。
5. 把真实卡点同步到根目录 `mistakes.md`。

## 验收清单

- [ ] `projects/chapter-{chapter["no"]}/README.md` 存在。
- [ ] 代码能从命令行运行。
- [ ] 核心逻辑可以被测试直接调用。
- [ ] 至少覆盖 1 个异常路径。
- [ ] 能口头解释本章知识在项目中的作用。
"""


GENERATORS = {
    "01-theory.md": theory,
    "02-demo.md": demo,
    "03-check.md": check,
    "04-project-task.md": project_task,
}


def main() -> int:
    changed: list[Path] = []
    for chapter in parse_chapters():
        directory = chapter_dir(chapter)
        for filename, renderer in GENERATORS.items():
            path = directory / filename
            if path.exists() and has_template_phrase(path):
                path.write_text(renderer(chapter), encoding="utf-8")
                changed.append(path.relative_to(ROOT))

    print(f"refreshed {len(changed)} generic files")
    for path in changed:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
