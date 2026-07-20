"""
EchelonShield Core Engine
统一调度引擎：管理所有安全组件的生命周期、任务调度、状态检测
"""

import os
import sys
import json
import time
import signal
import logging
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable

# 确保项目根目录在路径中
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.base import BaseComponent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(str(ROOT_DIR / "data" / "echelon.log"), encoding="utf-8")
    ]
)

logger = logging.getLogger("EchelonEngine")


class EngineStatus:
    STOPPED = "stopped"
    RUNNING = "running"
    ERROR = "error"


class EchelonEngine:
    """核心引擎 - 安全组件的指挥中枢"""

    def __init__(self):
        self.status = EngineStatus.STOPPED
        self.components: Dict[str, BaseComponent] = {}
        self.scheduler_threads: Dict[str, threading.Thread] = {}
        self.scheduler_intervals: Dict[str, int] = {}
        self._stop_events: Dict[str, threading.Event] = {}
        self.health_history: List[Dict] = []
        self.log_buffer: List[Dict] = []  # 统一日志缓冲区
        self._lock = threading.Lock()
        self._signal_handlers = {}

    # ─── 组件注册 ────────────────────────────────────────

    def register(self, component: BaseComponent) -> "EchelonEngine":
        name = component.name
        with self._lock:
            self.components[name] = component
        logger.info(f"[注册] {name} ({component.display_name}) 已挂载")
        return self

    def get_component(self, name: str) -> Optional[BaseComponent]:
        return self.components.get(name)

    def list_components(self) -> List[str]:
        return list(self.components.keys())

    # ─── 状态检测 ────────────────────────────────────────

    def check_all(self) -> Dict[str, Dict]:
        results = {}
        for name, comp in self.components.items():
            try:
                results[name] = comp.check_health()
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
        with self._lock:
            self.health_history.append({
                "time": datetime.now().isoformat(),
                "results": results
            })
        return results

    def component_status(self, name: str) -> Dict:
        comp = self.components.get(name)
        if not comp:
            return {"status": "unknown", "error": f"组件 {name} 未注册"}
        return comp.check_health()

    # ─── 启动 / 停止 ──────────────────────────────────────

    def start(self):
        logger.info("=" * 50)
        logger.info("EchelonShield 引擎启动")
        logger.info("=" * 50)
        self.status = EngineStatus.RUNNING
        # 对所有组件执行一次初始健康检查
        self.check_all()
        return self

    def stop(self):
        logger.info("EchelonShield 引擎停止中...")
        for name, event in self._stop_events.items():
            event.set()
        self.status = EngineStatus.STOPPED
        logger.info("EchelonShield 引擎已停止")

    # ─── 定时调度 ────────────────────────────────────────

    def schedule(self, name: str, interval_sec: int, target: Callable):
        """注册一个定时任务"""
        if name in self.scheduler_threads:
            logger.warning(f"[调度] {name} 已存在定时任务，跳过")
            return
        event = threading.Event()
        self._stop_events[name] = event
        self.scheduler_intervals[name] = interval_sec

        def runner():
            logger.info(f"[调度] {name} 启动，间隔 {interval_sec}s")
            while not event.is_set():
                try:
                    target()
                except Exception as e:
                    logger.error(f"[调度] {name} 执行失败: {e}")
                event.wait(interval_sec)
            logger.info(f"[调度] {name} 已停止")

        t = threading.Thread(target=runner, daemon=True, name=f"sched-{name}")
        self.scheduler_threads[name] = t
        t.start()
        return self

    def stop_schedule(self, name: str):
        event = self._stop_events.get(name)
        if event:
            event.set()
            logger.info(f"[调度] {name} 停止信号已发送")

    # ─── 日志系统 ────────────────────────────────────────

    def push_log(self, source: str, level: str, message: str, data: Dict = None):
        entry = {
            "time": datetime.now().isoformat(),
            "source": source,
            "level": level.upper(),
            "message": message,
            "data": data or {}
        }
        with self._lock:
            self.log_buffer.append(entry)
            if len(self.log_buffer) > 10000:
                self.log_buffer = self.log_buffer[-5000:]
        # 同时写入文件
        log_line = f"[{entry['time']}] [{entry['level']}] [{entry['source']}] {entry['message']}"
        logger.log(
            getattr(logging, level.upper(), logging.INFO),
            log_line
        )
        return entry

    def get_logs(self, source: str = None, level: str = None, limit: int = 200) -> List[Dict]:
        logs = self.log_buffer
        if source:
            logs = [l for l in logs if l["source"] == source]
        if level:
            logs = [l for l in logs if l["level"] == level.upper()]
        return logs[-limit:]

    # ─── 健康报告 ────────────────────────────────────────

    def health_report(self) -> Dict:
        latest = self.health_history[-1] if self.health_history else {"results": {}}
        report = {
            "engine_status": self.status,
            "components_total": len(self.components),
            "components_healthy": sum(
                1 for r in latest["results"].values()
                if r.get("status") == "healthy"
            ),
            "components_error": sum(
                1 for r in latest["results"].values()
                if r.get("status") == "error" or r.get("status") == "unhealthy"
            ),
            "last_check": latest.get("time", "never"),
            "details": latest["results"]
        }
        return report


# 全局单例
engine = EchelonEngine()