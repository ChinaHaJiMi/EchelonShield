cmake_minimum_required(VERSION 3.20)
project(EchelonShield
    VERSION 1.0.0
    DESCRIPTION "统一安全中枢 — 集成 15+ 安全组件的 Linux 桌面防护平台"
    LANGUAGES NONE
)

# ============================================================
# EchelonShield CMake Build Configuration
# 本项目为 Python (PyQt6) 应用，CMake 用于项目构建、打包和测试编排
# ============================================================

# ─── 项目元信息 ──────────────────────────────────────────────
set(APP_NAME "EchelonShield")
set(APP_VERSION "1.0.0")
set(APP_MAIN "python3 ${CMAKE_SOURCE_DIR}/__main__.py")

# ─── Python 检测 ─────────────────────────────────────────────
find_package(Python3 COMPONENTS Interpreter REQUIRED)
message(STATUS "Python: ${Python3_EXECUTABLE} (${Python3_VERSION})")

# ─── 自定义目标：运行应用 ────────────────────────────────────
add_custom_target(run
    COMMAND ${Python3_EXECUTABLE} "${CMAKE_SOURCE_DIR}/__main__.py"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "启动 EchelonShield 应用"
)

# ─── 自定义目标：检查依赖是否可用 ─────────────────────────────
add_custom_target(check-deps
    COMMAND ${Python3_EXECUTABLE} -c "
import sys
deps = ['PyQt6']
for dep in deps:
    try:
        __import__(dep)
        print(f'  ✅ {dep}')
    except ImportError:
        print(f'  ❌ {dep} (未安装)')
        sys.exit(1)
print('所有核心依赖已就绪')
"
    COMMENT "检查 Python 依赖"
)

# ─── 自定义目标：运行所有组件健康检查 ─────────────────────────
add_custom_target(health-check
    COMMAND ${Python3_EXECUTABLE} -c "
import sys, os
sys.path.insert(0, '${CMAKE_SOURCE_DIR}')
sys.path.insert(0, '${CMAKE_SOURCE_DIR}/lib')
from core.engine import engine
from components.registry import register_all
register_all()
results = engine.check_all()
total = len(results)
healthy = sum(1 for r in results.values() if r.get('status') == 'healthy')
print(f'组件总数: {total}')
print(f'健康数量: {healthy}')
for name, r in results.items():
    icon = '✅' if r.get('status') == 'healthy' else '❌'
    print(f'  {icon} {name}: {r.get(\"status\", \"unknown\")}')
"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "运行所有组件健康检查"
)

# ─── 自定义目标：PyInstaller 打包 ────────────────────────────
find_program(PYINSTALLER NAMES pyinstaller)
if(PYINSTALLER)
    add_custom_target(package
        COMMAND ${PYINSTALLER}
            --onefile
            --windowed
            --name "${APP_NAME}"
            --add-data "components:components"
            --add-data "core:core"
            --add-data "gui:gui"
            --add-data "data:data"
            --add-data "lib:lib"
            --icon "${CMAKE_SOURCE_DIR}/assets/icon.png"
            --distpath "${CMAKE_SOURCE_DIR}/dist"
            --workpath "${CMAKE_SOURCE_DIR}/build"
            "${CMAKE_SOURCE_DIR}/__main__.py"
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        COMMENT "使用 PyInstaller 打包 EchelonShield"
    )
else()
    message(WARNING "pyinstaller 未找到，'package' 目标不可用")
    add_custom_target(package
        COMMAND ${CMAKE_COMMAND} -E echo "错误: pyinstaller 未安装。运行: pip install pyinstaller"
    )
endif()

# ─── 自定义目标：清理构建产物 ─────────────────────────────────
add_custom_target(clean-all
    COMMAND ${CMAKE_COMMAND} -E remove_directory "${CMAKE_SOURCE_DIR}/build"
    COMMAND ${CMAKE_COMMAND} -E remove_directory "${CMAKE_SOURCE_DIR}/dist"
    COMMAND ${CMAKE_COMMAND} -E remove_directory "${CMAKE_SOURCE_DIR}/__pycache__"
    COMMAND ${CMAKE_COMMAND} -E remove "*.spec"
    COMMENT "清理构建产物和临时文件"
)

# ─── 自定义目标：运行 EchelonShield（使用本地 lib） ─────────
add_custom_target(run-local
    COMMAND ${CMAKE_COMMAND} -E env
        PYTHONPATH="${CMAKE_SOURCE_DIR}/lib:${CMAKE_SOURCE_DIR}"
        ${Python3_EXECUTABLE} "${CMAKE_SOURCE_DIR}/__main__.py"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "启动 EchelonShield（使用本地 lib）"
)

# ─── 安装规则 ────────────────────────────────────────────────
install(TARGETS run-local DESTINATION bin)
install(DIRECTORY components/ core/ gui/
    DESTINATION ${CMAKE_INSTALL_PREFIX}/${APP_NAME}
    FILES_MATCHING PATTERN "*.py"
)
install(FILES __main__.py run.sh
    DESTINATION ${CMAKE_INSTALL_PREFIX}/${APP_NAME}
    PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
                 GROUP_READ GROUP_EXECUTE
                 WORLD_READ WORLD_EXECUTE
)
install(DIRECTORY lib/
    DESTINATION ${CMAKE_INSTALL_PREFIX}/${APP_NAME}/lib
)
install(FILES README.md LICENSE SECURITY.md docs.md
    DESTINATION ${CMAKE_INSTALL_PREFIX}/${APP_NAME}/doc
)

# ─── 打印可用目标 ────────────────────────────────────────────
add_custom_target(help-targets
    COMMAND ${CMAKE_COMMAND} -E echo ""
    COMMAND ${CMAKE_COMMAND} -E echo "EchelonShield ${APP_VERSION} 可用目标:"
    COMMAND ${CMAKE_COMMAND} -E echo "  run         启动应用"
    COMMAND ${CMAKE_COMMAND} -E echo "  run-local   使用本地 lib 启动应用"
    COMMAND ${CMAKE_COMMAND} -E echo "  check-deps  检查 Python 依赖"
    COMMAND ${CMAKE_COMMAND} -E echo "  health-check 运行所有组件健康检查"
    COMMAND ${CMAKE_COMMAND} -E echo "  package     使用 PyInstaller 打包"
    COMMAND ${CMAKE_COMMAND} -E echo "  clean-all   清理临时文件"
    COMMAND ${CMAKE_COMMAND} -E echo ""
    COMMENT "显示可用构建目标"
)