# 第52章：项目结构与打包 — 自测题

## 题目1：布局选择

对比以下两种项目布局，回答问题：

**布局A（Flat）：**
```
my-project/
├── my_package/
│   ├── __init__.py
│   └── core.py
├── tests/
└── pyproject.toml
```

**布局B（Src）：**
```
my-project/
├── src/
│   └── my_package/
│       ├── __init__.py
│       └── core.py
├── tests/
└── pyproject.toml
```

问：Src 布局比 Flat 布局有什么优势？在使用 Src 布局时，`pip install -e .` 有什么特别的作用？

### 参考答案

**Src 布局的优势：**

1. **避免隐式导入问题**：使用 Flat 布局时，在项目根目录运行 `pytest`，Python 会将 `my_package/` 目录直接加入 `sys.path`，测试时实际导入的是本地未安装的版本，而不是已安装的版本。Src 布局强制使用已安装的包，测试结果更真实。

2. **结构更清晰**：源码与配置文件分离，一眼就能看出哪些是源码，哪些是项目配置。

3. **防止意外包含**：构建时不会意外将根目录下的其他 `.py` 文件打包进去。

**`pip install -e .`（可编辑安装）的作用：**

`-e` 表示 editable（可编辑）模式，会在 Python 环境中创建一个链接指向你的 `src/` 目录，而不是复制文件。这样：
- 修改源码后立即生效，无需重新安装
- 测试时使用的是 `src/my_package/` 下的代码（已安装路径）
- 既享受 Src 布局的隔离优势，又保持开发效率

---

## 题目2：pyproject.toml 填空

以下 pyproject.toml 有多处空白，请填写正确内容：

```toml
[___________]            # (1) 构建系统配置块
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "data-toolkit"
version = "0.3.1"
requires-python = "___"  # (2) 要求 Python 3.10 及以上
authors = [
    {name = "李四", ___ = "lisi@example.com"},  # (3) 邮箱字段名
]
dependencies = [
    "pandas___2.0.0",    # (4) 要求 pandas 2.0.0 或更高版本
]

[project.___-dependencies]  # (5) 可选依赖配置块名称
dev = ["pytest>=7.0", "black>=23.0"]
```

### 参考答案

```toml
[build-system]           # (1) 正确：build-system
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "data-toolkit"
version = "0.3.1"
requires-python = ">=3.10"  # (2) 正确：>=3.10
authors = [
    {name = "李四", email = "lisi@example.com"},  # (3) 正确：email
]
dependencies = [
    "pandas>=2.0.0",     # (4) 正确：>=2.0.0
]

[project.optional-dependencies]  # (5) 正确：optional-dependencies
dev = ["pytest>=7.0", "black>=23.0"]
```

---

## 题目3：Wheel 文件命名

解释以下 wheel 文件名的含义：

```
requests-2.31.0-py3-none-any.whl
numpy-1.26.0-cp311-cp311-macosx_11_0_arm64.whl
```

### 参考答案

**文件名格式：** `{包名}-{版本}-{Python实现标签}-{ABI标签}-{平台标签}.whl`

**requests-2.31.0-py3-none-any.whl：**
- `requests`：包名
- `2.31.0`：版本号
- `py3`：支持任意 Python 3.x 实现（纯 Python，不依赖 CPython 特性）
- `none`：无 ABI 要求（纯 Python，无 C 扩展）
- `any`：跨平台，在 Windows/macOS/Linux 都可使用

**numpy-1.26.0-cp311-cp311-macosx_11_0_arm64.whl：**
- `numpy`：包名
- `1.26.0`：版本号
- `cp311`：专为 CPython 3.11 编译
- `cp311`：需要 CPython 3.11 的 ABI
- `macosx_11_0_arm64`：仅支持 macOS 11.0+ ARM64（Apple Silicon）

**总结：** `any` 平台的包（纯 Python）可以跨平台安装；带有 C 扩展的包（如 numpy）需要针对特定 Python 版本和平台单独构建，所以 PyPI 上同一个包往往有多个 wheel 文件对应不同平台。

---

## 题目4：构建和发布流程排序

将以下步骤按正确顺序排列：

A. `twine upload dist/*`（发布到 PyPI）  
B. `python -m build`（构建 wheel 和 sdist）  
C. 在 `pyproject.toml` 填写完整项目元数据  
D. `pip install build twine`（安装构建和发布工具）  
E. `twine check dist/*`（检查包格式）  
F. 在测试 PyPI 验证安装效果  

### 参考答案

正确顺序：**C → D → B → E → F → A**

1. **C**：先准备好完整的 `pyproject.toml` 配置
2. **D**：安装 `build` 和 `twine` 工具
3. **B**：运行 `python -m build` 生成 `dist/` 目录下的 wheel 和 sdist
4. **E**：用 `twine check` 验证包的 README 格式和元数据是否符合 PyPI 要求
5. **F**：先用 `twine upload --repository testpypi dist/*` 发布到测试 PyPI，然后验证 `pip install --index-url https://test.pypi.org/simple/ 包名` 是否正常
6. **A**：确认无误后才正式发布到 PyPI

> 重要：跳过测试 PyPI 直接发布到正式 PyPI 是危险的！一旦发布，正式 PyPI 不允许删除或覆盖已发布的版本。

---

## 题目5：实战问题排查

同事的项目使用 Src 布局，但运行 `pytest` 时报错：

```
ModuleNotFoundError: No module named 'my_package'
```

请分析可能的原因并给出解决方案。

### 参考答案

**可能原因和解决方案：**

**原因1：包未安装（最常见）**  
使用 Src 布局时，必须先安装包才能导入。解决方法：
```bash
# 以可编辑模式安装（开发时推荐）
pip install -e .

# 或者普通安装
pip install .
```

**原因2：在错误的虚拟环境中运行**  
可能包安装在了另一个虚拟环境中。解决方法：
```bash
# 检查当前使用的 Python
which python
# 确认已安装包
pip list | grep my-package
# 重新激活正确的虚拟环境
source .venv/bin/activate
```

**原因3：pyproject.toml 未配置包路径**  
Hatchling 需要知道包在哪里。在 `pyproject.toml` 中添加：
```toml
[tool.hatch.build.targets.wheel]
packages = ["src/my_package"]
```

**原因4：`conftest.py` 路径配置问题**  
在项目根目录创建 `conftest.py` 或配置 `pytest.ini`：
```ini
# pytest.ini
[pytest]
testpaths = tests
```

**最佳实践总结：** Src 布局项目的标准开发工作流是：
1. 创建并激活虚拟环境
2. 运行 `pip install -e ".[dev]"` 以可编辑方式安装
3. 之后就可以正常运行 `pytest` 了
