---
name: sdd-workflow
description: "Software Development Director Workflow - Complete end-to-end development workflow. Use this skill whenever you need to develop a software feature, fix a bug, or refactor code. This skill automatically executes all 6 phases: requirements analysis, architecture design, implementation planning, module development, code review, and memory persistence. Developer confirmation is required at each phase transition."
version: "2.0.0"
author: "opencode team"
categories:
  - workflow
  - multi-agent
  - software-development
  - architecture-aware
enforcement:
  phase_gate: true
  review_artifacts_required: true
  memory_artifacts_required: true
dependencies:
  - nexus-mapper@^1.0.0
  - nexus-query@^1.0.0
  - rust-best-practices@^1.0.0
  - planning-with-files@^1.0.0
  - multi-agent-orchestration@^1.0.0
  - subagent-driven-development@^1.0.0
  - brainstorming@^1.0.0
  - writing-plans@^1.0.0
  - code-review-quality@^1.0.0
  - systematic-debugging@^1.0.0
  - verification-before-completion@^1.0.0
  - requesting-code-review@^1.0.0
  - using-superpowers@^1.0.0
  - test-driven-development@^1.0.0
  - using-git-worktrees@^1.0.0
---

# SDD-Workflow v2.0

## 架构设计

SDD-Workflow v2.0 采用**分层模块化架构**：

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 0: CLI                            │
│              (命令行解析、用户交互)                          │
├─────────────────────────────────────────────────────────────┤
│                    Layer 1: Director                        │
│         (主状态机、Gate 控制、流程编排)                       │
├─────────────────────────────────────────────────────────────┤
│               Layer 2: Phase Orchestrators                 │
│    (Phase 1-6 各阶段流程定义、Step 管理)                     │
├─────────────────────────────────────────────────────────────┤
│                    Layer 3: Capabilities                   │
│              (具体能力接口：brainstorming 等)                │
└─────────────────────────────────────────────────────────────┘

支持模块:
├── checkpoint/     多层 Checkpoint 持久化机制
├── quality/        Quality Harness Pipeline
└── rules/          MD/YAML 多格式规则支持
```

### 模块职责

| 模块 | 职责 |
|------|------|
| `cli.py` | Layer 0: 命令行解析、用户交互 |
| `director.py` | Layer 1: 主状态机、Gate 控制 |
| `phases/` | Layer 2: Phase 流程定义 |
| `capabilities/` | Layer 3: 能力接口 |
| `checkpoint/` | Checkpoint 管理、持久化、恢复 |
| `quality/` | 质量评估、Gate 引擎、报告 |
| `rules/` | MD/YAML 规则解析 |

### Checkpoint 机制

多层 Checkpoint 支持：
- **实时同步**: 后台线程定期保存
- **Phase 级**: Phase 入口/出口 Checkpoint
- **历史版本**: 保留最近 50 个版本
- **原子写入**: 写入前先备份

### Quality Harness

自动化质量评估：
- **Collectors**: 代码指标、测试覆盖率、复杂度、规范
- **Gate Engine**: 可配置的质量 Gate
- **Reporter**: Markdown 格式报告生成

## 完整流程概览

SDD-Workflow 提供 **6 阶段强制执行流程**，每个阶段有明确的输入、输出、验证点和强制确认：

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SDD 6-Phase Workflow                         │
├─────────┬─────────────────────────────────┬─────────────────────────┤
│ Phase 1 │ Requirements Analysis & Design    │ brainstorming skill     │
│    ↓    │         [GATE: Developer Confirm]                       │
│ Phase 2 │ Implementation Planning          │ writing-plans skill     │
│    ↓    │         [GATE: Plan Approved]                             │
│ Phase 3 │ Module Development               │ subagent-driven-dev     │
│    ↓    │         [GATE: Compile + Unit Tests]                      │
│ Phase 4 │ Integration & Testing            │ verification-before-*   │
│    ↓    │         [GATE: Integration Tests Pass]                   │
│ Phase 5 │ Code Quality Review              │ code-review-quality     │
│    ↓    │         [GATE: All 4 Artifacts Verified]                │
│ Phase 6 │ Memory Persistence               │ Auto-document           │
└─────────┴─────────────────────────────────┴─────────────────────────┘
```

## 强制执行机制

### Phase Gate System

**每个 Phase 之间的转换必须通过 Developer Confirmation Gate。**

```
┌──────────────────────────────────────────────────────────┐
│                    PHASE GATE CHECKLIST                  │
├──────────────────────────────────────────────────────────┤
│ 1. Current phase output exists?                          │
│ 2. Next phase input requirements met?                   │
│ 3. Developer explicit confirmation received?             │
│ 4. If ANY answer is NO → STOP, cannot proceed           │
└──────────────────────────────────────────────────────────┘
```

### 必需 Memory Artifacts (Phase 6 强制输出)

#### 项目级别（聚合视图）

| 文件 | 描述 | 强制 |
|------|------|------|
| `PROJECT_STATE.md` | 所有特性状态聚合 | ✅ |
| `AGENTS.md` | 项目级 AI 持久化指令 | ✅ |

#### 特性级别（每个特性独立）

| 文件 | 描述 | 强制 |
|------|------|------|
| `docs/features/<feature>/task_plan.md` | 该特性任务进度 | ✅ |
| `docs/features/<feature>/findings.md` | 该特性和研究发现 | ✅ |
| `docs/features/<feature>/progress.md` | 该特性执行日志 | ✅ |

### 必需 Review Artifacts (Phase 5 强制输出)

| 文件 | 描述 | 强制 |
|------|------|------|
| `docs/features/<feature>/reviews/architecture_review.md` | 架构合规性审查 | ✅ |
| `docs/features/<feature>/reviews/code_quality_review.md` | 代码质量审查 | ✅ |
| `docs/features/<feature>/reviews/test_coverage_report.md` | 测试覆盖率报告 | ✅ |
| `docs/features/<feature>/reviews/requirements_verification.md` | 需求验证报告 | ✅ |

