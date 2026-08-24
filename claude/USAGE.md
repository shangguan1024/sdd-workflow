# SDD-Workflow Usage Guide

## Plugin + Skill 配合使用（必需）

SDD-Workflow 由两部分组成，**必须同时安装才能完整工作**：

| 组件 | 路径 | 角色 | 功能 |
|------|------|------|------|
| **Plugin** | `sdd-workflow-plugin` | "Must do" | 强制约束、Phase Gate、工具命令 |
| **Skill** | `~/.config/opencode/skills/sdd-workflow` | "How to do" | 详细指导、设计模板、示例文档 |

```
┌─────────────────────────────────────┐
│  Plugin (强制约束)                   │
│  ├── Phase Gate Middleware          │  阻止跳过阶段
│  ├── Tool Commands (CLI 命令)        │  工具命令
│  ├── State Management               │  状态持久化
│  ├── Context Injection              │  注入 Phase Prompt
│  └── Project Initialization         │  创建目录结构
└─────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────┐
│  Skill (详细指导)                    │
│  ├── phases-reference.md            │  Phase 详细步骤
│  ├── design-doc-template.md         │  设计文档模板
│  ├── interface-example.md           │  8维接口示例
│  ├── dependency-example.md          │  5维依赖示例
│  └── visualization-guide.md         │  PlantUML/Mermaid
└─────────────────────────────────────┘
```

## 安装配置（Claude Code）

Claude Code 版由 `install.ps1` 自动部署（详见仓库根 `INSTALL.md`）：

```powershell
.\install.ps1 -Target claude -InstallRoot D:\sdd-workflow
```

部署产物：
- `~/.claude/skills/sdd-workflow/`（SKILL.md + 文档 + hooks + engine）
- `~/.claude/settings.json`（三组 hook）
- 子技能 junction 到 `~/.claude/skills/<name>`

> opencode 版安装走 `.\install.ps1 -Target opencode`，详见 `INSTALL.md`。

## 工具命令

### 初始化和状态管理

| 工具 | 描述 |
|------|------|
| `node "__SDD_CLAUDE_DIR__/engine/bin/sdd.js" init` | 初始化项目结构（.sdd/, CONSTITUTION/, docs/） |
| `start` | 开始功能开发（Phase 0: Research） |
| `resume` | 恢复中断的工作流 |
| `node "__SDD_CLAUDE_DIR__/engine/bin/sdd.js" status` | 显示当前 Phase、feature、编辑计数 |
| `node "__SDD_CLAUDE_DIR__/engine/bin/sdd.js" complete` | 完成工作流（Phase 6） |

### Phase Gate 操作

| 工具 | 描述 |
|------|------|
| `gate` phase=N action=check | 显示 Phase N Gate 要求 |
| `gate` phase=N action=approve | **需要人工确认**，过渡到 Phase N |
| `gate` phase=N action=block | 强制停留在当前 Phase |

### 上下文管理

| 工具 | 描述 |
|------|------|
| `node "__SDD_CLAUDE_DIR__/engine/bin/sdd.js" refresh` | 强制上下文刷新，注入关键需求 |
| `直接 Read findings.md` | Memory 时间线（Layer 2） |
| `直接 Read design.md` | Memory 详细内容（Layer 3） |

## 完整工作流示例

### Phase 0: Research & Understanding

```
# 1. 开始功能（进入 Phase 0）
调用 start 工具，参数 feature="user-auth"

# Plugin 行为:
✅ 创建 docs/features/user-auth/findings.md
✅ 设置 currentPhase = Phase.UNDERSTANDING
✅ 阻止 edit/write/bash 工具
✅ 注入 Phase 0 Prompt

# 2. 执行研究（只能用 read/glob/grep）
AI 读取 Skill 文档:
  - phases-reference.md (Phase 0 详细步骤)
  - interface-example.md (接口定义示例)

执行研究:
  - 分析 5+ 相关文件
  - 引用 2+ 外部资料
  - 识别 2+ 约束条件
  - 比较 2+ 方案

写入 findings.md (Phase 0 section)

# 3. 检查 Gate 要求
调用 gate 工具，参数 phase=1 action=check

# 输出:
✅ Phase 0 section: present
✅ 5+ files analyzed: src/auth.py, src/user.py, ...
✅ 2+ citations: RFC 6749, JWT spec
✅ 2+ constraints: Performance < 500ms, Security bcrypt
✅ 2+ alternatives: Session-based vs JWT-based

# 4. 批准进入 Phase 1（需要人工确认）
调用 gate 工具，参数 phase=1 action=approve
等待用户确认: "Phase gate requirements met. Should I proceed to Phase 1?"
用户回答: "Yes"

# Plugin 过渡到 Phase 1
✅ 解除 edit/write 限制（bash 仍被阻止）
✅ 注入 Phase 1 Prompt
```

