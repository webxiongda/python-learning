# 第52章：项目结构与打包 — Demo

## Demo 1：自动生成标准 Src 布局项目结构

```python
# demo1_project_scaffold.py
# 自动创建符合 src 布局的 Python 项目骨架

import os
from pathlib import Path
from textwrap import dedent

def create_project_scaffold(
    project_name: str,
    package_name: str,
    author: str,
    email: str,
    description: str,
    python_version: str = ">=3.9"
) -> None:
    """创建标准 src 布局的 Python 项目骨架"""
    
    base = Path(project_name)
    
    # 定义目录结构
    directories = [
        base / "src" / package_name,
        base / "tests",
        base / "docs",
        base / ".github" / "workflows",
    ]
    
    # 创建所有目录
    for d in directories:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  创建目录: {d}")
    
    # 定义文件内容
    files = {
        base / "src" / package_name / "__init__.py": dedent(f'''\
            """
            {package_name} - {description}
            """
            __version__ = "0.1.0"
            __author__ = "{author}"
        '''),
        
        base / "src" / package_name / "core.py": dedent('''\
            """核心功能模块"""
            
            def greet(name: str) -> str:
                """返回问候语"""
                return f"你好，{name}！"
        '''),
        
        base / "tests" / "__init__.py": "",
        
        base / "tests" / "test_core.py": dedent(f'''\
            """核心功能测试"""
            import pytest
            from {package_name}.core import greet
            
            def test_greet():
                assert greet("世界") == "你好，世界！"
            
            def test_greet_empty():
                result = greet("")
                assert "！" in result
        '''),
        
        base / "pyproject.toml": dedent(f'''\
            [build-system]
            requires = ["hatchling"]
            build-backend = "hatchling.build"
            
            [project]
            name = "{project_name}"
            version = "0.1.0"
            description = "{description}"
            readme = "README.md"
            requires-python = "{python_version}"
            authors = [
                {{name = "{author}", email = "{email}"}},
            ]
            dependencies = []
            
            [project.optional-dependencies]
            dev = [
                "pytest>=7.0",
                "black>=23.0",
                "mypy>=1.0",
            ]
            
            [tool.hatch.build.targets.wheel]
            packages = ["src/{package_name}"]
        '''),
        
        base / ".gitignore": dedent('''\
            # 虚拟环境
            .venv/
            venv/
            env/
            
            # 构建产物
            dist/
            build/
            *.egg-info/
            
            # Python 缓存
            __pycache__/
            *.py[cod]
            *.pyo
            
            # IDE
            .idea/
            .vscode/
            *.swp
            
            # 测试覆盖率
            .coverage
            htmlcov/
            .pytest_cache/
        '''),
        
        base / "README.md": dedent(f'''\
            # {project_name}
            
            {description}
            
            ## 安装
            
            ```bash
            pip install {project_name}
            ```
            
            ## 开发环境搭建
            
            ```bash
            python -m venv .venv
            source .venv/bin/activate  # macOS/Linux
            pip install -e ".[dev]"
            ```
            
            ## 运行测试
            
            ```bash
            pytest
            ```
        '''),
    }
    
    # 写入所有文件
    for filepath, content in files.items():
        filepath.write_text(content, encoding="utf-8")
        print(f"  创建文件: {filepath}")

def print_tree(path: Path, prefix: str = "", is_last: bool = True) -> None:
    """打印目录树"""
    connector = "└── " if is_last else "├── "
    print(prefix + connector + path.name)
    
    if path.is_dir():
        children = sorted(path.iterdir())
        for i, child in enumerate(children):
            is_child_last = i == len(children) - 1
            extension = "    " if is_last else "│   "
            print_tree(child, prefix + extension, is_child_last)

# 主程序
import tempfile
import os

with tempfile.TemporaryDirectory() as tmp_dir:
    original_dir = os.getcwd()
    os.chdir(tmp_dir)
    
    print("=== 创建项目骨架 ===\n")
    create_project_scaffold(
        project_name="my-awesome-lib",
        package_name="my_awesome_lib",
        author="张三",
        email="zhangsan@example.com",
        description="一个很棒的 Python 库",
    )
    
    print("\n=== 项目目录结构 ===\n")
    print_tree(Path("my-awesome-lib"))
    
    os.chdir(original_dir)
```

```
# 预期输出：
=== 创建项目骨架 ===

  创建目录: my-awesome-lib/src/my_awesome_lib
  创建目录: my-awesome-lib/tests
  创建目录: my-awesome-lib/docs
  创建目录: my-awesome-lib/.github/workflows
  创建文件: my-awesome-lib/src/my_awesome_lib/__init__.py
  创建文件: my-awesome-lib/src/my_awesome_lib/core.py
  创建文件: my-awesome-lib/tests/__init__.py
  创建文件: my-awesome-lib/tests/test_core.py
  创建文件: my-awesome-lib/pyproject.toml
  创建文件: my-awesome-lib/.gitignore
  创建文件: my-awesome-lib/README.md

=== 项目目录结构 ===

└── my-awesome-lib
    ├── .gitignore
    ├── .github
    │   └── workflows
    ├── README.md
    ├── docs
    ├── pyproject.toml
    ├── src
    │   └── my_awesome_lib
    │       ├── __init__.py
    │       └── core.py
    └── tests
        ├── __init__.py
        └── test_core.py
```

