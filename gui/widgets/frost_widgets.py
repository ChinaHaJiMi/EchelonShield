"""
KES 11.6 风格杀软界面组件
"""

from PyQt6.QtWidgets import (
    QFrame, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPainterPath, QFont

from gui.theme import Colors


class ModuleCard(QFrame):
    """功能模块卡片 — KES 卡片风格"""
    clicked = pyqtSignal(str)

    def __init__(self, title="", desc="", icon="🛡️", badge="",
                 status="idle", module_name="", parent=None):
        super().__init__(parent)
        self.module_name = module_name
        self.setObjectName("moduleCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(220, 140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        # 图标 + 状态指示
        top = QHBoxLayout()
        self.icon_label = QLabel(icon)
        self.icon_label.setStyleSheet("font-size: 32px;")
        top.addWidget(self.icon_label)
        top.addStretch()
        self.badge_label = QLabel(badge)
        self.badge_label.setStyleSheet("font-size: 11px; color: #3CC864; font-weight: 600;")
        top.addWidget(self.badge_label)
        layout.addLayout(top)

        # 标题
        self.title_label = QLabel(title)
        f = self.title_label.font()
        f.setPointSize(14)
        f.setBold(True)
        self.title_label.setFont(f)
        self.title_label.setStyleSheet("color: #F0F2F8;")
        layout.addWidget(self.title_label)

        # 描述
        self.desc_label = QLabel(desc)
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 12px; color: #AFB2BE;")
        layout.addWidget(self.desc_label)

        layout.addStretch()

    def set_badge(self, text: str, color: str = "#3CC864"):
        self.badge_label.setText(text)
        self.badge_label.setStyleSheet(f"font-size: 11px; color: {color}; font-weight: 600;")

    def mousePressEvent(self, event):
        if self.module_name:
            self.clicked.emit(self.module_name)
        super().mousePressEvent(event)


class StatusBarWidget(QFrame):
    """顶部绿色安全状态栏 — KES 风格"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)

        # 状态图标
        self.shield_icon = QLabel("🛡️")
        self.shield_icon.setStyleSheet("font-size: 22px;")
        layout.addWidget(self.shield_icon)

        # 状态文本
        self.status_text = QLabel("  设备防护状态：正常  ")
        self.status_text.setStyleSheet("""
            font-size: 14px; font-weight: bold; color: #F0F2F8;
            background: rgba(60, 200, 100, 25);
            border-radius: 4px; padding: 4px 12px;
        """)
        layout.addWidget(self.status_text)

        layout.addStretch()

        # 右侧信息
        self.info_btn = QPushButton("  授权有效  ")
        self.info_btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: 1px solid rgba(255,255,255,15);
                border-radius: 4px; padding: 4px 12px;
                font-size: 12px; color: #AFB2BE;
            }
            QPushButton:hover { background: rgba(255,255,255,8); color: #F0F2F8; }
        """)
        layout.addWidget(self.info_btn)

        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(32, 32)
        settings_btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                font-size: 18px; color: #AFB2BE;
            }
            QPushButton:hover { color: #F0F2F8; }
        """)
        layout.addWidget(settings_btn)

    def set_protected(self, protected: bool = True):
        if protected:
            self.shield_icon.setText("🛡️")
            self.status_text.setText("  设备防护状态：正常  ")
            self.status_text.setStyleSheet("""
                font-size: 14px; font-weight: bold; color: #F0F2F8;
                background: rgba(60, 200, 100, 25);
                border-radius: 4px; padding: 4px 12px;
            """)
        else:
            self.shield_icon.setText("⚠️")
            self.status_text.setText("  设备防护状态：风险  ")
            self.status_text.setStyleSheet("""
                font-size: 14px; font-weight: bold; color: #F0F2F8;
                background: rgba(230, 70, 70, 25);
                border-radius: 4px; padding: 4px 12px;
            """)

    def update_component_count(self, healthy: int, total: int):
        self.info_btn.setText(f"  {healthy}/{total} 组件在线  ")


class NavButton(QPushButton):
    """左侧导航按钮"""

    def __init__(self, text="", icon="", name=""):
        super().__init__(f"  {icon}  {text}")
        self._nav_name = name
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)

    def nav_name(self):
        return self._nav_name


class SectionTitle(QLabel):
    """分区标题"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        f = self.font()
        f.setPointSize(14)
        f.setBold(False)
        self.setFont(f)
        self.setStyleSheet("color: #AFB2BE; padding: 4px 0;")


class KESButton(QPushButton):
    """KES 风格按钮"""
    def __init__(self, text="", icon="", green=False, parent=None):
        super().__init__(f" {icon} {text}", parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if green:
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(60, 200, 100, 20);
                    border: 1px solid rgba(60, 200, 100, 40);
                    border-radius: 6px; padding: 8px 20px;
                    font-size: 13px; font-weight: 600;
                    color: #3CC864;
                }
                QPushButton:hover {
                    background: rgba(60, 200, 100, 35);
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: #262734;
                    border: 1px solid #414455;
                    border-radius: 6px; padding: 8px 20px;
                    font-size: 13px; color: #F0F2F8;
                }
                QPushButton:hover {
                    background: #323441;
                    border: 1px solid #3CC864;
                    color: #3CC864;
                }
            """)


class ScanCard(QFrame):
    """扫描任务卡片 - 带进度"""
    def __init__(self, title="", icon="🔍", status="ready", parent=None):
        super().__init__(parent)
        self.setObjectName("moduleCard")
        self.setMinimumHeight(180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 28px;")
        layout.addWidget(icon_lbl)

        self.title_lbl = QLabel(title)
        f = self.title_lbl.font()
        f.setPointSize(15)
        f.setBold(True)
        self.title_lbl.setFont(f)
        layout.addWidget(self.title_lbl)

        self.status_lbl = QLabel("就绪")
        self.status_lbl.setStyleSheet("font-size: 12px; color: #AFB2BE;")
        layout.addWidget(self.status_lbl)

        self.action_btn = QPushButton("开始扫描")
        self.action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.action_btn.setStyleSheet("""
            QPushButton {
                background: rgba(60, 200, 100, 20);
                border: 1px solid rgba(60, 200, 100, 40);
                border-radius: 6px; padding: 6px 16px;
                font-size: 12px; font-weight: 600;
                color: #3CC864;
            }
            QPushButton:hover { background: rgba(60, 200, 100, 35); }
        """)
        layout.addWidget(self.action_btn)

        layout.addStretch()

    def set_status(self, text: str, color: str = "#AFB2BE"):
        self.status_lbl.setText(text)
        self.status_lbl.setStyleSheet(f"font-size: 12px; color: {color};")