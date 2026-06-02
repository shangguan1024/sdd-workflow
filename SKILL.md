---
name: sdd-workflow
description: "Use when developing a software feature, fixing a bug, or refactoring code that requires end-to-end development workflow with phase gates and design documentation."
version: "2.5"
author: "opencode team"
categories:
  - workflow
  - multi-agent
  - software-development
enforcement:
  phase_gate: true
  requires_plugin: "sdd-workflow-plugin"
dependencies:
  - comprehensive-research-agent@^1.0.0
  - brainstorming@^1.0.0
  - writing-plans@^1.0.0
  - subagent-driven-development@^1.0.0
  - verification-before-completion@^1.0.0
  - requesting-code-review@^1.0.0
  - memory-systems@^1.0.0
---

# SDD-Workflow v2.5

## Plugin + Skill 配合流程（关键）

**工作流程（每一步都必须执行）**：

```
Phase 0: Research & Understanding
┌─────────────────────────────────────────┐
│ 1. Plugin: 注入 Phase Prompt            │
│    告诉 AI: "读取 phases-reference.md"   │
│                                          │
│ 2. AI: 读取 Skill 文档                   │
│    - phases-reference.md (详细步骤)      │
│    - interface-example.md (示例)         │
│                                          │
│ 3. AI: 调用 Skill                        │
│    skill("comprehensive-research-agent") │
│                                          │
│ 4. AI: 执行研究                          │
│    (Plugin 阻止 edit/write/bash)         │
│                                          │
│ 5. AI: 调用 sdd_gate action=check        │
│                                          │
│ 6. 用户: 确认过渡                         │
│                                          │
│ 7. Plugin: 过渡到 Phase 1                │
└─────────────────────────────────────────┘
```

---

## Phase 0: Research & Understanding

### Step 0: 读取 Skill 文档（MANDATORY）

**必须首先读取**：
- `phases-reference.md` - Phase 0 详细步骤（5+ files, 2+ citations 等）
- `interface-example.md` - 8维接口定义示例
- `dependency-example.md` - 5维依赖分析示例

### Step 1: 调用 Skill

```
skill("comprehensive-research-agent")
```

### Step 2: 执行研究（Plugin 阻止 edit/write/bash）

```
- 分析 5+ 相关文件（具体文件名）
- 引用 2+ 外部资料（RFC, 官方文档）
- 识别 2+ 约束条件（性能、安全）
- 比较 2+ 方案（3+ pros/cons each）
```

### Step 3: 写入 findings.md

```
docs/features/<feature>/findings.md

## Phase 0: Research
### Codebase Analysis
- src/auth.rs
- src/user.rs
...

### Technical Principles
- OAuth 2.0 (RFC 6749)
- JWT (RFC 7519)
...

### Constraints
- Response time < 500ms
- bcrypt for passwords
...

### Alternatives
| Approach | Pros | Cons |
| Session-based | Simple | Scalability |
| JWT-based | Stateless | Token management |
```

### Step 4: Gate 检查

```
sdd_gate phase=1 action=check

输出:
✅ findings.md exists
✅ Phase 0 section present
✅ 5+ files analyzed
✅ 2+ citations
✅ 2+ constraints
✅ 2+ alternatives
```

### Step 5: Gate 批准（需要用户确认）

```
sdd_gate phase=1 action=approve
等待用户: "Phase gate met. Should I proceed?"
用户回答: "Yes"
sdd_gate phase=1 action=approve confirmed=true
```

---

## Phase 1: Requirements & Design

### Step 0: 读取 Skill 文档

```
- design-doc-template.md (Total-Part 结构)
- interface-example.md (8维)
- dependency-example.md (5维)
- visualization-guide.md (PlantUML/Mermaid)
```

### Step 1: 调用 Skill

```
skill("brainstorming")
```

### Step 2: 生成设计文档

```
docs/features/<feature>/design.md

## Part 1: Overall Architecture
### 1.1 Overview
### 1.2 Requirements (REQ-001, REQ-002...)
### 1.3 Module List

## Part 2: Data Flow (PlantUML)
@startuml
[AuthService] -> [UserService]
@enduml

## Part 3: Module Decomposition
### Module: AuthService
#### Public Interfaces (8-dimension)
参见 interface-example.md 格式

#### Peripheral Dependencies (5-dimension)
参见 dependency-example.md 格式

## Part 4: Integration & Verification
```

### Step 3: Gate 检查

```
sdd_gate phase=2 action=check
```

---

## Phase 2-6 流程

每个 Phase 都遵循相同的模式：

```
Step 0: 读取 Skill 文档 (phases-reference.md)
Step 1: 调用 Skill (如 skill("writing-plans"))
Step 2: 执行 Phase 任务
Step 3: Gate 检查 (sdd_gate phase=N action=check)
Step 4: 用户确认批准
Step 5: Plugin 过渡到下一 Phase
```

