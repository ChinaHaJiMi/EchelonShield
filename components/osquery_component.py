"""
Osquery 组件 - 系统资产清单 / 账号 / 权限 / 基线查询
"""

import json
from datetime import datetime
from typing import Dict, List, Any

from components.base import BaseComponent


class OsqueryComponent(BaseComponent):
    def __init__(self):
        super().__init__(
            name="osquery",
            display_name="Osquery",
            description="系统资产清单与基线查询",
            icon="📊",
            category="forensics"
        )
        self.results_cache = {}

    def check_health(self) -> Dict[str, Any]:
        rc, out, _ = self.run_cmd(["osqueryi", "--version"], timeout=5)
        if rc == 0:
            self.status = "healthy"
            self.version = out.strip()[:60]
        else:
            self.status = "not_installed"
        self.last_check = datetime.now().isoformat()
        return {"status": self.status, "version": self.version}

    def query(self, sql: str) -> List[Dict]:
        rc, out, err = self.run_cmd(["osqueryi", "--json", sql], timeout=15)
        if rc == 0 and out.strip():
            try:
                return json.loads(out)
            except:
                return [{"raw": out}]
        return []

    def get_users(self) -> List[Dict]:
        return self.query("SELECT * FROM users;")

    def get_processes(self) -> List[Dict]:
        return self.query("SELECT * FROM processes;")

    def get_network(self) -> List[Dict]:
        return self.query("SELECT * FROM listening_ports;")

    def get_crontab(self) -> List[Dict]:
        return self.query("SELECT * FROM crontab;")

    def get_system_info(self) -> Dict:
        data = self.query("SELECT * FROM system_info;")
        return data[0] if data else {}

    def get_data(self, **kwargs) -> Dict[str, Any]:
        category = kwargs.get("category", "system")
        queries = {
            "system": "SELECT hostname, cpu_type, physical_memory, hardware_model FROM system_info;",
            "users": "SELECT uid, username, shell, directory FROM users;",
            "processes": "SELECT pid, name, path, state, cmdline FROM processes LIMIT 100;",
            "network": "SELECT pid, port, address, protocol FROM listening_ports;",
            "packages": "SELECT name, version, source FROM packages LIMIT 100;",
            "crontab": "SELECT * FROM crontab;",
            "startup": "SELECT * FROM startup_items;",
        }
        sql = queries.get(category, queries["system"])
        results = self.query(sql)
        return {
            "category": category,
            "results": results,
            "count": len(results)
        }

    def run_action(self, action: str, **kwargs) -> Dict[str, Any]:
        action_map = {
            "users": self.get_users,
            "processes": self.get_processes,
            "network": self.get_network,
            "crontab": self.get_crontab,
            "system_info": self.get_system_info,
        }
        if action in action_map:
            return {"results": action_map[action]()}
        return self.get_data(**kwargs)