---

## Demo 2：解析和验证 pyproject.toml

```python
# demo2_pyproject_validator.py
# 解析 pyproject.toml 并验证必填字段

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # 第三方兼容库
    except ImportError:
        tomllib = None

from dataclasses import dataclass
from typing import Optional
import re

@dataclass
class ValidationResult:
    field: str
    status: str  # "ok", "warning", "error"
    message: str

def validate_version(version: str) -> bool:
    """验证语义化版本号格式"""
    pattern = r"^\d+\.\d+\.\d+([.-]?(alpha|beta|rc)\d*)?$"
    return bool(re.match(pattern, version))

def validate_email(email: str) -> bool:
    """验证邮箱格式（简单验证）"""
    return "@" in email and "." in email.split("@")[1]

def validate_pyproject(config: dict) -> list:
    """验证 pyproject.toml 内容"""
    results = []
    
    # 检查 build-system
    if "build-system" not in config:
        results.append(ValidationResult(
            "build-system", "error", "缺少 [build-system] 配置"
        ))
    else:
        bs = config["build-system"]
        if "build-backend" not in bs:
            results.append(ValidationResult(
                "build-system.build-backend", "error", "缺少构建后端声明"
            ))
        else:
            results.append(ValidationResult(
                "build-system.build-backend", "ok",
                f"构建后端：{bs['build-backend']}"
            ))
    
    # 检查 project 配置
    project = config.get("project", {})
    
    # 必填字段
    required_fields = ["name", "version", "description"]
    for field in required_fields:
        if field not in project:
            results.append(ValidationResult(
                f"project.{field}", "error", f"缺少必填字段 {field}"
            ))
        else:
            results.append(ValidationResult(
                f"project.{field}", "ok", f"✓ {project[field]}"
            ))
    
    # 版本号格式验证
    if "version" in project:
        if validate_version(project["version"]):
            results.append(ValidationResult(
                "project.version格式", "ok", "语义化版本号格式正确"
            ))
        else:
            results.append(ValidationResult(
                "project.version格式", "warning",
                f"版本号 '{project['version']}' 不符合语义化版本规范"
            ))
    
    # Python 版本要求
    if "requires-python" not in project:
        results.append(ValidationResult(
            "project.requires-python", "warning",
            "建议添加 requires-python 约束"
        ))
    
    # 作者信息
    authors = project.get("authors", [])
    if not authors:
        results.append(ValidationResult(
            "project.authors", "warning", "建议添加作者信息"
        ))
    else:
        for i, author in enumerate(authors):
            if "email" in author and not validate_email(author["email"]):
                results.append(ValidationResult(
                    f"project.authors[{i}].email", "warning",
                    f"邮箱格式可能不正确：{author['email']}"
                ))
    
    return results

# 测试配置
sample_config = {
    "build-system": {
        "requires": ["hatchling"],
        "build-backend": "hatchling.build"
    },
    "project": {
        "name": "my-package",
        "version": "1.0.0",
        "description": "一个示例包",
        "requires-python": ">=3.9",
        "authors": [
            {"name": "张三", "email": "zhangsan@example.com"}
        ],
        "dependencies": ["requests>=2.28.0"]
    }
}

# 有问题的配置
bad_config = {
    "project": {
        "name": "bad-package",
        "version": "1.0",  # 不符合语义化版本
        "description": "有问题的配置",
    }
}

def print_validation_results(config: dict, title: str):
    print(f"\n=== {title} ===")
    results = validate_pyproject(config)
    for r in results:
        icon = {"ok": "✓", "warning": "⚠", "error": "✗"}[r.status]
        print(f"  {icon} [{r.status.upper():7s}] {r.field}: {r.message}")
    
    errors = sum(1 for r in results if r.status == "error")
    warnings = sum(1 for r in results if r.status == "warning")
    print(f"\n  汇总：{errors} 个错误，{warnings} 个警告")

print_validation_results(sample_config, "验证正常配置")
print_validation_results(bad_config, "验证有问题的配置")
```