---

## Skill 文档清单

| 文档 | 用途 | Phase |
|------|------|-------|
| phases-reference.md | Phase 详细步骤 | All |
| design-doc-template.md | Total-Part 模板 | 1 |
| interface-example.md | 8维接口定义 | 1 |
| dependency-example.md | 5维依赖分析 | 1 |
| visualization-guide.md | PlantUML/Mermaid | All |
| usage.md | 使用指南 | Setup |

---

## Tool Commands (Plugin)

```
sdd_init              # 初始化项目
sdd_start             # 开始功能 (Phase 0)
sdd_dispatch_skill    # 调用当前 Phase 推荐 Skill (支持 additional_skills)
sdd_gate              # Gate 检查/批准
sdd_status            # 状态查看
sdd_complete          # 完成工作流
```

---

## Skill Dispatch System (v2.5)

### ⚠️ 强制性 Skill 加载机制

` sdd_dispatch_skill` 返回**强制性指令**，AI 必须执行 skill() 调用：

```
sdd_dispatch_skill 返回:
┌─────────────────────────────────────────┐
│ ⚠️ MANDATORY Skill Chain for Phase 1   │
│                                         │
│ 🚨 REQUIRED ACTION NOW:                 │
│ You MUST execute:                       │
│   skill("brainstorming")                │
│   skill("test-driven-development")      │
│                                         │
│ Do NOT proceed until ALL skills invoked │
└─────────────────────────────────────────┘
```

**设计原理**：
- Plugin 不硬编码 skill 名
- 配置驱动 `.sdd/workflow_config.json`
- 返回强制性措辞 → AI 必定执行

### sdd_dispatch_skill 命令

```bash
# 自动调度当前 Phase 的所有 Skill（primary + additional）
sdd_dispatch_skill

# 只调度 primary skill
sdd_dispatch_skill mode=primary

# 只调度 additional skills
sdd_dispatch_skill mode=additional

# 手动调用指定 Skill
sdd_dispatch_skill skill_name="code-review-quality"
```

### Skill Invoke Modes

| Mode | 何时调用 | 使用场景 |
|------|----------|----------|
| `pre_phase` | Phase 开始前 | 研究、设计、规划阶段 |
| `during_phase` | Phase 执行中 | 实现阶段按需调用 |
| `pre_gate` | Gate 检查前 | 代码质量检查、审查阶段 |
| `post_gate` | Gate 批准后 | 状态持久化 |

### 示例：Phase 3 (Module Development)

**配置 (.sdd/workflow_config.json)**：
```json
{
  "id": 3,
  "name": "Module Development",
  "skill": "subagent-driven-development",
  "additional_skills": ["code-review-quality"],
  "skill_invoke_mode": "pre_gate"
}
```

**执行流程**：
```
1. AI 执行 Phase 3 实现任务
2. 调用 sdd_dispatch_skill → 收到强制性指令
3. AI 必定执行 skill chain:
   skill("subagent-driven-development")
   skill("code-review-quality")
4. Gate 检查:
   sdd_gate phase=4 action=check
4. 用户确认后过渡到 Phase 4
```

### 用户扩展 Skill

在项目根目录创建 `.sdd/workflow_config.json`（Plugin 自动创建）：

```json
{
  "version": "2.5",
  "phases": [
    { "id": 3, "additional_skills": ["test-driven-development"] },
    { "id": 5, "additional_skills": ["receiving-code-review"] }
  ]
}
```

**重要**：`additional_skills` 是**追加**，不覆盖默认 primary skill。

### 默认 Primary Skills（每个 Phase）

| Phase | Primary Skill | 说明 |
|-------|---------------|------|
| 0 | comprehensive-research-agent | 深度研究 |
| 1 | brainstorming | 设计探索 |
| 2 | writing-plans | 实现规划 |
| 3 | subagent-driven-development | 并行模块开发 |
| 4 | verification-before-completion | 测试验证 |
| 5 | requesting-code-review | 代码审查请求 |
| 6 | memory-systems | 状态持久化 |

### 配置合并规则

```
DEFAULT_CONFIG (内置)          workflow_config.json (用户)
─────────────────────────────────────────────────────
primary skill: 固定            → 不覆盖，保留
additional_skills: []          →追加用户配置
skill_invoke_mode: pre_phase   → 用户可覆盖
```

**示例**：
- 默认 Phase 3: `subagent-driven-development`
- 用户配置: `{ "id": 3, "additional_skills": ["test-driven-development"] }`
- 最终: `[subagent-driven-development, test-driven-development]`

---

## Red Flags

- ❌ 未读取 Skill 文档就开始执行
- ❌ 未调用推荐 Skill
- ❌ 跳过 Gate 检查
- ❌ Gate 未通过就尝试下一 Phase

---

## See Also

- `phases-reference.md` - 详细步骤
- `usage.md` - 安装配置