### 特性状态文件

| 文件 | 描述 |
|------|------|
| `docs/features/<feature>/status.toml` | 特性当前 Phase、开发者、进度 |

## Simplified Commands

### `sdd init`
**初始化项目** - 创建完整的文档目录结构

**注意**: 此命令每个项目只执行一次，用于建立项目的基础架构。

```
sdd init
```
自动执行:
1. 创建 8 层目录结构
2. 生成 Constitution 模板文件
3. 生成初始项目级内存 artifacts (PROJECT_STATE.md, AGENTS.md)
4. 初始化 .nexus-map/ (如果 nexus-mapper 可用)

**输出:**
```
✅ SDD-Workflow Initialized

Next: sdd start <feature-name>
```

### `sdd check-init`
**检查初始化状态** - 检查项目是否已初始化

```
sdd check-init
```

**输出:**
```
✅ Project already initialized
   Directory structure: ✓
   Constitution: ✓
   Memory artifacts: ✓
```

### `sdd start <feature-name>`
**开始新功能开发** - 自动执行完整 6 阶段流程

```
sdd start custom-format
```
自动执行:
1. 加载 required skills
2. 创建特性目录 `docs/features/<feature>/`
3. 创建特性级内存制品: task_plan.md, findings.md, progress.md
4. 触发 brainstorming (Phase 1)
5. 在每个 phase gate 暂停等待确认
6. 串联执行直到 Phase 6 完成
7. 更新 PROJECT_STATE.md 聚合视图

### `sdd resume [feature-name]`
**恢复之前会话** - 检查未完成的 phase

```
sdd resume           # 恢复最后一个特性
sdd resume custom-format  # 恢复指定特性
```

如果不指定特性名，显示所有进行中的特性列表供选择。

**检查内容:**
- `docs/features/<feature>/status.toml` - 特性状态
- `docs/features/<feature>/task_plan.md` - 特性任务进度
- `docs/features/<feature>/progress.md` - 特性执行日志
- `PROJECT_STATE.md` - 项目状态

**输出示例:**
```
SDD Resume Options
═══════════════════════════════════════
Active Features:
1. custom-format     [Phase 3: Task 2/5]
2. async-logger     [Phase 1: Design]
3. compression       [Phase 5: Review]

Select feature to resume:
- sdd resume custom-format
- sdd resume async-logger
- sdd resume compression
```

**工作流程:**
1. 如果指定特性：从该特性的最后一个 incomplete phase 继续
2. 如果未指定：显示特性列表，用户选择后继续

### `sdd status`
**查看项目状态** - 显示所有特性的进度

输出:
```
SDD Workflow Status
══════════════════════════════════════════
Active Features: 3

┌─────────────────┬────────────────┬──────────────────┐
│ Feature         │ Developer      │ Phase            │
├─────────────────┼────────────────┼──────────────────┤
│ custom-format   │ @zhangsan      │ Phase 3: Task 3/7│
│ async-logger    │ @lisi         │ Phase 1: Design  │
│ compression     │ @wangwu       │ Phase 5: Review  │
└─────────────────┴────────────────┴──────────────────┘

Project Memory Artifacts: ✅ Complete
Nexus Map: ✅ Ready
══════════════════════════════════════════
```
SDD Workflow Status
═══════════════════════════════════════════
Phase 1: ✅ Requirements Analysis     [Complete]
Phase 2: ✅ Implementation Planning   [Complete]
Phase 3: 🔄 Module Development       [In Progress: Task 3/7]
Phase 4: ⏳ Integration & Testing     [Pending]
Phase 5: ⏳ Code Quality Review      [Pending]
Phase 6: ⏳ Memory Persistence       [Pending]

Memory Artifacts: 3/5 present
Review Artifacts: 4/4 present
═══════════════════════════════════════════
```

### `sdd complete`
**完成当前 workflow** - 强制执行 Phase 5 Review 和 Phase 6 Persistence

如果 review artifacts 不存在或过期，自动触发生成流程。

## Phase 详细说明

### Phase 1: Requirements Analysis & Architecture Design

**Skill:** `brainstorming`

**输入:** Feature request (用户描述)

**输出:**
- `docs/superpowers/specs/YYYY-MM-DD-<feature>-design.md`
- `findings.md` (updated)
- `task_plan.md` (Phase 1 section)

**Gate Requirements:**
```
✅ 设计文档已生成
✅ Constitution 合规检查通过 ← 使用 ConstitutionEnforcer
✅ 用户已 review 并确认设计
✅ 架构方案已批准
```

**Constitution 合规检查 (自动执行):**
使用 `scripts/constitution_enforcer.py` 自动检查设计是否符合 Constitution 规则：
- DESIGN-001: 单一职责
- DESIGN-002: 接口分离
- DESIGN-003: 依赖方向
- DESIGN-004: 循环依赖检查
- DESIGN-005: 公开 API 文档化

违规时必须修复才能进入 Phase 2。

**Human-in-Loop:**
- 用户必须 review `docs/superpowers/specs/YYYY-MM-DD-<feature>-design.md`
- 用户必须明确确认 "Design approved, proceed to Phase 2"

---

### Phase 2: Implementation Planning

**Skill:** `writing-plans`

**输入:**
- Phase 1 输出的 design doc
- 用户确认

**输出:**
- `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`
- `task_plan.md` (Phase 2 section, with detailed tasks)
- **File Changes Scope (定义 Phase 5 审查范围)**

**File Changes Scope:**
```
## File Changes Scope

### New Files (Phase 5 审查范围)
- src/feature/__init__.py
- src/feature/core.py
- tests/test_feature.py

