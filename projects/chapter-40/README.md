# Chapter 40 Project: 异步网页状态采集器

## Goal

实现一个支持并发、超时、重试、限速和报告输出的网页状态采集器。

## Inputs and Outputs

- 输入：`urls.txt`
- 输出：JSON 或 CSV 结果文件
- 报告：成功数、失败数、平均耗时、最慢 URL

## Commands

```bash
python -m crawler.runner --urls urls.txt --concurrency 5 --timeout 5 --retries 2
python -m pytest
```

## Acceptance

- 单个 URL 失败不影响整体任务。
- 测试不依赖真实外网。
- 日志包含 URL、异常类型和耗时。
