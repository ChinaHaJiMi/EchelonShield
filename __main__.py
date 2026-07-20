#!/usr/bin/env python3
"""
EchelonShield - 统一安全中枢
启动入口
"""

import sys
import os

# 确保项目根目录和本地依赖在路径中
_project_root = os.path.dirname(os.path.abspath(__file__))
_local_lib = os.path.join(_project_root, "lib")

# 清理可能不可达的 Flatpak 系统路径
sys.path = [p for p in sys.path if '/var/data' not in p]

# 本地 lib 排在最前面
if os.path.isdir(_local_lib) and _local_lib not in sys.path:
    sys.path.insert(0, _local_lib)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from gui.theme import apply_theme
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    # 设置应用字体
    font = QFont("Segoe UI", 10)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)

    # 应用磨砂玻璃主题
    apply_theme(app)

    # 启动主窗口
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()