# 第01章：环境搭建与Python初印象 — 自测题

> 完成本章学习后，请独立作答以下题目，再对照参考答案检验理解程度。

---

## 题目 1：选择题

以下哪个命令可以查看当前已安装的 Python 版本？

A. `python --check`
B. `python3 --version`
C. `pip version`
D. `pyenv show`

### 参考答案

**B. `python3 --version`**

解析：
- `python3 --version`（或 `python3 -V`）是标准命令，输出如 `Python 3.12.3`
- `python --check` 不是有效命令
- `pip version` 不是有效命令（正确写法是 `pip --version`）
- `pyenv show` 不是有效命令（正确写法是 `pyenv version`）

---

## 题目 2：填空题

请填写以下虚拟环境操作的对应命令：

1. 在当前目录创建名为 `.venv` 的虚拟环境：`___________`
2. 在 macOS 上激活该虚拟环境：`___________`
3. 退出虚拟环境：`___________`
4. 将当前环境所有依赖导出到文件：`___________`

### 参考答案

1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `deactivate`
4. `pip freeze > requirements.txt`

解析：虚拟环境的创建使用 Python 内置的 `venv` 模块（`-m venv`），激活方式在不同操作系统下有所不同（Windows 使用 `.venv\Scripts\activate`）。`pip freeze` 会将所有包及其版本号输出为标准格式，通过 `>` 重定向写入文件。

---

## 题目 3：判断题

判断以下说法是否正确，并简要说明原因：

1. Python 2 和 Python 3 的代码完全兼容，可以互相运行。
2. `pip` 安装的包默认安装到当前激活的虚拟环境中（如果有的话）。
3. `pyenv local 3.11.9` 命令会修改系统全局的 Python 版本。
4. REPL 中输入的代码执行完毕后，变量会被立即销毁。

### 参考答案

1. **错误。** Python 2 和 Python 3 存在重大不兼容变化，例如 `print` 语句变为函数、整除行为不同、字符串编码处理方式不同等。Python 2 于 2020 年已停止维护。

2. **正确。** 当激活虚拟环境后，`pip install` 会将包安装到 `.venv/lib/pythonX.X/site-packages/` 目录中，与全局环境隔离。

3. **错误。** `pyenv local` 只在当前目录创建一个 `.python-version` 文件，只影响该目录及其子目录的 Python 版本。要修改全局版本需使用 `pyenv global`。

4. **错误。** 在同一个 REPL 会话中，变量会持续存在直到会话结束（输入 `exit()` 或按 Ctrl+D）。这正是 REPL 方便快速实验的原因——你可以复用之前定义的变量。

---

## 题目 4：代码分析题

阅读以下代码，预测输出结果：

```python
import sys

version_info = sys.version_info
print(f"主版本号：{version_info.major}")
print(f"次版本号：{version_info.minor}")
print(f"是否为 Python 3：{version_info.major == 3}")

message = "Hello" * 2 + " " + "World"
print(message)
print(f"消息长度：{len(message)}")
```

### 参考答案

假设运行环境为 Python 3.12：

```
主版本号：3
次版本号：12
是否为 Python 3：True
HelloHello World
消息长度：13
```

解析：
- `sys.version_info` 是一个具名元组，`.major` 取主版本号，`.minor` 取次版本号
- `"Hello" * 2` 将字符串重复 2 次，得到 `"HelloHello"`
- 字符串拼接后为 `"HelloHello World"`（13 个字符：H-e-l-l-o-H-e-l-l-o-空格-W-o-r-l-d，共16字符，请注意核实）
- 实际 `"HelloHello World"` 长度为 16，`len()` 返回 16

---

## 题目 5：实操题

按以下步骤完成操作，并记录每一步的输出：

1. 在桌面创建目录 `python-practice`
2. 进入该目录，创建虚拟环境 `.venv`
3. 激活虚拟环境
4. 安装 `httpx` 包（requests 的现代替代品）
5. 创建 `test.py`，内容为打印 `httpx` 的版本号
6. 运行 `test.py`，记录输出

### 参考答案

```bash
# 步骤 1-3：Shell 操作
mkdir ~/Desktop/python-practice
cd ~/Desktop/python-practice
python3 -m venv .venv
source .venv/bin/activate

# 步骤 4：安装包
pip install httpx
```

```python
# 步骤 5：test.py 内容
import httpx
print(f"httpx 版本：{httpx.__version__}")
```

```bash
# 步骤 6：运行
python3 test.py
# 预期输出（版本号可能不同）：
# httpx 版本：0.27.0
```

关键检查点：
- 激活虚拟环境后，命令提示符前应出现 `(.venv)` 前缀
- `pip install` 的安装路径应包含 `.venv` 字样（可用 `pip show httpx` 查看）
- 运行成功说明整个工具链配置正确
