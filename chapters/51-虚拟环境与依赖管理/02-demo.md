# 第51章：虚拟环境与依赖管理 — Demo

## Demo 1：用 venv 创建并管理虚拟环境

```python
# demo1_venv_manager.py
# 演示虚拟环境的创建、包安装和环境检测

import sys
import os
import subprocess
import venv
from pathlib import Path

def create_virtual_env(env_path: str) -> None:
    """创建虚拟环境"""
    path = Path(env_path)
    if path.exists():
        print(f"虚拟环境已存在：{env_path}")
        return
    
    print(f"正在创建虚拟环境：{env_path}")
    venv.create(env_path, with_pip=True, clear=False)
    print("虚拟环境创建成功！")

def check_in_venv() -> bool:
    """检查当前是否处于虚拟环境中"""
    return hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

def get_python_info() -> dict:
    """获取当前 Python 环境信息"""
    return {
        "python_版本": sys.version,
        "python_路径": sys.executable,
        "虚拟环境": "是" if check_in_venv() else "否",
        "site_packages": next(
            (p for p in sys.path if "site-packages" in p), "未找到"
        ),
    }

def list_installed_packages() -> list:
    """列出已安装的包"""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=columns"],
        capture_output=True,
        text=True
    )
    lines = result.stdout.strip().split("\n")
    # 跳过表头两行
    packages = []
    for line in lines[2:]:
        parts = line.split()
        if len(parts) >= 2:
            packages.append({"名称": parts[0], "版本": parts[1]})
    return packages

def generate_requirements(output_file: str = "requirements.txt") -> None:
    """生成 requirements.txt"""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        capture_output=True,
        text=True
    )
    with open(output_file, "w") as f:
        f.write(result.stdout)
    print(f"已生成：{output_file}")
    print("内容预览：")
    print(result.stdout[:500] if len(result.stdout) > 500 else result.stdout)

# 主程序演示
print("=== Python 环境信息 ===")
info = get_python_info()
for key, value in info.items():
    print(f"  {key}: {value}")

print("\n=== 已安装的包（前5个）===")
packages = list_installed_packages()
for pkg in packages[:5]:
    print(f"  {pkg['名称']} == {pkg['版本']}")
print(f"  ...共 {len(packages)} 个包")
```

```
# 预期输出：
=== Python 环境信息 ===
  python_版本: 3.11.6 (main, Oct  2 2023, 13:45:54) [Clang 15.0.0]
  python_路径: /Users/user/my-project/.venv/bin/python
  虚拟环境: 是
  site_packages: /Users/user/my-project/.venv/lib/python3.11/site-packages

=== 已安装的包（前5个）===
  certifi == 2023.11.17
  charset-normalizer == 3.3.2
  idna == 3.6
  pip == 23.3.1
  requests == 2.31.0
  ...共 8 个包
```

---

## Demo 2：解析和验证 requirements.txt

```python
# demo2_requirements_parser.py
# 解析 requirements.txt 文件，检查版本约束

import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class Requirement:
    name: str
    operator: Optional[str]
    version: Optional[str]
    extras: list
    comment: str

def parse_requirement_line(line: str) -> Optional[Requirement]:
    """解析一行 requirements.txt 内容"""
    line = line.strip()
    
    # 跳过空行和纯注释行
    if not line or line.startswith("#"):
        return None
    
    # 提取行内注释
    comment = ""
    if " #" in line:
        line, comment = line.split(" #", 1)
        comment = comment.strip()
    
    # 提取 extras（方括号内的内容）
    extras = []
    extras_match = re.search(r"\[([^\]]+)\]", line)
    if extras_match:
        extras = [e.strip() for e in extras_match.group(1).split(",")]
        line = line.replace(extras_match.group(0), "")
    
    # 解析包名和版本约束
    version_pattern = r"([a-zA-Z0-9_\-\.]+)\s*(==|>=|<=|!=|~=|>|<)\s*([^\s,]+)?"
    match = re.match(version_pattern, line.strip())
    
    if match:
        return Requirement(
            name=match.group(1),
            operator=match.group(2),
            version=match.group(3),
            extras=extras,
            comment=comment
        )
    else:
        # 只有包名，没有版本约束
        name = line.strip().split()[0]
        return Requirement(
            name=name,
            operator=None,
            version=None,
            extras=extras,
            comment=comment
        )

def parse_requirements_file(content: str) -> list:
    """解析完整的 requirements.txt 内容"""
    requirements = []
    for line in content.strip().split("\n"):
        req = parse_requirement_line(line)
        if req:
            requirements.append(req)
    return requirements

def check_pinned_versions(requirements: list) -> dict:
    """检查哪些包没有固定版本"""
    pinned = [r for r in requirements if r.operator == "=="]
    unpinned = [r for r in requirements if r.operator != "=="]
    return {"已固定": pinned, "未固定": unpinned}

# 示例 requirements.txt 内容
sample_requirements = """
# Web 框架
fastapi==0.104.1
uvicorn[standard]==0.24.0

# 数据库
sqlalchemy>=2.0,<3.0
psycopg2-binary==2.9.9  # 二进制版本，无需编译

# 工具
python-dotenv==1.0.0
pydantic
requests!=2.29.0  # 此版本有bug

# 测试（不要在生产环境安装）
pytest
pytest-asyncio==0.21.1
"""

print("=== 解析 requirements.txt ===\n")
reqs = parse_requirements_file(sample_requirements)

for req in reqs:
    extras_str = f"[{','.join(req.extras)}]" if req.extras else ""
    version_str = f" {req.operator} {req.version}" if req.operator else " (无版本约束)"
    comment_str = f"  # {req.comment}" if req.comment else ""
    print(f"  {req.name}{extras_str}{version_str}{comment_str}")

print("\n=== 版本固定状态检查 ===")
check = check_pinned_versions(reqs)
print(f"\n已固定版本的包（{len(check['已固定'])} 个）：")
for r in check["已固定"]:
    print(f"  ✓ {r.name}=={r.version}")

print(f"\n未固定版本的包（{len(check['未固定'])} 个）——部署风险！：")
for r in check["未固定"]:
    op_str = f"{r.operator}{r.version}" if r.operator else "无约束"
    print(f"  ✗ {r.name} ({op_str})")
```

