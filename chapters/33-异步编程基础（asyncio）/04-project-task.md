# 第33章 项目任务：异步天气数据聚合器

## 业务背景

气象应用需要同时从多个数据源（OpenWeatherMap、WeatherAPI、AccuWeather）查询同一城市的天气数据，并聚合返回最快响应的结果。需要实现超时控制、失败重试，以及并发查询多个城市。

---

## 技术要求

### 核心功能

1. **模拟多数据源**：3个异步函数分别模拟不同API（随机延迟和失败率）
2. **竞争查询**：用 `asyncio.wait(FIRST_COMPLETED)` 获取最快响应
3. **并发多城市**：用 `asyncio.gather` 同时查询10个城市
4. **超时保护**：每个API调用超时2秒（`asyncio.wait_for`）
5. **结果汇总**：统计各数据源使用次数、平均响应时间

### 代码框架

```python
# weather_aggregator.py
import asyncio
import random
import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class WeatherData:
    city: str
    source: str
    temp: float
    humidity: int
    response_time: float

async def fetch_openweather(city: str) -> WeatherData:
    """模拟 OpenWeatherMap API"""
    delay = random.uniform(0.3, 2.5)
    await asyncio.sleep(delay)
    if random.random() < 0.2:  # 20%失败率
        raise ConnectionError("OpenWeatherMap 连接超时")
    return WeatherData(
        city=city,
        source="OpenWeatherMap",
        temp=random.uniform(10, 35),
        humidity=random.randint(30, 90),
        response_time=delay
    )

async def fetch_weatherapi(city: str) -> WeatherData:
    """模拟 WeatherAPI"""
    # 请仿照上面实现（延迟0.5-3.0s，失败率15%）
    pass

async def fetch_accuweather(city: str) -> WeatherData:
    """模拟 AccuWeather"""
    # 请仿照上面实现（延迟0.2-1.5s，失败率10%）
    pass

async def query_city_weather(city: str) -> Optional[WeatherData]:
    """
    并发查询一个城市的天气
    1. 同时向3个API发起请求
    2. 返回第一个成功的结果
    3. 整体超时2秒
    4. 全部失败时返回 None
    """
    # TODO: 实现竞争查询逻辑
    pass

async def main():
    cities = ["北京", "上海", "广州", "深圳", "成都",
              "杭州", "武汉", "南京", "西安", "重庆"]

    print(f"开始查询 {len(cities)} 个城市的天气...\n")
    start = time.time()

    # TODO: 并发查询所有城市
    results = ...

    elapsed = time.time() - start

    # 打印结果
    success = [r for r in results if r is not None]
    print(f"查询完成！耗时: {elapsed:.2f}s")
    print(f"成功: {len(success)}/{len(cities)}\n")

    # TODO: 统计各数据源使用次数
    # TODO: 按城市打印结果表格

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 验收标准

| 验收项 | 要求 |
|--------|------|
| 并发效果 | 10个城市并发查询，总耗时不超过3秒 |
| 竞争逻辑 | 每个城市取最快响应的API结果 |
| 超时处理 | 超过2秒的请求被取消，视为失败 |
| 错误恢复 | API失败不影响其他城市查询 |
| 统计输出 | 打印各数据源命中率和平均响应时间 |

### 预期输出示例

```
开始查询 10 个城市的天气...

查询完成！耗时: 1.83s
成功: 9/10

城市天气结果:
  北京   | AccuWeather     | 28.3°C | 湿度 65% | 响应 0.42s
  上海   | OpenWeatherMap  | 31.1°C | 湿度 78% | 响应 0.61s
  广州   | WeatherAPI      | 33.5°C | 湿度 85% | 响应 0.38s
  ...
  重庆   | None            | 超时/全部失败

数据源统计:
  AccuWeather:    4次  (平均 0.51s)
  WeatherAPI:     3次  (平均 0.72s)
  OpenWeatherMap: 2次  (平均 0.89s)
```

### 加分项

- 实现缓存：相同城市5分钟内不重复请求（使用 `asyncio.Lock` 保护缓存字典）
- 添加重试：单个API失败时自动重试1次
- 用 `asyncio.Queue` 实现请求限速（最多5个并发请求）
