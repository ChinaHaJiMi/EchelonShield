"""
Suricata 组件 - 流量监控 / IDS/IPS
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

from components.base import BaseComponent


class SuricataComponent(BaseComponent):
    def __init__(self):
        super().__init__(
            name="suricata",
            display_name="Suricata",
            description="网络流量监控与入侵检测",
            icon="🌐",
            category="network"
        )
        self.alerts = []

    def check_health(self) -> Dict[str, Any]:
        rc, out, _ = self.run_cmd(["suricata", "--version"], timeout=5)
        if rc == 0:
            self.status = "healthy"
            self.version = out.strip()[:80]
        else:
            rc2, _, _ = self.run_cmd(["systemctl", "is-active", "suricata"], timeout=5)
            self.status = "healthy" if rc2 == 0 else "not_installed"
        self.last_check = datetime.now().isoformat()
        return {"status": self.status, "version": self.version}

    def read_eve_log(self, limit: int = 100) -> List[Dict]:
        """读取 Suricata 的 eve.json 日志"""
        paths = ["/var/log/suricata/eve.json", "/var/log/suricata/fast.log"]
        events = []
        for path in paths:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        for line in f:
                            try:
                                ev = json.loads(line.strip())
                                events.append(ev)
                            except:
                                pass
                            if len(events) >= limit:
                                break
                except: pass
        return events

    def get_attack_stats(self, events: List[Dict] = None) -> Dict:
        if events is None:
            events = self.read_eve_log(500)
        stats = {
            "total": len(events),
            "alert": 0,
            "flow": 0,
            "dns": 0,
            "tls": 0,
            "http": 0,
            "portscan": 0,
            "by_type": {}
        }
        for ev in events:
            ev_type = ev.get("event_type", "unknown")
            stats["by_type"][ev_type] = stats["by_type"].get(ev_type, 0) + 1
            stats[ev_type] = stats.get(ev_type, 0) + 1
            # 检查告警
            if ev_type == "alert":
                sig = ev.get("alert", {}).get("signature", "")
                cat = ev.get("alert", {}).get("category", "")
                if "portscan" in cat.lower(): stats["portscan"] += 1
        return stats

    def get_data(self, **kwargs) -> Dict[str, Any]:
        limit = kwargs.get("limit", 100)
        events = self.read_eve_log(limit)
        alerts = [e for e in events if e.get("event_type") == "alert"]
        return {
            "events": events[-50:],
            "alerts": alerts[-30:],
            "alert_count": len(alerts),
            "stats": self.get_attack_stats(events)
        }

    def run_action(self, action: str, **kwargs) -> Dict[str, Any]:
        return self.get_data(**kwargs)