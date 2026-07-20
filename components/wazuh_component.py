"""
Wazuh 组件 - EDR/HIDS/FIM 集成
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any

from components.base import BaseComponent


class WazuhComponent(BaseComponent):
    def __init__(self):
        super().__init__(
            name="wazuh",
            display_name="Wazuh",
            description="EDR/HIDS/文件完整性监控",
            icon="🛡️",
            category="edr"
        )
        self.alerts = []

    def check_health(self) -> Dict[str, Any]:
        # 检查 wazuh-agent / wazuh-manager
        rc1, out1, _ = self.run_cmd(["systemctl", "is-active", "wazuh-agent"], timeout=5)
        rc2, out2, _ = self.run_cmd(["systemctl", "is-active", "wazuh-manager"], timeout=5)
        rc3, out3, _ = self.run_cmd(["/var/ossec/bin/wazuh-agent", "--version"], timeout=5)
        rc4, out4, _ = self.run_cmd(["/var/ossec/bin/wazuh-control", "status"], timeout=10)

        if rc1 == 0 or rc2 == 0:
            self.status = "healthy"
            self.version = out3.strip()[:50] if out3 else "wazuh systemd"
        elif rc4 == 0:
            self.status = "healthy"
            self.version = "wazuh-control active"
        else:
            self.status = "not_installed"

        self.last_check = datetime.now().isoformat()
        return {"status": self.status, "version": self.version}

    def get_alerts(self, limit: int = 50) -> List[Dict]:
        try:
            with open("/var/ossec/logs/alerts/alerts.json", "r") as f:
                lines = f.readlines()[-limit:]
                self.alerts = [json.loads(l.strip()) for l in lines if l.strip()]
        except:
            try:
                with open("/var/ossec/logs/alerts/alerts.log", "r") as f:
                    lines = f.readlines()[-limit:]
                    self.alerts = [{"raw": l.strip()} for l in lines if l.strip()]
            except:
                self.alerts = []
        return self.alerts

    def get_data(self, **kwargs) -> Dict[str, Any]:
        limit = kwargs.get("limit", 50)
        alerts = self.get_alerts(limit)
        level_counts = {}
        for a in alerts:
            lvl = a.get("rule", {}).get("level", 0)
            level_counts[str(lvl)] = level_counts.get(str(lvl), 0) + 1
        return {
            "alerts": alerts,
            "alert_count": len(alerts),
            "level_distribution": level_counts
        }

    def run_action(self, action: str, **kwargs) -> Dict[str, Any]:
        return self.get_data(**kwargs)