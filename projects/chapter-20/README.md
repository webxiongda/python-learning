# Chapter 20 Project: 可复用 Python 工具库

## Goal

实现一个带类型注解、测试和本地安装能力的小型工具库。

## Modules

- `validators.py`：邮箱、手机号、URL、非空字符串校验
- `dates.py`：日期解析、时间差、时区安全当前时间
- `collections.py`：分组、去重、分批、扁平化
- `decorators.py`：计时、重试、缓存

## Commands

```bash
pip install -e .
python -m pytest
```

## Acceptance

- 所有公开函数有类型注解。
- 至少 20 个测试用例。
- README 写清安装、导入和 API 示例。
