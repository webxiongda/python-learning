# 第15章：模块与包 — Demo 篇

## Demo 1：最小反馈

目标：用最短路径验证 `import系统` 的基本行为。

```python
def run_demo():
    topic = "import系统、__init__.py、__all__、相对导入"
    result = {"topic": topic, "status": "ok"}
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
    return {"count": len(normalized), "items": normalized}
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
    return {"total": len(items), "unique": unique_items}


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
