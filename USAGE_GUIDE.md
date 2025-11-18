# 脚本对比与使用指南

## 文件说明

### 原始脚本
- **文件名**: `SERP_Monitor​_log.py`
- **特点**: 功能完整，配置硬编码在脚本中
- **适用**: 简单场景，配置不常变动

### 优化脚本
- **文件名**: `serp_monitor.py`
- **特点**: 模块化设计，配置外置，命令行支持
- **适用**: 生产环境，需要灵活配置和管理

## 主要改进对比

| 特性 | 原始脚本 | 优化脚本 |
|------|---------|---------|
| 配置方式 | 硬编码在脚本中 | 外置JSON配置文件 |
| 命令行参数 | 无 | 支持 --config, --engines, --duration |
| 代码结构 | 过程式 | 面向对象（4个类） |
| 搜索引擎数量 | 4个 | 6个（新增baidu, yahoo） |
| 关键词数量 | 30个 | 55个 |
| 文档 | 无 | 完整README + API说明 |
| 测试脚本 | 无 | API连接测试脚本 |
| 错误处理 | 基本 | 增强，带类型提示 |
| 可维护性 | 中 | 高 |

## 使用场景对比

### 场景1: 快速测试
```bash
# 原始脚本 - 需要编辑脚本修改配置
vim SERP_Monitor​_log.py  # 修改配置
python SERP_Monitor​_log.py

# 优化脚本 - 使用命令行参数
python serp_monitor.py --engines google --duration 5
```

### 场景2: 只监控特定引擎
```bash
# 原始脚本 - 需要注释代码
# 需要在脚本中注释掉不需要的引擎

# 优化脚本 - 命令行指定
python serp_monitor.py --engines google bing
```

### 场景3: 多环境配置
```bash
# 原始脚本 - 需要维护多个脚本副本
python SERP_Monitor​_log_prod.py
python SERP_Monitor​_log_test.py

# 优化脚本 - 使用不同配置文件
python serp_monitor.py -c config_prod.json
python serp_monitor.py -c config_test.json
```

## 功能保持不变

以下核心功能在两个版本中**完全相同**：

1. ✅ **预警逻辑**
   - 成功率连续3分钟低于阈值 → 告警
   - 超时率连续3分钟高于阈值 → 告警
   - 单分钟内连续3次5xx错误 → 告警

2. ✅ **监控指标**
   - 成功率、超时率、异常率、错误率
   - 响应时间、内容大小
   - 状态码统计

3. ✅ **日志记录**
   - 主日志：monitor.log
   - 引擎日志：logs/{engine}/{date}.log
   - 按日期自动分类

4. ✅ **钉钉通知**
   - Webhook集成
   - Markdown格式
   - 包含历史数据

5. ✅ **API请求**
   - 异步并发
   - 超时控制
   - 重试机制

## 配置迁移指南

### 从原始脚本迁移到优化脚本

1. **提取配置到config.json**

原始脚本中的配置：
```python
SEARCH_ENGINES = {
    "google": {"domain": "www.google.com", "param": "q"},
    # ...
}
THRESHOLD_SUCCESS_RATE = 95
AUTH_HEADER = {"Authorization": "Bearer xxx", ...}
```

迁移到config.json：
```json
{
  "search_engines": {
    "google": {"domain": "www.google.com", "param": "q"}
  },
  "thresholds": {
    "success_rate": 95
  },
  "auth": {
    "authorization": "Bearer xxx"
  }
}
```

2. **更新启动命令**

```bash
# 旧方式
python SERP_Monitor​_log.py

# 新方式（默认使用config.json）
python serp_monitor.py

# 或指定配置文件
python serp_monitor.py -c config.json
```

3. **保持原有功能不变**

所有预警阈值、监控逻辑、日志格式保持一致，无需修改依赖这些功能的其他系统。

## 扩展性对比

### 添加新搜索引擎

**原始脚本**：
```python
# 编辑 SERP_Monitor​_log.py
SEARCH_ENGINES = {
    "google": {...},
    "newengine": {"domain": "...", "param": "..."}  # 添加这行
}
```

**优化脚本**：
```json
// 编辑 config.json
{
  "search_engines": {
    "google": {...},
    "newengine": {"domain": "...", "param": "..."}
  }
}
```

### 添加新关键词

**原始脚本**：
```python
# 编辑 SERP_Monitor​_log.py
SEARCH_TERMS = [
    "Apple", "Bread",
    "NewKeyword"  # 添加这行
]
```

**优化脚本**：
```json
// 编辑 config.json
{
  "search_terms": [
    "Apple", "Bread",
    "NewKeyword"
  ]
}
```

### 修改告警阈值

**原始脚本**：
```python
# 编辑 SERP_Monitor​_log.py
THRESHOLD_SUCCESS_RATE = 90  # 修改这行
THRESHOLD_TIMEOUT_RATE = 15  # 修改这行
```

**优化脚本**：
```json
// 编辑 config.json
{
  "thresholds": {
    "success_rate": 90,
    "timeout_rate": 15
  }
}
```

## 推荐使用方式

### 新项目
推荐使用 **优化脚本** (`serp_monitor.py`)：
- ✅ 更好的可维护性
- ✅ 灵活的配置管理
- ✅ 完整的文档和测试
- ✅ 命令行支持

### 现有项目
可以继续使用 **原始脚本** (`SERP_Monitor​_log.py`)，但建议逐步迁移：
1. 保留原脚本作为备份
2. 使用config.json提取配置
3. 测试优化脚本的功能
4. 切换到优化脚本

### 快速验证
使用优化脚本进行短时间测试：
```bash
# 只监控google，运行5分钟
python serp_monitor.py --engines google --duration 5
```

## 常见问题

### Q: 两个脚本可以同时运行吗？
A: 可以，但会写入相同的日志文件，建议使用不同的配置文件。

### Q: 如何从原脚本切换到新脚本？
A: 
1. 复制配置到config.json
2. 测试新脚本：`python serp_monitor.py --duration 1`
3. 确认日志和告警正常
4. 替换生产环境的启动命令

### Q: 预警逻辑有变化吗？
A: 没有。预警逻辑、阈值计算、告警条件完全相同。

### Q: 性能有差异吗？
A: 基本相同。优化脚本增加了类封装，但对性能影响可忽略不计。

### Q: 日志格式有变化吗？
A: 没有。日志格式、文件路径、内容结构完全相同。

## 总结

优化脚本是原始脚本的**增强版本**，而不是替代版本：
- ✅ 保留所有核心功能
- ✅ 保持预警逻辑不变
- ✅ 增加灵活性和可维护性
- ✅ 添加文档和测试工具
- ✅ 支持更多引擎和关键词

**建议**：新部署使用优化脚本，现有部署可逐步迁移。
