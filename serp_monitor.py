#!/usr/bin/env python3
"""
SERP Monitor - 搜索引擎结果页面监控工具
功能：监控多个搜索引擎API的健康状态，自动告警异常情况
"""
import aiohttp
import asyncio
import json
import os
import sys
import time
import logging
import argparse
import random
from pathlib import Path
from urllib.parse import quote, urlencode
from datetime import datetime
from collections import deque, defaultdict
from logging import FileHandler
from typing import Dict, List, Any, Optional


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {e}")
    
    def _validate_config(self):
        """验证配置文件必需字段"""
        required_keys = ['search_engines', 'search_terms', 'monitoring', 'thresholds', 'auth']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"配置文件缺少必需字段: {key}")
    
    @property
    def search_engines(self) -> dict:
        return self.config['search_engines']
    
    @property
    def search_terms(self) -> list:
        return self.config['search_terms']
    
    @property
    def concurrency(self) -> int:
        return self.config['monitoring']['concurrency']
    
    @property
    def timeout_seconds(self) -> int:
        return self.config['monitoring']['timeout_seconds']
    
    @property
    def monitor_duration_minutes(self) -> int:
        return self.config['monitoring']['monitor_duration_minutes']
    
    @property
    def requests_per_engine(self) -> int:
        return self.config['monitoring']['requests_per_engine_per_minute']
    
    @property
    def threshold_success_rate(self) -> float:
        return self.config['thresholds']['success_rate']
    
    @property
    def threshold_timeout_rate(self) -> float:
        return self.config['thresholds']['timeout_rate']
    
    @property
    def timeout_limit(self) -> int:
        return self.config['thresholds']['timeout_limit']
    
    @property
    def min_content_size_kb(self) -> float:
        return self.config['thresholds']['min_content_size_kb']
    
    @property
    def dingtalk_webhook(self) -> Optional[str]:
        return self.config.get('dingtalk', {}).get('webhook')
    
    @property
    def dingtalk_keyword(self) -> str:
        return self.config.get('dingtalk', {}).get('keyword', 'Monitor')
    
    @property
    def auth_header(self) -> dict:
        auth_config = self.config['auth']
        return {
            "Authorization": auth_config['authorization'],
            "Content-Type": auth_config['content_type']
        }


