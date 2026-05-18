# 第51章：虚拟环境与依赖管理 — 自测题

## 题目1：基础概念

以下关于 Python 虚拟环境的说法，哪些是正确的？（多选）

A. 虚拟环境是 Python 3.3 之后的内置功能，通过 `python -m venv` 创建  
B. 激活虚拟环境后，`pip install` 会将包安装到系统全局 Python 目录  
C. `.venv` 目录应该加入 `.gitignore`，不提交到版本控制  
D. 退出虚拟环境使用 `deactivate` 命令  
E. 一个项目可以同时激活多个虚拟环境  

### 参考答案

**正确答案：A、C、D**

解析：
- **A 正确**：`venv` 模块从 Python 3.3 起内置，`python -m venv .venv` 是标准创建方式
- **B 错误**：激活虚拟环境后，`pip install` 会安装到虚拟环境的 `site-packages`，不会影响全局环境
- **C 正确**：`.venv` 包含大量二进制文件且因平台而异，不应提交到 git
- **D 正确**：`deactivate` 是退出虚拟环境的标准命令
- **E 错误**：同一个终端会话只能激活一个虚拟环境，后激活的会覆盖先激活的

---

## 题目2：pip 命令

写出以下操作对应的 pip 命令：

1. 安装 `requests` 库的 `2.31.0` 版本
2. 将当前环境所有包导出到 `requirements.txt`
3. 从 `requirements.txt` 安装所有依赖
4. 升级 `pip` 自身到最新版本
5. 查看 `requests` 包的详细信息（版本、依赖、安装位置）

### 参考答案

```bash
# 1. 安装指定版本
pip install "requests==2.31.0"

# 2. 导出依赖
pip freeze > requirements.txt

# 3. 从文件安装
pip install -r requirements.txt

# 4. 升级 pip
pip install --upgrade pip
# 或者（更安全的方式）
python -m pip install --upgrade pip

# 5. 查看包详情
pip show requests
```

补充说明：`pip freeze` 输出格式为 `包名==版本号`，适合生成 requirements.txt。而 `pip list` 输出更易读但不适合直接作为 requirements.txt 使用。

---

## 题目3：Poetry 依赖组

在 Poetry 项目中，如何将 `pytest` 添加为开发依赖（不部署到生产环境），并在生产部署时只安装生产依赖？

### 参考答案

**添加开发依赖：**

```bash
# 方式1：使用 --group dev 参数
poetry add pytest --group dev

# 方式2：使用旧版 --dev 参数（等效）
poetry add pytest --dev
```

添加后，`pyproject.toml` 会出现：

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
```

**生产部署时只安装生产依赖：**

```bash
# 排除 dev 组
poetry install --without dev

# 如果有多个非生产组
poetry install --without dev,test
```

**原理说明：** Poetry 将依赖分组管理，`[tool.poetry.dependencies]` 是必选依赖，`[tool.poetry.group.*.dependencies]` 是可选依赖组。生产环境通过 `--without` 参数跳过不需要的组。

---

## 题目4：版本约束符号

解释以下版本约束的含义，并给出一个满足约束的版本号示例：

| 约束 | 含义 | 满足的版本示例 |
|------|------|--------------|
| `^2.3.1` | ? | ? |
| `~=2.3.1` | ? | ? |
| `>=2.0,<3.0` | ? | ? |
| `!=1.5.0` | ? | ? |

### 参考答案

| 约束 | 含义 | 满足的版本示例 |
|------|------|--------------|
| `^2.3.1` | 兼容性约束：允许 minor 和 patch 升级，不允许 major 升级。即 `>=2.3.1, <3.0.0` | `2.3.1`、`2.4.0`、`2.99.99` |
| `~=2.3.1` | 近似匹配：允许 patch 升级，不允许 minor 升级。即 `>=2.3.1, <2.4.0` | `2.3.1`、`2.3.5`、`2.3.99` |
| `>=2.0,<3.0` | 范围约束：大于等于2.0，小于3.0 | `2.0.0`、`2.5.3`、`2.99.0` |
| `!=1.5.0` | 排除约束：除了1.5.0之外的任何版本 | `1.4.9`、`1.5.1`、`2.0.0` |

**重要区别：**
- `^` 是 Poetry/npm 风格，Python 原生 pip 不支持（需用 `>=x.y.z, <(x+1).0.0` 替代）
- `~=` 是 Python PEP 440 标准，pip 原生支持

---

## 题目5：实战场景

你的团队正在开发一个 Python Web 项目，新同事加入后如何快速搭建与团队一致的开发环境？请分别描述使用 **pip + venv** 和 **Poetry** 两种方案的完整步骤。

### 参考答案

**方案一：pip + venv**

```bash
# 1. 克隆项目代码
git clone https://github.com/team/project.git
cd project

# 2. 创建虚拟环境
python -m venv .venv

# 3. 激活虚拟环境
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 4. 安装依赖（开发环境）
pip install -r requirements/dev.txt

# 5. 验证安装
pip list
python -c "import fastapi; print(fastapi.__version__)"
```

前提：项目维护者需要预先执行 `pip freeze > requirements/base.txt` 并提交。

**方案二：Poetry**

```bash
# 1. 克隆项目代码
git clone https://github.com/team/project.git
cd project

# 2. 安装依赖（Poetry 会自动创建虚拟环境）
poetry install

# 3. 激活虚拟环境
poetry shell

# 4. 验证
python -m pytest
```

**Poetry 的优势：** `poetry.lock` 文件记录了所有依赖的精确版本（包括间接依赖），`poetry install` 会确保团队每个成员安装完全相同的版本，彻底消除 "在我电脑上能跑" 的问题。

**关键区别：**
- pip 方案需要手动维护 `requirements.txt`，可能遗漏间接依赖
- Poetry 方案通过 `poetry.lock` 自动锁定所有层级的依赖，可复现性更强