### Modified Files (Phase 5 审查范围)
- src/main.py
- Cargo.toml
```

> ⚠️ **重要**: Phase 2 必须定义 `file_changes`，Phase 5 仅审查该范围内的增量变更。

**Gate Requirements:**
```
✅ Implementation plan exists
✅ Constitution 合规检查通过 ← 使用 ConstitutionEnforcer
✅ Plan includes: file changes, test strategy, verification commands
✅ File Changes Scope 明确定义 (用于 Phase 5 增量审查)
✅ User approved plan
```

**Constitution 合规检查 (自动执行):**
使用 `scripts/constitution_enforcer.py` 检查计划是否符合实现规则：
- IMPL-001: 错误处理 (Result/Option)
- IMPL-002: 无裸 await
- IMPL-003: 测试覆盖
- IMPL-004: 日志规范

**Human-in-Loop:**
- 用户必须 review implementation plan
- 用户必须选择执行方式: subagent-driven OR inline execution
- 用户必须明确确认 "Plan approved, proceed to Phase 3"

---

### Phase 3: Module Development

**Skill:** `subagent-driven-development` OR `executing-plans`

**输入:**
- Phase 2 输出的 plan doc
- 用户确认的执行方式

**输出:**
- 实现的所有代码文件
- 单元测试文件
- **actual_file_changes** (记录实际变更，用于 Phase 5 增量审查)
- `progress.md` (updated with execution log)

**Phase 5 增量审查准备:**
Phase 3 会记录实际创建/修改的文件到 `context.metadata["actual_file_changes"]`:
```python
{
    "new_files": ["src/feature/core.py", ...],
    "modified_files": ["src/main.py", ...],
    "deleted_files": [],
    "all_review_files": ["src/feature/core.py", "src/main.py", ...]
}
```

**Gate Requirements:**
```
✅ cargo build succeeds (for Rust) OR equivalent build passes
✅ All unit tests compile
✅ Code compiles without errors
✅ Constitution 合规检查通过 ← 使用 ConstitutionEnforcer
```

**Doom Loop 检测 (自动执行):**
使用 `middleware/LoopDetectionMiddleware` 检测同一文件的反复编辑：
- 警告阈值: 5 次编辑
- 硬性限制: 15 次编辑
- 超限必须选择: reconsider / reset / continue

**Human-in-Loop:**
- 每个主要 task 完成时报告进度
- build 失败时停在当前 task，等待用户指示
- 用户必须确认 "Phase 3 complete, proceed to Phase 4"

---

### Phase 4: Integration & Testing

**Skill:** `verification-before-completion` + project test framework

**输入:**
- Phase 3 输出的代码

**输出:**
- 所有集成测试通过
- `progress.md` (updated with test results)

**Gate Requirements:**
```
✅ cargo test passes (or project test command passes)
✅ Integration tests complete
✅ No critical errors
```

**Human-in-Loop:**
- 测试失败时停在当前问题，等待用户指示
- 用户必须确认 "Phase 4 complete, proceed to Phase 5"

**Note:** 如果测试因依赖问题无法运行，记录到 `progress.md` 并标记为 "blocked by environment"，需用户确认是否继续。

---

### Phase 5: Code Quality Review

**Skill:** `code-review-quality` + custom enforcement

**输入:**
- Phase 3-4 输出的代码和测试
- Phase 2 定义的 **File Changes Scope**
- Phase 3 记录的 **actual_file_changes**

**核心特性: 增量审查 (Delta Review)**

> ⚠️ **重要变更**: Phase 5 **仅审查增量变更**，不审查整个代码库。

**审查范围确定流程:**
```
Phase 2: 定义 file_changes (计划)
         ↓
Phase 3: 实现代码，track_file_changes 步骤记录 actual_file_changes
         ↓
Phase 5: 仅审查 actual_file_changes 中的文件
```

**Review Scope vs Full Codebase:**
| 方面 | 旧方式 | 新方式 (Delta Review) |
|------|--------|---------------------|
| 审查范围 | 整个代码库 | 仅 file_changes |
| 审查效率 | 低 | 高 |
| 关注点 | 全面但分散 | 聚焦增量 |

**增量审查Artifacts:**

1. **code_quality_review.md** - 增量代码质量
   - 仅分析 `actual_file_changes` 中的文件
   - 计算增量复杂度、LOC、文档覆盖率

2. **test_coverage_report.md** - 增量测试覆盖
   - 增量代码文件的测试覆盖
   - 新文件的测试存在性检查

3. **requirements_verification.md** - 需求可追溯性
   - 需求 → 实现文件的映射
   - 文件变更与需求的对应关系

4. **architecture_review.md** - 架构合规性
   - 增量文件是否符合架构规范
   - 模块依赖关系检查

**输出:**
- `docs/reviews/architecture_review.md`
- `docs/reviews/code_quality_review.md`
- `docs/reviews/test_coverage_report.md`
- `docs/reviews/requirements_verification.md`

**Gate Requirements:**
```
✅ All 4 review artifacts exist
✅ Each artifact 审查的是 file_changes 范围内的文件
✅ Each artifact contains minimal required content:
   - architecture_review.md: Module analysis, dependency graph
   - code_quality_review.md: Quality checklist, issue list
   - test_coverage_report.md: Coverage %, test list
   - requirements_verification.md: Requirements checklist
