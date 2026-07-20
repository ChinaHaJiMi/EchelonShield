"""
Safety 组件 - Python/JS 依赖投毒检测
"""

import json
from datetime import datetime
from typing import Dict, List, Any

from components.base import BaseComponent


class SafetyComponent(BaseComponent):
    def __init__(self):
        super().__init__(
            name="safety",
            display_name="Safety",
            description="依赖投毒检测（Python/JS）",
            icon="🧪",
            category="vulnerability"
        )

    def check_health(self) -> Dict[str, Any]:
        rc, out, _ = self.run_cmd(["safety", "--version"], timeout=10)
        if rc == 0:
            self.status = "healthy"
            self.version = out.strip()[:60]
        else:
            self.status = "not_installed"
        self.last_check = datetime.now().isoformat()
        return {"status": self.status, "version": self.version}

    def check_requirements(self, req_file: str = "requirements.txt") -> Dict:
        rc, out, err = self.run_cmd(
            ["safety", "check", "-r", req_file, "--json"], timeout=120
        )
        if rc == 0 and out.strip():
            try:
                vulns = json.loads(out)
            except:
                vulns = [{"raw": out[:1000]}]
        else:
            vulns = [{"raw": out[:1000], "error": err[:500]}] if out else []

        summary = {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": len(vulns)}
        for v in vulns:
            if isinstance(v, dict):
                cvss = v.get("CVSS", 0) or v.get("cvss", 0)
            else:
                cvss = 0
            if cvss >= 9: summary["critical"] += 1
            elif cvss >= 7: summary["high"] += 1
            elif cvss >= 4: summary["medium"] += 1
            else: summary["low"] += 1

        return {
            "time": datetime.now().isoformat(),
            "file": req_file,
            "vulnerabilities": vulns[:100],
            "vuln_count": len(vulns),
            "summary": summary
        }

    def check_stdin(self, packages: str) -> Dict:
        """检查包列表（逗号分隔 pkg==version）"""
        rc, out, err = self.run_cmd(
            ["safety", "check", "--json", "--stdin"],
            input_data=packages,
            timeout=60
        )
        if rc == 0 and out.strip():
            try:
                vulns = json.loads(out)
            except:
                vulns = [{"raw": out[:500]}]
        else:
            vulns = []
        return {
            "time": datetime.now().isoformat(),
            "vulnerabilities": vulns[:50],
            "vuln_count": len(vulns)
        }

    def get_data(self, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "status")
        if action == "check":
            return self.check_requirements(kwargs.get("file", "requirements.txt"))
        return self.to_dict()

    def run_action(self, action: str, **kwargs) -> Dict[str, Any]:
        return self.get_data(action=action, **kwargs)