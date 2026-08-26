# SDD-Workflow

Software Development Director Workflow —— 7-phase 研发流程（Phase 0–6），每个 phase 之间有强制门控（Phase Gate），产出结构化文档工件（`findings.md` → `design.md` → `task_plan.md` → `reviews/`）。

同时支持 **Claude Code** 和 **opencode** 两个平台；核心引擎（纯 Node 状态机）与子技能由两平台共享。

## 快速安装

```powershell
# Windows 一键部署（详见 INSTALL.md）
Invoke-WebRequest https://raw.githubusercontent.com/shangguan1024/sdd-workflow/main/install.ps1 -OutFile install.ps1
.\install.ps1 -Target both -InstallRoot D:\sdd-workflow
```

`install.ps1` 自动完成：clone 两个仓库 → 构建引擎 → 改配置（opencode.json / settings.json hooks）→ 装子技能。详见 `INSTALL.md`。

## 使用

启动后（`/sdd-workflow` 或说「用 SDD 开发某功能」），流程自动走 7 个 phase，你只需回答需求提问、在每个 gate 拍板「行 / 不行」。

## 7-Phase 概览

```
Phase 0: Research & Requirement Clarification
Phase 1: Requirements & Design
Phase 2: Implementation Planning
Phase 3: Module Development
Phase 4: Integration & Testing
Phase 5: Code Quality Review
Phase 6: Memory Persistence
```

## 文档索引

| 文档 | 用途 |
|------|------|
| `INSTALL.md` | 部署安装（双平台，agent-readable） |
| `SKILL.md` | 工作流入口：phase 概览、gate 协议、命令 |
| `phases-reference.md` | Phase 0–6 详细步骤与 gate 要求 |
| `USAGE.md` | 命令表与工作流示例 |
| `design-doc-template.md` | 设计文档 Total-Part 结构 |
| `interface-example.md` | 8 维接口定义示例 |
| `dependency-example.md` | 5 维依赖分析示例 |
| `visualization-guide.md` | PlantUML / Mermaid 规范 |
| `templates/` | task_plan / change_summary 模板 |
| `claude/` | Claude Code 版外壳（SKILL + hooks） |