```
# 预期输出：
=== 解析 requirements.txt ===

  fastapi == 0.104.1
  uvicorn[standard] == 0.24.0
  sqlalchemy >= 2.0
  psycopg2-binary == 2.9.9  # 二进制版本，无需编译
  python-dotenv == 1.0.0
  pydantic (无版本约束)
  requests != 2.29.0
  pytest (无版本约束)
  pytest-asyncio == 0.21.1

=== 版本固定状态检查 ===

已固定版本的包（5 个）：
  ✓ fastapi==0.104.1
  ✓ uvicorn==0.24.0
  ✓ psycopg2-binary==2.9.9
  ✓ python-dotenv==1.0.0
  ✓ pytest-asyncio==0.21.1

未固定版本的包（4 个）——部署风险！：
  ✗ sqlalchemy (>=2.0)
  ✗ pydantic (无约束)
  ✗ requests (!=2.29.0)
  ✗ pytest (无约束)
```

---

## Demo 3：模拟 Poetry 的 pyproject.toml 生成

```python
# demo3_pyproject_generator.py
# 生成标准 pyproject.toml 文件

from dataclasses import dataclass, field
from typing import Optional
import json

@dataclass
class Dependency:
    name: str
    version_constraint: str
    optional: bool = False
    group: str = "main"  # main, dev, test

@dataclass
class ProjectConfig:
    name: str
    version: str
    description: str
    python_version: str
    authors: list
    dependencies: list = field(default_factory=list)
    
    def to_toml(self) -> str:
        """生成 pyproject.toml 内容"""
        lines = []
        
        # [tool.poetry] 部分
        lines.append("[tool.poetry]")
        lines.append(f'name = "{self.name}"')
        lines.append(f'version = "{self.version}"')
        lines.append(f'description = "{self.description}"')
        authors_str = ", ".join(f'"{a}"' for a in self.authors)
        lines.append(f"authors = [{authors_str}]")
        lines.append("")
        
        # 主依赖
        lines.append("[tool.poetry.dependencies]")
        lines.append(f'python = "{self.python_version}"')
        main_deps = [d for d in self.dependencies if d.group == "main"]
        for dep in main_deps:
            lines.append(f'{dep.name} = "{dep.version_constraint}"')
        lines.append("")
        
        # 开发依赖
        dev_deps = [d for d in self.dependencies if d.group == "dev"]
        if dev_deps:
            lines.append("[tool.poetry.group.dev.dependencies]")
            for dep in dev_deps:
                lines.append(f'{dep.name} = "{dep.version_constraint}"')
            lines.append("")
        
        # 测试依赖
        test_deps = [d for d in self.dependencies if d.group == "test"]
        if test_deps:
            lines.append("[tool.poetry.group.test.dependencies]")
            for dep in test_deps:
                lines.append(f'{dep.name} = "{dep.version_constraint}"')
            lines.append("")
        
        # build-system
        lines.append("[build-system]")
        lines.append('requires = ["poetry-core"]')
        lines.append('build-backend = "poetry.core.masonry.api"')
        
        return "\n".join(lines)
    
    def dependency_summary(self) -> dict:
        """输出依赖统计"""
        from collections import Counter
        groups = Counter(d.group for d in self.dependencies)
        return dict(groups)

# 创建项目配置
project = ProjectConfig(
    name="awesome-api",
    version="1.0.0",
    description="一个基于 FastAPI 的 REST API 项目",
    python_version="^3.11",
    authors=["张三 <zhangsan@example.com>"],
    dependencies=[
        Dependency("fastapi", "^0.104.1"),
        Dependency("uvicorn", "^0.24.0"),
        Dependency("sqlalchemy", "^2.0.23"),
        Dependency("pydantic", "^2.5.0"),
        Dependency("python-dotenv", "^1.0.0"),
        Dependency("black", "^23.11.0", group="dev"),
        Dependency("mypy", "^1.7.0", group="dev"),
        Dependency("pytest", "^7.4.3", group="test"),
        Dependency("pytest-asyncio", "^0.21.1", group="test"),
        Dependency("httpx", "^0.25.2", group="test"),
    ]
)

print("=== 生成的 pyproject.toml ===\n")
print(project.to_toml())

print("\n=== 依赖统计 ===")
summary = project.dependency_summary()
total = sum(summary.values())
for group, count in summary.items():
    print(f"  {group:8s}: {count} 个依赖")
print(f"  {'合计':8s}: {total} 个依赖")
```

