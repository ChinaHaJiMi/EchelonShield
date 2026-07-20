"""
EchelonShield Theme — KES 11.6 深色商务杀软风格
深灰/纯黑底色 + 绿色状态标识 + 白色文字 + 扁平卡片
"""

from PyQt6.QtGui import QColor, QPalette


class Colors:
    # KES 暗色基底
    BG_DEEP = QColor(14, 14, 18)             # 最深背景
    BG_MAIN = QColor(20, 21, 28)             # 主背景
    BG_SURFACE = QColor(27, 28, 36)          # 卡片/面板底色
    BG_HOVER = QColor(38, 39, 50)            # 悬停
    BG_ACTIVE = QColor(48, 50, 65)           # 选中

    # KES 绿色系（标志性防护绿）
    GREEN_PRIMARY = QColor(60, 200, 100)     # 主绿色
    GREEN_DIM = QColor(45, 155, 80)          # 暗绿
    GREEN_BG = QColor(60, 200, 100, 25)      # 绿色半透明背景
    GREEN_BAR = QColor(60, 200, 100, 45)     # 状态栏绿色

    # 功能色
    BLUE_ACCENT = QColor(80, 140, 240)       # 蓝色强调
    BLUE_BG = QColor(80, 140, 240, 20)
    ORANGE = QColor(245, 175, 50)            # 警告
    RED = QColor(230, 70, 70)                # 危险
    RED_BG = QColor(230, 70, 70, 20)

    # 文字
    TEXT_WHITE = QColor(240, 242, 248)
    TEXT_GRAY = QColor(175, 178, 190)
    TEXT_DIM = QColor(110, 114, 130)
    TEXT_GREEN = GREEN_PRIMARY

    # 边框
    BORDER = QColor(50, 52, 65)
    BORDER_LIGHT = QColor(65, 68, 85)


STYLESHEET = """
/* ===== 全局 ===== */
QWidget {
    font-family: 'Segoe UI', 'Ubuntu', 'Noto Sans CJK SC', -apple-system, sans-serif;
    font-size: 13px;
    color: #F0F2F8;
}

QMainWindow, QDialog {
    background-color: #14151C;
}

/* ===== 顶部状态栏 ===== */
#statusBar {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #14151C, stop:0.05 #3CC864);
    min-height: 56px;
    max-height: 56px;
    border-bottom: 1px solid #323441;
}

/* ===== 左侧导航 ===== */
#navPanel {
    background-color: #14151C;
    border-right: 1px solid #323441;
    min-width: 200px;
    max-width: 200px;
}

#navPanel QPushButton {
    background: transparent;
    border: none;
    border-radius: 6px;
    padding: 10px 16px;
    text-align: left;
    font-size: 13px;
    color: #AFB2BE;
    margin: 1px 8px;
}

#navPanel QPushButton:hover {
    background: #262734;
    color: #F0F2F8;
}

#navPanel QPushButton:checked {
    background: rgba(60, 200, 100, 20);
    color: #3CC864;
    border-left: 3px solid #3CC864;
}

/* ===== 功能卡片 ===== */
#moduleCard {
    background-color: #1B1C24;
    border: 1px solid #323441;
    border-radius: 10px;
}

#moduleCard:hover {
    border: 1px solid #414455;
    background-color: #262734;
}

/* ===== 滚动 ===== */
QScrollArea { border: none; background: transparent; }

QScrollBar:vertical {
    background: transparent;
    width: 4px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: rgba(255,255,255,25);
    border-radius: 2px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(60,200,100,60);
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height: 0; }

/* ===== 表格 ===== */
QTableWidget {
    background: #1B1C24;
    border: 1px solid #323441;
    border-radius: 8px;
    gridline-color: rgba(255,255,255,6);
    selection-background-color: rgba(60,200,100,25);
    padding: 4px;
}

QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid rgba(255,255,255,4);
}

QHeaderView::section {
    background: transparent;
    border: none;
    padding: 8px 10px;
    font-weight: 600;
    color: #AFB2BE;
    border-bottom: 2px solid #3CC864;
}

/* ===== 进度条 ===== */
QProgressBar {
    background: rgba(255,255,255,8);
    border: none;
    border-radius: 3px;
    height: 6px;
    text-align: center;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3CC864, stop:1 #50B878);
    border-radius: 3px;
}

/* ===== 输入框 ===== */
QLineEdit, QTextEdit, QPlainTextEdit {
    background: #1B1C24;
    border: 1px solid #323441;
    border-radius: 6px;
    padding: 8px 12px;
    color: #F0F2F8;
    font-size: 13px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #3CC864;
}

/* ===== 按钮 ===== */
QPushButton {
    background: #262734;
    border: 1px solid #414455;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
    color: #F0F2F8;
}

QPushButton:hover {
    background: #323441;
    border: 1px solid #3CC864;
    color: #3CC864;
}

QPushButton:pressed {
    background: #1B1C24;
}

/* ===== 选项卡 ===== */
QTabWidget::pane { background: transparent; border: none; }

QTabBar::tab {
    background: transparent;
    border: none;
    padding: 8px 16px;
    color: #AFB2BE;
    border-bottom: 2px solid transparent;
    margin-right: 4px;
}

QTabBar::tab:selected {
    color: #3CC864;
    border-bottom: 2px solid #3CC864;
}

QTabBar::tab:hover {
    color: #F0F2F8;
}

/* ===== 分组框 ===== */
QGroupBox {
    background: #1B1C24;
    border: 1px solid #323441;
    border-radius: 8px;
    margin-top: 16px;
    padding: 12px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #AFB2BE;
}
"""


def apply_theme(app):
    app.setStyleSheet(STYLESHEET)
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, Colors.BG_MAIN)
    pal.setColor(QPalette.ColorRole.WindowText, Colors.TEXT_WHITE)
    pal.setColor(QPalette.ColorRole.Base, Colors.BG_SURFACE)
    pal.setColor(QPalette.ColorRole.AlternateBase, Colors.BG_HOVER)
    pal.setColor(QPalette.ColorRole.Text, Colors.TEXT_WHITE)
    pal.setColor(QPalette.ColorRole.Button, Colors.BG_SURFACE)
    pal.setColor(QPalette.ColorRole.ButtonText, Colors.TEXT_WHITE)
    pal.setColor(QPalette.ColorRole.Highlight, Colors.GREEN_PRIMARY)
    pal.setColor(QPalette.ColorRole.HighlightedText, Colors.TEXT_WHITE)
    app.setPalette(pal)