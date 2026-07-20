"""
Rkhunter 组件 - Rootkit 检测
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any

from components.base import BaseComponent


class RkhunterComponent(BaseComponent):
    def __init__(self):
        super().__init__(
            name="rkhunter",
            display_name="Rkhunter",
            description="Rootkit 后门检测工具",
            icon="🐛",
            category="malware"
        )
        self.reports = []

    def check_health(self) -> Dict[str, Any]:
        rc, out, _ = self.run_cmd(["rkhunter", "--version"], timeout=10)
        if rc == 0:
            self.status = "healthy"
            for line in out.split("\n"):
                if "Version" in line:
                    self.version = line.strip()[:80]
                    break
        else:
            self.status = "not_installed"
        self.last_check = datetime.now().isoformat()
        return {"status": self.status, "version": self.version}

    def run_scan(self) -> Dict:
        rc, out, err = self.run_cmd(["rkhunter", "--check", "--skip-keypress",
                                      "--report-warnings-only"], timeout=300)
        report = {
            "time": datetime.now().isoformat(),
            "warnings": [],
            "suspicious": [],
            "ok": 0,
            "raw": out[-5000:] if out else err
        }
        for line in out.split("\n"):
            if "Warning" in line or "warning" in line:
                report["warnings"].append(line.strip())
            if "Suspicious" in line or "suspicious" in line:
                report["suspicious"].append(line.strip())
            if "OK" in line:
                report["ok"] += 1
        self.reports.append(report)
        return report

    def get_latest_report(self) -> Dict:
        log_path = "/var/log/rkhunter.log"
        try:
            with open(log_path, "r") as f:
                content = f.read()
            warnings = [l.strip() for l in content.split("\n") if "Warning" in l]
            return {
                "time": datetime.now().isoformat(),
                "warnings": warnings[-30:],
                "total_warnings": len(warnings)
            }
        except:
            return {"error": "日志文件不可读"}

    def get_data(self, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "status")
        if action == "scan":
            return self.run_scan()
        if action == "report":
            return self.get_latest_report()
        return self.to_dict()

    def run_action(self, action: str, **kwargs) -> Dict[str, Any]:
        return self.get_data(action=action, **kwargs)