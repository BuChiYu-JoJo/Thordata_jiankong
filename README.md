# Thordata_jiankong - SERP监控工具

## 项目简介

SERP（Search Engine Results Page）监控工具用于实时监控多个搜索引擎API的健康状态，包括成功率、超时率、异常率等指标，并在检测到异常时通过钉钉发送告警通知。

## 功能特性

- ✅ 支持多搜索引擎监控（Google, Bing, Yandex, DuckDuckGo, Baidu, Yahoo等）
- ✅ 自动告警机制（成功率低、超时率高、连续异常）
- ✅ 详细的日志记录（按引擎和日期分类）
- ✅ 灵活的配置系统（JSON配置文件）
- ✅ 命令行参数支持
- ✅ 异步并发请求
- ✅ 钉钉Webhook通知

## 环境要求

- Python 3.8+
- aiohttp 3.8.0+

## 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/BuChiYu-JoJo/Thordata_jiankong.git
cd Thordata_jiankong
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

## 配置说明

### config.json 配置文件

配置文件包含以下主要部分：

#### 1. 搜索引擎配置 (search_engines)
```json
{
  "search_engines": {
    "google": {
      "domain": "www.google.com",
      "param": "q"
    }
  }
}
```

#### 2. 搜索关键词 (search_terms)
```json
{
  "search_terms": [
    "Apple", "Bread", "Cheese", ...
  ]
}
```

#### 3. 监控参数 (monitoring)
- `concurrency`: 并发请求数
- `timeout_seconds`: 单次请求超时时间
- `monitor_duration_minutes`: 监控持续时间
- `requests_per_engine_per_minute`: 每个引擎每分钟的请求数

#### 4. 告警阈值 (thresholds)
- `success_rate`: 成功率告警阈值（%）
- `timeout_rate`: 超时率告警阈值（%）
- `timeout_limit`: 请求超时判定时间（秒）
- `min_content_size_kb`: 最小有效内容大小（KB）

#### 5. 钉钉配置 (dingtalk)
- `webhook`: 钉钉机器人Webhook地址
- `keyword`: 通知消息关键词

#### 6. 认证配置 (auth)
- `authorization`: API授权Token
- `content_type`: 请求内容类型

## 使用方法

### 基本使用

```bash
# 使用默认配置文件启动监控
python serp_monitor.py

# 或使用优化后的新脚本
python serp_monitor.py
```

### 高级用法

```bash
# 使用自定义配置文件
python serp_monitor.py -c custom_config.json

# 只监控指定的引擎
python serp_monitor.py --engines google bing

# 监控60分钟后自动停止
python serp_monitor.py --duration 60

# 组合使用
python serp_monitor.py -c custom.json --engines google --duration 120
```

### 命令行参数说明

- `-c, --config`: 指定配置文件路径（默认: config.json）
- `--engines`: 指定要监控的引擎列表（空格分隔）
- `--duration`: 监控持续时间（分钟）

## API测试示例

### 方法1: 使用http.client（标准库）
```python
import http.client 
import json

conn = http.client.HTTPSConnection("scraperapi.thordata.com")

payload = json.dumps({
    "url": "https://www.google.com/search?q=pizza&json=1"
})

headers = { 
    'Authorization': 'Bearer YOUR_TOKEN_HERE',
    'Content-Type': 'application/json'
}

conn.request("POST", "/request", payload, headers) 
res = conn.getresponse() 
data = res.read() 
print(data.decode("utf-8"))
```

### 方法2: 使用aiohttp（异步）
```python
import aiohttp
import asyncio

async def test_api():
    async with aiohttp.ClientSession() as session:
        headers = {
            'Authorization': 'Bearer YOUR_TOKEN_HERE',
            'Content-Type': 'application/json'
        }
        payload = {
            "url": "https://www.google.com/search?q=pizza&json=1"
        }
        async with session.post(
            'https://scraperapi.thordata.com/request',
            json=payload,
            headers=headers
        ) as response:
            data = await response.text()
            print(data)

asyncio.run(test_api())
```

## 告警规则

### 1. 成功率告警
- 触发条件：连续3分钟成功率低于设定阈值（默认95%）
- 通知内容：包含近3分钟成功率数据

### 2. 超时率告警
- 触发条件：连续3分钟超时率高于设定阈值（默认10%）
- 通知内容：包含近3分钟超时率数据

### 3. 连续异常告警
- 触发条件：单分钟内出现连续3次5xx错误
- 通知内容：异常情况说明

## 日志文件

### 主日志
- 文件：`monitor.log`
- 内容：监控整体运行状态、告警通知状态

### 引擎日志
- 位置：`logs/{engine}/{YYYYMMDD}.log`
- 内容：每个引擎的详细请求记录、错误信息
- 特点：按引擎和日期自动分类

## 扩展指南

### 添加新的搜索引擎

在 `config.json` 中添加新引擎配置：

```json
{
  "search_engines": {
    "newengine": {
      "domain": "www.newengine.com",
      "param": "q"
    }
  }
}
```

### 扩充搜索关键词

在 `config.json` 的 `search_terms` 数组中添加新关键词：

```json
{
  "search_terms": [
    "existing keywords...",
    "new keyword 1",
    "new keyword 2"
  ]
}
```

### 自定义告警阈值

修改 `config.json` 中的 `thresholds` 部分：

```json
{
  "thresholds": {
    "success_rate": 90,
    "timeout_rate": 15,
    "timeout_limit": 15,
    "min_content_size_kb": 3
  }
}
```

## 优化说明（相对于原版本）

### 代码结构优化
1. ✅ 引入面向对象设计（Config、Logger、AlertManager、SERPMonitor类）
2. ✅ 分离关注点，每个类职责清晰
3. ✅ 提高代码可读性和可维护性

### 配置管理优化
1. ✅ 使用JSON配置文件，易于修改和版本控制
2. ✅ 配置验证机制，启动时检查必需字段
3. ✅ 支持动态配置加载

### 命令行增强
1. ✅ 支持命令行参数（--config, --engines, --duration）
2. ✅ 提供帮助信息和使用示例
3. ✅ 增强灵活性和易用性

### 错误处理改进
1. ✅ 更完善的异常捕获和错误信息
2. ✅ 优雅退出机制（Ctrl+C）
3. ✅ 详细的错误日志记录

### 扩展性提升
1. ✅ 易于添加新引擎（只需修改配置文件）
2. ✅ 易于扩展新功能（类结构清晰）
3. ✅ 支持更多自定义选项

### 文档完善
1. ✅ 详细的README文档
2. ✅ 代码注释和docstring
3. ✅ 使用示例和API测试示例

## 维护预警逻辑

本次优化**完全保留**了原有的预警逻辑：

1. ✅ 成功率连续3分钟低于阈值 → 告警
2. ✅ 超时率连续3分钟高于阈值 → 告警  
3. ✅ 单分钟内连续3次5xx错误 → 告警
4. ✅ 告警阈值可配置
5. ✅ 钉钉通知机制保持不变

## 故障排查

### 问题：无法连接API
- 检查网络连接
- 验证Authorization Token是否正确
- 确认API服务是否正常

### 问题：没有收到钉钉通知
- 检查webhook地址是否正确
- 确认钉钉机器人是否添加了关键词
- 查看monitor.log中的通知状态

### 问题：日志文件过大
- 定期清理历史日志
- 可以添加日志轮转机制
- 调整日志级别

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或联系维护者。