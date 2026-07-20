"""
Trivy 组件 - 容器 / 依赖漏洞扫描
"""

import json
from datetime import datetime
from typing import Dict, List, Any

from components.base import BaseComponent


class TrivyComponent(BaseComponent):
    def __init__(self):
        super().__init__(
            name="trivy",
            display_name="Trivy",
            description="容器镜像与依赖漏洞扫描",
            icon="🐳",
            category="vulnerability"
        )
        self.scan_results = []

    def check_health(self) -> Dict[str, Any]:
        rc, out, _ = self.run_cmd(["trivy", "--version"], timeout=10)
        if rc == 0:
            self.status = "healthy"
            self.version = out.strip()[:60]
        else:
            self.status = "not_installed"
        self.last_check = datetime.now().isoformat()
        return {"status": self.status, "version": self.version}

    def scan_filesystem(self, path: str = ".") -> Dict:
        rc, out, err = self.run_cmd(
            ["trivy", "fs", "--format", "json", path], timeout=300
        )
        if rc == 0 and out.strip():
            try:
                data = json.loads(out)
            except:
                data = {"raw": out[:2000]}
        else:
            data = {"raw": out[:2000], "error": err[:500]}

        result = {
            "time": datetime.now().isoformat(),
            "target": path,
            "vulnerabilities": [],
            "summary": {"critical": 0, "high": 0, "medium": 0, "low": 0}
        }

        if isinstance(data, dict):
            results = data.get("Results", []) if "Results" in data else []
            for r in results:
                vulns = r.get("Vulnerabilities", [])
                for v in vulns:
                    severity = v.get("Severity", "UNKNOWN").lower()
                    result["summary"][severity] = result["summary"].get(severity, 0) + 1
                    result["vulnerabilities"].append({
                        "pkg": v.get("PkgName", ""),
                        "severity": v.get("Severity", ""),
                        "installed": v.get("InstalledVersion", ""),
                        "fixed": v.get("FixedVersion", ""),
                        "title": v.get("Title", "")[:100],
                        "cve": v.get("VulnerabilityID", "")
                    })
        self.scan_results.append(result)
        return result

    def scan_image(self, image: str) -> Dict:
        rc, out, err = self.run_cmd(
            ["trivy", "image", "--format", "json", image], timeout=300
        )
        return {"time": datetime.now().isoformat(), "image": image,
                "output": out[:2000], "error": err[:500]}

    def get_data(self, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "status")
        if action == "scan":
            path = kwargs.get("path", ".")
            return self.scan_filesystem(path)
        if action == "image":
            return self.scan_image(kwargs.get("image", ""))
        return self.to_dict()

    def run_action(self, action: str, **kwargs) -> Dict[str, Any]:
        return self.get_data(action=action, **kwargs)