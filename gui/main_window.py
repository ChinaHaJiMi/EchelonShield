"""
EchelonShield MainWindow — 极简杀软UI
顶部窗口栏 → 大状态区 ✓ → 三功能卡片 → 更多工具 → 底栏设置/通知
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QScrollArea,
    QGridLayout, QFrame, QMenu, QToolButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QAction

from core.engine import engine
from components.registry import init_engine


class MainWindow(QMainWindow):
    """极简杀软UI — 参考草图"""

    def __init__(self):
        super().__init__()
        self._init_window()
        self._init_engine()
        self._build_ui()
        self._start_timers()

    # ─── 初始化 ────────────────────────────────────────

    def _init_window(self):
        self.setWindowTitle("EchelonShield")
        self.setMinimumSize(820, 600)
        self.resize(900, 660)

    def _init_engine(self):
        try:
            init_engine()
            engine.push_log("system", "info", "安全引擎已就绪")
        except Exception as e:
            engine.push_log("system", "error", f"引擎错误: {e}")

    # ─── 构建 UI ────────────────────────────────────────

    def _build_ui(self):
        main = QWidget()
        layout = QVBoxLayout(main)
        layout.setContentsMargins(28, 16, 28, 16)
        layout.setSpacing(20)

        # ─── 大状态区 ──────────────────────────────────
        self._build_status_section(layout)

        # ─── 三功能卡片 ─────────────────────────────────
        self._build_cards_row(layout)

        # ─── 更多工具 下拉 ──────────────────────────────
        self._build_tools_menu(layout)

        # ─── 底部图标栏 ────────────────────────────────
        self._build_bottom_bar(layout)

        layout.addStretch(1)

        # 套滚动
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(main)
        self.setCentralWidget(scroll)

        self._main_widget = main
        self._layout = layout

    # ─── 大状态区 ────────────────────────────────────────

    def _build_status_section(self, parent_layout):
        status_widget = QWidget()
        status_widget.setStyleSheet("""
            QWidget {
                background-color: #1B1C24;
                border: 1px solid #323441;
                border-radius: 14px;
            }
        """)
        status_widget.setMinimumHeight(180)

        layout = QVBoxLayout(status_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 白色对勾图标
        self.check_icon = QLabel("✓")
        self.check_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.check_icon.setStyleSheet("""
            font-size: 56px; font-weight: bold;
            color: #3CC864; background: transparent;
            border: none; border-radius: 0;
            padding: 0; margin: 0;
        """)
        layout.addWidget(self.check_icon)

        # 状态文字
        self.status_label = QLabel("您的设备防护已正常启用")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            font-size: 18px; font-weight: 600;
            color: #F0F2F8; background: transparent;
            border: none;
        """)
        layout.addWidget(self.status_label)

        # 副状态
        self.status_sub = QLabel("所有安全组件运行正常")
        self.status_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_sub.setStyleSheet("""
            font-size: 13px; color: #AFB2BE;
            background: transparent; border: none;
        """)
        layout.addWidget(self.status_sub)

        parent_layout.addWidget(status_widget)

    # ─── 三功能卡片 ──────────────────────────────────────

    def _build_cards_row(self, parent_layout):
        cards = QWidget()
        cards_layout = QHBoxLayout(cards)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(16)

        # 卡片 1: 防护组件（点击查看15组件详情）
        self.card_protect = self._make_card(
            "🛡", "防护组件",
            [("总数", "15"), ("已启用", "—")]
        )
        self.card_protect.setCursor(Qt.CursorShape.PointingHandCursor)
        self.card_protect.mousePressEvent = lambda e: self._open_component_list()
        cards_layout.addWidget(self.card_protect, 1)

        # 卡片 2: 任务
        self.card_tasks = self._make_card(
            "📊", "任务",
            [("状态", "暂无任务")]
        )
        # 加一个操作按钮
        task_btn = QPushButton("运行扫描")
        task_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        task_btn.setStyleSheet("""
            QPushButton {
                background: rgba(60,200,100,20);
                border: 1px solid rgba(60,200,100,35);
                border-radius: 6px; padding: 6px 0;
                font-size: 12px; font-weight: 600;
                color: #3CC864;
            }
            QPushButton:hover { background: rgba(60,200,100,35); }
        """)
        task_btn.clicked.connect(self._quick_scan)
        # 把按钮加到卡片底部
        card_layout = self.card_tasks.layout()
        card_layout.addWidget(task_btn)
        cards_layout.addWidget(self.card_tasks, 1)

        # 卡片 3: 病毒库更新
        self.card_update = self._make_card(
            "🔄", "病毒库更新",
            [("状态", "不需要更新")]
        )
        upd_btn = QPushButton("检查更新")
        upd_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        upd_btn.setStyleSheet("""
            QPushButton {
                background: rgba(60,200,100,20);
                border: 1px solid rgba(60,200,100,35);
                border-radius: 6px; padding: 6px 0;
                font-size: 12px; font-weight: 600;
                color: #3CC864;
            }
            QPushButton:hover { background: rgba(60,200,100,35); }
        """)
        upd_btn.clicked.connect(self._check_updates)
        cl2 = self.card_update.layout()
        cl2.addWidget(upd_btn)
        cards_layout.addWidget(self.card_update, 1)

        parent_layout.addWidget(cards)

    def _make_card(self, icon, title, rows):
        """创建深色功能卡片"""
        card = QFrame()
        card.setObjectName("moduleCard")
        card.setMinimumHeight(160)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 16)
        layout.setSpacing(6)

        # 标题行
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 26px; background: transparent; border: none;")
        title_row.addWidget(icon_lbl)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("""
            font-size: 15px; font-weight: bold; color: #F0F2F8;
            background: transparent; border: none;
        """)
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        layout.addLayout(title_row)

        layout.addSpacing(4)

        # 数据行
        for key, val in rows:
            row_w = QWidget()
            row_w.setStyleSheet("background: transparent; border: none;")
            rl = QHBoxLayout(row_w)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(8)
            kl = QLabel(key)
            kl.setStyleSheet("font-size: 12px; color: #AFB2BE; background: transparent; border: none;")
            kl.setFixedWidth(50)
            vl = QLabel(str(val))
            vl.setStyleSheet("font-size: 12px; color: #F0F2F8; font-weight: 600; background: transparent; border: none;")
            rl.addWidget(kl)
            rl.addWidget(vl, 1)
            layout.addWidget(row_w)

            # 存引用方便更新
            if not hasattr(self, '_card_labels'):
                self._card_labels = {}
            self._card_labels[f"{title}_{key}"] = vl

        layout.addStretch()
        return card

    # ─── 更多工具 下拉 ──────────────────────────────────

    def _build_tools_menu(self, parent_layout):
        tool_widget = QWidget()
        tool_widget.setStyleSheet("background: transparent;")
        tool_layout = QHBoxLayout(tool_widget)
        tool_layout.setContentsMargins(0, 0, 0, 0)

        self.more_btn = QPushButton("  更多工具  ▾")
        self.more_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.more_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #323441;
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: 500;
                color: #AFB2BE;
            }
            QPushButton:hover {
                background: #262734;
                border: 1px solid #414455;
                color: #F0F2F8;
            }
        """)

        # 下拉菜单
        self.tools_menu = QMenu(self)
        self.tools_menu.setStyleSheet("""
            QMenu {
                background: #1B1C24;
                border: 1px solid #323441;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
                font-size: 13px;
                color: #F0F2F8;
            }
            QMenu::item:selected {
                background: #262734;
                color: #3CC864;
            }
        """)

        tools_items = [
            ("🔐", "安全键盘"),
            ("🧹", "空间释放"),
            ("💊", "急救盘"),
            ("⚔️", "内核剑"),
        ]
        for icon, text in tools_items:
            action = QAction(f"{icon}  {text}", self)
            action.setEnabled(False)  # 暂不实现
            self.tools_menu.addAction(action)

        self.more_btn.setMenu(self.tools_menu)

        tool_layout.addWidget(self.more_btn)
        tool_layout.addStretch()
        parent_layout.addWidget(tool_widget)

    # ─── 底部图标栏 ──────────────────────────────────────

    def _build_bottom_bar(self, parent_layout):
        bar = QWidget()
        bar.setStyleSheet("background: transparent;")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(0, 0, 0, 0)

        bar_layout.addStretch()

        # 通知图标
        self.notif_btn = QPushButton("🔔")
        self.notif_btn.setFixedSize(40, 40)
        self.notif_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.notif_btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                font-size: 20px; color: #AFB2BE;
            }
            QPushButton:hover { color: #F0F2F8; }
        """)
        bar_layout.addWidget(self.notif_btn)

        # 设置图标
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                font-size: 20px; color: #AFB2BE;
            }
            QPushButton:hover { color: #F0F2F8; }
        """)
        bar_layout.addWidget(self.settings_btn)

        parent_layout.addWidget(bar)

    # ─── 操作 ────────────────────────────────────────────

    def _quick_scan(self):
        comp = engine.get_component("clamav")
        if comp:
            self._update_card_task("扫描中...")
            result = comp.scan_directory("/tmp")
            infected = result.get('infected', 0)
            scanned = result.get('files_scanned', 0)
            self._update_card_task(f"完成: {scanned} 文件, {infected} 威胁")
            engine.push_log("clamav", "info", f"快速扫描: {scanned} 文件, {infected} 威胁")

    def _check_updates(self):
        comp = engine.get_component("clamav")
        if comp:
            result = comp.update_virus_db()
            status = "已是最新版" if result.get('success') else "更新失败"
            self._update_card_update(status)

    def _update_card_task(self, text):
        key = "任务_状态"
        if hasattr(self, '_card_labels') and key in self._card_labels:
            self._card_labels[key].setText(text)

    def _update_card_update(self, text):
        key = "病毒库更新_状态"
        if hasattr(self, '_card_labels') and key in self._card_labels:
            self._card_labels[key].setText(text)

    # ─── 15组件详情页 ──────────────────────────────────

    def _open_component_list(self):
        """切换到15组件详情页"""
        # 创建页面（如已存在则切换）
        if hasattr(self, '_comp_list_page'):
            self.content_stack.setCurrentWidget(self._comp_list_page)
            return

        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部栏：返回 + 标题
        top_bar = QWidget()
        top_bar.setStyleSheet("background: transparent;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(4, 8, 4, 8)

        back_btn = QPushButton("← 返回")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                font-size: 14px; color: #3CC864; font-weight: 600;
                padding: 4px 12px;
            }
            QPushButton:hover { color: #50D878; }
        """)
        back_btn.clicked.connect(self._back_home)
        top_layout.addWidget(back_btn)

        title_lbl = QLabel("安全防护组件")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #F0F2F8;")
        top_layout.addWidget(title_lbl)
        top_layout.addStretch()
        layout.addWidget(top_bar)

        # 滚动列表
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(12, 8, 12, 12)
        content_layout.setSpacing(10)

        comps = engine.list_components()
        for name in comps:
            comp = engine.get_component(name)
            data = comp.to_dict()
            status = data.get("status", "unknown")
            desc = data.get("description", "")

            # 组件卡片
            card = QFrame()
            card.setObjectName("moduleCard")
            card.setMinimumHeight(72)
            cl = QHBoxLayout(card)
            cl.setContentsMargins(16, 10, 16, 10)
            cl.setSpacing(12)

            # 图标
            icon_lbl = QLabel(data.get("icon", "🔒"))
            icon_lbl.setStyleSheet("font-size: 24px; background: transparent; border: none;")
            cl.addWidget(icon_lbl)

            # 名称 + 描述
            text_col = QVBoxLayout()
            text_col.setSpacing(2)
            name_lbl = QLabel(data.get("display_name", name))
            name_lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #F0F2F8; background: transparent; border: none;")
            text_col.addWidget(name_lbl)

            desc_lbl = QLabel(desc)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet("font-size: 11px; color: #AFB2BE; background: transparent; border: none;")
            text_col.addWidget(desc_lbl)
            cl.addLayout(text_col, 1)

            # 版本
            ver_lbl = QLabel(data.get("version", "-")[:20])
            ver_lbl.setStyleSheet("font-size: 11px; color: #6E7282; background: transparent; border: none;")
            ver_lbl.setFixedWidth(120)
            cl.addWidget(ver_lbl)

            # 状态圆点
            dot_colors = {
                "healthy": "#3CC864", "degraded": "#F5AF32",
                "unhealthy": "#E64646", "not_installed": "#6E7282",
                "error": "#E64646",
            }
            dot_color = dot_colors.get(status, "#6E7282")
            status_lbl = QLabel("●")
            status_lbl.setStyleSheet(f"font-size: 16px; color: {dot_color}; background: transparent; border: none;")
            status_lbl.setFixedWidth(24)
            cl.addWidget(status_lbl)

            content_layout.addWidget(card)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        # 保存引用
        self._comp_list_page = page

        # 如果还没有 content_stack 则创建
        if not hasattr(self, 'content_stack'):
            self._build_content_stack()
        self.content_stack.addWidget(page)
        self.content_stack.setCurrentWidget(page)

    def _back_home(self):
        """返回首页"""
        if hasattr(self, 'content_stack'):
            self.content_stack.setCurrentIndex(0)

    def _build_content_stack(self):
        """把主内容包装进 content_stack"""
        # 取现有 scroll 放入 stack
        old_central = self.centralWidget()
        if old_central:
            old_central.setParent(None)
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(old_central)
        self.setCentralWidget(self.content_stack)

    # ─── 定时刷新 ────────────────────────────────────────

    def _start_timers(self):
        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh)
        self._timer.start(15000)
        QTimer.singleShot(500, self._refresh)

    def _refresh(self):
        results = engine.check_all()
        total = len(results)
        healthy = sum(1 for r in results.values() if r.get("status") == "healthy")
        unhealthy = total - healthy

        # 更新大状态区
        if unhealthy > 0:
            self.check_icon.setStyleSheet("""
                font-size: 56px; font-weight: bold;
                color: #E64646; background: transparent;
                border: none;
            """)
            self.status_label.setText("存在威胁")
            self.status_label.setStyleSheet("""
                font-size: 18px; font-weight: 600;
                color: #E64646; background: transparent; border: none;
            """)
            self.status_sub.setText(f"{unhealthy} 个组件存在异常")
            self.status_sub.setStyleSheet("""
                font-size: 13px; color: #E64646;
                background: transparent; border: none;
            """)
        else:
            self.check_icon.setStyleSheet("""
                font-size: 56px; font-weight: bold;
                color: #3CC864; background: transparent;
                border: none;
            """)
            self.status_label.setText("您的设备防护已正常启用")
            self.status_label.setStyleSheet("""
                font-size: 18px; font-weight: 600;
                color: #F0F2F8; background: transparent; border: none;
            """)
            self.status_sub.setText(f"{healthy}/{total} 个组件运行正常")
            self.status_sub.setStyleSheet("""
                font-size: 13px; color: #AFB2BE;
                background: transparent; border: none;
            """)

        # 更新卡片
        key_protect_total = "防护组件_总数"
        key_protect_online = "防护组件_已启用"
        if hasattr(self, '_card_labels'):
            if key_protect_total in self._card_labels:
                self._card_labels[key_protect_total].setText(str(total))
            if key_protect_online in self._card_labels:
                self._card_labels[key_protect_online].setText(str(healthy))

    def closeEvent(self, event):
        engine.stop()
        event.accept()