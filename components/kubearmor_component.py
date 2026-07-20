"""
KubeArmor 组件 - 容器权限策略可视化
"""

import json
from datetime import datetime
from typing import Dict, List, Any

from components.base import BaseComponent


class KubeArmorComponent(BaseComponent):
    def __init__(self):
        super().__init__(
            name="kubearmor",
            display_name="KubeArmor",
            description="容器权限策略与越权拦截",
            icon="☸️",
            category="container_security"
        )

    def check_health(self) -> Dict[str, Any]:
        rc, out, _ = self.run_cmd(["kubearmor", "--version"], timeout=5)
        if rc == 0:
            self.status = "healthy"
            self.version = out.strip()[:60]
        else:
            rc2, _, _ = self.run_cmd(["systemctl", "is-active", "kubearmor"], timeout=5)
            self.status = "healthy" if rc2 == 0 else "not_installed"
        self.last_check = datetime.now().isoformat()
        return {"status": self.status, "version": self.version}

    def get_alerts(self, limit: int = 50) -> List[Dict]:
        log_paths = [
            "/var/log/kubearmor/alerts.log",
            "/var/log/kubearmor.log",
            "/tmp/kubearmor.log"
        ]
        alerts = []
        for lp in log_paths:
            try:
                with open(lp, "r") as f:
                    for line in f.readlines()[-limit:]:
                        try:
                            alerts.append(json.loads(line.strip()))
                        except:
                            alerts.append({"raw": line.strip()})
                if alerts:
                    break
            except: pass
        return alerts

    def get_policies(self) -> List[Dict]:
        rc, out, _ = self.run_cmd(["karmor", "policy", "list", "-o", "json"], timeout=10)
        if rc == 0 and out.strip():
            try:
                return json.loads(out)
            except: pass
        return []

    def get_data(self, **kwargs) -> Dict[str, Any]:
        limit = kwargs.get("limit", 50)
        alerts = self.get_alerts(limit)
        policies = self.get_policies()
        # 统计拦截事件
        blocked = sum(1 for a in alerts if a.get("action") == "Block" or
                      a.get("raw", "").lower().find("block") >= 0)
        return {
            "alerts": alerts[-30:],
            "alert_count": len(alerts),
            "policies": policies,
            "blocked_count": blocked
        }

    def run_action(self, action: str, **kwargs) -> Dict[str, Any]:
        return self.get_data(**kwargs)