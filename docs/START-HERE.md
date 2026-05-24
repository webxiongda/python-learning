# Start Here

这份路线的正确使用方式不是从第 01 章一路读到第 60 章，而是按“FastAPI + AI 应用后端”主线推进。

## 每次学习前

1. 打开 `progress.md`，确认当前章节。
2. 打开 `review-plan.md`，如果今天有复习任务，先复习。
3. 打开当前章节的 `01-theory.md` 和 `02-demo.md`。

## 每章完成顺序

1. 阅读 `01-theory.md`，只抓核心概念和常见坑。
2. 跑通 `02-demo.md`，必须实际执行或手动推演。
3. 完成 `03-check.md`，不会的写入 `mistakes.md`。
4. 做 `04-project-task.md`，至少产出 README 或最小代码。
5. 更新本章 `review.md` 和根目录 `review-plan.md`。

## 主线优先级

先完成 FastAPI + AI 应用第一层：

```text
01-12、15、19、29、39、41、44、45、46、49、50、51
```

第 50 章 AI Assistant API 是第一层的核心验收点。能完成它，说明基础语法、测试、HTTP、FastAPI、流式响应、数据库和工程结构已经串起来。

FastAPI 重点学习说明见 `docs/FASTAPI-AI-FOCUS.md`。

## 每周复盘

每周固定做一次：

- 运行 `make all` 或 `python3 tools/check_learning_repo.py`。
- 查看 `mistakes.md`，挑 1-2 个问题复盘。
- 更新 `progress.md` 的当前状态。
- 确认 `projects/` 至少有一个项目在推进。
