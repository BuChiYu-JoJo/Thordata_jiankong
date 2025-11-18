# API请求格式说明

## 更新说明

根据用户反馈，监控脚本已更新为使用 `application/x-www-form-urlencoded` 格式，这是ScraperAPI推荐的格式。

## 当前使用的API请求格式（推荐）

监控脚本现在使用 `application/x-www-form-urlencoded` 格式：

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

## 旧的API请求格式

之前的版本使用 `application/json` 格式：

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

| 特性 | URL编码格式（当前） | JSON格式（旧版） |
|------|-------------|-----------------|
| Content-Type | application/x-www-form-urlencoded | application/json |
| 数据结构 | key1=value1&key2=value2 | {"key": "value"} |
| 参数形式 | engine=google&q=pizza&json=1 | {"url": "https://..."} |
| 可读性 | 好 | 好 |
| API直接支持 | ✅ 是 | ❌ 否 |
| 监控脚本使用 | ✅ 是 | ❌ 否（已更新） |

## URL编码格式的优势

1. **直接的引擎参数**：使用engine参数直接指定搜索引擎
2. **简洁明了**：参数简单，易于理解
3. **API原生支持**：ScraperAPI推荐的格式
4. **易于调试**：参数清晰可见

## 在监控脚本中的实现

### 当前版本 (serp_monitor.py)
```python
# 配置文件
"auth": {
    "authorization": "Bearer 5d7caa7f1e33019f9b1851e179415bc9",
    "content_type": "application/x-www-form-urlencoded"  # URL编码格式
}

# 构建请求参数
def build_payload(self, engine: str, term: str) -> dict:
    engine_config = self.config.search_engines[engine]
    api_engine = engine_config.get("engine", engine)
    param = engine_config["param"]
    
    # 构建API请求参数
    params = {
        "engine": api_engine,
        param: term,
        "json": "1"
    }
    
    return {
        "url": url,  # 用于日志记录
        "params": params  # 用于API请求
    }

# 发送请求
async with session.post(
    url=self.api_url,
    headers=self.config.auth_header,
    data=urlencode(payload["params"]),  # URL编码
    timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
) as r:
```

### 原始脚本 (SERP_Monitor​_log.py) - 旧格式
```python
AUTH_HEADER = {
    "Authorization": "Bearer 5d7caa7f1e33019f9b1851e179415bc9",
    "Content-Type": "application/json"  # 使用JSON格式
}

async with session.post(
    url="https://scraperapi.thordata.com/request",
    headers=AUTH_HEADER,
    json=build_payload(engine, term),  # JSON格式（旧方式）
    timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
) as r:
```

## 日志记录保持不变

虽然API请求格式已更新为URL编码，但日志中仍然记录完整的URL以便调试：

```python
# 构建时同时返回URL（用于日志）和params（用于API）
def build_payload(self, engine: str, term: str) -> dict:
    engine_config = self.config.search_engines[engine]
    domain = engine_config["domain"]
    param = engine_config["param"]
    api_engine = engine_config.get("engine", engine)
    
    # URL用于日志记录
    url = f"https://{domain}/search?{param}={quote(term)}&json=1"
    
    # params用于API请求
    params = {
        "engine": api_engine,
        param: term,
        "json": "1"
    }
    
    return {"url": url, "params": params}

# 日志记录
request_url = self.build_payload(engine, term)["url"]
error_msg = (
    f"[{engine}] 请求失败\n"
    f"关键词: {term}\n"
    f"请求URL: {request_url}\n"  # 日志中显示完整URL
    ...
)
```

## 测试脚本

项目包含 `test_api_connection.py` 脚本，可以测试两种格式：

```bash
python test_api_connection.py
```

该脚本会：
1. 测试URL编码格式（当前脚本使用的格式）
2. 测试JSON格式（旧格式）
3. 显示对比结果和推荐使用方式

## 结论

监控脚本已更新为使用 **URL编码格式** (`application/x-www-form-urlencoded`)，这是ScraperAPI推荐的格式。

### 主要改进
✅ 使用 `Content-Type: application/x-www-form-urlencoded`  
✅ 使用 `data=urlencode(params)` 参数发送请求  
✅ 使用 `engine` 参数直接指定搜索引擎  
✅ 保持日志记录URL的逻辑不变  

### 建议
- 继续使用URL编码格式作为API请求方式
- 日志中保持记录完整URL便于调试
- engine参数映射在config.json中配置
