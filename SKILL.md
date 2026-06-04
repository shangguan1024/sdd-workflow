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
Phase 0: Research & Requirement Clarification
┌─────────────────────────────────────────┐
│ 1. Plugin: 注入 Phase Prompt            │
│    告诉 AI: "读取 phases-reference.md"   │
│                                          │
│ 2. AI: 读取 Skill 文档                   │
│    - phases-reference.md (详细步骤)      │
│    - interface-example.md (示例)         │
│                                          │
│ 3. AI: 调用主技能 (sdd_dispatch_skill)    │
│    → 返回的主技能名，不硬编码             │
│                                          │
│ 4. AI: 向用户询问需求详情                │
│    (功能简介、需求规格、性能要求、        │
│     核心模块设计)                        │
│    (Plugin 阻止 edit/bash)              │
│                                          │
│ 5. AI: 调用 sdd_gate action=check        │
│                                          │
│ 6. 用户: 确认过渡                         │
│                                          │
│ 7. Plugin: 过渡到 Phase 1                │
└─────────────────────────────────────────┘
```

---

## Phase 0: Research & Requirement Clarification

### Step 0: 读取 Skill 文档（MANDATORY）

**必须首先读取**：
- `phases-reference.md` - Phase 0 详细步骤（需求澄清流程）
- `interface-example.md` - 8维接口定义示例
- `dependency-example.md` - 5维依赖分析示例

### Step 1: 调用 Skill（配置驱动）

**⚠️ 不要硬编码 skill 名！先检查 workflow_config.json 的配置**

```
# Step 0: 确定当前 Phase 的主技能
sdd_dispatch_skill mode=primary
→ 返回实际主技能名（可能是默认的，也可能是用户配置覆盖的）

# Step 1: 调用返回的主技能
skill("<returned-skill-name>")
# 例如：默认 → skill("comprehensive-research-agent")
# 例如：配置覆盖 → skill("requirement-web-kernel-clarifier")
```

**配置规则**（workflow_config.json）：
- `skills` 字段有配置且非空 → 替换默认主技能
- `skills` 字段为空或未配置 → 使用 `default_primary_skills`

### Step 2: 向用户询问需求详情（Plugin 阻止 edit/bash）

```
根据用户的功能描述，向用户提出澄清问题：
- Feature Overview: 功能简介，这个功能做什么？
- Requirement Specifications: 需求规格，详细的输入/输出、边界条件
- Performance Requirements: 性能要求，响应时间、吞吐量、并发约束
- Core Modules: 核心模块设计，关键模块职责和交互

⚠️ 不要假设需求 — 先问用户
⚠️ 如果主技能覆盖此步骤，由主技能完成交互
```

### Step 3: 写入 findings.md

```
docs/features/<feature>/findings.md

## Phase 0: Requirement Clarification
### Feature Overview
用户认证功能：支持注册、登录、密码重置...

### Requirement Specifications
- REQ-001: 用户注册（邮箱+密码）
- REQ-002: JWT 登录认证
...

### Performance Requirements
- 登录响应 < 200ms
- 支持 1000 并发连接
...

### Core Modules
- AuthService: 认证核心逻辑
- UserRepository: 用户数据持久化
- TokenManager: JWT 令牌管理
...
```

### Step 4: Gate 检查

```
sdd_gate phase=1 action=check

输出:
✅ findings.md exists
✅ Phase 0 section present
✅ Feature Overview described
✅ Requirement Specifications clarified
✅ Performance Requirements identified
✅ Core Modules designed
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

### ⚠️ Knowledge Base First Principle（代码理解优先级）

**进入 Phase 1 设计阶段时，理解代码/架构必须遵循以下优先级**：

```
优先级顺序：
  1️⃣ FIRST: 优先使用附加技能（additional skills）查询知识库
     - 通过 sdd_dispatch_skill 调度 workflow_config.json 配置的知识库技能
     
  2️⃣ THEN: 知识库没有回答时 → 才进行代码搜索理解
     - 使用 grep/glob/read 搜索源代码
     
  3️⃣ NEVER: 绝不跳过知识库直接进行代码搜索
```

**原因**：知识库是人类/AI 已经总结的结构化理解，比逐文件搜索更高效、更准确、更省 context。代码搜索应作为补充手段，而非首选。

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
sdd_rollback          # 回滚到之前的 Phase（SDD状态+关联代码自动回退，其他代码提示用户选择）
```

---

## Rollback System (v2.5)

### 回滚设计原则

- **SDD状态 + 关联代码**：自动一起回退（不需要用户逐个确认）
  - state.json: currentPhase、gateApprovals 自动回退
  - SDD docs: findings.md、design.md、task_plan.md 通过 git restore 自动回退
  - 关联代码: task_plan.md 中列出的代码文件通过 git restore 自动回退

- **其他代码**：提示用户选择，由用户决定
  - 列出所有不在 task_plan.md 中的代码变更
  - 用户可选择：逐个回退 / 全量回退 / 保留不动

### sdd_rollback 命令

```bash
# 查看回滚计划（不执行）
sdd_rollback target_phase=2 action=plan

# 执行回滚（需要用户确认）
sdd_rollback target_phase=2 code_scope="related" confirmed=true

# 只回滚SDD状态+文档，不碰代码
sdd_rollback target_phase=2 code_scope="none" confirmed=true

