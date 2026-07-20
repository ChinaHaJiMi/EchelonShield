"""
Falco 组件 - eBPF 运行时安全监控
"""

import json
from datetime import datetime
from typing import Dict, List, Any

from components.base import BaseComponent


class FalcoComponent(BaseComponent):
    def __init__(self):
        super().__init__(
            name="falco",
            display_name="Falco",
            description="eBPF 运行时安全监控",
            icon="🦅",
            category="runtime_security"
        )
        self.events = []

    def check_health(self) -> Dict[str, Any]:
        rc, out, _ = self.run_cmd(["falco", "--version"], timeout=10)
        if rc == 0:
            self.status = "healthy"
            self.version = out.strip()[:100]
        else:
            rc2, out2, _ = self.run_cmd(["systemctl", "is-active", "falco"], timeout=5)
            if rc2 == 0:
                self.status = "healthy"
                self.version = "systemd service"
            else:
                self.status = "not_installed"
        self.last_check = datetime.now().isoformat()
        return {"status": self.status, "version": self.version}

    def get_events(self, limit: int = 50) -> List[Dict]:
        """读取 Falco 日志事件"""
        log_paths = [
            "/var/log/falco/events.json",
            "/var/log/falco_events.json",
            "/var/log/syslog"
        ]
        events = []
        for lp in log_paths:
            try:
                with open(lp, "r") as f:
                    for line in f:
                        try:
                            ev = json.loads(line.strip())
                            events.append(ev)
                        except:
                            pass
            except:
                continue
        self.events = events[-limit:]
        return self.events

    def get_data(self, **kwargs) -> Dict[str, Any]:
        limit = kwargs.get("limit", 50)
        events = self.get_events(limit)
        return {
            "events": events,
            "event_count": len(events),
            "priority_counts": self._count_priorities(events)
        }

    def _count_priorities(self, events: List[Dict]) -> Dict:
        counts = {"emergency": 0, "alert": 0, "critical": 0, "error": 0,
                  "warning": 0, "notice": 0, "informational": 0, "debug": 0}
        for ev in events:
            prio = ev.get("priority", "informational").lower()
            if prio in counts:
                counts[prio] += 1
        return counts

    def run_action(self, action: str, **kwargs) -> Dict[str, Any]:
        return self.get_data(**kwargs)