```
# 预期输出：
=== 验证正常配置 ===
  ✓ [OK     ] build-system.build-backend: 构建后端：hatchling.build
  ✓ [OK     ] project.name: ✓ my-package
  ✓ [OK     ] project.version: ✓ 1.0.0
  ✓ [OK     ] project.description: ✓ 一个示例包
  ✓ [OK     ] project.version格式: 语义化版本号格式正确

  汇总：0 个错误，0 个警告

=== 验证有问题的配置 ===
  ✗ [ERROR  ] build-system: 缺少 [build-system] 配置
  ✓ [OK     ] project.name: ✓ bad-package
  ✓ [OK     ] project.version: ✓ 1.0
  ✓ [OK     ] project.description: ✓ 有问题的配置
  ⚠ [WARNING] project.version格式: 版本号 '1.0' 不符合语义化版本规范
  ⚠ [WARNING] project.requires-python: 建议添加 requires-python 约束
  ⚠ [WARNING] project.authors: 建议添加作者信息

  汇总：1 个错误，3 个警告
```

---

## Demo 3：语义化版本管理工具

```python
# demo3_semver_manager.py
# 语义化版本号解析、比较和升级

import re
from dataclasses import dataclass
from enum import Enum

class BumpType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"

@dataclass
class SemVer:
    major: int
    minor: int
    patch: int
    pre_release: str = ""

    @classmethod
    def parse(cls, version_str: str) -> "SemVer":
        """解析版本字符串"""
        # 去掉 v 前缀
        v = version_str.lstrip("v")
        pattern = r"^(\d+)\.(\d+)\.(\d+)(?:[-.]?(alpha|beta|rc)(\d*))?$"
        match = re.match(pattern, v)
        if not match:
            raise ValueError(f"无效的版本号：{version_str}")
        
        pre = ""
        if match.group(4):
            pre = match.group(4) + (match.group(5) or "")
        
        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
            pre_release=pre,
        )
    
    def bump(self, bump_type: BumpType) -> "SemVer":
        """升级版本号"""
        if bump_type == BumpType.MAJOR:
            return SemVer(self.major + 1, 0, 0)
        elif bump_type == BumpType.MINOR:
            return SemVer(self.major, self.minor + 1, 0)
        else:  # PATCH
            return SemVer(self.major, self.minor, self.patch + 1)
    
    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        return f"{base}-{self.pre_release}" if self.pre_release else base
    
    def __lt__(self, other: "SemVer") -> bool:
        return (self.major, self.minor, self.patch) < (
            other.major, other.minor, other.patch
        )
    
    def __eq__(self, other: "SemVer") -> bool:
        return (self.major, self.minor, self.patch, self.pre_release) == (
            other.major, other.minor, other.patch, other.pre_release
        )

def show_version_timeline(versions: list) -> None:
    """展示版本发布时间线"""
    sorted_versions = sorted(SemVer.parse(v) for v in versions)
    
    print("版本发布时间线：")
    print("  " + " → ".join(str(v) for v in sorted_versions))

# 演示
versions = ["0.1.0", "0.2.0", "1.0.0", "1.0.1", "1.1.0", "2.0.0"]

print("=== 版本号解析与升级 ===\n")
current = SemVer.parse("1.2.3")
print(f"当前版本: {current}")
print(f"  升级 patch → {current.bump(BumpType.PATCH)}")
print(f"  升级 minor → {current.bump(BumpType.MINOR)}")
print(f"  升级 major → {current.bump(BumpType.MAJOR)}")

print("\n=== 版本比较 ===")
v1 = SemVer.parse("1.0.0")
v2 = SemVer.parse("2.0.0")
v3 = SemVer.parse("1.0.0")
print(f"  {v1} < {v2} : {v1 < v2}")
print(f"  {v2} < {v1} : {v2 < v1}")
print(f"  {v1} == {v3}: {v1 == v3}")

print()
show_version_timeline(versions)

print("\n=== 版本变更含义 ===")
changes = [
    ("1.0.0", "1.0.1", "修复了登录页面的 bug"),
    ("1.0.1", "1.1.0", "新增了用户导出功能"),
    ("1.1.0", "2.0.0", "重构 API，接口不向后兼容"),
]
for old, new, desc in changes:
    o, n = SemVer.parse(old), SemVer.parse(new)
    if n.major > o.major:
        change_type = "MAJOR（破坏性变更）"
    elif n.minor > o.minor:
        change_type = "MINOR（新功能）"
    else:
        change_type = "PATCH（Bug修复）"
    print(f"  {old} → {new}  [{change_type}]  {desc}")
```

```
# 预期输出：
=== 版本号解析与升级 ===

当前版本: 1.2.3
  升级 patch → 1.2.4
  升级 minor → 1.3.0
  升级 major → 2.0.0

=== 版本比较 ===
  1.0.0 < 2.0.0 : True
  2.0.0 < 1.0.0 : False
  1.0.0 == 1.0.0: True

版本发布时间线：
  0.1.0 → 0.2.0 → 1.0.0 → 1.0.1 → 1.1.0 → 2.0.0

=== 版本变更含义 ===
  1.0.0 → 1.0.1  [PATCH（Bug修复）]  修复了登录页面的 bug
  1.0.1 → 1.1.0  [MINOR（新功能）]  新增了用户导出功能
  1.1.0 → 2.0.0  [MAJOR（破坏性变更）]  重构 API，接口不向后兼容
```
