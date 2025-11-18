# 快速开始指南

## 5分钟快速上手

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 修改配置（可选）
编辑 `config.json`，修改以下内容：
- `auth.authorization`: 你的API Token
- `dingtalk.webhook`: 你的钉钉Webhook地址
- `dingtalk.keyword`: 钉钉通知关键词

### 3. 运行监控
```bash
# 方式1: 使用默认配置，监控所有引擎
python serp_monitor.py

# 方式2: 只监控Google，运行5分钟
python serp_monitor.py --engines google --duration 5

# 方式3: 使用自定义配置文件
python serp_monitor.py -c my_config.json
```

### 4. 查看日志
```bash
# 主日志
cat monitor.log

# 引擎日志（按引擎和日期分类）
ls logs/
cat logs/google/20241118.log
```

## 常用命令

```bash
# 显示帮助
python serp_monitor.py --help

# 测试API连接
python test_api_connection.py

# 只监控Google和Bing
python serp_monitor.py --engines google bing

# 监控30分钟后自动停止
python serp_monitor.py --duration 30

# 停止监控（Ctrl+C）
# 在运行中的终端按 Ctrl+C
```

## 配置快速修改

### 添加新引擎
编辑 `config.json`：
```json
{
  "search_engines": {
    "existing_engines": {...},
    "newengine": {
      "domain": "www.newengine.com",
      "param": "q"
    }
  }
}
```

### 添加新关键词
编辑 `config.json`：
```json
{
  "search_terms": [
    "existing keywords...",
    "new keyword 1",
    "new keyword 2"
  ]
}
```

### 修改告警阈值
编辑 `config.json`：
```json
{
  "thresholds": {
    "success_rate": 90,
    "timeout_rate": 15
  }
}
```

## 文档导航

- **README.md** - 完整项目文档
- **API_FORMAT_EXPLANATION.md** - API格式说明
- **USAGE_GUIDE.md** - 使用指南和对比
- **OPTIMIZATION_SUMMARY.md** - 优化总结

## 故障排查

### 问题: 无法连接API
```bash
# 检查网络连接和Token
python test_api_connection.py
```

### 问题: 没有收到钉钉通知
1. 检查 config.json 中的 webhook 地址
2. 确认钉钉机器人配置了正确的关键词
3. 查看 monitor.log 中的通知状态

### 问题: 日志文件过大
```bash
# 定期清理历史日志
rm -rf logs/*/202*.log
```

## 下一步

1. ✅ 根据实际需求调整配置
2. ✅ 添加更多监控引擎
3. ✅ 扩充关键词列表
4. ✅ 调整告警阈值
5. ✅ 设置定时任务（cron）

## 获取帮助

查看完整文档：
- **README.md** - 项目主文档
- **USAGE_GUIDE.md** - 详细使用指南

提交Issue：
https://github.com/BuChiYu-JoJo/Thordata_jiankong/issues
