# 第01章：环境搭建与Python初印象 — Demo 篇

## Demo 1：验证 Python 环境并打印版本信息

```python
# demo1_check_env.py
# 目标：验证 Python 安装正确，了解基本系统信息

import sys
import platform

print("=" * 40)
print("Python 环境信息")
print("=" * 40)
print(f"Python 版本：{sys.version}")
print(f"操作系统：{platform.system()} {platform.release()}")
print(f"Python 可执行路径：{sys.executable}")
print("=" * 40)
print("恭喜！Python 环境配置成功 🎉")
```

```
# 预期输出：
========================================
Python 环境信息
========================================
Python 版本：3.12.3 (main, Apr  9 2024, 08:09:14) [GCC 11.4.0]
操作系统：Darwin 23.4.0
Python 可执行路径：/usr/local/bin/python3
========================================
恭喜！Python 环境配置成功 🎉
```

---

## Demo 2：第一个交互式程序——自我介绍生成器

```python
# demo2_greeting.py
# 目标：学习 print() 和 input() 的基本用法

# input() 等待用户输入，返回字符串
name = input("请输入你的名字：")
age = input("请输入你的年龄：")
city = input("请输入你所在的城市：")

print()  # 打印空行
print("=" * 30)
print("--- 自我介绍 ---")
print(f"大家好，我叫 {name}！")
print(f"我今年 {age} 岁，来自 {city}。")
print(f"很高兴认识大家！")
print("=" * 30)
```

```
# 预期输出（输入：张三 / 22 / 北京）：
请输入你的名字：张三
请输入你的年龄：22
请输入你所在的城市：北京

==============================
--- 自我介绍 ---
大家好，我叫 张三！
我今年 22 岁，来自 北京。
很高兴认识大家！
==============================
```

---

## Demo 3：用 REPL 快速体验 Python 计算能力

> 以下代码可直接在终端 `python3` 交互模式中逐行输入运行。

```python
# 在 REPL 中逐行输入以下内容

# 基本数学运算
>>> 100 + 200
300

>>> 2 ** 10        # 2 的 10 次方
1024

>>> 17 // 3        # 整除
5

>>> 17 % 3         # 取余
2

>>> round(3.14159, 2)   # 四舍五入保留2位小数
3.14

# 字符串操作
>>> "Hello" + " " + "World"
'Hello World'

>>> "Python" * 3
'PythonPythonPython'

>>> len("Hello, 世界")
8
```

```
# 预期输出（已在代码中标注每行结果）
```

---

## Demo 4：pip 操作演示——安装并使用 requests 库

```python
# 第一步：在终端运行（不是 Python 文件内）
# pip install requests

# demo4_requests.py
# 目标：验证 pip 安装成功，发送一个真实 HTTP 请求

import requests

print("正在发送请求到 httpbin.org ...")
response = requests.get("https://httpbin.org/get")

print(f"状态码：{response.status_code}")
print(f"响应类型：{response.headers['Content-Type']}")

# 解析 JSON 响应
data = response.json()
print(f"你的 IP 地址：{data['origin']}")
print(f"请求来源：{data['headers']['User-Agent']}")
```

```
# 预期输出：
正在发送请求到 httpbin.org ...
状态码：200
响应类型：application/json
你的 IP 地址：203.0.113.42
请求来源：python-requests/2.31.0
```

> 注意：IP 地址会因网络环境不同而不同。如网络不通，会抛出 `ConnectionError`。

---

## Demo 5：创建并使用虚拟环境（Shell 脚本演示）

```bash
# demo5_venv.sh
# 目标：演示虚拟环境的完整创建和使用流程
# 在终端中逐行执行以下命令

# 1. 创建项目目录
mkdir my_first_project
cd my_first_project

# 2. 创建虚拟环境
python3 -m venv .venv

# 3. 激活虚拟环境（macOS/Linux）
source .venv/bin/activate

# 4. 确认当前使用的 Python 路径（应指向 .venv 内部）
which python3

# 5. 安装一个包（只影响当前虚拟环境）
pip install rich

# 6. 验证安装
pip list

# 7. 退出虚拟环境
deactivate

# 8. 退出后确认路径恢复到系统 Python
which python3
```

```python
# 激活虚拟环境后，运行以下 Python 文件测试 rich 库
# demo5_rich_test.py

from rich.console import Console
from rich.table import Table

console = Console()

table = Table(title="Python 学习计划")
table.add_column("章节", style="cyan")
table.add_column("主题", style="green")
table.add_column("状态", style="magenta")

table.add_row("第01章", "环境搭建", "✅ 进行中")
table.add_row("第02章", "基础语法", "⏳ 待开始")
table.add_row("第03章", "控制流程", "⏳ 待开始")

console.print(table)
```

```
# 预期输出（带颜色的表格）：
          Python 学习计划
┌──────┬──────────┬──────────┐
│ 章节  │ 主题     │ 状态     │
├──────┼──────────┼──────────┤
│ 第01章│ 环境搭建 │ ✅ 进行中│
│ 第02章│ 基础语法 │ ⏳ 待开始│
│ 第03章│ 控制流程 │ ⏳ 待开始│
└──────┴──────────┴──────────┘
```
