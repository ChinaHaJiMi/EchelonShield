"""
Loki 组件 - 统一日志检索 / 时间线溯源 / 攻击链路还原
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

from components.base import BaseComponent


class LokiComponent(BaseComponent):
    def __init__(self):
        super().__init__(
            name="loki",
            display_name="Loki",
            description="统一日志检索与时间线溯源",
            icon="📜",
            category="log_management"
        )

    def check_health(self) -> Dict[str, Any]:
        rc, out, _ = self.run_cmd(["loki", "--version"], timeout=5)
        if rc == 0:
            self.status = "healthy"
            self.version = out.strip()[:60]
        else:
            rc2, _, _ = self.run_cmd(["systemctl", "is-active", "loki"], timeout=5)
            if rc2 == 0:
                self.status = "healthy"
                self.version = "systemd"
            else:
                # 检查 promtail/logcli
                rc3, _, _ = self.run_cmd(["logcli", "--version"], timeout=5)
                self.status = "healthy" if rc3 == 0 else "not_installed"
        self.last_check = datetime.now().isoformat()
        return {"status": self.status, "version": self.version}

    def query(self, query_str: str, limit: int = 50,
              start: str = None, end: str = None) -> Dict:
        """使用 logcli 查询 Loki"""
        cmd = ["logcli", "query", f'--limit={limit}', '--output=json', query_str]
        if start:
            cmd.append(f'--from={start}')
        if end:
            cmd.append(f'--to={end}')
        rc, out, err = self.run_cmd(cmd, timeout=30)
        if rc == 0 and out.strip():
            try:
                data = json.loads(out)
            except:
                data = {"raw": out[:2000]}
        else:
            data = {"raw": out[:1000], "error": err[:500]}
        return {"query": query_str, "results": data, "time": datetime.now().isoformat()}

    def search_logs(self, keyword: str, source: str = None, limit: int = 100) -> Dict:
        """搜索关键词日志"""
        query = f'{{job=~".+"}} |= "{keyword}"'
        if source:
            query = f'{{job="{source}"}} |= "{keyword}"'
        return self.query(query, limit=limit)

    def timeline(self, hours: int = 24) -> Dict:
        """获取时间线事件"""
        start = (datetime.now() - timedelta(hours=hours)).isoformat()
        end = datetime.now().isoformat()

        # 聚合各日志源的事件
        all_events = []
        log_sources = [
            "/var/log/syslog", "/var/log/auth.log",
            "/var/log/kern.log", "/var/log/dpkg.log"
        ]
        for src in log_sources:
            if os.path.exists(src):
                try:
                    with open(src, "r") as f:
                        lines = f.readlines()[-200:]
                    for line in lines:
                        all_events.append({
                            "source": os.path.basename(src),
                            "timestamp": line[:19] if len(line) > 19 else "",
                            "message": line.strip()
                        })
                except: pass

        # 尝试 Loki 查询
        loki_result = self.query('{job="systemd"}', limit=50, start=start, end=end)

        return {
            "time_range": f"{hours}h",
            "local_events": all_events[-100:],
            "loki_result": loki_result,
            "total_events": len(all_events)
        }

    def get_data(self, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "status")
        if action == "query":
            return self.query(
                kwargs.get("query", '{job=~".+"}'),
                kwargs.get("limit", 50),
                kwargs.get("start"),
                kwargs.get("end")
            )
        if action == "search":
            return self.search_logs(
                kwargs.get("keyword", ""),
                kwargs.get("source"),
                kwargs.get("limit", 100)
            )
        if action == "timeline":
            return self.timeline(kwargs.get("hours", 24))
        return self.to_dict()

    def run_action(self, action: str, **kwargs) -> Dict[str, Any]:
        return self.get_data(action=action, **kwargs)