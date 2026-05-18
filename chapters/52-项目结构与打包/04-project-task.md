# 第52章：项目结构与打包 — 项目任务

## 项目名称：字符串工具库 `strkit`

## 业务背景

你需要将日常使用的字符串处理工具整理成一个可复用的 Python 库，供团队其他项目通过 `pip install strkit` 安装使用。这是你第一次从零开始发布一个 Python 包到（测试）PyPI。

---

## 技术要求

### 包功能实现

在 `src/strkit/` 下实现以下功能：

**`strkit/text.py`** — 文本处理工具：
- `truncate(text, max_length, suffix="...")` — 截断超长文本，添加省略号
- `snake_to_camel(snake_str)` — 蛇形命名转驼峰命名（`user_name` → `userName`）
- `camel_to_snake(camel_str)` — 驼峰命名转蛇形命名（`userName` → `user_name`）
- `word_count(text)` — 统计单词/字符数量

**`strkit/validate.py`** — 验证工具：
- `is_email(s)` — 验证是否为有效邮箱
- `is_phone_cn(s)` — 验证是否为中国手机号（1开头，11位数字）
- `is_url(s)` — 验证是否为有效 URL

### 项目配置要求

- 使用 Src 布局
- `pyproject.toml` 使用 `hatchling` 构建后端
- 填写完整的项目元数据：name、version、description、authors、license、classifiers
- `requires-python = ">=3.9"`
- 在 `[project.scripts]` 中添加 `strkit` 命令行入口，执行后打印版本信息

### 测试要求

在 `tests/` 目录下编写 `pytest` 测试：
- 每个公开函数至少有 2 个测试用例
- 包含边界条件测试（空字符串、超长输入等）

---

## 项目结构

```
strkit/
├── src/
│   └── strkit/
│       ├── __init__.py      # 导出所有公开 API，设置 __version__
│       ├── text.py
│       ├── validate.py
│       └── cli.py           # 命令行入口
├── tests/
│   ├── test_text.py
│   └── test_validate.py
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## 验收标准

- [ ] `pip install -e ".[dev]"` 安装成功
- [ ] `strkit` 命令可运行，输出版本号
- [ ] `pytest tests/` 全部通过，覆盖率 ≥ 80%
- [ ] `python -m build` 成功生成 `dist/strkit-*.whl`
- [ ] `twine check dist/*` 无错误
- [ ] `pip install dist/strkit-*.whl` 安装后可正常 `import strkit`

## 加分项

- [ ] 将 `strkit` 发布到测试 PyPI，并截图证明
- [ ] 添加 GitHub Actions 工作流，在 push 时自动运行测试
- [ ] 用 `hatch version patch` 自动升级版本号后重新构建
