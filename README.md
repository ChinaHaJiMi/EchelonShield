# EchelonShield

> 统一安全中枢 — 集成 15+ 安全组件的 Linux 桌面防护平台

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.7%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey)

EchelonShield 是一个基于 PyQt6 构建的 Linux 桌面安全应用程序，它将多种开源安全工具整合到统一的图形界面中。用户无需记住复杂的命令行参数，即可集中管理病毒查杀、入侵检测、日志监控、漏洞扫描等安全任务。

---

## 功能特色

- 🛡️ **统一管理** — 一个界面管理所有安全组件，实时查看各组件运行状态
- 🔍 **病毒查杀** — 集成 ClamAV，支持快速扫描、全盘扫描和病毒库更新
- 📊 **健康监控** — 定时检测所有组件健康状态，异常实时告警
- 🎨 **KES 风格 UI** — 深色商务主题，磨砂玻璃质感，低视觉疲劳
- 🔌 **可扩展架构** — 基于 `BaseComponent` 基类，新增组件只需实现三个接口方法
- 🧩 **15 个内置组件** — 覆盖防病毒、入侵检测、日志分析、文件完整性、漏洞扫描等

## 已集成组件

| 组件 | 分类 | 功能描述 |
|------|------|----------|
| ClamAV | 防病毒 | 开源病毒查杀引擎，支持文件/目录扫描 |
| Falco | 运行时安全 | 容器和主机运行时异常检测 |
| Wazuh | 统一安全 | 日志分析、文件完整性监控、漏洞检测 |
| Tetragon | 内核安全 | 基于 eBPF 的内核安全监控 |
| Rkhunter | Rootkit 检测 | Rootkit、后门、可疑文件检测 |
| Osquery | 系统监控 | SQL 驱动的操作系统监控框架 |
| Fail2ban | 暴力破解防护 | 自动封禁多次认证失败的 IP |
| Suricata | 入侵检测 | 高性能网络威胁检测引擎 |
| UFW | 防火墙管理 | 简化版 iptables 防火墙管理 |
| CrowdSec | 协同防御 | 社区驱动的 IP 信誉和协同防御 |
| Lynis | 安全审计 | 系统安全审计和加固建议 |
| Trivy | 漏洞扫描 | 容器镜像、文件系统漏洞扫描 |
| KubeArmor | 容器安全 | 基于 eBPF 的容器安全策略实施 |
| Safety | Python 依赖 | Python 依赖库已知漏洞检查 |
| Loki | 日志聚合 | 日志聚合查询系统 |

## 快速开始

### 前置条件

- Python 3.10 或更高版本
- PyQt6 及其依赖
- Linux 操作系统（部分组件需要特定内核版本）

### 安装

```bash
# 克隆仓库
git clone https://github.com/your-org/echelonshield.git
cd echelonshield

# 运行（自动使用内置 PyQt6 依赖）
chmod +x run.sh
./run.sh
```

如需手动管理依赖：

```bash
pip install -r requirements.txt
python __main__.py
```

### 运行

```bash
./run.sh
```

项目根目录下的 `lib/` 已包含完整 PyQt6 运行时，`run.sh` 自动处理路径加载。

## 项目架构

```
EchelonShield/
├── __main__.py             # 应用入口
├── run.sh                  # 启动脚本
├── core/
│   └── engine.py           # 核心引擎（组件注册、调度、健康检查、日志）
├── components/
│   ├── base.py             # 组件基类（CLI 执行、状态管理）
│   ├── registry.py         # 组件注册表
│   ├── clamav_component.py
│   ├── falco_component.py
│   ├── wazuh_component.py
│   ├── tetragon_component.py
│   ├── rkhunter_component.py
│   ├── osquery_component.py
│   ├── fail2ban_component.py
│   ├── suricata_component.py
│   ├── ufw_component.py
│   ├── crowdsec_component.py
│   ├── lynis_component.py
│   ├── trivy_component.py
│   ├── kubearmor_component.py
│   ├── safety_component.py
│   └── loki_component.py
├── gui/
│   ├── main_window.py      # 主窗口 UI
│   ├── theme.py            # 主题系统
│   ├── pages/              # 子页面
│   └── widgets/            # 自定义组件
├── data/                   # 数据和日志目录
└── lib/                    # PyQt6 本地运行时库
```

## 贡献指南

欢迎贡献代码！请先阅读 [SECURITY.md](SECURITY.md) 了解安全策略。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交变更 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证 — 详见 [LICENSE](LICENSE) 文件。

## 致谢
- 致敬所有的开源作者们
- 致敬所有时刻奋战在一线的计算机工作者们

## 闲话&搞笑后记
- 开发者是一只啥也不会的哈基米，第一次用GitHub，请多多指教哈
- 哦对了，你不会以为这代码是本喵写的？（哪为什么注释这样多
- Ai写的阿，Agent：cline全家桶 模型：DeepSeek V4 Flash
- 本喵一点代码都不会（除了cin>>和print()）交bug记得写简单点（太难看不懂）
- 想看开发者日常点个心，以后会用AI写更多胡思乱想…阿不，奇思妙想
- 代码99%都是DeepSeek写的，不会有人误会代码全是我手写吧？
- 文明交流，共创好环境，不然开发者就要哈气了

