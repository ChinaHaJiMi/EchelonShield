"""
BaseComponent - 所有安全组件基类
定义统一接口：健康检查、CLI执行、数据解析、状态输出
"""

import os
import sys
import json
import time
import shutil
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger("EchelonComponent")


class BaseComponent:
    """安全组件基类"""

    def __init__(
        self,
        name: str,
        display_name: str,
        description: str = "",
        icon: str = "🔒",
        category: str = "security"
    ):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.icon = icon
        self.category = category
        self.status = "unknown"  # unknown / healthy / unhealthy / not_installed
        self.version = ""
        self.last_check = None
        self.last_error = None
        self.data_dir = Path(__file__).parent.parent / "data" / name
        self.data_dir.mkdir(parents=True, exist_ok=True)

    # ─── CLI 执行工具 ────────────────────────────────────

    def run_cmd(
        self,
        cmd: List[str],
        timeout: int = 30,
        check: bool = False,
        sudo: bool = False
    ) -> Tuple[int, str, str]:
        """执行CLI命令，返回 (returncode, stdout, stderr)"""
        full_cmd = cmd
        if sudo and os.geteuid() != 0:
            full_cmd = ["sudo"] + cmd
        try:
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if check and result.returncode != 0:
                raise RuntimeError(
                    f"命令执行失败 ({result.returncode}): {result.stderr.strip()}"
                )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"命令超时 ({timeout}s)"
        except FileNotFoundError:
            return -2, "", f"命令未找到: {cmd[0]}"
        except Exception as e:
            return -3, "", str(e)

    def which(self, name: str) -> Optional[str]:
        """检查可执行文件路径"""
        return shutil.which(name)

    def bin_exists(self, name: str) -> bool:
        """检查二进制是否存在"""
        return self.which(name) is not None

    def parse_table_output(self, text: str) -> List[Dict]:
        """通用表格解析（按行、按空格/冒号分隔）"""
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        results = []
        for line in lines:
            parts = [p.strip() for p in line.split(":") if p.strip()]
            if len(parts) >= 2:
                results.append({parts[0]: ":".join(parts[1:])})
            elif line:
                results.append({"line": line})
        return results

    def parse_key_value(self, text: str, sep: str = ":") -> Dict[str, str]:
        """解析键值对输出"""
        result = {}
        for line in text.strip().split("\n"):
            if sep in line:
                key, val = line.split(sep, 1)
                result[key.strip().lower()] = val.strip()
        return result

    # ─── 组件接口 ────────────────────────────────────────

    def check_health(self) -> Dict[str, Any]:
        """检查组件运行状态"""
        raise NotImplementedError("子类必须实现 check_health()")

    def get_data(self, **kwargs) -> Dict[str, Any]:
        """获取组件具体数据"""
        return {"status": self.status, "version": self.version}

    def run_action(self, action: str, **kwargs) -> Dict[str, Any]:
        """执行组件自定义操作（扫描、更新等）"""
        raise NotImplementedError(f"组件 {self.name} 不支持操作: {action}")

    # ─── 辅助 ────────────────────────────────────────────

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "icon": self.icon,
            "category": self.category,
            "status": self.status,
            "version": self.version,
            "last_check": self.last_check,
            "last_error": self.last_error
        }

    def __repr__(self) -> str:
        return f"<{self.icon} {self.display_name} [{self.status}]>"