### Phase 1: Requirements & Design

```
# 1. AI 读取 Skill 模板
读取 design-doc-template.md (Total-Part 结构)
读取 interface-example.md (8维接口定义)
读取 dependency-example.md (5维依赖分析)

# 2. 生成设计文档
Part 1: Overall Architecture
Part 2: Data Flow (PlantUML)
Part 3: Module Decomposition (Mermaid + 8-dim + 5-dim)
Part 4: Integration & Verification

# 3. Constitution 合规检查

# 4. 检查 Gate 要求
调用 gate 工具，参数 phase=2 action=check

# 5. 批准进入 Phase 2
调用 gate 工具，参数 phase=2 action=approve
等待用户确认
```

### Phase 2-6 流程

```
Phase 2: Implementation Planning
  - AI 读取 design.md
  - 分解任务（每个任务：input, output, estimate）
  - 写入 task_plan.md
  - node "__SDD_CLAUDE_DIR__/engine/bin/sdd.js" gate 3 approve

Phase 3: Module Development
  - Plugin 允许所有工具
  - AI 执行任务（subagent-driven-development）
  - 编写代码 + 单元测试
  - node "__SDD_CLAUDE_DIR__/engine/bin/sdd.js" gate 4 approve

Phase 4: Integration & Testing
  - AI 运行集成测试、E2E测试
  - node "__SDD_CLAUDE_DIR__/engine/bin/sdd.js" gate 5 approve

Phase 5: Code Quality Review
  - AI 生成 architecture_review.md
  - AI 生成 code_quality_review.md
  - node "__SDD_CLAUDE_DIR__/engine/bin/sdd.js" gate 6 approve

Phase 6: Memory Persistence
  - AI 更新 AGENTS.md
  - AI 更新 PROJECT_STATE.md
  - node "__SDD_CLAUDE_DIR__/engine/bin/sdd.js" complete
```

## Phase Gate 人工确认机制

`gate` 工具的 `approve` 动作需要人工确认：

```
# AI 调用:
node "__SDD_CLAUDE_DIR__/engine/bin/sdd.js" gate 1 approve

# Plugin 返回:
⚠️ HUMAN CONFIRMATION REQUIRED for Phase 1
DO NOT proceed without explicit human approval.
Ask the user: 'Phase gate requirements met. Should I proceed to Phase X?'
Only call gate again with confirmed=true after user says yes.

# AI 必须等待用户确认:
用户: "Yes, proceed to Phase 1"

# AI 再次调用:
node "__SDD_CLAUDE_DIR__/engine/bin/sdd.js" gate 1 approve --confirmed true

# Plugin 过渡:
✅ Gate approved by human. Transitioned to Phase 1.
```

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| Plugin 工具未加载 | 检查 opencode.json plugin 路径，重启 opencode |
| Skill 文档未加载 | 检查 skills.paths 配置，重启 opencode |
| Phase Gate 阻止操作 | 完成 Phase 要求，调用 gate approve |
| 上下文漂移 | 调用 node "__SDD_CLAUDE_DIR__/engine/bin/sdd.js" refresh |

## 项目结构

```
project/
├── .sdd/
│   └── state.json           # Workflow 状态（Plugin 管理）
│   └── project.json         # 项目配置
├── CONSTITUTION/
│   └── core.md              # 核心原则
│   └── design-rules.md      # 设计规则
│   └── implementation-rules.md # 实现规则
│   └── review-rules.md      # 审查规则
│   └── workflow-rules.md    # 工作流规则
├── PROJECT_STATE.md         # 项目状态聚合
├── AGENTS.md                # AI 上下文
└── docs/
    └── features/
        └── <feature>/
            ├── findings.md     # 研究发现
            ├── design.md       # 设计文档
            ├── task_plan.md    # 实现计划
            ├── reviews/        # 代码审查
            │   ├── architecture_review.md
            │   └── code_quality_review.md
            └── .sdd/
                └── checkpoint.json  # 检查点
```