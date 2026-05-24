# FastAPI + AI 应用学习重点

## 定位

这条 Python 路线现在按“Java 工程基础 + Python AI 应用后端”优化。FastAPI 是主框架，学习目标不是做传统 CMS 或后台管理系统，而是能交付 AI 应用 API：

- AI 聊天接口
- 流式输出
- RAG 文档处理任务
- Agent 工具调用入口
- 会话历史和任务状态
- 模型供应商封装
- API Key、限流、日志和部署

## 主线章节

| 阶段 | 章节 | 重点 |
|------|------|------|
| Python 基础 | 01-12、15、19 | 语法、函数、模块、类型注解、Pydantic 思维 |
| 测试和调试 | 29、39 | pytest、mock、日志、错误定位 |
| HTTP 和 API | 41、44、49 | 请求响应、OpenAPI、错误码、限流、版本控制 |
| FastAPI 进阶 | 45 | 依赖注入、认证、中间件、后台任务、流式响应 |
| AI API 项目 | 50 | AI Assistant API 项目 |
| 数据和缓存 | 46-48 | 会话、任务、缓存、模型调用记录 |
| 工程化 | 51-56 | Docker、CI/CD、安全、部署 |

## FastAPI 必会能力

### 1. Pydantic 请求/响应建模

AI 接口通常参数多、结构嵌套深，必须用 schema 固定边界：

- `ChatRequest`
- `ChatResponse`
- `StreamEvent`
- `TaskStatus`
- `ErrorResponse`

### 2. 依赖注入

必须能用 `Depends` 管理：

- 当前用户或 API Key
- 数据库会话
- 配置对象
- 模型客户端
- request_id / trace_id

### 3. 模型客户端封装

不要在 Router 中直接调用模型 SDK。统一封装：

```text
Router -> Service -> ModelClient -> Provider SDK / HTTP API
```

这样才能测试、替换供应商、加重试、加超时、加日志。

### 4. 流式响应

AI 聊天体验通常需要边生成边返回。FastAPI 中重点掌握：

- `StreamingResponse`
- SSE 格式：`data: ...\n\n`
- 完成事件
- 流中错误事件
- 客户端断开处理

### 5. 后台任务边界

`BackgroundTasks` 只适合轻量后处理。长任务要进入任务表或 Worker：

- 适合：写日志、保存统计、发送非关键通知。
- 不适合：PDF 解析、向量索引、长时间模型批处理、付费结算。

### 6. 测试策略

AI API 测试不能依赖真实模型：

- 用 mock model client。
- 测普通 JSON 响应。
- 测流式事件。
- 测超时和供应商错误。
- 测认证和限流。

## 第 50 章最终项目

第 50 章核心项目是 `AI Assistant API`：

- `/chat`
- `/chat/stream`
- `/conversations`
- `/tasks/document-ingest`
- `/tasks/{id}`
- 统一错误响应
- Mock 模型客户端
- 测试覆盖核心路径

完成后，你应该能把真实 OpenAI、通义、智谱、DeepSeek 或内部模型 API 接到 `ModelClient` 后面，而不破坏 FastAPI 路由和测试。
