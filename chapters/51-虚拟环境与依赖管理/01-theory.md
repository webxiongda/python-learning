# 第51章：虚拟环境与依赖管理 — 理论

## 为什么需要虚拟环境？

Python 项目的核心问题：不同项目可能依赖同一个库的不同版本。

```
系统 Python 环境（全局污染问题）
┌─────────────────────────────────────────┐
│  项目A 需要 requests==2.26.0            │
│  项目B 需要 requests==2.31.0  ← 冲突！ │
│  项目C 需要 Django==3.2                 │
│  项目D 需要 Django==4.2       ← 冲突！ │
└─────────────────────────────────────────┘

虚拟环境解决方案（隔离）
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   项目A 环境 │  │   项目B 环境 │  │   项目C 环境 │
│  requests    │  │  requests    │  │  Django 4.2  │
│  2.26.0      │  │  2.31.0      │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
        ↑                ↑                ↑
      隔离             隔离             隔离
```

---

## 1. venv — Python 内置虚拟环境

Python 3.3+ 内置 `venv` 模块，无需额外安装。

### 基本操作

```bash
# 创建虚拟环境（在项目根目录执行）
python -m venv .venv

# 激活虚拟环境
# macOS / Linux
source .venv/bin/activate

# Windows CMD
.venv\Scripts\activate.bat

# Windows PowerShell
.venv\Scripts\Activate.ps1

# 退出虚拟环境
deactivate
```

### 目录结构

```
my-project/
├── .venv/
│   ├── bin/           # macOS/Linux 可执行文件
│   │   ├── python
│   │   ├── pip
│   │   └── activate
│   ├── lib/
│   │   └── python3.11/
│   │       └── site-packages/   # 安装的包
│   └── pyvenv.cfg               # 环境配置
├── src/
├── requirements.txt
└── README.md
```

> **最佳实践：** `.venv` 目录必须加入 `.gitignore`，不应提交到版本控制。

---

## 2. pip — 包管理工具

### 常用命令

```bash
# 安装包
pip install requests
pip install "requests==2.31.0"      # 指定版本
pip install "requests>=2.28,<3.0"  # 版本范围

# 卸载包
pip uninstall requests

# 查看已安装包
pip list
pip show requests    # 详细信息

# 升级包
pip install --upgrade requests
pip install --upgrade pip   # 升级pip本身

# 搜索（已废弃，建议用 PyPI 网站）
# pip search requests
```

### requirements.txt

`requirements.txt` 是最经典的依赖记录方式：

```bash
# 导出当前环境所有依赖（含精确版本）
pip freeze > requirements.txt

# 从 requirements.txt 安装
pip install -r requirements.txt
```

**requirements.txt 示例：**

```
# requirements.txt
# Web 框架
fastapi==0.104.1
uvicorn[standard]==0.24.0

# 数据库
sqlalchemy==2.0.23
psycopg2-binary==2.9.9

# 工具
python-dotenv==1.0.0
pydantic==2.5.0
```

**分层管理（推荐）：**

```
requirements/
├── base.txt        # 生产环境依赖
├── dev.txt         # 开发环境（含测试、lint工具）
└── test.txt        # 测试专用
```

`dev.txt` 内容示例：
```
-r base.txt         # 引入 base 依赖
pytest==7.4.3
black==23.11.0
flake8==6.1.0
mypy==1.7.0
```

---

## 3. Poetry — 现代依赖管理工具

Poetry 解决了 `pip + requirements.txt` 的痛点：依赖解析、锁文件、打包一体化。

```
Poetry 工作流
┌─────────────────────────────────────────────────┐
│  pyproject.toml    → 声明依赖（人读）            │
│  poetry.lock       → 精确版本锁定（机器用）      │
│                                                  │
│  poetry install    → 读 lock 文件安装            │
│  poetry add        → 添加依赖，更新 lock         │
│  poetry update     → 升级依赖，更新 lock         │
│  poetry build      → 打包项目                    │
│  poetry publish    → 发布到 PyPI                 │
└─────────────────────────────────────────────────┘
```

### 安装 Poetry

```bash
# 官方推荐安装方式
curl -sSL https://install.python-poetry.org | python3 -

# 验证安装
poetry --version
```

### 基本使用

```bash
# 新建项目
poetry new my-project

# 在现有项目初始化
poetry init

# 添加依赖
poetry add requests
poetry add "fastapi[all]"
poetry add pytest --group dev    # 添加到开发依赖组

# 安装所有依赖
poetry install

# 只安装生产依赖（部署时）
poetry install --without dev

# 运行命令（在虚拟环境中）
poetry run python main.py
poetry run pytest

# 进入虚拟环境 shell
poetry shell
```

### pyproject.toml 结构

```toml
[tool.poetry]
name = "my-project"
version = "0.1.0"
description = "示例项目"
authors = ["张三 <zhangsan@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.1"
sqlalchemy = "^2.0.23"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
black = "^23.11.0"
mypy = "^1.7.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

---

## 4. pipx — 全局工具安装

`pipx` 专门用于安装 Python 命令行工具，为每个工具创建独立环境，避免全局污染。

```bash
# 安装 pipx
pip install pipx
pipx ensurepath

# 安装全局工具
pipx install black       # 代码格式化
pipx install poetry      # 项目管理
pipx install httpie      # HTTP 客户端
pipx install youtube-dl  # 下载工具

# 运行一次性工具（不安装）
pipx run pycowsay "hello"

# 列出已安装工具
pipx list

# 升级工具
pipx upgrade black
pipx upgrade-all         # 升级所有工具
```

---

## 工具对比总结

```
工具选择决策树
                    需要管理 Python 工具？
                           │
                    ┌──────┴──────┐
                    是            否
                    │             │
                  pipx      需要发布包？
                              │
                    ┌─────────┴──────────┐
                    是                   否
                    │                    │
                 Poetry          小项目用 venv+pip
                                 中大项目用 Poetry
```

| 工具 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| venv | 简单隔离 | 内置，无需安装 | 无依赖解析 |
| pip | 安装包 | 内置，使用广泛 | 无锁文件 |
| Poetry | 完整项目管理 | 依赖解析、锁文件、打包 | 学习成本稍高 |
| pipx | 全局工具 | 隔离工具环境 | 仅适合 CLI 工具 |

---

## 关键概念回顾

- **虚拟环境**：隔离项目依赖，避免版本冲突
- **requirements.txt**：记录精确依赖版本，确保可复现
- **poetry.lock**：Poetry 的锁文件，保证团队成员依赖完全一致
- **pyproject.toml**：现代 Python 项目的统一配置文件（PEP 517/518）
- **pipx**：安装 Python CLI 工具的正确方式