✅ ArtifactCompleteMiddleware verified ← 自动检查
```

**Artifact 完整性检查 (自动执行):**
使用 `middleware/ArtifactCompleteMiddleware` 检查 4 个制品是否存在且有效：
- 自动生成缺失的制品
- 检查必需章节是否完整
- 配置: `config/artifact_checker.yaml`

**Automatic Generation:**
如果 artifacts 不存在，**自动触发生成流程**：
1. 使用 code-review-quality skill 生成 review
2. 使用 nexus-query 分析代码结构
3. 生成所有 4 个 artifacts
4. 报告生成结果

**Human-in-Loop:**
- 用户必须 review 至少一个 artifact (建议 architecture_review.md)
- 用户必须确认 "Phase 5 complete, proceed to Phase 6"

---

### Phase 6: Memory Persistence

**Automatic Documentation**

**输入:**
- All previous phase outputs (当前特性)

**输出:**
- `PROJECT_STATE.md` (updated - 聚合所有特性状态)
- `AGENTS.md` (updated - 当前特性上下文)
- `docs/features/<feature>/task_plan.md` (finalized)
- `docs/features/<feature>/findings.md` (complete)
- `docs/features/<feature>/progress.md` (finalized)
- `docs/features/<feature>/status.toml` (updated)

**Gate Requirements:**
```
✅ PROJECT_STATE.md updated with feature summary
✅ AGENTS.md updated with current feature context
✅ docs/features/<feature>/task_plan.md finalized
✅ docs/features/<feature>/findings.md complete
✅ docs/features/<feature>/progress.md finalized
```

**Human-in-Loop:**
无 (自动执行)

---

## Automatic Enforcement in finisher

**finishing-a-development-branch skill** 现在包含 Phase 5 强制检查：

```
Step 1: Verify Tests
    ↓ (tests pass)
Step 1.5: Verify SDD Phase 5 Artifacts [NEW]
    - 检查 4 个必需 review artifacts
    - 缺失则 BLOCK 并提示完成 Phase 5
    ↓ (全部存在)
Step 1.6: Developer Confirmation [NEW]
    - 确认这是 SDD-Workflow 项目
    - 等待明确确认
    ↓ (确认后)
Step 2: Present Options (merge/PR/etc)
```

## Workflow Coordinator Script

`scripts/workflow_coordinator.py` 现在提供：

```python
class WorkflowCoordinator:
    def detect_current_phase(self) -> int
    """返回当前完成的 phase (1-6)"""

    def get_phase_status(self) -> dict
    """返回每个 phase 的状态"""

    def verify_phase_gate(self, from_phase: int) -> tuple[bool, str]
    """验证是否可以进入下一个 phase"""

    def auto_generate_review_artifacts(self) -> bool
    """自动生成缺失的 review artifacts"""

    def execute_phase(self, phase: int, context: dict) -> bool
        """执行指定 phase"""
```

## 完整使用示例

```
> sdd start custom-format-string

[Phase 1: Requirements Analysis]
✅ Brainstorming initiated
✅ Design doc generated: docs/superpowers/specs/2026-04-05-custom-format-design.md
⏳ Awaiting your review and confirmation...

> 用户 review 设计，确认 ok

[Phase 1 Gate: PASSED]
⏳ Awaiting: "Design approved, proceed to Phase 2" ...

> 用户确认

[Phase 2: Implementation Planning]
✅ Writing-plans skill activated
✅ Plan generated: docs/superpowers/plans/2026-04-05-custom-format.md
⏳ Awaiting your review and selection...

> 用户选择 subagent-driven，确认 plan

[Phase 3: Module Development]
✅ Subagent-driven mode selected
🔄 Task 1/7: Update Config module
🔄 Task 2/7: Update LogFormatter
...
✅ cargo build succeeded
⏳ Awaiting: "Phase 3 complete, proceed to Phase 4" ...

> 用户确认

[Phase 4: Integration & Testing]
🔄 Running cargo test...
⚠️ Tests blocked by getrandom dependency issue (recorded)
⏳ Awaiting: "Proceed despite test block?" ...

> 用户确认继续

[Phase 5: Code Quality Review]
🔄 Checking review artifacts...
⚠️ Missing: code_quality_review.md
🔄 Auto-generating review artifacts...
✅ All 4 review artifacts generated
⏳ Awaiting your review...

> 用户 review，确认 ok

[Phase 6: Memory Persistence]
✅ PROJECT_STATE.md updated
✅ AGENTS.md updated
✅ task_plan.md finalized
✅ All memory artifacts present

