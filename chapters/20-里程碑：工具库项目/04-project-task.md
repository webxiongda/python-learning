# 第20章：里程碑：工具库项目 — 项目任务

## 项目名称

可复用 Python 工具库

## 目标

把函数进阶、迭代器、生成器、装饰器、模块与包、正则、日期时间、标准库和类型注解整合成一个小型工具库。重点是包结构、类型清晰、测试完整和文档可读。

## 交付目录

在 `projects/chapter-20/` 下完成：

```text
projects/chapter-20/
├── README.md
├── pyproject.toml
├── src/
│   └── pytoolkit/
│       ├── __init__.py
│       ├── validators.py
│       ├── dates.py
│       ├── collections.py
│       └── decorators.py
└── tests/
    ├── test_validators.py
    ├── test_dates.py
    └── test_decorators.py
```

## 功能要求

- `validators.py`：实现邮箱、手机号、URL、非空字符串校验。
- `dates.py`：实现日期解析、时间差计算、时区安全的当前时间函数。
- `collections.py`：实现分组、去重、分批、扁平化等数据处理工具。
- `decorators.py`：实现计时、重试、缓存三个装饰器。
- `__init__.py`：只导出稳定 API，避免把内部实现全暴露。

## 设计约束

- 所有公开函数必须有类型注解。
- 校验函数返回布尔值或结构化结果，不直接打印。
- 装饰器必须保留原函数元信息，使用 `functools.wraps`。
- 日期处理必须说明是否包含时区，禁止混用 naive 和 aware datetime。

## 测试要求

- `pytest` 覆盖正常输入、非法输入、空输入和边界值。
- 至少 20 个测试用例。
- 能运行 `python -m pytest`。
- 如果配置了 mypy，公开函数应能通过基础类型检查。

## 阶段拆分

1. **API 设计**：先写 README 中的函数清单和调用示例，再写实现。
2. **模块实现**：每次只完成一个模块，完成后立刻补测试。
3. **包结构**：使用 `src/` 布局，确认 `pip install -e .` 后能从任意目录导入。
4. **类型检查**：为公开函数补类型注解，避免使用含义不明的 `Any`。
5. **发布准备**：补 `pyproject.toml` 元数据、版本号、许可证和 README 示例。

## 完成定义

这个项目完成时，你应该能解释清楚：

- 一个工具函数什么时候应该返回 `bool`，什么时候应该抛异常。
- 为什么公开 API 要通过 `__init__.py` 控制。
- 装饰器为什么必须使用 `functools.wraps`。
- 日期时间函数如何避免 naive datetime 和 aware datetime 混用。
- 测试如何证明工具库没有隐藏副作用。

## 验收清单

- [ ] 可以通过 `pip install -e .` 本地安装。
- [ ] README 有安装、导入、示例和 API 列表。
- [ ] 测试覆盖每个模块。
- [ ] 每个工具函数都有明确输入输出。
- [ ] 至少记录 1 个 API 设计取舍。
