# 第52章：项目结构与打包 — 理论

## Python 项目为什么需要打包？

打包让你的代码可以被他人通过 `pip install` 安装使用，也让你的项目结构更规范、可维护。

```
从脚本到可安装包的演进
┌─────────────┐    ┌──────────────────┐    ┌──────────────────────┐
│  单文件脚本  │ → │  多文件项目结构   │ → │  可安装的 Python 包  │
│  main.py    │    │  src/ + tests/   │    │  pip install my-pkg  │
└─────────────┘    └──────────────────┘    └──────────────────────┘
```

---

## 1. 两种主流项目布局

### Flat 布局（扁平布局）

包代码直接放在项目根目录下：

```
my-project/                  ← 项目根目录
├── my_package/              ← 包代码（与项目同级）
│   ├── __init__.py
│   ├── core.py
│   └── utils.py
├── tests/
│   └── test_core.py
├── pyproject.toml
└── README.md
```

**优点：** 简单直接，历史悠久  
**缺点：** 开发时可能意外导入到未安装的本地版本，测试不够准确

### Src 布局（推荐）

包代码放在 `src/` 子目录下：

```
my-project/                  ← 项目根目录
├── src/                     ← 源码目录
│   └── my_package/          ← 包代码
│       ├── __init__.py
│       ├── core.py
│       └── utils.py
├── tests/
│   └── test_core.py
├── pyproject.toml
└── README.md
```

**优点：**
- 强制在测试时使用已安装版本，避免本地路径干扰
- 分隔源码与配置文件，结构更清晰
- 是 Python 社区目前的最佳实践（PEP 517）

**选择建议：** 新项目优先使用 Src 布局。

---

## 2. pyproject.toml — 现代打包配置

`pyproject.toml` 是 Python 打包的现代标准（PEP 517/518/621），取代了传统的 `setup.py` 和 `setup.cfg`。

### 最小化配置示例

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-awesome-package"
version = "1.0.0"
description = "一个很棒的 Python 包"
readme = "README.md"
license = {file = "LICENSE"}
requires-python = ">=3.9"
authors = [
    {name = "张三", email = "zhangsan@example.com"},
]
keywords = ["python", "example"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
dependencies = [
    "requests>=2.28.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0", "black>=23.0"]
docs = ["sphinx>=7.0"]

[project.urls]
Homepage = "https://github.com/zhangsan/my-awesome-package"
Repository = "https://github.com/zhangsan/my-awesome-package"
"Bug Tracker" = "https://github.com/zhangsan/my-awesome-package/issues"

[project.scripts]
my-tool = "my_package.cli:main"   # 命令行入口点
```

### 主流构建后端对比

```
构建后端生态系统
┌──────────────────────────────────────────────────────┐
│                   pyproject.toml                     │
│              [build-system] 声明后端                  │
└──────────────────────────────────────────────────────┘
         │              │              │
    ┌────▼────┐    ┌────▼────┐   ┌────▼──────┐
    │Hatchling│    │setuptools│  │  Flit      │
    │（推荐） │    │（老牌）  │  │（简单包）  │
    │功能全面 │    │最广泛   │  │纯Python包  │
    └─────────┘    └─────────┘  └────────────┘
```

**Hatchling（推荐新项目）：**
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**setuptools（最广泛兼容）：**
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
```

---

## 3. 构建 Wheel 包

### 什么是 Wheel？

Wheel（`.whl` 文件）是 Python 的二进制分发格式，比 sdist（源码包）安装更快。

```
Python 包格式
┌─────────────────────────────────────────────────────┐
│  my_package-1.0.0-py3-none-any.whl                  │
│      │           │   │    │   │                      │
│      │           │   │    │   └── 平台（any=纯Python） │
│      │           │   │    └────── ABI（none=纯Python） │
│      │           │   └─────────── Python实现（cp/py）  │
│      │           └─────────────── 版本号               │
│      └─────────────────────────────── 包名             │
└─────────────────────────────────────────────────────┘
```

### 构建命令

```bash
# 安装构建工具
pip install build

# 构建（同时生成 wheel 和 sdist）
python -m build

# 只构建 wheel
python -m build --wheel

# 构建结果在 dist/ 目录
dist/
├── my_package-1.0.0-py3-none-any.whl   # 二进制包
└── my_package-1.0.0.tar.gz             # 源码包
```

### 使用 Hatch 构建（Hatchling 的 CLI 工具）

```bash
# 安装 hatch
pip install hatch

# 构建
hatch build

# 发布到 PyPI
hatch publish

# 发布到测试 PyPI
hatch publish -r test
```

---

## 4. 发布到 PyPI

### 准备工作

1. 在 [PyPI](https://pypi.org) 注册账号
2. 创建 API Token（推荐替代密码）
3. 配置 `~/.pypirc`：

```ini
[pypi]
username = __token__
password = pypi-xxxxxxxxxxxxxxxxxxxxxxxx
```

### 发布步骤

```bash
# 1. 安装发布工具
pip install twine

# 2. 构建包
python -m build

# 3. 检查包是否符合 PyPI 要求
twine check dist/*

# 4. 先发布到测试 PyPI（测试）
twine upload --repository testpypi dist/*

# 5. 测试从测试 PyPI 安装
pip install --index-url https://test.pypi.org/simple/ my-package

# 6. 确认无误后发布到正式 PyPI
twine upload dist/*
```

---

## 5. 版本管理策略

遵循 **语义化版本（SemVer）**：

```
版本号格式：MAJOR.MINOR.PATCH
                │      │      │
                │      │      └── 向后兼容的 bug 修复
                │      └───────── 向后兼容的新功能
                └──────────────── 不兼容的 API 变更

示例：
  1.0.0  → 首次正式发布
  1.0.1  → 修复 bug
  1.1.0  → 添加新功能（向后兼容）
  2.0.0  → 重大重构（可能破坏兼容性）
```

### 动态版本（从 git tag 读取）

```toml
# pyproject.toml
[tool.hatch.version]
source = "vcs"  # 从 git tag 读取版本

# 对应标签：git tag v1.2.3
```

---

## 关键概念回顾

- **Src 布局**：源码在 `src/` 下，测试更可靠，是现代最佳实践
- **pyproject.toml**：统一配置文件，声明构建系统、项目元数据、依赖
- **Wheel**：预构建的二进制包格式，安装速度比 sdist 快
- **Hatchling/setuptools**：构建后端，负责将源码打包成 wheel/sdist
- **Twine**：将打好的包发布到 PyPI 的工具
- **语义化版本**：规范的版本号命名方式，让用户理解升级影响
