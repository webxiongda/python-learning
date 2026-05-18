# 第01章：环境搭建与Python初印象 — 理论篇

## 1. 为什么选择 Python？

Python 是一门以"可读性第一"为设计哲学的高级编程语言。它由 Guido van Rossum 于 1991 年发布，目前已成为数据科学、Web 开发、自动化脚本、人工智能等领域的主流语言。

```
Python 的核心优势
├── 语法简洁，接近英语伪代码
├── 生态丰富，PyPI 拥有 50 万+ 包
├── 跨平台，Windows / macOS / Linux 均可运行
├── 动态类型，开发速度快
└── 社区庞大，学习资源极多
```

---

## 2. Python 版本体系

目前主流使用 **Python 3.x**，Python 2 已于 2020 年 1 月停止维护。

```
版本历史（简要）
Python 2.7  ──── 2010  （已废弃，勿用）
Python 3.6  ──── 2016  （f-string 引入）
Python 3.8  ──── 2019  （海象运算符 :=）
Python 3.10 ──── 2021  （match/case）
Python 3.12 ──── 2023  （性能大幅提升）
Python 3.13 ──── 2024  （更稳定的新特性与性能优化） ← 项目学习推荐
Python 3.14 ──── 2025  （新特性更多，注意第三方库兼容）
```

> 版本说明（2026-05-18）：Python.org 当前最新 3.x 版本是 Python 3.14.5，发布日期为 2026-05-10。学习项目可以使用 3.13 或 3.14；如果依赖某些第三方库，优先选择生态兼容更稳的版本。

---

## 3. 安装 Python

### 3.1 直接安装（简单方式）

访问 [https://python.org](https://python.org) 下载对应平台安装包。

- **macOS**：下载 `.pkg` 文件，双击安装
- **Windows**：下载 `.exe`，勾选 **"Add Python to PATH"** 后安装
- **Linux（Ubuntu）**：`sudo apt update && sudo apt install python3`

安装后验证：

```bash
python3 --version
# 输出示例：Python 3.12.3
```

### 3.2 使用 pyenv 管理多版本（推荐方式）

当你需要在不同项目中使用不同 Python 版本时，`pyenv` 是最佳选择。

```
pyenv 工作原理
┌─────────────────────────────────────┐
│         你的 Shell 环境              │
│  PATH 最前面插入 ~/.pyenv/shims/     │
│         ↓                           │
│  shim 脚本拦截 python3 命令          │
│         ↓                           │
│  读取 .python-version 文件           │
│         ↓                           │
│  调用对应版本的真实 Python 解释器    │
└─────────────────────────────────────┘
```

安装 pyenv（macOS）：

```bash
# 方式一：Homebrew
brew install pyenv

# 方式二：官方脚本
curl https://pyenv.run | bash
```

常用 pyenv 命令：

```bash
pyenv install --list          # 查看可安装版本
pyenv install 3.12.3          # 安装指定版本
pyenv global 3.12.3           # 设置全局默认版本
pyenv local 3.11.9            # 为当前目录设置版本（生成 .python-version 文件）
pyenv versions                # 查看已安装版本
```

---

## 4. pip：Python 包管理器

`pip` 是 Python 的官方包管理器，用于安装、升级、卸载第三方库。

```
pip 操作流程
你的命令 ──→ pip ──→ PyPI（Python Package Index）
                        ↓
                   下载 .whl 文件
                        ↓
                   安装到 site-packages/
```

常用命令：

```bash
pip install requests           # 安装包
pip install requests==2.31.0   # 安装指定版本
pip uninstall requests         # 卸载包
pip list                       # 查看已安装包
pip show requests              # 查看包详情
pip install --upgrade pip      # 升级 pip 本身
pip freeze > requirements.txt  # 导出依赖列表
pip install -r requirements.txt  # 从文件批量安装
```

---

## 5. venv：虚拟环境

虚拟环境让每个项目拥有**独立的依赖空间**，避免版本冲突。

```
没有虚拟环境的问题
┌────────────────────────────────┐
│  全局 Python                   │
│  项目A 需要 Django 3.2         │
│  项目B 需要 Django 4.2  ← 冲突！│
└────────────────────────────────┘

使用虚拟环境后
┌──────────────┐  ┌──────────────┐
│ 项目A/.venv  │  │ 项目B/.venv  │
│ Django 3.2   │  │ Django 4.2   │
│ 独立隔离     │  │ 独立隔离     │
└──────────────┘  └──────────────┘
```

创建和使用虚拟环境：

```bash
# 创建虚拟环境（在项目目录下）
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# 激活后命令行前缀变为 (.venv)
# (.venv) $ pip install requests  ← 只安装到当前虚拟环境

# 退出虚拟环境
deactivate
```

---

## 6. 第一个 Python 程序

创建文件 `hello.py`：

```python
# 这是 Python 的单行注释
print("Hello, World!")
print("欢迎来到 Python 的世界！")
```

运行：

```bash
python3 hello.py
# 输出：
# Hello, World!
# 欢迎来到 Python 的世界！
```

---

## 7. REPL：交互式解释器

REPL（Read-Eval-Print Loop）是 Python 内置的交互模式，适合快速实验代码片段。

```
REPL 工作循环
  ┌─────────────────────┐
  │  R ─ Read（读取输入）│
  │  E ─ Eval（执行代码）│  ← 循环往复
  │  P ─ Print（打印结果）│
  │  L ─ Loop（再次等待）│
  └─────────────────────┘
```

启动 REPL：

```bash
python3
```

常用操作：

```
>>> 1 + 2          # 直接计算
3
>>> name = "Alice"  # 定义变量
>>> print(name)
Alice
>>> help(print)    # 查看内置函数帮助
>>> exit()         # 退出 REPL
```

### IPython（增强版 REPL）

```bash
pip install ipython
ipython
```

IPython 提供语法高亮、Tab 补全、历史记录等功能，强烈推荐日常使用。

---

## 8. 推荐的开发工具

```
工具选择建议
├── VS Code + Python 扩展（免费，轻量，推荐入门）
├── PyCharm Community（免费，功能全面，推荐进阶）
├── Jupyter Notebook（数据分析场景首选）
└── 命令行 + vim/neovim（高手专属）
```

---

## 9. 项目目录结构约定

良好的项目结构从一开始就要养成习惯：

```
my_project/
├── .venv/              # 虚拟环境（不提交 git）
├── src/                # 源代码
│   └── main.py
├── tests/              # 测试代码
│   └── test_main.py
├── requirements.txt    # 依赖列表
├── .gitignore          # Git 忽略规则
└── README.md           # 项目说明
```

---

## 小结

| 工具 | 作用 |
|------|------|
| Python 解释器 | 运行 .py 文件 |
| pyenv | 管理多个 Python 版本 |
| pip | 安装/卸载第三方包 |
| venv | 隔离项目依赖环境 |
| REPL | 交互式实验代码 |

掌握这套工具链，你就拥有了 Python 开发的完整基础设施。