# 回滚所有代码（包括不在task_plan中的）
sdd_rollback target_phase=2 code_scope="all" confirmed=true
```

### code_scope 参数说明

| 值 | SDD状态+文档 | task_plan关联代码 | 其他代码 | 说明 |
|----|:---:|:---:|:---:|------|
| `none` | ✅ 自动 | ❌ 不碰 | ❌ 不碰 | 只回滚SDD状态和文档 |
| `related` | ✅ 自动 | ✅ 自动 | 🤔 提示用户 | 推荐：自动回退关联，提示其他 |
| `all` | ✅ 自动 | ✅ 自动 | ✅ 自动 | 全量回退一切 |

### Git SHA Tracking

每次 Phase gate 批准后，checkpoint.json 会记录当前 git HEAD SHA：
```json
{
  "feature": "Pipeline Dump",
  "phase": "3",
  "gitSha": "abc123...",
  "gateApprovals": { "0": true, "1": true, "2": true }
}
```

回滚时利用 SHA 执行 `git checkout <sha> -- <files>` 恢复文件。

---

## Skill Dispatch System (v2.5)

### ⚠️ 强制性 Skill 加载机制

进入 Phase 时，自动加载配置的主技能和附加技能：

```
sdd_dispatch_skill 返回:
┌─────────────────────────────────────────────┐
│ ⚠️ MANDATORY Skill Chain for Phase 1        │
│                                             │
│ Primary Skills: brainstorming, tdd-skill    │
│ Additional Skills: code-review-quality      │
│                                             │
│ 🚨 REQUIRED ACTION NOW:                     │
│ You MUST execute:                           │
│   skill("brainstorming")                    │
│   skill("tdd-skill")                        │
│   skill("code-review-quality")              │
│                                             │
│ Do NOT proceed until ALL skills invoked     │
└─────────────────────────────────────────────┘
```

**设计原理**：
- Plugin 不硬编码 skill 名
- 配置驱动 `.sdd/workflow_config.json`
- `skills: []` - 主技能数组（支持多个）
- `additional_skills: []` - 附加技能数组（用户自定义）
- 返回强制性措辞 → AI 必定执行

### sdd_dispatch_skill 命令

```bash
# 自动调度当前 Phase 的所有 Skill（primary + additional）
sdd_dispatch_skill

# 只调度 primary skills
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

### 配置示例：多个主技能 + 附加技能

**配置 (.sdd/workflow_config.json)**：
```json
{
  "phases": [
    {
      "id": 1,
      "skills": ["brainstorming", "test-driven-development"],
      "additional_skills": ["code-review-quality"],
      "skill_invoke_mode": "pre_phase"
    },
    {
      "id": 3,
      "skills": ["subagent-driven-development", "systematic-debugging"],
      "additional_skills": ["verification-before-completion"],
      "skill_invoke_mode": "pre_gate"
    }
  ]
}
```

**执行流程**：
```
进入 Phase 1:
1. Plugin 注入 Phase Prompt
2. AI 调用 sdd_dispatch_skill → 收到强制性指令
3. AI 必定执行所有主技能:
   skill("brainstorming")
   skill("test-driven-development")
4. AI 必定执行所有附加技能:
   skill("code-review-quality")
5. 继续执行 Phase 任务
```

### 默认 Primary Skills（每个 Phase）

| Phase | Default Skills | 说明 |
|-------|---------------|------|
| 0 | comprehensive-research-agent | 调研与需求澄清 |
| 1 | brainstorming | 设计探索 |
| 2 | writing-plans | 实现规划 |
| 3 | subagent-driven-development | 并行模块开发 |
| 4 | verification-before-completion | 测试验证 |
| 5 | requesting-code-review | 代码审查请求 |
| 6 | memory-systems | 状态持久化 |

### 配置合并规则

```
合并逻辑:
  primary_skills = phase.skills ?? [default_primary_skills[phase.id]]
  additional_skills = phase.additional_skills ?? []
```

**三种配置场景**：

#### 场景 1: 替换默认主技能（覆盖单个）

```json
{
  "id": 0,
  "skills": ["requirement-web-kernel-clarifier"],
  "additional_skills": []
}
```
→ primary: `["requirement-web-kernel-clarifier"]` (完全替换 default)
→ additional: `[]`

#### 场景 2: 配置多个主技能（覆盖多个）

```json
{
  "id": 3,
  "skills": ["subagent-driven-development", "rust-best-practices"],
  "additional_skills": ["code-review-quality"]
}
```
→ primary: `["subagent-driven-development", "rust-best-practices"]` (完全替换 default)
→ additional: `["code-review-quality"]`

⚠️ 多个主技能时，AI 必须按顺序全部调用：
```
skill("subagent-driven-development")
skill("rust-best-practices")
skill("code-review-quality")
```

#### 场景 3: 不替换，只追加附加技能

```json
{
  "id": 1,
  "additional_skills": ["requirement-web-kernel-clarifier"]
}
```
→ primary: `["brainstorming"]` (skills 未配置 → 使用 default)
→ additional: `["requirement-web-kernel-clarifier"]`

#### ⚠️ 注意事项

- `skills` 字段是**完全替换**，不是追加！`skills: ["tdd"]` 会替换掉默认的 brainstorming，而非在 brainstorming 之上追加 tdd
- 如果想保留默认主技能并追加，需显式写进 skills：`skills: ["brainstorming", "tdd"]`
- `additional_skills` 是追加，始终在 primary skills 之后调用

---

## Red Flags

- ❌ 未读取 Skill 文档就开始执行
- ❌ 未调用推荐 Skill
- ❌ 跳过 Gate 检查
- ❌ Gate 未通过就尝试下一 Phase
- ❌ Phase 1 中跳过知识库直接进行代码搜索（违反 Knowledge Base First Principle）

---

## See Also

- `phases-reference.md` - 详细步骤
- `usage.md` - 安装配置