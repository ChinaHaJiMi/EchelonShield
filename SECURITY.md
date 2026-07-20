# 安全策略

## 支持的版本

| 版本 | 支持状态 |
|------|----------|
| 1.x (开发版) | ✅ 活跃开发中 |

## 提交漏洞报告

EchelonShield 是一个安全工具，自身的安全性至关重要。如果您发现了安全漏洞，请负责任的披露：

### 步骤

1. **不要公开披露** — 请勿在公开的 Issue、讨论区或社交媒体上报告漏洞
2. **发送邮件** — 将漏洞详情发送至项目维护者邮箱（见仓库主页）
3. **提供详情** — 请包含以下信息：
   - 漏洞描述与潜在影响
   - 复现步骤（PoC 优先）
   - 受影响的组件/版本
   - 建议的修复方案（可选）

### 响应时间

- 初次确认：48 小时内
- 修复计划：5 个工作日内
- 发布修复补丁：视严重程度而定（严重漏洞目标 14 天内）

## 安全使用建议

### 运行时安全

- 始终从官方仓库或可信的发布渠道获取 EchelonShield
- 验证下载文件的完整性（SHA-256 校验和）
- 以最小权限运行：不要以 root 身份运行主进程
- 部分组件（如防火墙修改、系统审计）需要 sudo 提权，但主 GUI 进程应为普通用户

### 组件安全

EchelonShield 集成的每个第三方组件都遵循其自身的安全策略：

| 组件 | 安全公告 |
|------|----------|
| ClamAV | https://github.com/Cisco-Talos/clamav-devel/security |
| Falco | https://github.com/falcosecurity/falco/security |
| Wazuh | https://github.com/wazuh/wazuh/security |
| Suricata | https://github.com/OISF/suricata/security |
| Trivy | https://github.com/aquasecurity/trivy/security |

### 数据处理

- 日志文件存储在 `data/` 目录下，默认权限为 600
- 扫描结果默认不自动上传，所有数据保留在本地
- 组件健康检查仅调用系统命令读取状态，不传输敏感信息

## 依赖管理

- 第三方依赖需定期审查 CVE 公告
- 使用 `pip-audit` 或 Safety 组件检查 Python 依赖漏洞
- 关键安全组件（ClamAV、Suricata 等）建议启用自动更新

## 致谢

我们感谢所有负责任的安全研究人员和贡献者的努力。