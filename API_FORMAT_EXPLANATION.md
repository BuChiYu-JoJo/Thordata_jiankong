# API请求格式说明

## 问题陈述中的代码问题

问题陈述中提供的示例代码使用了 `application/x-www-form-urlencoded` 格式：

```python
import http.client 
from urllib.parse import urlencode

conn = http.client.HTTPSConnection("scraperapi.thordata.com")
params = {
    "engine": "google",
    "q": "pizza",
    "json": "1"
}
payload = urlencode(params)  # URL编码格式

headers = { 
    'Authorization': 'Bearer 663fba4eb51f1fb2ec007f1b7bd73f16',
    'Content-Type': 'application/x-www-form-urlencoded'  # URL编码
}

conn.request("POST", "/request", payload, headers) 
```

## 正确的API请求格式

监控脚本使用的是 `application/json` 格式（推荐）：

```python
import http.client 
import json

conn = http.client.HTTPSConnection("scraperapi.thordata.com")

payload = json.dumps({
    "url": "https://www.google.com/search?q=pizza&json=1"
})

headers = { 
    'Authorization': 'Bearer 663fba4eb51f1fb2ec007f1b7bd73f16',
    'Content-Type': 'application/json'  # JSON格式
}

conn.request("POST", "/request", payload, headers)
```

## 两种格式的对比

| 特性 | URL编码格式 | JSON格式（推荐） |
|------|-------------|-----------------|
| Content-Type | application/x-www-form-urlencoded | application/json |
| 数据结构 | key1=value1&key2=value2 | {"key": "value"} |
| 嵌套数据 | 不支持或复杂 | 原生支持 |
| 可读性 | 一般 | 好 |
| RESTful标准 | 较旧 | 现代标准 |
| 监控脚本使用 | ❌ 否 | ✅ 是 |

## JSON格式的优势

1. **更好的结构化支持**：原生支持嵌套对象和数组
2. **标准化**：符合现代RESTful API设计规范
3. **易于维护**：代码更清晰，易于理解和修改
4. **类型安全**：保留数据类型信息
5. **工具支持**：大多数开发工具和库对JSON有更好的支持

## 在监控脚本中的实现

### 原始脚本 (SERP_Monitor​_log.py)
```python
AUTH_HEADER = {
    "Authorization": "Bearer 5d7caa7f1e33019f9b1851e179415bc9",
    "Content-Type": "application/json"  # 使用JSON格式
}

async with session.post(
    url="https://scraperapi.thordata.com/request",
    headers=AUTH_HEADER,
    json=build_payload(engine, term),  # aiohttp自动处理JSON序列化
    timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
) as r:
```

### 优化脚本 (serp_monitor.py)
```python
def build_payload(self, engine: str, term: str) -> dict:
    """构建API请求payload"""
    engine_config = self.config.search_engines[engine]
    domain = engine_config["domain"]
    param = engine_config["param"]
    return {
        "url": f"https://{domain}/search?{param}={quote(term)}&json=1"
    }

async with session.post(
    url=self.api_url,
    headers=self.config.auth_header,  # 包含 Content-Type: application/json
    json=self.build_payload(engine, term),
    timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
) as r:
```

## 测试脚本

项目包含 `test_api_connection.py` 脚本，可以测试两种格式：

```bash
python test_api_connection.py
```

该脚本会：
1. 测试JSON格式（监控脚本使用的格式）
2. 测试URL编码格式（问题陈述中的格式）
3. 显示对比结果和推荐使用方式

## 结论

监控脚本使用的 **JSON格式** 是正确且推荐的方式。问题陈述中的URL编码格式示例可能是旧版本或示例代码，不应替换当前实现。

### 建议
✅ 保持使用 `Content-Type: application/json`  
✅ 继续使用 `json=payload` 参数自动序列化  
❌ 不要改为 `application/x-www-form-urlencoded`
