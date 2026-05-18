# Chapter 10 Project: 学生成绩管理系统 CLI

## Goal

实现一个可运行、可测试的命令行学生成绩管理系统。

## Required Commands

```bash
python -m student_scores.cli add-student --id 1 --name Alice
python -m student_scores.cli add-score --id 1 --course math --score 95
python -m student_scores.cli list
python -m student_scores.cli rank
python -m student_scores.cli stats
python -m pytest
```

## Deliverables

- `student_scores/` 源码包
- `tests/` 单元测试
- `data/students.json` 示例数据
- README 中的运行说明和踩坑记录

## Acceptance

- 能从空 JSON 文件开始运行。
- 重复学号、非法成绩、找不到学生都有明确错误。
- 排名和统计函数可以被单独测试。

## Notes

- 业务函数返回结构化数据，CLI 层负责打印。
- 文件读写只放在 `storage.py`。
