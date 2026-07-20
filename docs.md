# EchelonShield 技术文档

## 目录

1. [架构概览](#1-架构概览)
2. [核心引擎](#2-核心引擎)
3. [组件系统](#3-组件系统)
4. [GUI 层](#4-gui-层)
5. [主题系统](#5-主题系统)
6. [数据流](#6-数据流)
7. [扩展指南](#7-扩展指南)
8. [打包与部署](#8-打包与部署)
9. [API 参考](#9-api-参考)

---

## 1. 架构概览

EchelonShield 采用分层架构：

```
┌──────────────────────────────────────────┐
│              GUI 层 (PyQt6)              │
│  MainWindow · ComponentPage · Widgets    │
├──────────────────────────────────────────┤
│         核心引擎层 (EchelonEngine)         │
│  组件注册 · 调度 · 健康检查 · 日志         │
├──────────────────────────────────────────┤
│         组件层 (BaseComponent)            │
│  ClamAV · Falco · Wazuh · … (15个)       │
├──────────────────────────────────────────┤
│         系统层 (CLI / OS)                │
│  systemd · eBPF · iptables · docker …    │
└──────────────────────────────────────────┘
```

### 设计原则

- **组件化**：每个安全工具封装为一个独立组件，遵循统一接口
- **松耦合**：引擎仅通过 `BaseComponent` 接口与组件交互，不关心内部实现
- **本地优先**：所有安全检测通过系统 CLI 命令完成，不依赖云端服务
- **健壮性**：每个组件独立运行，单个组件故障不影响整体

---

## 2. 核心引擎

### EchelonEngine (# core/engine.py)

单例模式的引擎类，负责：

#### 2.1 组件注册与管理

```python
engine = EchelonEngine()
engine.register(clamav_component)
engine.get_component("clamav")       # 按名称获取组件
engine.list_components()             # 列出所有已注册组件
```

#### 2.2 健康检查

```python
engine.check_all()  # 检查所有组件，返回 Dict[name → result]
engine.component_status("clamav")  # 检查单个组件
engine.health_report()  # 汇总健康报告
```

检查结果缓存于 `health_history` 列表中，`health_report()` 返回最后一次检查的摘要统计。

#### 2.3 定时调度

```python
engine.schedule("health_check", 60, engine.check_all)
engine.stop_schedule("health_check")
```

定时任务以守护线程运行，通过 `threading.Event` 优雅停止。

#### 2.4 日志系统

```python
engine.push_log("clamav", "info", "扫描完成", {"files": 100})
engine.get_logs(source="clamav", level="info", limit=200)
```

日志缓冲上限 10000 条，超出后自动裁剪至最近 5000 条。

### 引擎状态

- `STOPPED` — 引擎未启动
- `RUNNING` — 运行中
- `ERROR` — 错误状态

---

## 3. 组件系统

### 3.1 BaseComponent 基类

所有组件继承自 `BaseComponent`，路径：`components/base.py`

**构造函数参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | str | 内部标识名（如 "clamav"） |
| `display_name` | str | 显示名称（如 "ClamAV"） |
| `description` | str | 功能描述 |
| `icon` | str | Emoji 图标 |
| `category` | str | 分类标签 |

**必须实现的抽象方法：**

```python
def check_health(self) -> Dict[str, Any]:
    """返回健康状态字典，必须包含 'status' 键"""
    # status 取值: "healthy" | "degraded" | "unhealthy" | "not_installed" | "error"
```

**可选重写的方法：**

```python
def get_data(self, **kwargs) -> Dict[str, Any]:
    """获取组件的具体数据（扫描结果、隔离区等）"""

def run_action(self, action: str, **kwargs) -> Dict[str, Any]:
    """执行自定义操作（触发扫描、更新病毒库等）"""
```

**内置工具方法：**

- `run_cmd(cmd, timeout, check, sudo)` — 执行 CLI 命令，返回 `(returncode, stdout, stderr)`
- `which(name)` — 检查可执行文件路径
- `bin_exists(name)` — 检查二进制是否安装
- `parse_table_output(text)` — 解析表格输出
- `parse_key_value(text, sep)` — 解析键值对输出

### 3.2 注册机制

通过 `components/registry.py` 集中注册：

```python
def register_all():
    components = [
        ClamAVComponent(),  # 实例化后自动注册到引擎
        FalcoComponent(),
        # ...
    ]
    for comp in components:
        engine.register(comp)
```

### 3.3 现有组件列表

| 内部名称 | 类名 | 检测方法 |
|----------|------|----------|
| clamav | ClamAVComponent | `clamscan --version` |
| falco | FalcoComponent | `falco --version` |
| wazuh | WazuhComponent | 检查 agent 进程/服务状态 |
| tetragon | TetragonComponent | 检查 eBPF 程序加载 |
| rkhunter | RkhunterComponent | `rkhunter --version` |
| osquery | OsqueryComponent | `osqueryi --version` |
| fail2ban | Fail2banComponent | `fail2ban-client ping` |
| suricata | SuricataComponent | `suricata --build-info` |
| ufw | UFWComponent | `ufw status` |
| crowdsec | CrowdSecComponent | `cscli version` |
| lynis | LynisComponent | `lynis show version` |
| trivy | TrivyComponent | `trivy --version` |
| kubearmor | KubeArmorComponent | 检查 KubeArmor 服务状态 |
| safety | SafetyComponent | `safety check --version` |
| loki | LokiComponent | 检查 Loki 服务状态 |

---

## 4. GUI 层

### 4.1 MainWindow

路径：`gui/main_window.py`

主窗口布局从上到下：

1. **大状态区** — 显示整体安全状态（绿色 ✓ = 正常，红色 = 存在威胁）
2. **功能卡片行** — 三张卡片：
   - 防护组件（点击可展开 15 组件详情页）
   - 任务（含"运行扫描"按钮）
   - 病毒库更新（含"检查更新"按钮）
3. **更多工具下拉** — 安全键盘、空间释放、急救盘、内核剑（暂未实现）
4. **底部栏** — 通知和设置按钮

### 4.2 组件详情页

点击"防护组件"卡片时，`_open_component_list()` 方法动态生成包含所有 15 个组件的滚动列表。每个组件显示：
- Emoji 图标
- 显示名称 + 描述
- 版本号
- 状态圆点（健康=绿色，降级=橙色，异常=红色，未安装=灰色）

### 4.3 定时刷新

`QTimer` 每 15 秒触发 `_refresh()`，更新：
- 大状态区的图标颜色和文字
- 组件总数和健康数量

---

## 5. 主题系统

路径：`gui/theme.py`

### Colors 类

定义了完整的 KES 11.6 风格颜色体系：

| 类别 | 颜色值 | 用途 |
|------|--------|------|
| BG_DEEP | #0E0E12 | 最深背景 |
| BG_MAIN | #14151C | 主背景 |
| BG_SURFACE | #1B1C24 | 卡片/面板底色 |
| GREEN_PRIMARY | #3CC864 | 主绿色（防护正常） |
| RED | #E64646 | 危险/异常 |
| TEXT_WHITE | #F0F2F8 | 主文字 |
| TEXT_GRAY | #AFB2BE | 辅助文字 |

### STYLESHEET

全局 QSS 样式表覆盖了：
- 主窗口和对话框背景
- 左侧导航（#navPanel）
- 功能卡片（#moduleCard）
- 滚动条（4px 细条风格）
- 表格、进度条、输入框、按钮、选项卡、分组框

### apply_theme()

```python
def apply_theme(app):
    app.setStyleSheet(STYLESHEET)
    app.setPalette(pal)  # QPalette 颜色角色设置
```

---

## 6. 数据流

### 健康检查流程

```
QTimer (15s) ──→ MainWindow._refresh()
                    │
                    ▼
                 engine.check_all()
                    │
                    ├── clamav.check_health()  ──→ clamscan --version
                    ├── falco.check_health()    ──→ falco --version
                    ├── ... (其余13个组件)
                    │
                    ▼
                ┌── 更新大状态区图标/文字
                └── 更新防护组件卡片计数
```

### 扫描流程（ClamAV 示例）

```
用户点击 "运行扫描"
    │
    ▼
MainWindow._quick_scan()
    │
    ▼
ClamAVComponent.scan_directory("/tmp")
    │
    ├── clamscan -r /tmp
    ├── 解析输出 (Scanned files / Infected files)
    └── 返回 {files_scanned, infected, summary}
    │
    ▼
引擎记录日志 ──→ data/echelon.log
    │
    ▼
UI 卡片更新为 "完成: N 文件, M 威胁"
```

---

## 7. 扩展指南

### 添加新的安全组件

1. 在 `components/` 下创建新文件，继承 `BaseComponent`：

```python
# components/my_tool_component.py
from components.base import BaseComponent

class MyToolComponent(BaseComponent):
    def __init__(self):
        super().__init__(
            name="mytool",
            display_name="MyTool",
            description="我的自定义安全工具",
            icon="🔧",
            category="security"
        )

    def check_health(self):
        rc, out, err = self.run_cmd(["mytool", "--version"])
        self.status = "healthy" if rc == 0 else "not_installed"
        self.version = out.strip()[:50] if rc == 0 else ""
        return {
            "status": self.status,
            "version": self.version
        }

    def run_action(self, action, **kwargs):
        if action == "scan":
            return {"result": "scan completed"}
        return super().run_action(action, **kwargs)
```

2. 在 `components/registry.py` 中注册：

```python
from components.my_tool_component import MyToolComponent

def register_all():
    components = [
        # ... 现有组件
        MyToolComponent(),
    ]
```

3. 如果组件有 GUI 交互需求，在 `gui/main_window.py` 中添加对应 UI 元素

### 组件生命周期

```
实例化 ──→ register() ──→ engine.start()
                              │
                         check_health()  (首次)
                              │
                     ── 定时 check_health() ──
                     │                       │
                run_action()           get_data()
                     │
                     ▼
               engine.stop() → 释放资源
```

---

## 8. 打包与部署

### 常规运行

```bash
./run.sh
```

### 使用 PyInstaller 打包

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "EchelonShield" __main__.py
```

### 依赖

- Python ≥ 3.10
- PyQt6（已内置在 `lib/` 目录）
- 各安全组件对应的系统工具（可选，缺失时组件标记为 "not_installed"）

### 目录结构说明

| 目录 | 用途 | 是否版本控制 |
|------|------|-------------|
| `core/` | 引擎核心 | ✅ |
| `components/` | 安全组件 | ✅ |
| `gui/` | 界面层 | ✅ |
| `data/` | 运行时数据和日志 | ❌ (.gitignore) |
| `lib/` | 本地 PyQt6 运行时 | ✅ |

---

## 9. API 参考

### EchelonEngine

```python
class EchelonEngine:
    def register(self, component: BaseComponent) -> EchelonEngine
    def get_component(self, name: str) -> Optional[BaseComponent]
    def list_components(self) -> List[str]
    def check_all(self) -> Dict[str, Dict]
    def component_status(self, name: str) -> Dict
    def health_report(self) -> Dict
    def start(self) -> EchelonEngine
    def stop(self)
    def schedule(self, name: str, interval_sec: int, target: Callable)
    def stop_schedule(self, name: str)
    def push_log(self, source: str, level: str, message: str, data: Dict = None) -> Dict
    def get_logs(self, source: str = None, level: str = None, limit: int = 200) -> List[Dict]
```

### BaseComponent

```python
class BaseComponent:
    def __init__(self, name, display_name, description="", icon="🔒", category="security")
    def run_cmd(self, cmd: List[str], timeout=30, check=False, sudo=False) -> Tuple[int, str, str]
    def which(self, name: str) -> Optional[str]
    def bin_exists(self, name: str) -> bool
    def parse_table_output(self, text: str) -> List[Dict]
    def parse_key_value(self, text: str, sep=":") -> Dict[str, str]
    def check_health(self) -> Dict[str, Any]                # 抽象方法
    def get_data(self, **kwargs) -> Dict[str, Any]           # 可选重写
    def run_action(self, action: str, **kwargs) -> Dict[str, Any]  # 抽象方法
    def to_dict(self) -> Dict
```

### 健康检查返回值格式

```python
{
    "status": "healthy" | "degraded" | "unhealthy" | "not_installed" | "error",
    "version": "1.2.3",
    "last_check": "2026-07-20T11:30:00",
    # ... 组件自定义字段
}
```

### 健康报告返回值格式

```python
{
    "engine_status": "running",
    "components_total": 15,
    "components_healthy": 12,
    "components_error": 0,
    "last_check": "2026-07-20T11:30:00",
    "details": {
        "clamav": {"status": "healthy", ...},
        "falco": {"status": "not_installed", ...},
        # ...
    }
}
```

---

## 附录：开发环境

### 推荐的开发工具

- IDE: VS Code 或 PyCharm
- Python 版本管理: pyenv
- 调试工具: pdb / ipdb
- 代码格式化: black (行宽 100)
- 类型检查: mypy / pyright
- 测试框架: pytest

### 调试技巧

```python
# 启动开发模式，查看详细日志
export ECHELON_DEBUG=1
./run.sh

# 在代码中插入断点
import pdb; pdb.set_trace()
```

---

> 文档版本: 1.0 · 最后更新: 2026-07