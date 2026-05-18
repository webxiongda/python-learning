# 第41章 项目任务：天气数据聚合工具

## 业务背景

你受雇于一家旅游公司，需要开发一个命令行工具，能够通过免费天气 API（Open-Meteo，无需注册）批量查询多个城市的当前温度，并输出对比报告。该工具需要稳健地处理网络错误，避免因单个城市查询失败导致整体崩溃。

## 技术要求

使用 `requests` 库完成以下功能：

1. **城市坐标查询**（使用 Open-Meteo Geocoding API）
   - `GET https://geocoding-api.open-meteo.com/v1/search?name={城市名}&count=1&language=zh`
   - 解析返回的经纬度

2. **天气数据获取**（使用 Open-Meteo Weather API）
   - `GET https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true`
   - 提取当前温度和风速

3. **创建带重试的 Session**
   - `Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 503])`

4. **超时设置**：每个请求 `timeout=8` 秒

5. **错误处理**：单个城市失败时打印错误并继续处理下一个

6. **输出格式**：
```
城市天气报告
============
城市          温度(°C)   风速(km/h)  状态
北京          28.5       12.3       晴天
上海          31.2       8.7        晴天
成都          查询失败：连接超时
广州          33.1       15.6       晴天
```

## 代码框架

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Tuple

CITIES = ["Beijing", "Shanghai", "Chengdu", "Guangzhou", "Shenzhen"]

def create_session() -> requests.Session:
    # TODO: 创建带重试的 Session
    pass

def get_coordinates(session: requests.Session, city: str) -> Optional[Tuple[float, float]]:
    # TODO: 查询城市经纬度
    # 返回 (latitude, longitude) 或 None
    pass

def get_weather(session: requests.Session, lat: float, lon: float) -> Optional[dict]:
    # TODO: 查询天气数据
    # 返回 {"temperature": 28.5, "windspeed": 12.3, "weathercode": 0} 或 None
    pass

def format_report(results: list) -> str:
    # TODO: 格式化输出报告
    pass

def main():
    session = create_session()
    results = []
    
    for city in CITIES:
        # TODO: 查询每个城市并收集结果
        pass
    
    print(format_report(results))
    session.close()

if __name__ == "__main__":
    main()
```

## 验收标准

- [ ] 使用 Session + HTTPAdapter 配置了重试策略
- [ ] 所有请求都设置了 timeout
- [ ] 使用 `try/except` 捕获 `Timeout`、`ConnectionError`、`HTTPError`
- [ ] 单个城市失败不影响其他城市的查询
- [ ] 输出包含城市名、温度、风速三列数据
- [ ] 代码有适当的函数拆分（≥3个函数），每个函数有注释说明

## 加分项

- 添加并发请求（使用 `concurrent.futures.ThreadPoolExecutor`）加速批量查询
- 将结果保存为 CSV 文件
- 添加命令行参数（`argparse`）支持用户自定义城市列表