class Logger:
    """日志管理类"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 主日志
        self.main_logger = self._create_main_logger()
        
        # 引擎日志缓存
        self.logger_cache: Dict[str, Dict[str, Any]] = {}
    
    def _create_main_logger(self) -> logging.Logger:
        """创建主日志记录器"""
        logger = logging.getLogger("main")
        logger.setLevel(logging.INFO)
        
        # 防止重复添加handler
        if not logger.handlers:
            fh = logging.FileHandler("monitor.log", encoding="utf-8")
            fh.setFormatter(
                logging.Formatter("%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            )
            logger.addHandler(fh)
        
        return logger
    
    def get_engine_logger(self, engine: str) -> logging.Logger:
        """获取引擎专用日志记录器"""
        date_str = datetime.now().strftime("%Y%m%d")
        log_path = self.log_dir / engine / f"{date_str}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger_name = f"{engine}_daily"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        
        # 检查是否需要更新handler（日期变更）
        cached = self.logger_cache.get(engine)
        if not cached or cached["date"] != date_str:
            # 清理旧handler
            for h in list(logger.handlers):
                if isinstance(h, FileHandler):
                    logger.removeHandler(h)
                    h.close()
            
            # 添加新handler
            fh = FileHandler(str(log_path), encoding="utf-8")
            fh.setFormatter(
                logging.Formatter("%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            )
            logger.addHandler(fh)
            
            # 更新缓存
            self.logger_cache[engine] = {"date": date_str, "handler": fh}
        
        return logger
    
    def info(self, message: str):
        """记录信息日志"""
        self.main_logger.info(message)
    
    def error(self, message: str):
        """记录错误日志"""
        self.main_logger.error(message)


class AlertManager:
    """告警管理类"""
    
    def __init__(self, webhook: Optional[str], keyword: str, logger: Logger):
        self.webhook = webhook
        self.keyword = keyword
        self.logger = logger
    
    async def send_alert(self, title: str, content: str, 
                        data_list: Optional[List[float]] = None, 
                        metric_label: str = "指标值",
                        engine: Optional[str] = None):
        """发送钉钉告警"""
        if not self.webhook:
            self.logger.info(f"未配置webhook，跳过告警: {title}")
            return
        
        data_section = ""
        if data_list:
            data_section = f"<br><br>近3分钟{metric_label}：<br>{', '.join(str(x) + '%' for x in data_list)}"
        
        engine_suffix = ""
        if engine:
            engine_suffix = f" | {engine.upper()}_{datetime.now().strftime('%H:%M:%S')}"
        
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": f"{self.keyword} | {title}{engine_suffix}",
                "text": f"### SERP_{self.keyword} | {title}<br><br>{content}{data_section}"
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook, json=payload) as resp:
                    self.logger.info(f"钉钉通知状态: {resp.status}")
        except Exception as e:
            self.logger.error(f"钉钉发送异常: {e}")


class SERPMonitor:
    """SERP监控主类"""
    
    def __init__(self, config: Config, logger: Logger, alert_manager: AlertManager):
        self.config = config
        self.logger = logger
        self.alert_manager = alert_manager
        self.api_url = "https://scraperapi.thordata.com/request"
    
    def build_payload(self, engine: str, term: str) -> dict:
        """构建API请求payload
        返回包含url（用于日志）和params（用于API请求）的字典
        """
        engine_config = self.config.search_engines[engine]
        domain = engine_config["domain"]
        param = engine_config["param"]
        api_engine = engine_config.get("engine", engine)
        
        # 构建URL（用于日志记录）
        url = f"https://{domain}/search?{param}={quote(term)}&json=1"
        
        # 构建API请求参数（URL编码格式）
        params = {
            "engine": api_engine,
            param: term,
            "json": "1"
        }
        
        return {
            "url": url,
            "params": params
        }
    
    async def fetch(self, session: aiohttp.ClientSession, engine: str, 
                   term: str, engine_logger: logging.Logger) -> dict:
        """执行单次API请求"""
        start = time.time()
        
        try:
            payload = self.build_payload(engine, term)
            
            # 使用URL编码格式发送请求
            async with session.post(
                url=self.api_url,
                headers=self.config.auth_header,
                data=urlencode(payload["params"]),
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            ) as r:
                content = await r.text()
                elapsed = time.time() - start
                content_size = len(content.encode("utf-8")) / 1024
                
                # 判断是否成功：状态200，非HTML内容，大小足够
                is_success = (
                    r.status == 200 and 
                    "html" not in r.headers.get("Content-Type", "").lower() and 
                    content_size >= self.config.min_content_size_kb
                )
                
                return {
                    "engine": engine,
                    "term": term,
                    "status": r.status,
                    "elapsed": elapsed,
                    "is_timeout": elapsed > self.config.timeout_limit,
                    "success": is_success,
                    "content_size": content_size,
                    "timestamp": time.time()
                }
        
        except Exception as e:
            elapsed = time.time() - start
            err_type = type(e).__name__
            error_text = str(e)
            request_url = self.build_payload(engine, term)["url"]
            
            # 记录错误信息
            error_msg = (
                f"[{engine}] 请求失败\n"
                f"关键词: {term}\n"
                f"请求URL: {request_url}\n"
                f"异常类型: {err_type}\n"
                f"错误信息: {error_text}\n"
                f"耗时: {elapsed:.2f}s"
            )
            engine_logger.error(error_msg)
            
            return {
                "engine": engine,
                "term": term,
                "status": 0,
                "elapsed": elapsed,
                "is_timeout": True,
                "success": False,
                "exception": f"{err_type}: {error_text}",
                "content_size": 0,
                "timestamp": time.time()
            }
    
    def analyze_results(self, results: List[dict]) -> Dict[str, dict]:
        """分析请求结果"""
        grouped = defaultdict(list)
        for r in results:
            grouped[r["engine"]].append(r)
        
        analysis = {}
        for engine, group in grouped.items():
            total = len(group)
            if total == 0:
                continue
            
            success = sum(1 for r in group if r["success"])
            timeout = sum(1 for r in group if r["is_timeout"])
            exceptions = sum(1 for r in group if r["status"] in (500, 502, 504))
            errors = sum(1 for r in group if r["status"] == 0)
            
            analysis[engine] = {
                "total": total,
                "success": success,
                "timeout": timeout,
                "exceptions": exceptions,
                "errors": errors,
                "success_rate": round(success / total * 100, 2),
                "timeout_rate": round(timeout / total * 100, 2),
                "exception_rate": round(exceptions / total * 100, 2),
                "error_rate": round(errors / total * 100, 2),
                "results": group
            }
        
        return analysis
    
    async def check_alerts(self, engine: str, stats: dict, status_window: dict):
        """检查并触发告警"""
        s = status_window[engine]
        
        # 成功率告警
        if len(s["success_rate"]) == 3 and all(
            x < self.config.threshold_success_rate for x in s["success_rate"]
        ):
            await self.alert_manager.send_alert(
                f"{engine.upper()} 成功率告警",
                f"连续3分钟成功率低于 {self.config.threshold_success_rate}%",
                list(s["success_rate"]),
                metric_label="成功率",
                engine=engine
            )
        
        # 超时率告警
        if len(s["timeout_rate"]) == 3 and all(
            x > self.config.threshold_timeout_rate for x in s["timeout_rate"]
        ):
            await self.alert_manager.send_alert(
                f"{engine.upper()} 超时率告警",
                f"连续3分钟超时率高于 {self.config.threshold_timeout_rate}%",
                list(s["timeout_rate"]),
                metric_label="超时率",
                engine=engine
            )
        
        # 连续3次5xx错误告警
        results = sorted(stats["results"], key=lambda x: x.get("timestamp", 0))
        codes = [r["status"] for r in results]
        found_3_in_row = any(
            codes[i] in (500, 502, 504) and
            codes[i + 1] in (500, 502, 504) and
            codes[i + 2] in (500, 502, 504)
            for i in range(len(codes) - 2)
        )
        
        if found_3_in_row:
            await self.alert_manager.send_alert(
                f"{engine.upper()} 连续3次异常请求告警",
                "本分钟内出现连续3次异常请求（5xx），触发预警",
                engine=engine
            )
    
    async def monitor(self):
        """主监控循环"""
        self.logger.info("=" * 60)
        self.logger.info("SERP监控启动")
        self.logger.info(f"监控引擎: {', '.join(self.config.search_engines.keys())}")
        self.logger.info(f"关键词数量: {len(self.config.search_terms)}")
        self.logger.info(f"并发数: {self.config.concurrency}")
        self.logger.info(f"每引擎每分钟请求数: {self.config.requests_per_engine}")
        self.logger.info("=" * 60)
        
        # 检查监控时长
        if self.config.monitor_duration_minutes <= 0:
            self.logger.info("监控时长为0，直接退出")
            return
        
        # 初始化状态窗口
        status_window = {
            engine: {
                "success_rate": deque(maxlen=3),
                "timeout_rate": deque(maxlen=3),
                "exception_rate": deque(maxlen=3),
                "error_rate": deque(maxlen=3),
                "logger": self.logger.get_engine_logger(engine)
            } for engine in self.config.search_engines
        }
        
        try:
            for minute in range(self.config.monitor_duration_minutes):
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.logger.info(f"\n===== 第 {minute + 1} 分钟监控 =====")
                
                # 为每个引擎日志添加分隔线
                for engine in self.config.search_engines:
                    engine_logger = status_window[engine]["logger"]
                    engine_logger.info("\n" + "=" * 50)
                    engine_logger.info(f"第 {minute + 1} 分钟请求开始时间：{now_str}")
                    engine_logger.info("=" * 50 + "\n")
                
                # 执行请求
                async with aiohttp.ClientSession() as session:
                    sem = asyncio.Semaphore(self.config.concurrency)
                    tasks = []
                    
                    for engine in self.config.search_engines:
                        for _ in range(self.config.requests_per_engine):
                            term = random.choice(self.config.search_terms)
                            
                            async def task(eng=engine, t=term):
                                async with sem:
                                    engine_logger = status_window[eng]["logger"]
                                    result = await self.fetch(session, eng, t, engine_logger)
                                    
                                    # 记录请求日志
                                    engine_logger.info(
                                        f"[{t}] 状态: {result['status']} "
                                        f"成功: {result['success']} "
                                        f"耗时: {result['elapsed']:.2f}s "
                                        f"大小: {result['content_size']:.2f}KB"
                                    )
                                    return result
                            
                            tasks.append(task())
                    
                    results = await asyncio.gather(*tasks)
                
                # 分析结果
                analysis = self.analyze_results(results)
                
                # 更新状态窗口并检查告警
                for engine, stats in analysis.items():
                    s = status_window[engine]
                    s["success_rate"].append(stats["success_rate"])
                    s["timeout_rate"].append(stats["timeout_rate"])
                    s["exception_rate"].append(stats["exception_rate"])
                    s["error_rate"].append(stats["error_rate"])
                    
                    # 记录汇总日志
                    engine_logger = s["logger"]
                    engine_logger.info(f"第 {minute + 1} 分钟汇总：")
                    engine_logger.info(
                        f"总请求数: {stats['total']} | "
                        f"成功数: {stats['success']} | "
                        f"超时数: {stats['timeout']} | "
                        f"异常数: {stats['exceptions']} | "
                        f"错误数: {stats['errors']}"
                    )
                    engine_logger.info(
                        f"成功率: {stats['success_rate']}% | "
                        f"超时率: {stats['timeout_rate']}% | "
                        f"异常率: {stats['exception_rate']}% | "
                        f"错误率: {stats['error_rate']}%"
                    )
                    engine_logger.info("-" * 50 + "\n")
                    
                    # 检查告警
                    await self.check_alerts(engine, stats, status_window)
                
                # 等待下一分钟
                await asyncio.sleep(60)
        
        except KeyboardInterrupt:
            self.logger.info("\n监控被用户中断")
        except Exception as e:
            self.logger.error(f"监控发生异常: {e}")
            raise
        finally:
            self.logger.info("监控结束")


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="SERP监控工具 - 监控搜索引擎API健康状态",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                           # 使用默认配置文件 config.json
  %(prog)s -c custom_config.json     # 使用自定义配置文件
  %(prog)s --engines google bing     # 只监控指定的引擎
  %(prog)s --duration 60             # 监控60分钟后自动停止
        """
    )
    
    parser.add_argument(
        '-c', '--config',
        default='config.json',
        help='配置文件路径 (默认: config.json)'
    )
    
    parser.add_argument(
        '--engines',
        nargs='+',
        help='指定要监控的引擎（不指定则监控所有配置的引擎）'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        help='监控持续时间（分钟），不指定则持续运行直到手动停止'
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 加载配置
        config = Config(args.config)
        
        # 如果指定了引擎，过滤配置
        if args.engines:
            available_engines = set(config.search_engines.keys())
            requested_engines = set(args.engines)
            
            invalid_engines = requested_engines - available_engines
            if invalid_engines:
                print(f"错误: 以下引擎未在配置中定义: {', '.join(invalid_engines)}")
                print(f"可用引擎: {', '.join(available_engines)}")
                sys.exit(1)
            
            # 过滤引擎
            config.config['search_engines'] = {
                k: v for k, v in config.search_engines.items() 
                if k in requested_engines
            }
        
        # 如果指定了持续时间，更新配置
        if args.duration:
            config.config['monitoring']['monitor_duration_minutes'] = args.duration
        
        # 初始化组件
        logger = Logger()
        alert_manager = AlertManager(
            config.dingtalk_webhook,
            config.dingtalk_keyword,
            logger
        )
        monitor = SERPMonitor(config, logger, alert_manager)
        
        # 启动监控
        asyncio.run(monitor.monitor())
        
    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"配置错误: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n监控已停止")
        sys.exit(0)
    except Exception as e:
        print(f"未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
