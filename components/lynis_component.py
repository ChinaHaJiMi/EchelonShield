"""
Lynis 组件 - 合规扫描 / CVE / 系统加固
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

from components.base import BaseComponent


class LynisComponent(BaseComponent):
    def __init__(self):
        super().__init__(
            name="lynis",
            display_name="Lynis",
            description="合规审计与系统加固扫描",
            icon="📋",
            category="compliance"
        )
        self.reports = []

    def check_health(self) -> Dict[str, Any]:
        rc, out, _ = self.run_cmd(["lynis", "--version"], timeout=10)
        if rc == 0:
            self.status = "healthy"
            for line in out.split("\n"):
                if "version" in line.lower():
                    self.version = line.strip()[:60]
                    break
        else:
            self.status = "not_installed"
        self.last_check = datetime.now().isoformat()
        return {"status": self.status, "version": self.version}

    def run_audit(self) -> Dict:
        rc, out, err = self.run_cmd(["lynis", "audit", "system", "--quick"],
                                     timeout=300)
        result = {
            "time": datetime.now().isoformat(),
            "warnings": [],
            "suggestions": [],
            "hardening_score": 0,
            "raw": out[-5000:] if out else err
        }
        for line in out.split("\n"):
            if "Warning" in line or "warn" in line.lower():
                result["warnings"].append(line.strip())
            if "suggestion" in line.lower() or "Suggestion" in line:
                result["suggestions"].append(line.strip())
            if "hardening" in line.lower() and "score" in line.lower():
                try:
                    score = int(line.split(":")[-1].strip())
                    result["hardening_score"] = score
                except: pass
        self.reports.append(result)
        return result

    def get_latest_report(self) -> Dict:
        log_dir = "/var/log/lynis"
        if not os.path.exists(log_dir):
            log_dir = "/var/log/lynis.log"
        try:
            with open("/var/log/lynis.log", "r") as f:
                content = f.read()
            warnings = [l.strip() for l in content.split("\n") if "Warning" in l]
            suggestions = [l.strip() for l in content.split("\n") if "suggestion" in l.lower()]
            return {
                "time": datetime.now().isoformat(),
                "warnings": warnings[-20:],
                "suggestions": suggestions[-20:],
                "warning_count": len(warnings),
                "suggestion_count": len(suggestions)
            }
        except:
            return {"error": "未找到日志"}

    def get_data(self, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "status")
        if action == "audit":
            return self.run_audit()
        if action == "report":
            return self.get_latest_report()
        return self.to_dict()

    def run_action(self, action: str, **kwargs) -> Dict[str, Any]:
        return self.get_data(action=action, **kwargs)