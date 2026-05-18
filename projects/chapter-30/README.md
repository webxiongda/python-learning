# Chapter 30 Project: 图书馆 OOP 系统

## Goal

使用面向对象方式实现图书馆借阅系统，重点练习类职责、策略模式和测试。

## Core Use Cases

- 添加图书
- 注册会员
- 借书和还书
- 查询逾期
- 按会员等级限制借阅数量

## Commands

```bash
python -m pytest
```

## Acceptance

- 至少两个会员策略。
- 不同策略行为由测试验证。
- 不出现承载所有逻辑的万能类。
