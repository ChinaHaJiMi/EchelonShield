"""
ClamAV 组件 - 病毒查杀、定时扫描、实时监控
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any

from components.base import BaseComponent


class ClamAVComponent(BaseComponent):
    def __init__(self):
        super().__init__(
            name="clamav",
            display_name="ClamAV",
            description="开源病毒查杀引擎",
            icon="🦠",
            category="antivirus"
        )
        self.scan_results = []
        self.quarantine_list = []
        self.watch_dirs = []

    def check_health(self) -> Dict[str, Any]:
        rc0, out0, _ = self.run_cmd(["clamscan", "--version"], timeout=10)
        rc1, out1, _ = self.run_cmd(["freshclam", "--version"], timeout=10)

        if rc0 == 0 and rc1 == 0:
            ver = out0.strip().split("\n")[0] if out0 else "unknown"
            self.version = ver
            self.status = "healthy"
        elif rc0 == 0:
            self.status = "degraded"
            self.version = out0.strip()[:50]
        else:
            self.status = "not_installed"
            self.last_error = "clamscan 未安装"

        self.last_check = datetime.now().isoformat()
        return {
            "status": self.status,
            "version": self.version,
            "freshclam": rc1 == 0,
            "last_check": self.last_check
        }

    def scan_file(self, path: str) -> Dict:
        rc, out, err = self.run_cmd(["clamscan", "--stdout", path], timeout=120)
        result = {
            "path": path,
            "time": datetime.now().isoformat(),
            "infected": "FOUND" in out or "Infected" in out,
            "summary": out.strip().split("\n")[-1] if out else err,
            "details": out[:2000]
        }
        self.scan_results.append(result)
        return result

    def scan_directory(self, path: str, recursive: bool = True) -> Dict:
        cmd = ["clamscan", "--stdout", "-r" if recursive else "", path]
        cmd = [c for c in cmd if c]
        rc, out, err = self.run_cmd(cmd, timeout=300)
        infected_count = 0
        files_scanned = 0
        for line in out.split("\n"):
            if "Infected files:" in line:
                try:
                    infected_count = int(line.split(":")[1].strip())
                except: pass
            if "Scanned files:" in line:
                try:
                    files_scanned = int(line.split(":")[1].strip())
                except: pass

        result = {
            "path": path,
            "time": datetime.now().isoformat(),
            "files_scanned": files_scanned,
            "infected": infected_count,
            "summary": out.strip().split("\n")[-2:] if out else [],
            "raw": out[-3000:]
        }
        self.scan_results.append(result)
        return result

    def update_virus_db(self) -> Dict:
        rc, out, err = self.run_cmd(["freshclam"], timeout=120)
        success = rc == 0
        return {
            "success": success,
            "output": out.strip()[:1000],
            "time": datetime.now().isoformat()
        }

    def get_quarantine(self) -> List[Dict]:
        # ClamAV 默认隔离在 /var/log/clamav/ 或用户指定
        return self.quarantine_list

    def get_data(self, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "status")
        if action == "scan_results":
            return {"results": self.scan_results[-20:]}
        if action == "quarantine":
            return {"quarantine": self.quarantine_list}
        if action == "scan":
            path = kwargs.get("path", "/tmp")
            return self.scan_directory(path)
        if action == "update":
            return self.update_virus_db()
        return self.to_dict()

    def run_action(self, action: str, **kwargs) -> Dict[str, Any]:
        return self.get_data(action=action, **kwargs)