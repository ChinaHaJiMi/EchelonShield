"""
CrowdSec 组件 - 社区威胁情报
"""

import json
from datetime import datetime
from typing import Dict, List, Any

from components.base import BaseComponent


class CrowdSecComponent(BaseComponent):
    def __init__(self):
        super().__init__(
            name="crowdsec",
            display_name="CrowdSec",
            description="社区协同威胁情报与拦截",
            icon="👥",
            category="network"
        )

    def check_health(self) -> Dict[str, Any]:
        rc, out, _ = self.run_cmd(["cscli", "version"], timeout=5)
        if rc == 0:
            self.status = "healthy"
            self.version = out.strip()[:60]
        else:
            rc2, _, _ = self.run_cmd(["systemctl", "is-active", "crowdsec"], timeout=5)
            self.status = "healthy" if rc2 == 0 else "not_installed"
        self.last_check = datetime.now().isoformat()
        return {"status": self.status, "version": self.version}

    def get_decisions(self, limit: int = 50) -> List[Dict]:
        rc, out, _ = self.run_cmd(["cscli", "decisions", "list", "-o", "json"], timeout=10)
        if rc == 0 and out.strip():
            try:
                return json.loads(out)[:limit]
            except:
                pass
        # fallback: 文本解析
        rc2, out2, _ = self.run_cmd(["cscli", "decisions", "list"], timeout=10)
        decisions = []
        for line in out2.split("\n")[1:]:
            parts = line.split()
            if len(parts) >= 4:
                decisions.append({
                    "ip": parts[0],
                    "duration": parts[1],
                    "reason": parts[2],
                    "scope": parts[3] if len(parts) > 3 else ""
                })
        return decisions[:limit]

    def get_alerts(self, limit: int = 50) -> List[Dict]:
        rc, out, _ = self.run_cmd(["cscli", "alerts", "list", "-o", "json"], timeout=10)
        if rc == 0 and out.strip():
            try:
                return json.loads(out)[:limit]
            except:
                pass
        return []

    def get_metrics(self) -> Dict:
        rc, out, _ = self.run_cmd(["cscli", "metrics", "-o", "json"], timeout=10)
        if rc == 0 and out.strip():
            try:
                return json.loads(out)
            except:
                pass
        return {}

    def get_data(self, **kwargs) -> Dict[str, Any]:
        limit = kwargs.get("limit", 50)
        decisions = self.get_decisions(limit)
        alerts = self.get_alerts(limit)
        blocked = sum(1 for d in decisions if "ban" in str(d).lower())
        return {
            "decisions": decisions,
            "decision_count": len(decisions),
            "alerts": alerts,
            "alert_count": len(alerts),
            "blocked_ip_count": blocked
        }

    def run_action(self, action: str, **kwargs) -> Dict[str, Any]:
        return self.get_data(**kwargs)