═══════════════════════════════════
SDD Workflow Complete!
Feature: custom-format-string
Status: Ready for merge
Next: sdd complete
═══════════════════════════════════
```

## Quality Gates Summary

| Phase | Gate | Blocker Condition |
|-------|------|------------------|
| 1→2 | Design Approval | 用户未确认设计 |
| 2→3 | Plan Approval | 用户未选择执行方式 |
| 3→4 | Build Success | 编译失败 |
| 4→5 | Tests Pass* | 测试失败 (*可配置跳过) |
| 5→6 | 4 Artifacts | 任一 artifact 缺失 |

## Document Architecture (v2.0)

### Core Design Principles

| Principle | Description |
|-----------|-------------|
| **Constitution-First** | Constitution is the supreme law, all design/implementation must comply |
| **Module Ownership** | Each module has clear owner and responsibility boundaries |
| **Feature Isolation** | Features developed independently, mapped to modules |
| **Knowledge-Driven** | Automatic retrieval of relevant docs during design |

### 8-Layer Directory Structure

```
project/
├── CONSTITUTION/                     # Layer 1: Supreme Law (最高准则)
│   ├── README.md                     # Constitution index
│   ├── core.md                       # Core principles (immutable)
│   ├── module-ownership.md           # Module ownership definitions
│   ├── design-rules.md              # Design rules
│   ├── implementation-rules.md      # Implementation rules
│   ├── review-rules.md              # Review rules
│   ├── communication-protocols.md   # Developer communication
│   └── decision-records/            # Architecture decisions
│
├── .nexus-map/                       # Layer 2: Architecture Knowledge (Agent auto-load)
│   ├── INDEX.md                     # Architecture index
│   ├── systems.md                   # System overview
│   ├── concept_model.json           # Concept model (machine-readable)
│   ├── module-graph.md              # Module dependency graph
│   └── module-specs/                # Module specifications
│
├── docs/
│   ├── knowledge/                    # Layer 3: Knowledge Base (auto-retrieval)
│   │   ├── rust-best-practices/    # Rust best practices
│   │   ├── design-patterns/         # Design patterns
│   │   ├── security/               # Security rules
│   │   ├── performance/            # Performance rules
│   │   └── domain/                 # Domain-specific rules
│   │
│   ├── modules/                     # Layer 4: Module Design (per-module specs)
│   │   ├── README.md               # Module index
│   │   └── [module-name]/
│   │       ├── SPEC.md             # Module specification
│   │       ├── IMPLEMENTATION.md    # Implementation details
│   │       ├── TESTS.md            # Test strategy
│   │       └── OWNERS.md           # Module owners
│   │
│   ├── features/                    # Layer 5: Feature Design (per-feature specs)
│   │   ├── README.md               # Feature index
│   │   └── [feature-name]/         # 特性独立工作空间
│   │       ├── SPEC.md             # Feature specification
│   │       ├── MODULES.md          # Module changes
│   │       ├── API-CHANGES.md      # API changes
│   │       ├── DEPENDENCIES.md     # Dependencies
│   │       ├── REVIEW.md           # Design review
│   │       ├── status.toml         # Feature status (Phase, developer)
│   │       ├── task_plan.md        # Feature task progress
│   │       ├── findings.md         # Feature findings
│   │       ├── progress.md         # Feature execution log
│   │       │
│   │       ├── specs/              # Phase 1 产出
│   │       │   └── YYYY-MM-DD-<feature>-design.md
│   │       │
│   │       ├── plans/              # Phase 2 产出
│   │       │   └── YYYY-MM-DD-<feature>.md
│   │       │
│   │       └── reviews/            # Phase 5 产出
│   │           ├── architecture_review.md
│   │           ├── code_quality_review.md
│   │           ├── test_coverage_report.md
│   │           └── requirements_verification.md
│   │
│   └── collaboration/               # Layer 6: Team Collaboration
│       ├── feature-matrix.md        # Feature-Module matrix
│       ├── module-owners.md        # Module owners list
│       └── decision-log.md         # Decision log
│
├── PROJECT_STATE.md                  # Project state (all features aggregation)
├── AGENTS.md                        # AI persistence (current feature context)
└── .nexus-map/                      # Architecture knowledge graph
```

### Constitution Mechanism

#### Constitution Files

| File | Purpose | Mandatory |
|------|---------|-----------|
| `core.md` | Core principles (immutable) | ✅ |
| `module-ownership.md` | Module ownership definitions | ✅ |
| `design-rules.md` | Design phase rules | ✅ |
| `implementation-rules.md` | Implementation rules | ✅ |
| `review-rules.md` | Review rules | ✅ |

#### Constitution Pipeline (Phase 1-6)

```
┌─────────────────────────────────────────────────────────────┐
│                    Constitution Compliance Check               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Phase 1 (brainstorming)                                    │
│      ↓                                                      │
│  Auto-check: design vs CONSTITUTION/design-rules.md          │
│      ↓ Violation?                                            │
│      STOP: Design violates constitution                       │
│                                                              │
│  Phase 2 (writing-plans)                                    │
│      ↓                                                      │
│  Auto-check: plan vs CONSTITUTION/implementation-rules.md     │
│      ↓ Violation?                                            │
│      STOP: Plan violates constitution                         │
│                                                              │
│  Phase 3 (executing-plans)                                  │
│      ↓                                                      │
│  Auto-check: code vs relevant constitution rules              │
│      ↓ Violation?                                            │
│      BLOCK: Must fix before continue                          │
│                                                              │
│  Phase 5 (code-review-quality)                               │
│      ↓                                                      │
│  Review includes: Constitution compliance                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### Constitution Example (core.md)

```markdown
# Core Principles

## 1. Safety First
- All user input must be validated
- No sensitive info in logs
- Critical operations require audit logging

## 2. Modularity
- Modules communicate via explicit interfaces
- No direct internal state access
- Single responsibility per module

## 3. Testability
- All public APIs must have tests
- No untestable code paths
- Tests must run independently

## 4. Backward Compatibility
- No breaking changes to public APIs
- No breaking changes to config formats
- No breaking changes to CLI interfaces

## 5. Performance
- Logging must not block main thread
- Large file operations must be async
- Memory usage must have upper bounds
```

### Knowledge Retrieval Mechanism

#### Retrieval Triggers

| Phase | Trigger | Retrieved Content |
|-------|---------|------------------|
| 1 | Design starts | Module specs, design patterns, domain rules |
| 1 | Interface defined | API rules, dependency module specs |
| 2 | Plan writing | Implementation rules, best practices |
| 3 | Code writing | Ownership rules, concurrency patterns |
| 5 | Review | Review rules, quality standards |

#### Automatic Retrieval Process

```
User starts Phase 1: "Add custom format string support"

Auto-retrieval:
1. Knowledge Base:
   - docs/knowledge/domain/logging-best-practices.md
   - docs/knowledge/design-patterns/layered-architecture.md

2. Module Specs:
   - docs/modules/logger/SPEC.md
   - docs/modules/config/SPEC.md

3. Constitution:
   - CONSTITUTION/design-rules.md

4. Nexus Map:
   - .nexus-map/module-graph.md

Output: "Based on retrieval:
- Logger module uses Arc<Mutex<>>, complies with Constitution §2
- Recommend LogFormatter pattern, consistent with layered architecture
- See docs/knowledge/rust-best-practices/ownership.md §3.2"
```

### Module Ownership Mechanism

#### Module Specification (docs/modules/[name]/SPEC.md)

```markdown
# [Module] Module Specification

## Basic Info
- **Module**: [name]
- **Owner**: @[username]
- **Created**: [date]
- **Version**: [version]

## Responsibilities
- [List of responsibilities]

## Public APIs
```rust
[Public interfaces]
```

## Sub-modules
| Sub-module | Responsibility | File |
|------------|---------------|------|
| [name] | [desc] | [file] |

## Dependencies
| Module | Reason |
|--------|--------|
| [name] | [reason] |

## Dependents
| Module | Usage |
|--------|-------|
| [name] | [usage] |
```