```
# 预期输出：
=== 生成的 pyproject.toml ===

[tool.poetry]
name = "awesome-api"
version = "1.0.0"
description = "一个基于 FastAPI 的 REST API 项目"
authors = ["张三 <zhangsan@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.1"
uvicorn = "^0.24.0"
sqlalchemy = "^2.0.23"
pydantic = "^2.5.0"
python-dotenv = "^1.0.0"

[tool.poetry.group.dev.dependencies]
black = "^23.11.0"
mypy = "^1.7.0"

[tool.poetry.group.test.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
httpx = "^0.25.2"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

=== 依赖统计 ===
  main    : 5 个依赖
  dev     : 2 个依赖
  test    : 3 个依赖
  合计    : 10 个依赖
```

---

## Demo 4：依赖冲突检测模拟

```python
# demo4_conflict_checker.py
# 模拟依赖冲突检测逻辑

from typing import Tuple
import re

def parse_version(version: str) -> Tuple[int, ...]:
    """将版本字符串解析为元组，便于比较"""
    # 去掉前缀符号
    version = re.sub(r'^[^0-9]*', '', version)
    parts = version.split(".")
    result = []
    for p in parts[:3]:  # 只取 major.minor.patch
        try:
            result.append(int(re.sub(r'\D.*', '', p)))
        except ValueError:
            result.append(0)
    while len(result) < 3:
        result.append(0)
    return tuple(result)

def satisfies_constraint(version: str, constraint: str) -> bool:
    """检查版本是否满足约束"""
    v = parse_version(version)
    
    # 处理 ^（兼容性约束：不升级 major 版本）
    if constraint.startswith("^"):
        lower = parse_version(constraint[1:])
        upper = (lower[0] + 1, 0, 0)
        return lower <= v < upper
    
    # 处理 ~ （补丁级别兼容）
    if constraint.startswith("~="):
        lower = parse_version(constraint[2:])
        upper = (lower[0], lower[1] + 1, 0)
        return lower <= v < upper
    
    # 处理比较运算符
    ops = {">=": lambda a, b: a >= b,
           "<=": lambda a, b: a <= b,
           "==": lambda a, b: a == b,
           "!=": lambda a, b: a != b,
           ">":  lambda a, b: a > b,
           "<":  lambda a, b: a < b}
    
    for op, func in sorted(ops.items(), key=lambda x: -len(x[0])):
        if constraint.startswith(op):
            c = parse_version(constraint[len(op):])
            return func(v, c)
    
    return True  # 无约束则满足

def check_conflicts(package_name: str, requirements: list) -> dict:
    """检查某个包的多个版本约束是否存在冲突"""
    test_versions = ["1.0.0", "1.5.0", "2.0.0", "2.5.0", "3.0.0"]
    
    compatible = []
    for v in test_versions:
        if all(satisfies_constraint(v, req) for req in requirements):
            compatible.append(v)
    
    return {
        "包名": package_name,
        "约束列表": requirements,
        "兼容版本": compatible,
        "有冲突": len(compatible) == 0
    }

# 测试场景
scenarios = [
    ("requests", [">=2.0.0", "<3.0.0"]),          # 正常
    ("sqlalchemy", ["^2.0.0", ">=2.0.5"]),          # 正常
    ("numpy", [">=1.0.0", "<2.0.0", "!=1.5.0"]),    # 排除特定版本
    ("django", [">=3.0.0", "<4.0.0", ">=4.0.0"]),   # 冲突！
]

print("=== 依赖冲突检测 ===\n")
for pkg_name, constraints in scenarios:
    result = check_conflicts(pkg_name, constraints)
    status = "冲突！" if result["有冲突"] else "正常"
    print(f"[{status}] {result['包名']}")
    print(f"  约束: {' AND '.join(result['约束列表'])}")
    if result["兼容版本"]:
        print(f"  兼容版本: {', '.join(result['兼容版本'])}")
    else:
        print(f"  兼容版本: 无（存在版本冲突！）")
    print()
```

```
# 预期输出：
=== 依赖冲突检测 ===

[正常] requests
  约束: >=2.0.0 AND <3.0.0
  兼容版本: 2.0.0, 2.5.0

[正常] sqlalchemy
  约束: ^2.0.0 AND >=2.0.5
  兼容版本: 2.5.0

[正常] numpy
  约束: >=1.0.0 AND <2.0.0 AND !=1.5.0
  兼容版本: 1.0.0

[冲突！] django
  约束: >=3.0.0 AND <4.0.0 AND >=4.0.0
  兼容版本: 无（存在版本冲突！）
```
