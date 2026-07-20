"""
Tetragon 组件 - 系统调用拦截 / 提权 / Shell / 进程派生监控
"""

import json
from datetime import datetime
from typing import Dict, List, Any

from components.base import BaseComponent


class TetragonComponent(BaseComponent):
    def __init__(self):
        super().__init__(
            name="tetragon",
            display_name="Tetragon",
            description="eBPF 系统调用拦截与风险分析",
            icon="🔍",
            category="runtime_security"
        )
        self.events = []

    def check_health(self) -> Dict[str, Any]:
        rc, out, _ = self.run_cmd(["tetragon", "--version"], timeout=5)
        if rc == 0:
            self.status = "healthy"
            self.version = out.strip()[:80]
        else:
            rc2, out2, _ = self.run_cmd(["systemctl", "is-active", "tetragon"], timeout=5)
            if rc2 == 0:
                self.status = "healthy"
                self.version = "systemd service"
            else:
                self.status = "not_installed"
        self.last_check = datetime.now().isoformat()
        return {"status": self.status, "version": self.version}

    def get_events(self, limit: int = 50) -> List[Dict]:
        try:
            with open("/var/log/tetragon/tetragon.log", "r") as f:
                lines = f.readlines()[-limit:]
                self.events = [json.loads(l.strip()) for l in lines if l.strip()]
        except:
            self.events = []
        return self.events

    def get_data(self, **kwargs) -> Dict[str, Any]:
        limit = kwargs.get("limit", 50)
        events = self.get_events(limit)
        risk_types = {"privilege_escalation": 0, "shell_spawn": 0,
                      "process_fork": 0, "file_access": 0, "network": 0}
        for ev in events:
            ev_type = ev.get("type", "").lower()
            if "exec" in ev_type or "fork" in ev_type: risk_types["process_fork"] += 1
            if "capability" in ev_type or "privilege" in ev_type: risk_types["privilege_escalation"] += 1
            if "shell" in ev_type or "bash" in ev_type: risk_types["shell_spawn"] += 1
        return {
            "events": events,
            "event_count": len(events),
            "risk_types": risk_types
        }

    def run_action(self, action: str, **kwargs) -> Dict[str, Any]:
        return self.get_data(**kwargs)