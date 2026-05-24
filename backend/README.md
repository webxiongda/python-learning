# Python FastAPI Learning Workbench Backend

本后端为 Python 学习工作台提供本地 API，默认读取仓库根目录的 `README.md` 和 `chapters/`，并把用户进度写入根目录 `python-workbench.db`。

## 安装依赖

```bash
python3 -m pip install -r backend/requirements.txt
npm install
```

## 启动

```bash
make backend
```

或同时启动前后端：

```bash
npm run dev
```

前端默认运行在 `http://localhost:5173`，后端默认运行在 `http://localhost:8000`。

## 验证

```bash
python3 -m pytest backend/tests/test_workbench_api.py -q
npm run check
npm run build
make all
```

## AI 扩展点

当前面试评分是本地规则占位，代码集中在 `backend/app/interview_service.py`。后续接入模型评分、流式输出、RAG 检索或 Agent 工具调用时，优先替换该服务层，不要把模型 SDK 调用散落到路由函数里。