### Feature-Module Matrix

#### docs/collaboration/feature-matrix.md

```markdown
# Feature-Module Matrix

## Legend
- **✓**: Module is primary implementation
- **△**: Module affected but not primary
- **-**: Module not affected

| Feature | logger | config | cli | core |
|---------|--------|--------|-----|------|
| custom-format | ✓ | ✓ | - | - |
| async-logging | ✓ | - | - | △ |
| compression | ✓ | - | - | - |
```

### Agent Context Loading Order

**When Agent starts, auto-load in priority order:**

```
1. CONSTITUTION/core.md                    # Must (core principles)
2. .nexus-map/INDEX.md                   # Architecture overview
3. docs/modules/[relevant]/SPEC.md        # Relevant module specs
4. docs/knowledge/[relevant]/*.md         # Relevant knowledge
5. PROJECT_STATE.md                       # Project state
6. AGENTS.md                             # AI persistence
```

**ContextLoader (自动上下文加载):**

使用 `scripts/context_loader.py` 自动加载项目上下文：

```
sdd start <feature-name>
         ↓
ContextLoader 启动
         ↓
1. 确定当前任务涉及的模块 (feature-matrix / nexus-query)
2. 加载 Constitution (core.md + 相关规则)
3. 加载相关模块规格 (docs/modules/<name>/SPEC.md)
4. 加载知识库 (docs/knowledge/[relevant]/*)
5. 加载项目状态 (PROJECT_STATE.md, task_plan.md)
         ↓
注入到 agent 上下文
```

**Agent should be able to answer:**
- What is the core architecture?
- What are Logger module's responsibilities and interfaces?
- What rules must I follow when designing?
- What is the current project state?

---

## Red Flags (Never Skip)

- ❌ **Never** skip Phase 1 design review
- ❌ **Never** proceed without user confirmation at each gate
- ❌ **Never** skip Constitution 合规检查 (ConstitutionEnforcer)
- ❌ **Never** ignore LoopDetection 警告 (LoopDetectionMiddleware)
- ❌ **Never** mark Phase 5 complete without all 4 artifacts
- ❌ **Never** mark Phase 5 complete without ArtifactCompleteMiddleware verification
- ❌ **Never** claim implementation complete without build passing
- ❌ **Never** skip memory persistence (Phase 6)

## 新组件集成

### Middleware

| Middleware | 功能 | 配置 |
|------------|------|------|
| `PhaseGateMiddleware` | Phase Gate Constitution 检查 | `config/constitution_enforcer.yaml` |
| `LoopDetectionMiddleware` | Doom Loop 检测 | `config/loop_detection.yaml` |
| `ArtifactCompleteMiddleware` | Phase 5 制品完整性检查 | `config/artifact_checker.yaml` |

### Scripts

| Script | 功能 |
|--------|------|
| `scripts/constitution_enforcer.py` | 自动检查设计/计划/代码是否符合 Constitution |
| `scripts/artifact_checker.py` | 检查 4 个审查制品是否完整 |
| `scripts/context_loader.py` | 自动加载项目上下文 |
| `scripts/trace_collector.py` | 收集 session 执行轨迹 |

### Trace Analysis

使用 `scripts/trace_collector.py` 收集执行轨迹：

```
sdd session 结束
         ↓
TraceCollector 保存轨迹
         ↓
sdd analyze (手动触发)
         ↓
分析模式：
- Gate Skip Pattern: phase gate 被跳过的频率
- Doom Loop Pattern: 同一文件反复编辑
- Phase Skip Pattern: phase 直接跳过
- Violation Cluster Pattern: 规则违反聚集
         ↓
生成改进建议
```

## Integration with Other Skills

### Complete Skill Invocation Map

| Skill | Phase | When Used | Purpose |
|-------|-------|-----------|---------|
| **using-superpowers** | 0 (Init) | Before any workflow | Load all required skills |
| **nexus-mapper** | 0 (Init) | Project context | Generate .nexus-map/ for architecture understanding |
| **brainstorming** | 1 | Requirements gathering | Explore requirements, propose design |
| **planning-with-files** | 1, 2, 6 | Memory artifacts | Create/update task_plan.md, findings.md, progress.md |
| **rust-best-practices** | 1, 3 | Rust projects | Language-specific guidance for Rust |
| **nexus-query** | 1, 5 | Code analysis | Analyze code structure for design and review |
| **writing-plans** | 2 | Plan creation | Generate implementation plan from design |
| **multi-agent-orchestration** | 3 | Complex projects | Coordinate parallel agent teams (optional) |
| **subagent-driven-development** | 3 | Execution (mode A) | Parallel task execution with review |
| **executing-plans** | 3 | Execution (mode B) | Sequential execution with checkpoints |
| **test-driven-development** | 3 | Test strategy | Define test approach for each module |
| **using-git-worktrees** | 3 | Isolation | Create isolated branch for development |
| **systematic-debugging** | 4 | Build/Test failure | Debug issues before proceeding |
| **verification-before-completion** | 4 | Test verification | Verify build and tests pass |
| **code-review-quality** | 5 | Review generation | Generate code quality review artifacts |
| **requesting-code-review** | 5 | External review | Request human code review |
| **finishing-a-development-branch** | 6+ | Completion | Present merge options, execute choice |

### Phase-by-Phase Skill Flow

