"""
UFW 组件 - 防火墙管理
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any

from components.base import BaseComponent


class UFWComponent(BaseComponent):
    def __init__(self):
        super().__init__(
            name="ufw",
            display_name="UFW",
            description="图形化防火墙策略管理",
            icon="🧱",
            category="firewall"
        )

    def check_health(self) -> Dict[str, Any]:
        rc, out, _ = self.run_cmd(["ufw", "--version"], timeout=5)
        rc2, out2, _ = self.run_cmd(["ufw", "status"], timeout=5)
        if rc == 0:
            self.status = "healthy"
            self.version = out.strip()[:60]
            if "inactive" in out2.lower():
                self.status = "degraded"
        else:
            self.status = "not_installed"
        self.last_check = datetime.now().isoformat()
        return {"status": self.status, "version": self.version}

    def get_status(self) -> Dict:
        rc, out, _ = self.run_cmd(["ufw", "status", "verbose"], timeout=5)
        status = {"active": False, "default_incoming": "", "default_outgoing": "", "rules": []}
        for line in out.split("\n"):
            if "Status:" in line:
                status["active"] = "active" in line.lower()
            if "Default:" in line and "incoming" in line.lower():
                status["default_incoming"] = line.split(":")[-1].strip()
            if "Default:" in line and "outgoing" in line.lower():
                status["default_outgoing"] = line.split(":")[-1].strip()
        # 解析规则
        rc2, out2, _ = self.run_cmd(["ufw", "show", "added"], timeout=5)
        for line in out2.split("\n"):
            if line.strip() and "ufw" in line:
                status["rules"].append(line.strip())
        return status

    def enable(self) -> Dict:
        rc, out, err = self.run_cmd(["ufw", "--force", "enable"], sudo=True, timeout=15)
        return {"success": rc == 0, "output": out.strip(), "error": err}

    def disable(self) -> Dict:
        rc, out, err = self.run_cmd(["ufw", "disable"], sudo=True, timeout=10)
        return {"success": rc == 0, "output": out.strip(), "error": err}

    def add_rule(self, rule: str) -> Dict:
        rc, out, err = self.run_cmd(["ufw"] + rule.split(), sudo=True, timeout=10)
        return {"success": rc == 0, "rule": rule, "output": out.strip(), "error": err}

    def delete_rule(self, rule: str) -> Dict:
        rc, out, err = self.run_cmd(["ufw", "delete"] + rule.split(), sudo=True, timeout=10)
        return {"success": rc == 0, "rule": rule, "output": out.strip(), "error": err}

    def get_data(self, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "status")
        if action == "status":
            return self.get_status()
        if action == "enable":
            return self.enable()
        if action == "disable":
            return self.disable()
        if action == "add":
            return self.add_rule(kwargs.get("rule", ""))
        if action == "delete":
            return self.delete_rule(kwargs.get("rule", ""))
        return {**self.to_dict(), **self.get_status()}

    def run_action(self, action: str, **kwargs) -> Dict[str, Any]:
        return self.get_data(action=action, **kwargs)