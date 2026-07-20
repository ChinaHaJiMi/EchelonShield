"""
Fail2ban 组件 - 爆破封禁 / 规则管理
"""

import json
from datetime import datetime
from typing import Dict, List, Any

from components.base import BaseComponent


class Fail2banComponent(BaseComponent):
    def __init__(self):
        super().__init__(
            name="fail2ban",
            display_name="Fail2ban",
            description="爆破攻击封禁与规则管理",
            icon="🚫",
            category="network"
        )
        self.jail_status_cache = {}

    def check_health(self) -> Dict[str, Any]:
        rc, out, _ = self.run_cmd(["fail2ban-client", "--version"], timeout=5)
        rc2, _, _ = self.run_cmd(["systemctl", "is-active", "fail2ban"], timeout=5)
        if rc == 0:
            self.status = "healthy"
            self.version = out.strip()[:60]
        elif rc2 == 0:
            self.status = "healthy"
            self.version = "systemd service"
        else:
            self.status = "not_installed"
        self.last_check = datetime.now().isoformat()
        return {"status": self.status, "version": self.version}

    def get_jail_status(self, jail: str = "ssh") -> Dict:
        rc, out, err = self.run_cmd(["fail2ban-client", "status", jail], timeout=5)
        if rc != 0:
            return {"jail": jail, "status": "inactive", "error": err}
        result = {"jail": jail, "status": "active"}
        for line in out.split("\n"):
            if "|" in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) == 2:
                    result[parts[0].lower()] = parts[1]
        return result

    def get_all_jails(self) -> List[str]:
        rc, out, _ = self.run_cmd(["fail2ban-client", "status"], timeout=5)
        for line in out.split("\n"):
            if "Jail list" in line or "jail list" in line:
                parts = line.split(":")[-1].strip()
                return [j.strip() for j in parts.split(",") if j.strip()]
        return ["ssh", "sshd", "nginx-http-auth", "apache-auth"]

    def ban_ip(self, ip: str, jail: str = "ssh") -> Dict:
        rc, out, err = self.run_cmd(["fail2ban-client", "set", jail, "banip", ip], timeout=5)
        return {"success": rc == 0, "output": out.strip(), "error": err}

    def unban_ip(self, ip: str, jail: str = "ssh") -> Dict:
        rc, out, err = self.run_cmd(["fail2ban-client", "set", jail, "unbanip", ip], timeout=5)
        return {"success": rc == 0, "output": out.strip(), "error": err}

    def get_data(self, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "status")
        if action == "jails":
            jails = self.get_all_jails()
            statuses = [self.get_jail_status(j) for j in jails]
            return {"jails": statuses}
        if action == "ban":
            return self.ban_ip(kwargs.get("ip", ""), kwargs.get("jail", "ssh"))
        if action == "unban":
            return self.unban_ip(kwargs.get("ip", ""), kwargs.get("jail", "ssh"))
        return self.to_dict()

    def run_action(self, action: str, **kwargs) -> Dict[str, Any]:
        return self.get_data(action=action, **kwargs)