```
PHASE 0: Initialization (using-superpowers)
├── Load required skills
├── Detect project type (Rust/Node/etc)
├── Run nexus-mapper for architecture context
└── Prepare memory artifacts structure

PHASE 1: Requirements Analysis (brainstorming)
├── Load nexus-query for codebase understanding
├── If Rust: load rust-best-practices
├── brainstorming: explore requirements
├── planning-with-files: initialize task_plan.md Phase 1
└── [GATE: User confirms "Design approved"]

PHASE 2: Implementation Planning (writing-plans)
├── brainstorming output (design doc) as input
├── writing-plans: create detailed plan
├── planning-with-files: update task_plan.md Phase 2
└── [GATE: User confirms "Plan approved", selects execution mode]

PHASE 3: Module Development (subagent-driven OR executing-plans)
├── If subagent-driven:
│   ├── using-git-worktrees: create isolated branch
│   ├── multi-agent-orchestration: coordinate parallel agents
│   ├── subagent-driven-development: dispatch per-task
│   └── planning-with-files: update progress.md per task
├── If executing-plans:
│   ├── using-git-worktrees: create isolated branch
│   ├── executing-plans: sequential execution
│   ├── test-driven-development: define test strategy
│   ├── rust-best-practices: Rust-specific implementation
│   ├── planning-with-files: update progress.md per task
│   └── systematic-debugging: if build fails
└── [GATE: Build succeeds]

PHASE 4: Integration & Testing (verification-before-completion)
├── verification-before-completion: run full test suite
├── systematic-debugging: if tests fail
├── planning-with-files: update progress.md with results
└── [GATE: Tests pass or user approves to skip]

PHASE 5: Code Quality Review (code-review-quality)
├── code-review-quality: generate 4 review artifacts
├── nexus-query: analyze code structure
├── planning-with-files: update task_plan.md Phase 5
├── requesting-code-review: optional external review
└── [GATE: All 4 artifacts exist, user confirms]

PHASE 6: Memory Persistence (planning-with-files)
├── planning-with-files: finalize all memory artifacts
├── Update PROJECT_STATE.md
├── Update AGENTS.md
├── Finalize progress.md
└── [AUTO-COMPLETE]

POST-PHASE 6: (finishing-a-development-branch)
├── finishing-a-development-branch: present 4 options
├── Step 1.5: Verify review artifacts (from Phase 5)
├── Step 1.6: User confirmation
├── Step 1.7: Verify memory artifacts (from Phase 6)
└── Execute selected option
```

### When to Use multi-agent-orchestration

**Use multi-agent-orchestration in Phase 3 when:**

1. **Complex Project with Independent Modules**
   - Multiple modules can be developed in parallel
   - Example: Logger (file_rotator, concurrent_writer, log_formatter) can be built simultaneously

2. **Domain-Specific Expertise Needed**
   - Different parts need different specialized knowledge
   - Example: Security review + Performance optimization + Core logic

3. **Parallel Task Execution Beneficial**
   - Tasks have no dependencies on each other
   - Want to reduce total development time

**Decision Flow:**

```
Is project complex (>5 tasks) AND tasks are independent?
├── YES → Use multi-agent-orchestration with subagent-driven
└── NO  → Use sequential executing-plans
```

### Conflict Resolution in Multi-Agent Development

**Coordinator Agent Pattern:**

When using parallel agents, a **Coordinator Agent** manages task distribution and conflict resolution:

```
┌─────────────────────────────────────────────────────────────┐
│                    Coordinator Agent                         │
├─────────────────────────────────────────────────────────────┤
│  1. Task Assignment: Assign non-overlapping tasks          │
│  2. Conflict Detection: Monitor for file access conflicts  │
│  3. Conflict Resolution: Merge or reassign tasks           │
│  4. Integration: Combine results after completion          │
└─────────────────────────────────────────────────────────────┘
```

**Conflict Types and Resolution:**

| Conflict Type | Detection | Resolution |
|--------------|-----------|------------|
| **Same file modified** | Coordinator tracks file ownership | Sequential edits to same file |
| **Interface change** | Review by Coordinator | Re-coordinate if interface changes |
| **Dependency conflict** | Build verification | Coordinator reassigns tasks |
| **Git merge conflict** | Git merge failure | Coordinator resolves or re-assigns |

**Conflict Prevention Rules:**

1. **Strict Module Boundaries**
   - Each agent owns specific files/modules
   - No agent can modify another agent's files
   - Shared interfaces defined upfront

2. **Interface Freezing**
   - Interfaces (traits, structs) defined in Phase 1
   - No interface changes during Phase 3 without Coordinator approval
   - Breaking changes trigger re-planning

3. **Task Dependency Declaration**
   - Each task declares which files it will modify
   - Coordinator prevents overlapping assignments
   - Dependencies made explicit in plan

**Coordinator Agent Responsibilities:**

```
1. Before Parallel Execution:
   - Parse plan, extract tasks
   - Identify file ownership per task
   - Detect potential conflicts
   - Assign tasks to agents with no overlap

2. During Parallel Execution:
   - Monitor agent progress
   - Detect conflicts (file overlap, interface changes)
   - Resolve: either re-assign or sequence conflicting tasks
   - Aggregate completed work

3. After Parallel Execution:
   - Verify all tasks completed
   - Run integration tests
   - Handle any remaining conflicts
   - Report final status
```

**Example: Rotating Logger with Coordinator**

```
Phase 3: Module Development (Multi-Agent with Coordinator)

[Coordinator Agent]
├── Task 1: FileRotator → Agent 1 (owns: file_rotator.rs)
├── Task 2: ConcurrentWriter → Agent 2 (owns: concurrent_writer.rs)
├── Task 3: LogFormatter → Agent 3 (owns: log_formatter.rs)
├── Task 4: Logger Integration → Agent 4 (owns: logger/mod.rs)
└── Task 5: Config Module → Agent 5 (owns: config.rs)

[Conflict Prevention]
- FileRotator interface: fixed at Phase 1
- ConcurrentWriter interface: fixed at Phase 1
- LogFormatter interface: fixed at Phase 1
- No agent can modify another's files

[Conflict Detection]
- If Agent 4 needs to change FileRotator interface:
  → Coordinator detects conflict
  → Re-assigns to Agent 1 (sequential)
  → Agent 4 waits for updated interface

[Conflict Resolution]
- Git merge conflict detected
- Coordinator: "Conflict in config.rs, Agent 5 owns it - sequential edit"
```

