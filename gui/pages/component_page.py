"""
ComponentPage - KES 风格组件详情页
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QScrollArea, QGridLayout,
    QHeaderView, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont

from gui.theme import Colors
from gui.widgets.frost_widgets import (
    SectionTitle, KESButton, ModuleCard
)


class ComponentPage(QWidget):
    """通用组件详情页 — KES 风格"""

    def __init__(self, component, engine, parent=None):
        super().__init__(parent)
        self.component = component
        self.engine = engine
        self.log_output = None
        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 20, 28, 20)
        layout.setSpacing(16)

        # ─── 标题栏 ──────────────────────────────────────
        header = QFrame()
        header.setObjectName("moduleCard")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 14, 20, 14)

        icon_label = QLabel(self.component.icon)
        icon_label.setStyleSheet("font-size: 30px;")
        header_layout.addWidget(icon_label)

        info_layout = QVBoxLayout()
        name_label = QLabel(self.component.display_name)
        f = name_label.font()
        f.setPointSize(18)
        f.setBold(True)
        name_label.setFont(f)
        name_label.setStyleSheet("color: #F0F2F8;")
        info_layout.addWidget(name_label)

        desc_label = QLabel(self.component.description)
        desc_label.setStyleSheet("font-size: 12px; color: #AFB2BE;")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)
        header_layout.addLayout(info_layout, 1)

        self.status_badge = QLabel()
        self.status_badge.setStyleSheet("""
            font-size: 12px; font-weight: 600; padding: 4px 14px;
            border-radius: 4px; background: rgba(60, 200, 100, 20);
            color: #3CC864;
        """)
        header_layout.addWidget(self.status_badge, 0, Qt.AlignmentFlag.AlignRight)

        layout.addWidget(header)

        # ─── 操作按钮 ────────────────────────────────────
        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)

        self.btn_refresh = KESButton("⟳ 刷新", "")
        self.btn_refresh.clicked.connect(self._refresh)
        actions_layout.addWidget(self.btn_refresh)

        self._add_action_buttons(actions_layout)
        actions_layout.addStretch()
        layout.addWidget(actions)

        # ─── 内容区 ──────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(12)

        self._build_status_section()
        self._build_data_section()

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        self._timer.start(5000)

    def _add_action_buttons(self, layout):
        pass

    def _card(self, title_text: str) -> QFrame:
        """创建一个 KES 风格卡片容器"""
        card = QFrame()
        card.setObjectName("moduleCard")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(10)
        t = SectionTitle(title_text)
        cl.addWidget(t)
        return card

    def _card_layout(self, card) -> QVBoxLayout:
        return card.layout()

    def _build_status_section(self):
        card = self._card("组件状态")
        cl = self._card_layout(card)

        info = self.component.to_dict()
        rows = [
            ("名称", info.get("display_name", "-")),
            ("版本", info.get("version", "未知")),
            ("状态", info.get("status", "unknown")),
            ("分类", info.get("category", "-")),
            ("最后检查", str(info.get("last_check", "从未"))),
        ]
        for k, v in rows:
            row_w = QWidget()
            rl = QHBoxLayout(row_w)
            rl.setContentsMargins(0, 2, 0, 2)
            kl = QLabel(k)
            kl.setFixedWidth(80)
            kl.setStyleSheet("color: #AFB2BE; font-size: 13px;")
            vl = QLabel(str(v))
            vl.setStyleSheet("color: #F0F2F8; font-weight: 600; font-size: 13px;")
            rl.addWidget(kl)
            rl.addWidget(vl, 1)
            cl.addWidget(row_w)

        self.content_layout.addWidget(card)

    def _build_data_section(self):
        card = self._card("运行数据")
        cl = self._card_layout(card)

        self.data_table = QTableWidget()
        self.data_table.setColumnCount(2)
        self.data_table.setHorizontalHeaderLabels(["指标", "值"])
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.data_table.setMinimumHeight(120)
        cl.addWidget(self.data_table)

        self.content_layout.addWidget(card)

    def _build_log_section(self):
        card = self._card("日志输出")
        cl = self._card_layout(card)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(160)
        self.log_output.setStyleSheet("""
            QTextEdit {
                background: rgba(0, 0, 0, 30);
                border: 1px solid rgba(255, 255, 255, 8);
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                color: #C0C0D0;
            }
        """)
        cl.addWidget(self.log_output)
        self.content_layout.addWidget(card)

    def _refresh(self):
        try:
            health = self.component.check_health()
            status = health.get("status", "unknown")
            self.component.status = status
            self.component.version = health.get("version", "")
            self._update_status_badge(status)
            self._update_data_table(health)
            self._update_log()
        except Exception as e:
            self.status_badge.setText(f"错误: {str(e)}")
            self.status_badge.setStyleSheet("""
                font-size: 12px; font-weight: 600; padding: 4px 14px;
                border-radius: 4px; background: rgba(230, 70, 70, 20);
                color: #E64646;
            """)

    def _update_status_badge(self, status):
        color_map = {
            "healthy": ("● 运行中", "#3CC864"),
            "degraded": ("● 降级", "#F5AF32"),
            "unhealthy": ("● 异常", "#E64646"),
            "not_installed": ("○ 未安装", "#6E7282"),
            "error": ("● 错误", "#E64646"),
        }
        text, color = color_map.get(status, ("○ 未知", "#6E7282"))
        self.status_badge.setText(text)
        self.status_badge.setStyleSheet(f"""
            font-size: 12px; font-weight: 600; padding: 4px 14px;
            border-radius: 4px; background: rgba({self._hex_to_rgb(color)}, 20);
            color: {color};
        """)

    def _update_data_table(self, health: dict):
        if not hasattr(self, "data_table"):
            return
        self.data_table.setRowCount(0)
        for k, v in health.items():
            row = self.data_table.rowCount()
            self.data_table.insertRow(row)
            self.data_table.setItem(row, 0, QTableWidgetItem(str(k)))
            val = QTableWidgetItem(str(v)[:200])
            val.setToolTip(str(v))
            self.data_table.setItem(row, 1, val)

    def _update_log(self):
        if not hasattr(self, "log_output") or self.log_output is None:
            return
        logs = self.engine.get_logs(source=self.component.name, limit=20)
        text = "\n".join(
            f"[{l.get('time','')[-8:]}] [{l.get('level','')}] {l.get('message','')}"
            for l in logs
        )
        if text:
            self.log_output.setText(text)

    def _hex_to_rgb(self, h: str) -> str:
        h = h.lstrip("#")
        return f"{int(h[0:2],16)}, {int(h[2:4],16)}, {int(h[4:6],16)}"

    def stop(self):
        self._timer.stop()


# ─── 特化页面 ──────────────────────────────────────────────

class ClamAVPage(ComponentPage):
    def _add_action_buttons(self, layout):
        btn_scan = KESButton("🔄 快速扫描 /tmp", "")
        btn_scan.clicked.connect(self._quick_scan)
        layout.addWidget(btn_scan)
        btn_upd = KESButton("📥 更新病毒库", "")
        btn_upd.setStyleSheet("""
            QPushButton {
                background: rgba(60,200,100,20); border: 1px solid rgba(60,200,100,40);
                border-radius: 6px; padding: 8px 20px; font-size: 13px;
                font-weight: 600; color: #3CC864;
            }
            QPushButton:hover { background: rgba(60,200,100,35); }
        """)
        btn_upd.clicked.connect(self._update_db)
        layout.addWidget(btn_upd)

    def _build_data_section(self):
        super()._build_data_section()
        self._build_log_section()

    def _quick_scan(self):
        result = self.component.scan_directory("/tmp")
        if self.log_output:
            self.log_output.setText(
                f"扫描完成: {result.get('files_scanned',0)} 文件, "
                f"{result.get('infected',0)} 威胁\n"
                + "\n".join(result.get('summary',[]))
            )

    def _update_db(self):
        result = self.component.update_virus_db()
        if self.log_output:
            self.log_output.setText(
                f"病毒库更新 {'成功' if result.get('success') else '失败'}\n"
                f"{result.get('output','')[:500]}"
            )


class SuricataPage(ComponentPage):
    def _build_data_section(self):
        card = QFrame()
        card.setObjectName("moduleCard")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(10)
        cl.addWidget(SectionTitle("攻击类型统计"))

        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["类型", "数量"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        self.stats_table.setMinimumHeight(150)
        cl.addWidget(self.stats_table)
        self.content_layout.addWidget(card)
        self._build_log_section()

    def _update_data_table(self, health: dict):
        super()._update_data_table(health)
        try:
            data = self.component.get_data()
            stats = data.get("stats", {})
            by_type = stats.get("by_type", {})
            self.stats_table.setRowCount(0)
            for k, v in sorted(by_type.items(), key=lambda x: -x[1]):
                row = self.stats_table.rowCount()
                self.stats_table.insertRow(row)
                self.stats_table.setItem(row, 0, QTableWidgetItem(str(k)))
                self.stats_table.setItem(row, 1, QTableWidgetItem(str(v)))
        except:
            pass


class Fail2banPage(ComponentPage):
    def _add_action_buttons(self, layout):
        btn = KESButton("🔄 刷新封禁列表", "")
        btn.clicked.connect(self._refresh)
        layout.addWidget(btn)

    def _build_data_section(self):
        card = QFrame()
        card.setObjectName("moduleCard")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(10)
        cl.addWidget(SectionTitle("封禁统计"))

        self.jail_table = QTableWidget()
        self.jail_table.setColumnCount(5)
        self.jail_table.setHorizontalHeaderLabels(
            ["Jail", "状态", "当前封禁", "总计封禁", "最近封禁"]
        )
        self.jail_table.horizontalHeader().setStretchLastSection(True)
        self.jail_table.setMinimumHeight(150)
        cl.addWidget(self.jail_table)
        self.content_layout.addWidget(card)
        self._build_log_section()

    def _update_data_table(self, health: dict):
        super()._update_data_table(health)
        try:
            data = self.component.get_data(action="jails")
            jails = data.get("jails", [])
            self.jail_table.setRowCount(0)
            for j in jails:
                row = self.jail_table.rowCount()
                self.jail_table.insertRow(row)
                self.jail_table.setItem(row, 0, QTableWidgetItem(j.get("jail","")))
                self.jail_table.setItem(row, 1, QTableWidgetItem(j.get("status","")))
                self.jail_table.setItem(row, 2, QTableWidgetItem(str(j.get("currently banned","0"))))
                self.jail_table.setItem(row, 3, QTableWidgetItem(str(j.get("total banned","0"))))
                self.jail_table.setItem(row, 4, QTableWidgetItem(str(j.get("last banned",""))))
        except:
            pass


class OsqueryPage(ComponentPage):
    def _build_data_section(self):
        for cat in ["system", "users", "processes", "network", "packages"]:
            card = QFrame()
            card.setObjectName("moduleCard")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            cl.addWidget(SectionTitle(cat.capitalize()))
            table = QTableWidget()
            table.setMinimumHeight(80)
            table.setMaximumHeight(180)
            cl.addWidget(table)
            setattr(self, f"table_{cat}", table)
            self.content_layout.addWidget(card)
        self._build_log_section()

    def _update_data_table(self, health: dict):
        super()._update_data_table(health)
        for cat in ["system", "users", "processes", "network", "packages"]:
            data = self.component.get_data(category=cat)
            table = getattr(self, f"table_{cat}", None)
            if not table:
                continue
            results = data.get("results", [])
            table.setColumnCount(0)
            table.setRowCount(0)
            if results:
                headers = list(results[0].keys())
                table.setColumnCount(len(headers))
                table.setHorizontalHeaderLabels(headers)
                for r in results:
                    row = table.rowCount()
                    table.insertRow(row)
                    for col, h in enumerate(headers):
                        table.setItem(row, col, QTableWidgetItem(str(r.get(h,""))))


PAGE_MAP = {
    "clamav": ClamAVPage,
    "suricata": SuricataPage,
    "fail2ban": Fail2banPage,
    "osquery": OsqueryPage,
}


def get_component_page(component, engine):
    page_class = PAGE_MAP.get(component.name, ComponentPage)
    return page_class(component, engine)