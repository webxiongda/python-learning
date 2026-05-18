# 第51章：虚拟环境与依赖管理 — 项目任务

## 项目名称：依赖环境检查工具

## 业务背景

你所在的开发团队经常遇到以下问题：
- 新同事拿到项目后不知道如何搭建环境
- `requirements.txt` 里有些包没有锁定版本，导致不同人安装的版本不同
- 生产环境和开发环境的包混在一起，部署包体积过大
- 不确定本地环境和 CI 环境是否一致

你需要开发一个命令行工具 `env-check`，帮助团队自动检查和诊断项目的依赖管理状态。

---

## 技术要求

### 功能 1：环境信息报告

读取当前 Python 环境信息并以结构化方式输出：

```
Python 版本:    3.11.6
虚拟环境:       是 (.venv)
pip 版本:       23.3.1
已安装包数量:   42 个
```

### 功能 2：requirements.txt 质量检查

分析项目的 `requirements.txt`，输出以下检查结果：

- 总依赖数量
- 已固定版本的包（`==`）数量和列表
- 未固定版本的包列表（警告）
- 是否存在已知有安全漏洞的包版本（可用简单的硬编码列表模拟）

### 功能 3：环境与 requirements.txt 对比

比较当前安装的包与 `requirements.txt` 中声明的包：

- 已安装但未在 requirements.txt 中的包（多余的包）
- 在 requirements.txt 中但未安装的包（缺失的包）
- 版本不匹配的包

### 功能 4：生成报告文件

将检查结果输出为 Markdown 格式的 `env-report.md` 文件。

---

## 项目结构

```
env-checker/
├── env_checker/
│   ├── __init__.py
│   ├── checker.py      # 核心检查逻辑
│   ├── reporter.py     # 报告生成
│   └── cli.py          # 命令行入口
├── tests/
│   └── test_checker.py
├── requirements.txt
└── README.md
```

---

## 验收标准

- [ ] `python cli.py` 能无错运行，输出环境信息报告
- [ ] 能正确解析 `requirements.txt`，区分固定版本和非固定版本的包
- [ ] 能对比当前环境与 `requirements.txt`，列出差异
- [ ] 生成的 `env-report.md` 格式正确，内容完整
- [ ] 代码有适当注释，关键函数有 docstring
- [ ] 处理文件不存在、格式错误等异常情况

## 加分项

- [ ] 支持 `--format json` 参数，以 JSON 格式输出结果
- [ ] 支持检查 `pyproject.toml`（Poetry 项目）
- [ ] 添加颜色输出（使用 `colorama` 或 ANSI 转义码）