**Integration with subagent-driven:**

multi-agent-orchestration coordinates multiple subagent-driven agents:
- Coordinator parses plan, assigns non-overlapping tasks
- Each subagent executes its task sequentially (no parallel within task)
- Coordinator handles cross-agent conflicts
- Final integration by dedicated agent or Coordinator

**Example Flow:**

```
[Coordinator]
1. Parse plan: 5 tasks identified
2. Assign tasks:
   - Agent A: Task 1 (FileRotator)
   - Agent B: Task 2 (ConcurrentWriter)
   - Agent C: Task 3 (LogFormatter)
   - Agent D: Task 4 + 5 (Integration + Config)
3. Execute in parallel:
   - Agent A → Task 1 complete
   - Agent B → Task 2 complete
   - Agent C → Task 3 complete
   - Agent D → Task 4 + 5 complete
4. Detect: No file conflicts (all different files)
5. Integration: Combine results
6. Final verification: cargo build, cargo test
```

**Example: Rotating Logger with Multi-Agent**

```
Phase 3: Module Development
├── Agent 1 (FileRotator specialist)
│   └── Task: Implement file rotation logic
├── Agent 2 (ConcurrentWriter specialist)
│   └── Task: Implement thread-safe writer
├── Agent 3 (LogFormatter specialist)
│   └── Task: Implement formatting
└── Agent 4 (Integration specialist)
    └── Task: Integrate modules, write tests
```

**Without Multi-Agent (simpler projects):**

```
Phase 3: Module Development (sequential)
├── Task 1: Implement Config module
├── Task 2: Implement LogFormatter
├── Task 3: Implement FileRotator
├── Task 4: Implement ConcurrentWriter
└── Task 5: Integrate and test
```

### Skill Loading Order

**At workflow start, load skills in this order:**

1. `using-superpowers` - Entry point
2. `nexus-mapper` - For architecture discovery
3. `brainstorming` - Phase 1
4. `writing-plans` - Phase 2
5. `planning-with-files` - Throughout (memory artifacts)
6. `subagent-driven-development` OR `executing-plans` - Phase 3
7. `test-driven-development` - Phase 3 (test strategy)
8. `rust-best-practices` - Phase 3 (Rust projects)
9. `using-git-worktrees` - Phase 3 (isolation)
10. `systematic-debugging` - Phase 4 (if needed)
11. `verification-before-completion` - Phase 4
12. `code-review-quality` - Phase 5
13. `requesting-code-review` - Phase 5 (optional)
14. `finishing-a-development-branch` - Post-Phase 6
15. `nexus-query` - Throughout (code analysis)

### Why Some Skills Don't Appear Directly

**planning-with-files:**
- Used throughout the workflow to manage memory artifacts
- Not a "phase" skill but a supporting skill
- Called when creating/updating task_plan.md, findings.md, progress.md

**rust-best-practices:**
- Auto-loaded for Rust projects
- Provides guidance during brainstorming (Phase 1) and implementation (Phase 3)
- Not a separate phase, integrated into other skills

**nexus-mapper/nexus-query:**
- Used for codebase understanding
- nexus-mapper runs at initialization to generate .nexus-map/
- nexus-query used during design and review phases

**systematic-debugging:**
- Only called if build or test fails
- Breaks are built into Phase 3 and Phase 4 gates

### Example: Rust Project Full Flow

```
> sdd start async-logger

[Skill Loading]
✅ using-superpowers
✅ nexus-mapper (generating .nexus-map/...)
✅ rust-best-practices (Rust project detected)

[Phase 1: Requirements]
✅ brainstorming loaded
🔍 Exploring requirements with nexus-query context...
📝 Design doc: docs/superpowers/specs/2026-04-06-async-logger-design.md
✅ rust-best-practices applied to design
✅ task_plan.md initialized

[GATE] User: "Design approved, proceed to Phase 2"

[Phase 2: Planning]
✅ writing-plans loaded
📋 Plan: docs/superpowers/plans/2026-04-06-async-logger.md
✅ planning-with-files: task_plan.md Phase 2 complete

[GATE] User: "subagent-driven, Plan approved, proceed to Phase 3"

[Phase 3: Development]
✅ using-git-worktrees: created branch feature/async-logger
✅ subagent-driven-development loaded
✅ test-driven-development: test strategy defined
✅ rust-best-practices: async Rust guidance active
🔄 Task 1/5: Implement async writer
...
✅ cargo build succeeded

[GATE] User: "Phase 3 complete, proceed to Phase 4"

[Phase 4: Integration]
✅ verification-before-completion: running tests...
✅ cargo test passed (after rand fix)

[GATE] User: "Phase 4 complete, proceed to Phase 5"

[Phase 5: Review]
✅ code-review-quality: generating artifacts...
✅ nexus-query: analyzing code structure...
📄 4 review artifacts generated
✅ planning-with-files: task_plan.md Phase 5 complete

[GATE] User: "Phase 5 complete, proceed to Phase 6"

[Phase 6: Memory]
✅ planning-with-files: finalizing artifacts...
✅ PROJECT_STATE.md updated
✅ AGENTS.md updated

✅ SDD Workflow Complete!

[finishing-a-development-branch]
✅ Step 1: Tests passed
✅ Step 1.5: Review artifacts verified (4/4)
✅ Step 1.6: User confirmed SDD project
✅ Step 1.7: Memory artifacts verified (5/5)
... (present 4 merge options)
```

---

*This SDD-Workflow ensures complete, traceable development with mandatory quality gates.*