---
name: sdd-workflow
description: "Software Development Director Workflow - Complete end-to-end development workflow for large and standard features. Use this skill whenever you need to develop a software feature, fix a bug, or refactor code. This skill automatically executes all phases based on feature complexity: Large Features (Scene Analysis → Understanding → Phase 1 with 4 sub-stages → Phase 2-6), Standard Features (Understanding → Phase 1-6). Developer confirmation is required at each phase transition. v2.1.1 adds Module Implementation Deep Dive for complete implementation logic design, peripheral module analysis, and change impact assessment."
version: "2.1.1"
author: "opencode team"
categories:
  - workflow
  - multi-agent
  - software-development
  - architecture-aware
  - scene-first (v2.1)
  - bounded-context (v2.1)
  - implementation-deep-dive (v2.1.1)
enforcement:
  phase_gate: true
  review_artifacts_required: true
  memory_artifacts_required: true
  scene_analysis_required: true (large features)
  implementation_deep_dive_required: true (large features)
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

# SDD-Workflow v2.1.1

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

SDD-Workflow 提供 **6+1 阶段强制执行流程**，每个阶段有明确的输入、输出、验证点和强制确认：

### v2.1 Large Feature Enhanced Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SDD 6+1 Phase Workflow (v2.1)                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  检测特性复杂度                                                       │
│      ↓                                                               │
│  复杂度 >= HIGH? (任务数>5 或 模块>3)                                  │
│      ↓ YES                  ↓ NO                                     │
│  Scene Analysis Phase    → 直接 Understanding                        │
│      ↓                                                               │
│         [GATE: Scene Analysis Approved]                              │
│      ↓                                                               │
│ Understanding 阶段 (前置强制阶段)                                      │
│      ↓                                                               │
│         [GATE: Anti-Superficiality Check]                            │
│      ↓                                                               │
│ Phase 1 │ Requirements Analysis & Design                             │
│         │ ├── Interface Definitions (现有)                           │
│         │ ├── Module Decomposition (新增) ← 强化                     │
│         │ └── Module Internal Architecture (新增) ← 深化             │
│    ↓    │         [GATE: Design + Decomposition Approved]            │
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

### Standard Workflow (v2.0)

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

### 必需 Memory Artifacts (Phase 6 强制输出) - OPTIMIZED

#### 项目级别（聚合视图）

| 文件 | 描述 | 强制 |
|------|------|------|
| `PROJECT_STATE.md` | 所有特性状态聚合 | ✅ |
| `AGENTS.md` | 项目级 AI 持久化指令（包含变更清单） | ✅ |

#### 特性级别（每个特性独立）- OPTIMIZED

| 文件 | 描述 | 强制 |
|------|------|------|
| `docs/features/<feature>/findings.md` | 统一决策记录（Phase 0-5） | ✅ |
| `docs/features/<feature>/design-doc.md` | 详细设计（接口定义、数据流） | ✅ |
| `docs/features/<feature>/task_plan.md` | 任务进度（Phase 1-6） | ✅ |
| `docs/features/<feature>/.sdd/conversation_memory.json` | 决策记忆（跨会话） | ✅ |

### 必需 Review Artifacts (Phase 5 强制输出) - OPTIMIZED

| 文件 | 描述 | 强制 |
|------|------|------|
| `docs/features/<feature>/reviews/architecture_review.md` | 架构审查 + 需求验证（合并） | ✅ |
| `docs/features/<feature>/reviews/code_quality_review.md` | 代码质量 + 测试覆盖（合并） | ✅ |

### 已删除的冗余文档（优化后的变化）

| 删除的文档 | 原因 | 合并到 |
|-----------|------|--------|
| ❌ `findings.md Phase 0` | 冗余 | `findings.md` Phase 0 section |
| ❌ `think_before_coding.md` | 冗余 | `findings.md` Phase 0 section |
| ❌ `plan-doc.md` | 冗余 | `findings.md` + `task_plan.md` Phase 2 section |
| ❌ `findings.md (relevant section)` | 过度详细 | `findings.md` (仅关键事件) |
| ❌ `change_summary.md` | 冗余 | `AGENTS.md` Section 4 |
| ❌ `code_quality_review.md (merged)` | 冗余 | `code_quality_review.md` Testing section |
| ❌ `architecture_review.md (merged)` | 冗余 | `architecture_review.md` Requirements section |
| ❌ `status.toml` | 冗余 | 信息在 `task_plan.md` |

**文档数量变化：17 → 7 (减少 59%)**

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
3. 创建特性级内存制品: task_plan.md, findings.md, design-doc.md
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
- `docs/features/<feature>/.sdd/checkpoint.json` - 特性状态
- `docs/features/<feature>/task_plan.md` - 特性任务进度
- `docs/features/<feature>/findings.md` - 特性决策记录
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

### Scene Analysis Phase (前置阶段 - 大型特性专用)

> ⚠️ **重要**: Scene Analysis 是大型特性的**前置阶段**。仅当特性复杂度评估 >= HIGH 时触发。
> 
> **复杂度评估标准**:
> - 任务数 > 5
> - 涉及模块 > 3
> - 需要跨团队协作
> - 业务场景复杂（多个用户旅程）

**Capability:** `scene-analysis`

**目标:** 在技术设计之前，进行业务场景分析，避免"技术视角主导，忽略业务需求"。

**触发时机:** `sdd start <feature>` 时自动检测复杂度，高复杂度特性触发此阶段。

**输入:**
- Feature request (用户描述)
- 项目业务背景文档
- 用户/领域专家访谈记录（可选）

**输出:**
- `docs/features/<feature>/scene_analysis.md` - 业务场景分析文档

**执行流程:**

```
Step 1: 业务背景收集
    Read docs/knowledge/domain/ (领域知识)
    Read PROJECT_STATE.md (项目状态)
    可选: 用户访谈记录
    
Step 2: 用户旅程映射
    绘制核心用户旅程
    标注每个旅程阶段的系统响应
    
Step 3: 用例提取
    从旅程中提取具体用例
    标注频率、复杂度
    
Step 4: 优先级排序
    使用 MoSCoW 方法排序
    P0 (Must), P1 (Should), P2 (Could), P3 (Won't)
    
Step 5: 模块映射
    分析每个场景需要哪些模块
    标注集成点
    
Step 6: 边缘场景分析
    分析错误场景、异常流程
    
Step 7: NFR 标注
    为每个场景标注非功能性需求
    
Step 8: 依赖分析
    绘制场景依赖图
    确定实现顺序
    
Step 9: 风险评估
    识别高风险场景
    提出缓解措施
    
Step 10: Write scene_analysis.md
```

**scene_analysis.md 结构:**

```markdown
# Scene Analysis: <feature-name>

## 1. Business Context
- 业务目标
- 用户群体
- 核心价值主张

## 2. User Journey Mapping
| Journey | Stage | User Action | System Response | Module Involved |
|---------|-------|-------------|-----------------|-----------------|
| [旅程名] | [阶段] | [用户行为] | [系统响应] | [涉及模块] |

## 3. Core Use Cases (Top 10)
| Use Case ID | Description | Frequency | Complexity | Priority |
|-------------|-------------|-----------|------------|----------|
| UC-001 | [用例描述] | [频率] | [复杂度] | P0/P1/P2 |

## 4. Scene Priority Matrix
### P0 Scenes (MVP - 必须实现)
- [场景列表]

### P1 Scenes (核心扩展 - 应该实现)
- [场景列表]

### P2 Scenes (边缘场景 - 可以延后)
- [场景列表]

## 5. Scene-to-Module Mapping
| Scene ID | Primary Module | Secondary Modules | Integration Points |
|----------|----------------|-------------------|-------------------|
| UC-001 | [主模块] | [辅助模块] | [集成点] |

## 6. Edge Cases & Error Scenarios
| Error Type | Trigger | Handling Strategy | Affected Modules |
|------------|---------|-------------------|-----------------|
| [错误类型] | [触发条件] | [处理策略] | [影响模块] |

## 7. Non-Functional Requirements per Scene
| Scene ID | Performance | Security | Reliability |
|----------|-------------|----------|-------------|
| UC-001 | [性能需求] | [安全需求] | [可靠性需求] |

## 8. Scene Dependencies
- 场景依赖图（哪些场景依赖其他场景）
- 实现顺序建议

## 9. Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [风险] | [概率] | [影响] | [缓解措施] |
```

**Gate Requirements:**
```
✅ scene_analysis.md 存在且包含所有必需章节
✅ P0 场景数量 >= 3 (大型特性至少有核心场景)
✅ 场景-模块映射覆盖所有 P0 场景
✅ 用户确认场景分析足够全面
```

**Human-in-Loop:**
- 用户必须 review scene_analysis.md
- 用户必须明确确认 "Scene analysis approved, proceed to Understanding Phase"
- 如果用户反馈"场景分析不够全面"，AI 必须回到 Step 2 重新分析

---

### Understanding 阶段 (前置强制阶段)

> ⚠️ **重要**: Understanding 是进入 Phase 1 (Design) 的**前置强制阶段**。未完成深度研究的方案设计将被视为不合格。

**Capability:** `understanding`

**目标:** 在设计之前，深入理解现有系统和相关原理，避免浅显分析直接给出方案。

**触发时机:** `sdd start <feature>` 时自动触发，在 Phase 1 之前执行。

**输入:**
- Feature request (用户描述)
- 现有代码库
- 相关技术文档

**输出:**
- `docs/features/<feature>/findings.md Phase 0` - 深度研究报告

**研究范围:**

| 维度 | 内容 | 深度要求 |
|------|------|---------|
| 代码库分析 | 现有模块、相关文件、架构模式 | 必须分析现有代码，而非假设 |
| 技术原理 | 核心原理、关键概念 | 必须引用权威来源 |
| 约束条件 | 性能、安全、兼容性限制 | 必须识别所有约束 |
| 类似方案 | 现有方案对比、优缺点 | 必须分析 2+ 种方案 |

**Anti-Superficiality 检查 (自动执行):**

研究报告必须通过以下检查，否则不能进入 Phase 1：

| 检查项 | 要求 |
|--------|------|
| 代码库分析 | 识别到相关文件 |
| 技术原理 | 包含具体原理，非框架性描述 |
| 约束条件 | 识别到 2+ 个约束 |
| 类似方案 | 分析了 2+ 种方案 |

**Think Before Coding (基于 Karpathy 原则):**

> 基于 Andrej Karpathy 的观察：AI 会错误假设但不检查、不管理自己的困惑、不主动澄清问题。

在 Understanding 阶段，AI 必须完成以下思考：

| 原则 | 说明 | 产出 |
|------|------|------|
| **State assumptions explicitly** | 显式声明所有假设 | `assumptions` 列表 |
| **Present multiple interpretations** | 呈现 2-3 个方案并对比 | `alternatives` 表格 |
| **Push back when warranted** | 必要时主动反驳/提问 | `pushback` 检查 |
| **Stop when confused** | 困惑时停下来提问 | `concerns` 问题列表 |

**Think Before Coding 检查点:**

```
- [ ] 我理解用户真正想要的是什么吗？
- [ ] 我是否声明了所有关键假设？
- [ ] 我是否呈现了多个方案并给出了推荐？
- [ ] 我是否识别了所有潜在问题？
- [ ] 我是否定义了明确的成功标准？
- [ ] 我是否需要向用户提问以澄清问题？
```

**Concrete Execution Requirements (具体执行要求):**

> 🔴 **以下每一项都是强制要求**。如果任何一项未满足，Understanding 阶段视为未通过。

#### 1. 代码库分析 — 必须具体到文件和模块

禁止输出：`"项目使用模块化架构"` 这种空泛描述。

必须输出：
```
## 代码库分析

### 项目类型识别
- 语言/框架: [具体版本]
- 构建系统: [Cargo/npm/pip/etc]
- 项目结构: [列出顶层目录及其用途]

### 相关文件清单 (至少 5 个)
| 文件 | 用途 | 与本特性关系 |
|------|------|------------|
| src/foo/bar.rs | Foo 模块核心逻辑 | 需要修改 Bar trait |
| ... | ... | ... |

### 关键接口/Trait (如果存在)
列出相关模块的公开 API，标注哪些需要修改、哪些不能动。

### 依赖图
描述相关模块之间的依赖关系。如有循环依赖必须标注。
```

#### 2. 技术原理 — 必须引用具体来源

禁止输出：`"根据官方文档..."` 而不引用具体章节。

必须输出：
```
## 技术原理

### 核心技术栈
- [技术名称]: [版本], 用于 [具体用途]

### 关键概念
对于每个概念，必须包含：
- 概念名称
- 为什么与本特性相关
- 来源引用 (URL / 文档章节 / spec 编号)

### 参考资料
| 来源 | 类型 | 相关内容 |
|------|------|---------|
| [具体URL或文档章节] | 官方文档 | [说明相关段落] |
```

#### 3. 约束条件 — 至少识别 3 个

必须覆盖以下维度中的至少 3 个：
- 性能约束 (延迟、吞吐量、内存上限)
- 安全约束 (输入验证、权限、敏感数据)
- 兼容性约束 (API 向后兼容、平台兼容)
- 资源约束 (文件大小、并发数、连接数)
- 规范约束 (编码规范、架构规范、Constitution)

#### 4. 方案对比 — 至少 2 个方案，含具体优缺点

禁止输出：`"方案 A 优点：快速；缺点：不完整"` 这种泛泛之谈。

必须输出：
```
| 维度 | 方案 A (最小化) | 方案 B (标准) | 方案 C (扩展) |
|------|----------------|--------------|--------------|
| 实现复杂度 | 低 (约 X 行代码) | 中 | 高 |
| 性能影响 | [具体数据或评估] | [具体数据或评估] | [具体数据或评估] |
| 维护成本 | [具体评估] | [具体评估] | [具体评估] |
| 测试覆盖难度 | [具体评估] | [具体评估] | [具体评估] |
| 推荐场景 | [说明] | [说明] | [说明] |
```

**Red Flags (红旗 — 以下任一情况出现则研究不合格):**

- 🔴 研究报告中未列出具体文件名（只有模块名没有文件名）
- 🔴 "技术原理"章节内容少于 200 字
- 🔴 约束条件少于 2 个（如果是简单特性，必须说明"为什么约束少"）
- 🔴 没有引用任何外部来源（URL 或文档章节）
- 🔴 方案对比只有 1 个方案
- 🔴 方案对比中每个方案优缺点各不足 2 条
- 🔴 "技术原理"中出现"需要研究 X"这种占位文本

**Gate Requirements:**
```
✅ findings.md Phase 0 存在且非空
✅ 代码库分析包含 5+ 个具体文件
✅ 技术原理引用了 2+ 个外部来源
✅ 约束条件 2+ 个
✅ 方案对比 2+ 个方案，每个含 3+ 条具体优缺点
✅ Anti-Superficiality 检查全部通过
✅ 用户确认研究足够深入
```

**Human-in-Loop:**
- 用户必须阅读 findings.md Phase 0
- 用户必须确认"研究足够深入，可以进入设计阶段"
- 如果用户反馈"分析不够深入"，AI 必须回到 Understanding 阶段重新研究

---

### Phase 1: Requirements Analysis & Architecture Design

**Skill:** `brainstorming`

**前置要求:** Understanding 阶段必须通过

**输入:** Feature request (用户描述) + findings.md Phase 0

**输出:**
- `docs/superpowers/specs/YYYY-MM-DD-<feature>-design.md`
- `findings.md` (updated)
- `task_plan.md` (Phase 1 section)

**Gate Requirements:**
```
✅ Understanding 阶段已通过
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

#### Phase 1 LLM Action Sequence

> 🔧 **在此阶段，LLM 必须按以下步骤逐一执行:**
> 
> **注意**: 大型特性（复杂度 >= HIGH）需要执行所有 Step（1-21），标准特性仅执行 Step 1-5。

```
Step 1: 读取研究报告
    Read docs/features/<feature>/findings.md Phase 0
    Read PROJECT_STATE.md (了解项目整体状态)
    Read CONSTITUTION/design-rules.md
    Read scene_analysis.md (如果存在，大型特性)

Step 2: 读取相关代码
    对 findings.md Phase 0 中识别的每个关键文件:
        Read <file_path> (至少读取前 200 行了解接口和结构)
    使用 Grep 搜索相关 trait/interface/class 定义

Step 3: 审查设计文档模板
    Read docs/features/<feature>/specs/YYYY-MM-DD-<feature>-design.md
    ⚠️ 这是 Python 生成的详细模板，包含：
    - Interface Definitions（API 签名模板）
    - Data Flow（流程图模板）
    - Error Handling Strategy（错误处理策略模板）
    - Integration Points（集成点模板）
    
    ✅ LLM 需要填充具体内容：
    - 补充 API 参数名、返回值类型、异常类型
    - 补充数据流中的具体组件
    - 补充错误处理的具体策略
    - 补充集成点的具体方法

Step 4: Constitution 合规自查
    检查设计是否满足:
    - DESIGN-001 单一职责
    - DESIGN-003 依赖方向正确
    - DESIGN-004 无循环依赖

Step 5: 更新 findings.md (标准特性到此结束)
    追加 ## Design Summary 章节到 findings.md
    (Phase 1 边界压缩)

[大型特性继续执行以下步骤]

Step 6-9: Module Decomposition Workshop
    (已在 Module Decomposition Workshop 章节详细说明)

Step 10-14: Module Internal Architecture Design
    (已在 Module Internal Architecture Design 章节详细说明)

Step 15-21: Module Implementation Deep Dive
    (已在 Module Implementation Deep Dive 章节详细说明)

Step 22: 更新 findings.md (大型特性最终步骤)
    追加 ## Design Summary 章节到 findings.md
    包含:
    - Scene Analysis Summary (如果存在)
    - Module Decomposition Summary
    - Module Architecture Summary
    - Implementation Deep Dive Summary
    (Phase 1 边界压缩)
```

**设计文档内容要求（Python 生成 + LLM 补充） - v2.1 完整版:**

| 章节 | Python 生成 | LLM 补充 | 最终内容 | 适用范围 |
|------|-----------|---------|---------|---------|
| **Overview** | ✅ 基础信息 | ✅ 风险等级评估 | 完整 | 所有特性 |
| **Requirements** | ✅ 分类需求 | ✅ REQ-ID 编号 | 完整 | 所有特性 |
| **Architecture** | ✅ 模块列表 | ✅ Nexus-Map 集成 | 完整 | 所有特性 |
| **Module Design** | ✅ 目录结构 | ✅ 职责说明 | 完整 | 所有特性 |
| **Interface Definitions** | ✅ API 模板 | ⚠️ **需补充参数/返回值** | 半完成 | 所有特性 |
| **Module Decomposition (v2.1)** | ❌ 无模板 | ✅ **LLM 全量生成** | 完整 | 大型特性 |
| **Module Internal Architecture (v2.1)** | ❌ 无模板 | ✅ **LLM 全量生成** | 完整 | 大型特性 |
| **Module Implementation Deep Dive (v2.1)** | ❌ 无模板 | ✅ **LLM 全量生成** | 完整 | 大型特性 |
| **Data Flow** | ✅ 流程图模板 | ⚠️ **需补充具体组件** | 半完成 | 所有特性 |
| **Error Handling** | ✅ 策略模板 | ⚠️ **需补充具体策略** | 半完成 | 所有特性 |
| **Integration Points** | ✅ 模块列表 | ⚠️ **需补充具体方法** | 半完成 | 所有特性 |
| **Implementation Plan** | ✅ 任务表格 | ✅ 时间估算 | 完整 | 所有特性 |
| **Verification** | ✅ Checklist | ✅ REQ-ID 验证项 | 完整 | 所有特性 |

**大型特性专属章节详细说明 (v2.1):**

| 章节 | 内容 | LLM 工作量 | 依赖输入 |
|------|------|-----------|---------|
| **Module Decomposition** | Bounded Context + Boundary Matrix + Dependency Constraints + Ownership | 高 | scene_analysis.md, nexus-query |
| **Module Internal Architecture** | Layer Structure + Components + Protocol + Test Strategy | 中 | Module Decomposition 输出 |
| **Module Implementation Deep Dive** | Peripheral Analysis + Interface Detail + Logic Design + Interaction Design + Impact Analysis + Implementation Order | 高 | Module Internal Architecture 输出 + 周边模块代码 |

**LLM 补充指引：**

```
Interface Definitions 补充：
- 参数名：根据需求推断（如 user_id, provider）
- 返回值类型：根据需求推断（如 Token, AuthorizationCode）
- 异常类型：根据约束推断（如 OAuthError, TimeoutError）

Data Flow 补充：
- 具体组件：根据 Nexus-Map 模块名（如 OAuthService, TokenManager）
- 依赖关系：根据 module-graph.md

Error Handling 补充：
- 具体策略：根据约束（如 bcrypt cost=12 → SecurityError）
- Recovery 方式：根据性能约束（如 Timeout → retry 3 times）

Integration Points 补充：
- 具体方法：根据现有接口（如 UserController.login()）
- 修改类型：根据影响分析（如 modify, extend, replace）
```

#### Module Decomposition Workshop (v2.1 新增 - 大型特性)

> ⚠️ **重要**: 此子阶段仅对大型特性启用（复杂度 >= HIGH）。
> 
> **触发条件**: 特性涉及模块 > 3 或 scene_analysis.md 存在。

**目标:** 明确模块边界、约束依赖关系、定义模块职责。

**执行流程:**

```
Step 5: Bounded Context 定义
    对 design doc 中的每个模块:
    - 定义业务边界（处理什么业务问题）
    - 定义数据边界（管理什么数据）
    - 定义行为边界（提供什么能力）
    
Step 6: Module Boundary Matrix
    绘制模块间交互矩阵:
    | Module A | Module B | Interaction Type | Contract |
    |----------|----------|------------------|----------|
    | [模块名] | [模块名] | [交互类型] | [契约] |
    
    Interaction Type: API_CALL / EVENT / DATA_SHARE
    
Step 7: Dependency Constraints
    定义允许的依赖方向:
    - 正向依赖（允许）
    - 反向依赖（禁止，需要重构）
    
    使用 nexus-query 验证依赖方向
    
Step 8: Module Ownership Declaration
    定义模块负责人和变更权限:
    - Owner: @[username]
    - Reviewers: @[username1, username2]
    - Change Policy: [变更策略]
    
Step 9: Update design doc
    追加 Module Decomposition 章节
```

**新增设计文档章节:**

```markdown
## Module Decomposition

### Bounded Contexts

| Module | Business Boundary | Data Boundary | Behavior Boundary |
|--------|------------------|---------------|-------------------|
| [模块名] | [处理什么业务问题] | [管理什么数据] | [提供什么能力] |

**Example:**
| Module | Business Boundary | Data Boundary | Behavior Boundary |
|--------|------------------|---------------|-------------------|
| OrderService | 订单生命周期管理 | Order, OrderItem, OrderStatus | 创建订单、取消订单、查询订单 |
| PaymentService | 支付处理 | Payment, PaymentMethod, Transaction | 发起支付、确认支付、退款 |

### Module Boundary Matrix

```
          OrderService  PaymentService  NotificationService
OrderService    ×         API_CALL          EVENT
PaymentService  ×            ×              EVENT
NotificationService ×          ×              ×
```

Legend:
- ×: No interaction
- API_CALL: Direct API call
- EVENT: Event-driven communication
- DATA_SHARE: Shared data model

### Dependency Constraints

**Allowed Dependencies (正向依赖):**
```
OrderService → PaymentService (订单依赖支付)
OrderService → NotificationService (订单依赖通知)
```

**Forbidden Dependencies (反向依赖 - 需重构):**
```
PaymentService → OrderService (禁止，支付不应依赖订单细节)
```

**Validation:**
使用 nexus-query 检查现有代码是否存在禁止依赖。

### Module Ownership

| Module | Owner | Reviewers | Change Policy |
|--------|-------|-----------|---------------|
| OrderService | @alice | @bob, @charlie | API 变更需 2 人批准 |
| PaymentService | @bob | @alice | 安全相关需安全团队审核 |
```

**Gate Requirements:**
```
✅ Bounded Context 定义覆盖所有模块
✅ Module Boundary Matrix 存在且非空
✅ Dependency Constraints 定义且 nexus-query 验证通过
✅ 无禁止依赖（或已标注需要重构）
✅ Module Ownership 定义（如果团队规模 >3）
```

#### Module Internal Architecture Design (v2.1 新增 - 大型特性)

> ⚠️ **重要**: 此子阶段仅对大型特性启用（复杂度 >= HIGH）。
> 
> **触发条件**: 特性涉及模块 > 3 或 Module Decomposition 已完成。

**目标:** 深化模块内部设计，定义分层结构、组件关系、通信协议、测试策略。

**执行流程:**

```
Step 10: Module Layer Design
    对每个模块定义分层结构:
    - API Layer: 对外接口层
    - Core Layer: 核心业务逻辑层
    - Infrastructure Layer: 基础设施层（DB、缓存、外部服务）
    - Test Layer: 测试层
    
Step 11: Component Decomposition
    将 Core Layer 拆分为组件:
    - 组件关系图
    - 组件接口定义
    - 组件依赖关系
    
Step 12: Communication Protocol Design
    定义模块通信协议:
    - Inbound APIs: 外部如何调用本模块
    - Outbound APIs: 本模块如何调用外部
    - Events: 本模块发布/订阅的事件
    - Data Contracts: 数据契约定义
    
Step 13: Test Strategy Design
    定义模块独立测试策略:
    - Unit Test Scope: 单元测试范围
    - Integration Test Scope: 模块内集成测试
    - Mock Strategy: Mock 外部依赖的策略
    - Test Data Strategy: 测试数据生成策略
    
Step 14: Update design doc
    追加 Module Internal Architecture 章节
```

**新增设计文档章节:**

```markdown
## Module Internal Architecture

### Module: OrderService

#### Layer Structure

```
┌─────────────────────────────────────┐
│         API Layer                    │ ← 对外接口
│  OrderController, OrderAPI           │
├─────────────────────────────────────┤
│         Core Layer                   │ ← 核心业务逻辑
│  OrderAggregate, OrderValidator,     │
│  OrderStateMachine                   │
├─────────────────────────────────────┤
│    Infrastructure Layer              │ ← 基础设施
│  OrderRepository, OrderDAO,          │
│  PaymentGatewayAdapter               │
└─────────────────────────────────────┘
```

#### Internal Components

**Core Layer Components:**

| Component | Responsibility | Dependencies |
|-----------|---------------|--------------|
| OrderAggregate | 订单聚合根，管理订单状态 | OrderValidator |
| OrderValidator | 订单验证逻辑 | × |
| OrderStateMachine | 订单状态机 | OrderAggregate |

**Component Diagram:**
```
OrderAggregate
    ↓
OrderValidator (验证订单数据)
    ↓
OrderStateMachine (管理状态流转)
```

#### Communication Protocol

**Inbound APIs (外部调用):**
```rust
trait OrderServiceAPI {
    fn create_order(cmd: CreateOrderCommand) -> Result<Order>;
    fn cancel_order(cmd: CancelOrderCommand) -> Result<Order>;
    fn get_order(query: GetOrderQuery) -> Result<Order>;
}
```

**Outbound APIs (调用外部):**
```rust
trait PaymentGateway {
    fn initiate_payment(order: &Order) -> Result<PaymentId>;
}

trait NotificationService {
    fn notify_order_created(order: &Order) -> Result<()>;
}
```

**Events (发布):**
```rust
enum OrderEvent {
    OrderCreated(Order),
    OrderCancelled(Order),
    OrderStatusChanged { old: Status, new: Status },
}
```

**Data Contracts:**
```rust
struct CreateOrderCommand {
    user_id: UserId,
    items: Vec<OrderItem>,
}

struct Order {
    id: OrderId,
    user_id: UserId,
    items: Vec<OrderItem>,
    status: OrderStatus,
    created_at: DateTime,
}
```

#### Test Strategy

**Unit Test Scope:**
- OrderValidator 单元测试（纯逻辑，无依赖）
- OrderStateMachine 单元测试（状态流转）

**Integration Test Scope (模块内):**
- OrderAggregate + Repository 集成测试
- API Layer + Core Layer 集成测试

**Mock Strategy:**
- Mock PaymentGateway（支付网关）
- Mock NotificationService（通知服务）
- Mock Repository（数据库）

**Test Data Strategy:**
- 使用 TestOrderBuilder 构建测试订单
- 使用 Fixture 数据（标准订单模板）

### Module: PaymentService

[Same structure as above for each module...]
```

**Gate Requirements:**
```
✅ 每个模块有 Layer Structure 定义
✅ Core Layer 有 Component Decomposition
✅ Communication Protocol 定义完整（Inbound + Outbound + Events）
✅ Test Strategy 定义且包含 Mock 策略
✅ 用户确认模块内部设计足够详细
```

#### Module Implementation Deep Dive (v2.1 新增 - 深度实现设计)

> ⚠️ **重要**: 此子阶段仅对大型特性启用（复杂度 >= HIGH）。
> 
> **触发条件**: 特性涉及模块 > 3 或 Module Internal Architecture 已完成。
> 
> **目标**: 深化实现逻辑设计，分析周边模块依赖，评估变更影响，为 Phase 3 开发提供完整指导。

**执行流程:**

```
Step 15: Peripheral Module Deep Analysis
    对每个依赖模块:
    - Read 依赖模块的核心实现文件
    - 分析依赖模块的数据结构
    - 分析依赖模块的性能约束
    - 分析依赖模块的错误处理策略
    
Step 16: Interface Detailed Design
    对每个接口:
    - 定义完整的参数结构（包括边界值）
    - 定义返回值结构（包括错误类型）
    - 定义接口的约束条件（性能、安全）
    - 定义接口的使用示例
    
Step 17: Implementation Logic Design
    对每个组件:
    - 设计核心算法（伪代码或流程图）
    - 设计数据结构（struct/class 定义）
    - 设计关键逻辑流程（步骤序列）
    - 设计边界条件处理（异常情况）
    - 设计性能优化策略
    
Step 18: Module Interaction Detailed Design
    对每个交互点:
    - 定义调用序列（调用顺序）
    - 定义数据流（数据传递路径）
    - 定义错误传播（错误如何传递）
    - 定义同步/异步策略
    
Step 19: Change Impact Analysis
    分析变更影响:
    - 定义变更影响范围（影响的模块列表）
    - 定义影响程度（API 变更 vs 内部变更）
    - 定义影响矩阵（模块间影响关系）
    - 定义风险评估（变更风险）
    - 定义缓解策略（如何降低风险）
    
Step 20: Implementation Order Planning
    基于依赖关系和影响分析:
    - 定义模块开发顺序（依赖关系图）
    - 定义关键路径（Critical Path）
    - 定义并行开发机会（可并行任务）
    - 定义阻塞检测（Blocker Detection）
    
Step 21: Update design doc
    追加 Module Implementation Deep Dive 章节
```

**新增设计文档章节:**

```markdown
## Module Implementation Deep Dive

### 1. Peripheral Module Deep Analysis (周边模块深入分析)

#### Dependency: PaymentService

**Core Implementation:**
```rust
// Read from: src/payment/service.rs
struct PaymentService {
    gateway: PaymentGateway,
    transaction_repo: TransactionRepository,
}

impl PaymentService {
    fn initiate_payment(order: &Order) -> Result<PaymentId> {
        // 核心实现逻辑（从代码中提取）
        let transaction = Transaction::new(order);
        self.gateway.process(transaction)?;
        self.transaction_repo.save(transaction)?;
        Ok(transaction.id)
    }
}
```

**Data Structure:**
```rust
struct Payment {
    id: PaymentId,
    order_id: OrderId,
    amount: Decimal,
    status: PaymentStatus, // Pending, Completed, Failed
    created_at: DateTime,
}

struct Transaction {
    payment: Payment,
    gateway_response: GatewayResponse,
}
```

**Performance Constraints:**
- PaymentService 响应时间 < 2s（从 PaymentGateway 文档）
- 并发支付数 < 100（从 config.yaml）
- 超时时间 = 30s（从 PaymentService::TIMEOUT）

**Error Handling:**
```rust
enum PaymentError {
    GatewayTimeout,        // 重试 3 次
    InsufficientFunds,     // 直接返回用户
    PaymentDeclined,       // 记录日志，返回用户
    NetworkError,          // 重试 + 降级
}
```

**Integration Constraints:**
- 必须在 Order 创建后 5s 内发起支付（业务规则）
- Payment 状态变更必须通知 OrderService（事件驱动）

#### Dependency: NotificationService

[Same structure for each dependency...]

---

### 2. Interface Detailed Design (接口详细设计)

#### Inbound API: create_order

**Full Signature:**
```rust
fn create_order(
    cmd: CreateOrderCommand,
    ctx: RequestContext,  // 新增：请求上下文
) -> Result<Order, OrderError>
```

**Parameter Structure:**
```rust
struct CreateOrderCommand {
    user_id: UserId,           // 必须，格式: UUID v4
    items: Vec<OrderItem>,     // 必须，长度: 1-100
    payment_method: PaymentMethod, // 可选，默认: CreditCard
    delivery_address: Address, // 必须，验证格式
}

struct OrderItem {
    product_id: ProductId,     // 必须，格式: UUID v4
    quantity: u32,             // 必须，范围: 1-999
    unit_price: Decimal,       // 必须，范围: > 0
}
```

**Boundary Values:**
| 参数 | 边界 | 处理 |
|------|------|------|
| items.len() | > 100 | 返回 OrderTooLargeError |
| quantity | > 999 | 返回 InvalidQuantityError |
| unit_price | <= 0 | 返回 InvalidPriceError |

**Return Structure:**
```rust
struct Order {
    id: OrderId,
    user_id: UserId,
    items: Vec<OrderItem>,
    status: OrderStatus,       // Created, PendingPayment, Paid
    total_amount: Decimal,
    created_at: DateTime,
    estimated_delivery: DateTime,
}

enum OrderError {
    ValidationError(ValidationError),
    PaymentError(PaymentError),
    InventoryError(InventoryError),
    TimeoutError,
}
```

**Constraints:**
- 性能约束：响应时间 < 500ms
- 安全约束：user_id 必须验证权限
- 并发约束：同一用户最多 5 个 Pending 订单

**Usage Example:**
```rust
let cmd = CreateOrderCommand {
    user_id: UserId::new("uuid-v4"),
    items: vec![
        OrderItem { product_id: "...", quantity: 2, unit_price: 10.0 },
    ],
    payment_method: PaymentMethod::CreditCard,
    delivery_address: Address { ... },
};

let order = order_service.create_order(cmd, ctx)?;
```

---

### 3. Implementation Logic Design (实现逻辑设计)

#### Component: OrderValidator

**Core Algorithm:**
```
Algorithm: validate_order(cmd, inventory)

1. Validate user_id
   - Check format (UUID v4)
   - Check user exists (UserService)
   - Check user has permission (AuthService)
   
2. Validate items
   - For each item:
     - Check product exists (InventoryService)
     - Check quantity available (InventoryService)
     - Check price matches (PriceService)
   
3. Validate business rules
   - Check max items count (<= 100)
   - Check max pending orders (<= 5)
   - Check delivery address format
   
4. Return ValidationResult
   - Success: { is_valid: true, validated_order: Order }
   - Failure: { is_valid: false, errors: Vec<ValidationError> }

Performance: O(n) where n = items.len()
```

**Data Structure:**
```rust
struct ValidationResult {
    is_valid: bool,
    validated_order: Option<Order>,
    errors: Vec<ValidationError>,
}

struct ValidationError {
    field: String,
    message: String,
    code: ErrorCode,
}

struct ValidationContext {
    user: User,             // 从 UserService 获取
    products: Vec<Product>, // 从 InventoryService 获取
    pending_orders: u32,    // 从 OrderRepository 查询
}
```

**Critical Logic Flow:**
```
Step 1: Fetch user (UserService.get_user(user_id))
        ↓ Success → Step 2
        ↓ Failure → return ValidationError
        
Step 2: Fetch products (InventoryService.batch_get(product_ids))
        ↓ Success → Step 3
        ↓ Failure → return ValidationError
        
Step 3: Check inventory (InventoryService.check_availability(items))
        ↓ Available → Step 4
        ↓ Not Available → return InventoryError
        
Step 4: Validate business rules
        ↓ Pass → return Success
        ↓ Fail → return ValidationError
```

**Boundary Condition Handling:**
| 边界情况 | 处理策略 |
|---------|---------|
| UserService timeout | 返回 TimeoutError，记录日志 |
| InventoryService partial failure | 返回部分验证结果 + 错误列表 |
| User pending orders = 5 | 返回 MaxPendingOrdersError |
| Product price mismatch | 返回 PriceMismatchError |

**Performance Optimization:**
- 批量查询 InventoryService（而非逐个查询）
- 缓存用户信息（Redis，TTL=5min）
- 并行验证多个 item（async/await）

[Same structure for other components...]

---

### 4. Module Interaction Detailed Design (模块交互详细设计)

#### Interaction: OrderService → PaymentService

**Call Sequence:**
```
OrderService.create_order()
    ↓
OrderValidator.validate()
    ↓ Success
OrderStateMachine.transition_to(PendingPayment)
    ↓
PaymentService.initiate_payment(order)
    ↓ Success
OrderStateMachine.transition_to(Paid)
    ↓ Failure
OrderStateMachine.transition_to(Cancelled)
    ↓
NotificationService.notify_order_failed(order)
```

**Data Flow:**
```
CreateOrderCommand → Order
    ↓
Order → PaymentService.initiate_payment()
    ↓
PaymentId → Order.payment_id
    ↓
Order → OrderRepository.save()
```

**Error Propagation:**
```
PaymentService.PaymentError
    ↓
OrderError.PaymentError
    ↓
Controller: HTTP 400 Bad Request
    ↓
Client: Error message
```

**Sync/Async Strategy:**
- 支付请求：同步（用户等待结果）
- 支付确认：异步（PaymentGateway webhook）
- 状态更新：异步（事件驱动）

[Same structure for other interactions...]

---

### 5. Change Impact Analysis (变更影响分析)

#### Change Impact Matrix

| Change Type | Affected Modules | Impact Level | Risk |
|-------------|------------------|--------------|------|
| create_order API | PaymentService, NotificationService | High | Payment 可能超时 |
| OrderStatus 新增 | OrderStateMachine, NotificationService | Medium | 事件处理需更新 |
| OrderItem 结构变更 | InventoryService, PriceService | High | 需验证兼容性 |
| OrderValidator 逻辑 | UserService, InventoryService | Medium | 性能影响 |

**Impact Assessment:**

1. **create_order API 变更**
   - 影响模块：PaymentService（调用参数）、NotificationService（事件数据）
   - 影响程度：API Breaking Change（需要版本升级）
   - 风险：PaymentService 可能无法处理新参数格式
   - 缓解策略：API 版本协商 + 兼容层

2. **OrderStatus 新增**
   - 影响模块：OrderStateMachine（状态机）、NotificationService（事件处理）
   - 影响程度：Internal Change（向后兼容）
   - 风险：NotificationService 可能遗漏新状态的事件
   - 缓解策略：事件版本号 + 降级处理

[Same structure for other changes...]

**Risk Mitigation Strategies:**

| Risk | Mitigation |
|------|------------|
| Payment 超时 | 增加超时时间 + 降级策略 |
| API Breaking Change | API 版本协商 + 兼容层 |
| 事件处理遗漏 | 事件版本号 + 降级处理 |
| 性能下降 | 性能测试 + 监控 |

**Dependency Validation:**

使用 nexus-query 验证：
- OrderService → PaymentService 依赖是否存在
- PaymentService → OrderService 依赖是否被禁止（反向依赖）
- 循环依赖是否检测

---

### 6. Implementation Order (实现顺序建议)

**Dependency Graph:**
```
OrderValidator (独立)
    ↓
OrderStateMachine (依赖 Validator)
    ↓
OrderAggregate (依赖 Validator + StateMachine)
    ↓
OrderService (依赖 Aggregate + PaymentAdapter + NotificationAdapter)
    ↓
PaymentAdapter (外部依赖)
NotificationAdapter (外部依赖)
```

**Critical Path:**
- Task 1 → Task 2 → Task 3 → Task 4 → Task 7（关键路径）
- Task 5、Task 6 可并行开发（独立模块）

**Parallel Development Opportunities:**
- Task 1 完成后：Task 2 和 Task 5/6 可并行启动
- Task 3 完成后：Task 4 和 Task 7 测试准备可并行

**Blocker Detection:**
- 如果 Task 5（PaymentAdapter）失败：Task 4 等待 PaymentMock
- 如果 Task 6（NotificationAdapter）失败：Task 4 等待 NotificationMock
```

**Gate Requirements:**
```
✅ 周边模块分析覆盖所有依赖模块
✅ 接口设计包含完整参数/返回值/边界值
✅ 实现逻辑包含算法/数据结构/关键流程
✅ 交互设计包含调用序列/数据流/错误传播
✅ 影响分析包含影响矩阵/风险评估/缓解策略
✅ 实现顺序包含依赖图/关键路径/并行机会
✅ nexus-query 依赖验证通过（无禁止依赖）
✅ 用户确认实现设计足够详细，可以进入 Phase 2
```

**Human-in-Loop (v2.1 深度增强):**
- 用户必须 review Module Implementation Deep Dive
- 用户必须确认"周边模块分析足够深入"
- 用户必须确认"接口设计完整且可实施"
- 用户必须确认"实现逻辑清晰且性能优化合理"
- 用户必须确认"变更影响分析全面"
- 用户必须明确确认 "Implementation design approved, proceed to Phase 2"
- 如果用户反馈"周边模块分析不够深入"或"实现逻辑不够详细"，AI 必须回到相应子阶段重新设计

**Human-in-Loop (v2.1 增强):**
- 用户必须 review Module Decomposition + Internal Architecture
- 用户必须明确确认 "Module design approved, proceed to Phase 2"
- 如果用户反馈"模块边界不清晰"或"内部设计不够详细"，AI 必须回到相应子阶段重新设计

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

#### Phase 2 LLM Action Sequence

```
Step 1: 读取设计文档
    Read docs/features/<feature>/specs/YYYY-MM-DD-<feature>-design.md
    Read CONSTITUTION/implementation-rules.md

Step 2: 任务拆分
    将设计文档拆分为独立的任务列表，每个任务:
    - 有明确的输入/输出
    - 有预估的工作量 (low/medium/high)
    - 有依赖关系声明
    - 有对应的文件变更范围

Step 3: 定义 File Changes Scope
    明确列出:
    - new_files: 将要新建的文件列表
    - modified_files: 将要修改的文件列表
    - 这是 Phase 5 增量审查的依据

Step 4: 定义测试策略
    对每个新建文件:
    - 指定对应的测试文件
    - 列出需要覆盖的测试场景

Step 5: 生成实现计划
    Write docs/features/<feature>/plans/YYYY-MM-DD-<feature>.md
    Write task_plan.md (Phase 2 section)

Step 6: 更新 findings.md
    追加 ## Plan Summary 章节到 findings.md
    (Phase 2 边界压缩)
```

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
- `findings.md (relevant section)` (updated with execution log)

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

#### Phase 3 LLM Action Sequence

```
Step 0: 上下文刷新 (ContextMonitor 自动执行)
    ⚠️ 进入 Phase 3 时自动刷新上下文
    打印 findings.md Phase 0 + design spec + constraints 的紧凑摘要到 stdout
    确保 LLM 在大量编辑前重新获取需求和设计决策

Step 1: 读取实现计划
    Read docs/features/<feature>/plans/YYYY-MM-DD-<feature>.md
    Read task_plan.md (Phase 2 section)

Step 2: 创建 git worktree (隔离开发)
    git worktree add -b feature/<feature> ../<feature>-worktree

Step 3: 逐 task 实现
    对 plan 中的每个 task:
        a. 使用 Edit/Write 工具创建或修改文件
        b. 记录实际变更到 actual_file_changes
        c. 每个 task 完成后:
           - Git commit (atomic commits)
           - 更新 findings.md (relevant section)
           - ContextMonitor.record_task() 追踪 task 进度
           - 每 3 个 task 或 20 次编辑后自动刷新上下文
        d. 如果 LoopDetection 触发警告 (同文件编辑>5次):
           - 暂停，检查方向是否正确
           - ContextMonitor 自动触发上下文刷新
           - 如果 2 次循环无进展 → 询问用户

Step 4: 编译验证
    cargo build (或项目对应的构建命令)
    如果失败:
        - 使用 systematic-debugging skill 排查
        - 修复后重新构建

Step 5: 单元测试
    编写或更新测试文件
    确保所有新代码有对应的单元测试

Step 6: 更新 findings.md (relevant section)
    追加 ## Implementation Summary 章节到 findings.md (relevant section)
    (Phase 3 边界压缩)
    记录 actual_file_changes 到 context.metadata
```

---

### Phase 4: Integration & Testing

**Skill:** `verification-before-completion` + project test framework

**输入:**
- Phase 3 输出的代码

**输出:**
- 所有集成测试通过
- `findings.md (relevant section)` (updated with test results)

**Gate Requirements:**
```
✅ cargo test passes (or project test command passes)
✅ Integration tests complete
✅ No critical errors
```

**Human-in-Loop:**
- 测试失败时停在当前问题，等待用户指示
- 用户必须确认 "Phase 4 complete, proceed to Phase 5"

**Note:** 如果测试因依赖问题无法运行，记录到 `findings.md (relevant section)` 并标记为 "blocked by environment"，需用户确认是否继续。

#### Phase 4 LLM Action Sequence

```
Step 1: 运行完整测试套件
    cargo test (或项目对应命令)
    如果失败:
        - 读取错误信息
        - 使用 systematic-debugging skill 分析
        - 修复后重新运行

Step 2: 检查测试覆盖率
    确认增量代码的测试覆盖情况

Step 3: 更新 findings.md (relevant section)
    追加 ## Test Summary 章节到 findings.md (relevant section)
    (Phase 4 边界压缩)
    记录: 通过/失败/跳过 的测试数量
```

---

### Phase 5: Code Quality Review

**Implementation:** Built-in review logic (Phase 5 orchestrator)

> **Note**: Phase 5 uses built-in review generation logic defined in `src/phases/phase5.py`. 
> While `code-review-quality` skill can be optionally loaded for enhanced review capabilities, 
> the core review process is self-contained and automatically generates 2 review documents.

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

2. **code_quality_review.md (merged)** - 增量测试覆盖
   - 增量代码文件的测试覆盖
   - 新文件的测试存在性检查

3. **architecture_review.md (merged)** - 需求可追溯性
   - 需求 → 实现文件的映射
   - 文件变更与需求的对应关系

4. **architecture_review.md** - 架构合规性
   - 增量文件是否符合架构规范
   - 模块依赖关系检查

**输出:**
- `docs/reviews/architecture_review.md`
- `docs/reviews/code_quality_review.md`
- `docs/reviews/code_quality_review.md (merged)`
- `docs/reviews/architecture_review.md (merged)`

**Gate Requirements:**
```
✅ All 4 review artifacts exist
✅ Each artifact 审查的是 file_changes 范围内的文件
✅ Each artifact contains minimal required content:
   - architecture_review.md: Module analysis, dependency graph
   - code_quality_review.md: Quality checklist, issue list
   - code_quality_review.md (merged): Coverage %, test list
   - architecture_review.md (merged): Requirements checklist
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

#### Phase 5 LLM Action Sequence

```
Step 1: 确定审查范围
    读取 actual_file_changes (Phase 3 记录)
    读取 file_changes (Phase 2 计划)
    仅审查这两个范围内的文件

Step 2: 生成 4 个审查制品
    Write docs/features/<feature>/reviews/architecture_review.md
        - 增量文件的模块分析
        - 依赖关系图
        - 架构合规性检查
    Write docs/features/<feature>/reviews/code_quality_review.md
        - 增量代码质量检查清单
        - 问题列表 (如果发现问题)
    Write docs/features/<feature>/reviews/code_quality_review.md (merged)
        - 增量文件的测试覆盖 %
        - 测试文件列表
    Write docs/features/<feature>/reviews/architecture_review.md (merged)
        - 需求 → 实现文件 的可追溯性映射
        - 文件变更与需求的对应关系

Step 3: 更新 findings.md (relevant section)
    追加 ## Review Summary 章节到 findings.md (relevant section)
    (Phase 5 边界压缩)
```

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
- `docs/features/<feature>/findings.md (relevant section)` (finalized)
- `docs/features/<feature>/.sdd/checkpoint.json` (updated)

**Gate Requirements:**
```
✅ PROJECT_STATE.md updated with feature summary
✅ AGENTS.md updated with current feature context
✅ docs/features/<feature>/task_plan.md finalized
✅ docs/features/<feature>/findings.md complete
✅ docs/features/<feature>/findings.md (relevant section) finalized
```

**Human-in-Loop:**
无 (自动执行)

#### Phase 6 LLM Action Sequence

```
Step 1: 收集所有制品
    读取本特性目录下的所有产出:
    - findings.md Phase 0, task_plan.md, findings.md, findings.md (relevant section)
    - specs/, plans/, reviews/ 目录下的文件
    - ConversationMemory 快照

Step 2: 生成 AGENTS.md
    Write AGENTS.md (项目根目录)
    包含 8 个章节:
    1. Current Feature 状态
    2. Requirements 汇总
    3. Architecture & Design 决策
    4. Implementation Files 清单
    5. Review Artifacts 状态
    6. Conversation Memory 摘要
    7. Key Artifacts Map
    8. How to Resume 恢复指引

Step 3: 更新 PROJECT_STATE.md
    聚合所有特性的状态表
    Write PROJECT_STATE.md

Step 4: Generate Change Summary (merged into AGENTS.md)
    Change summary is now part of AGENTS.md Section 4
    No separate file needed

Step 5: 最终化特性状态
    Write docs/features/<feature>/.sdd/checkpoint.json
    标记 completed = true

Step 6: 更新 ConversationMemory
    将所有 MemoryNode 持久化到 conversation_memory.json
    保存到 memory_history/ 历史版本
```

---

## Automatic Enforcement in finisher

**finishing-a-development-branch skill** 现在包含 Phase 5 强制检查：

```
Step 1: Verify Tests
    ↓ (tests pass)
Step 1.5: Verify SDD Phase 5 Artifacts [NEW]
    - 检查 2 个必需 review artifacts
    - 缺失则 BLOCK 并提示完成 Phase 5
    ↓ (全部存在)
Step 1.6: Developer Confirmation [NEW]
    - 确认这是 SDD-Workflow 项目
    - 等待明确确认
    ↓ (确认后)
Step 2: Present Options (merge/PR/etc)
```

## Workflow Orchestration

## 完整使用示例

### Large Feature Workflow (v2.1)

```
> sdd start order-management-system

[Complexity Detection]
✅ Feature complexity: HIGH (tasks>5, modules>3)
✅ Triggering Scene Analysis Phase...

[Scene Analysis Phase]
✅ Business context collected
✅ User journey mapped: 3 journeys
✅ Core use cases extracted: 10 use cases
✅ Priority matrix: P0=4, P1=3, P2=3
✅ Scene-to-module mapping complete
✅ scene_analysis.md generated: docs/features/order-management/scene_analysis.md
⏳ Awaiting: "Scene analysis approved, proceed to Understanding Phase" ...

> 用户 review scene_analysis.md，确认场景覆盖全面

[Scene Analysis Gate: PASSED]

[Understanding 阶段]
✅ findings.md Phase 0 generated
✅ Codebase analysis: 15+ files identified
✅ Technical principles: 3+ sources cited
✅ Constraints: 5+ identified
✅ Alternatives: 3 solutions compared
⏳ Awaiting: "Research approved, proceed to Phase 1" ...

> 用户确认研究足够深入

[Understanding Gate: PASSED]

[Phase 1: Requirements Analysis]
✅ Brainstorming initiated
✅ Design doc generated: docs/features/order-management/specs/2026-05-14-order-design.md

[Module Decomposition Workshop]
✅ Bounded Contexts defined: OrderService, PaymentService, NotificationService
✅ Module Boundary Matrix created
✅ Dependency Constraints validated via nexus-query
✅ Module Ownership declared
⏳ Awaiting: "Decomposition approved" ...

> 用户确认模块边界清晰

[Module Internal Architecture Design]
✅ Layer Structure defined for each module
✅ Component Decomposition: OrderAggregate, OrderValidator, OrderStateMachine
✅ Communication Protocol: Inbound APIs + Outbound APIs + Events
✅ Test Strategy: Unit + Integration + Mock Strategy
⏳ Awaiting: "Module architecture approved" ...

> 用户确认模块内部设计足够详细

[Module Implementation Deep Dive]
✅ Peripheral Module Analysis:
   - PaymentService: Read src/payment/service.rs, analyzed data structures, performance constraints
   - NotificationService: Read src/notification/service.rs, analyzed event handling
   - InventoryService: Read src/inventory/service.rs, analyzed batch query optimization
✅ Interface Detailed Design:
   - create_order: Full signature + parameter structure + boundary values + return structure
   - cancel_order: Full signature + constraints + usage examples
   - get_order: Full signature + query parameters + caching strategy
✅ Implementation Logic Design:
   - OrderValidator: Algorithm (O(n)) + data structures + logic flow + boundary handling + performance optimization
   - OrderStateMachine: State machine definition + transitions + event emission
   - OrderAggregate: Aggregate root logic + repository integration + concurrency handling
✅ Module Interaction Design:
   - OrderService → PaymentService: Call sequence + data flow + error propagation + sync strategy
   - OrderService → NotificationService: Event-driven interaction + async handling
✅ Change Impact Analysis:
   - Impact Matrix: 4 changes analyzed (API, Status, Item structure, Validator logic)
   - Risk Assessment: Payment timeout risk identified + mitigation strategy defined
   - nexus-query validation: All dependencies verified, no forbidden dependencies
✅ Implementation Order:
   - Dependency Graph: OrderValidator → OrderStateMachine → OrderAggregate → OrderService
   - Critical Path: Task 1→2→3→4→7
   - Parallel Opportunities: Task 5/6 can run parallel with Task 2
⏳ Awaiting: "Implementation design approved, proceed to Phase 2" ...

> 用户 review Module Implementation Deep Dive，确认:
> - 周边模块分析深入（PaymentService、NotificationService、InventoryService 实现细节已理解）
> - 接口设计完整（边界值、错误类型已定义）
> - 实现逻辑清晰（算法复杂度、数据结构已设计）
> - 变更影响分析全面（风险已识别，缓解策略已定义）

[Phase 1 Gate: PASSED]

[Phase 2: Implementation Planning]
... (rest same as v2.0)
```

### Standard Feature Workflow (v2.0)

```
> sdd start custom-format-string

[Complexity Detection]
✅ Feature complexity: LOW (tasks<5, modules<3)
✅ Skipping Scene Analysis Phase...

[Understanding 阶段]
... (same as v2.0)

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

### v2.1 Enhanced Gates (Large Features - Full Pipeline)

| Phase | Gate | Blocker Condition |
|-------|------|------------------|
| Scene→Understanding | Scene Analysis Approval | 场景分析不全面、P0<3、用户未确认 |
| Understanding→1 | Research Approval | 研究不够深入、代码库分析<5文件、用户未确认 |
| 1→2 (Decomposition) | Decomposition Approval | 模块边界不清晰、禁止依赖存在、nexus-query验证失败 |
| 1→2 (Architecture) | Module Architecture Approval | 模块内部设计不够详细、缺少Layer/Component/Protocol定义 |
| 1→2 (Deep Dive) | Implementation Design Approval | 周边模块分析缺失、接口设计不完整、实现逻辑不清晰、影响分析缺失 |
| 1→2 | Final Design Approval | 用户未确认完整设计文档 |
| 2→3 | Plan Approval | 用户未选择执行方式、Implementation Order未定义 |
| 3→4 | Build Success | 编译失败、LoopDetection触发 |
| 4→5 | Tests Pass* | 测试失败 (*可配置跳过) |
| 5→6 | 4 Artifacts | 任一 artifact 缺失 |
| 6→End | Memory Persistence | PROJECT_STATE.md/AGENTS.md未更新 |

### v2.1 Phase 1 Sub-Gates (Large Features - Detailed)

| Sub-Phase | Gate | Requirements |
|-----------|------|--------------|
| Scene Analysis | Scene Approval | P0场景≥3、场景-模块映射完整、用户确认 |
| Understanding | Research Approval | 代码库分析≥5文件、技术原理≥2来源、方案对比≥2、用户确认 |
| Interface Definitions | Interface Template | Python生成模板存在、LLM补充参数/返回值 |
| Module Decomposition | Boundary Approval | Bounded Context定义、Boundary Matrix存在、nexus-query验证通过 |
| Module Architecture | Architecture Approval | Layer结构定义、Component分解、Protocol定义、Test策略 |
| Implementation Deep Dive | Implementation Approval | 周边模块分析≥所有依赖、接口详细设计完整、实现逻辑包含算法/数据结构、影响矩阵存在、实现顺序定义 |

### v2.0 Standard Gates

| Phase | Gate | Blocker Condition |
|-------|------|------------------|
| Understanding→1 | Research Approval | 研究不够深入或用户未确认 |
| 1→2 | Design Approval | 用户未确认设计 |
| 2→3 | Plan Approval | 用户未选择执行方式 |
| 3→4 | Build Success | 编译失败 |
| 4→5 | Tests Pass* | 测试失败 (*可配置跳过) |
| 5→6 | 4 Artifacts | 任一 artifact 缺失 |

---

## Git Workflow

### 核心原则

| 原则 | 说明 |
|------|------|
| **Trunk-Based Development** | main 始终可部署，短命分支 (1-3 天) |
| **Atomic Commits** | 每个 commit 做一件事 |
| **Descriptive Messages** | 解释 why，不只是 what |
| **Change Summaries** | 变更说明 + 未触及部分 + 潜在风险 |
| **Pre-Commit Hygiene** | 提交前检查 secrets、测试 |

### 分支命名规范

```
feature/<short-description>   → feature/task-creation
fix/<short-description>        → fix/duplicate-tasks
chore/<short-description>      → chore/update-deps
refactor/<short-description>   → refactor/auth-module
docs/<short-description>       → docs/api-documentation
test/<short-description>       → test/task-creation
```

### Commit Message 规范

**格式:**
```
<type>(<scope>): <short description>

<optional body explaining why, not what>
```

**Type:**
| Type | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| refactor | 重构 (非功能变更) |
| test | 测试 |
| docs | 文档 |
| chore | 工具/依赖 |
| style | 格式调整 |
| perf | 性能优化 |
| ci | CI/CD |
| build | 构建 |
| revert | 回滚 |

**示例:**
```bash
# Good
feat(auth): add email validation to registration

Uses Zod schema validation at the route handler level.
Prevents invalid email formats from reaching database.

# Bad
update auth.ts
```

### Change Summary

每次代码变更后必须填写 `docs/features/<feature>/change_summary.md`：

| 章节 | 内容 |
|------|------|
| 变更的文件 | 新增/修改/删除的文件列表 |
| 主要变更 | 做了什么，为什么 |
| 未变更的部分 | **有意**没有修改的部分 |
| 潜在风险 | 向后兼容性、性能影响 |
| Rollback 计划 | 如何回滚 |

### Pre-Commit Hook

安装 pre-commit hook:
```bash
python scripts/pre_commit_hook.py --install
```

自动检查:
- ✅ 分支名是否符合规范
- ✅ staged 文件中是否有 secrets
- ✅ 文件大小是否合理 (<500KB)
- ✅ commit message 格式

### Save Point Pattern

每次完成一个 increment 就 commit：

```
实现 slice → 测试 → 验证 → Commit → 下一个 slice
```

### Common Rationalizations

| 借口 | 现实 |
|------|------|
| "功能完成后再提交" | 大 commit 无法审查、回滚、重建 narrative |
| "message 不重要" | 未来需要理解历史 |
| "之后再 split" | 大变更风险更高 |
| "分支增加开销" | 短命分支 (1-3 天) 防止冲突 |

### Red Flags

- 大量未提交的变更累积
- commit message 如 "fix", "update"
- 格式变更混在功能变更中
- 没有 .gitignore 或未忽略 node_modules/.env
- 长生命周期分支与 main 严重偏离

## Document Architecture (v2.1)

### Core Design Principles

| Principle | Description |
|-----------|-------------|
| **Constitution-First** | Constitution is the supreme law, all design/implementation must comply |
| **Module Ownership** | Each module has clear owner and responsibility boundaries |
| **Feature Isolation** | Features developed independently, mapped to modules |
| **Knowledge-Driven** | Automatic retrieval of relevant docs during design |
| **Scene-First (v2.1)** | Large features start with scene analysis before technical design |
| **Bounded Context (v2.1)** | Each module has clear business, data, and behavior boundaries |

### 8-Layer Directory Structure (v2.1 Enhanced)

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
│   │       ├── scene_analysis.md   # [v2.1] Scene analysis (large features only)
│   │       ├── MODULES.md          # Module changes
│   │       ├── API-CHANGES.md      # API changes
│   │       ├── DEPENDENCIES.md     # Dependencies
│   │       ├── REVIEW.md           # Design review
│   │       ├── .sdd/              # Feature internal data
│   │       │   ├── checkpoint.json
│   │       │   └── conversation_memory.json
│   │       ├── task_plan.md        # Feature task progress
│   │       ├── findings.md         # Feature findings
│   │       ├── findings.md (relevant section)         # Feature execution log
│   │       │
│   │       ├── specs/              # Phase 1 产出 (v2.1 Enhanced)
│   │       │   └── YYYY-MM-DD-<feature>-design.md
│   │       │       ├── Overview
│   │       │       ├── Requirements
│   │       │       ├── Architecture
│   │       │       ├── Module Design
│   │       │       ├── Interface Definitions
│   │       │       ├── Module Decomposition (v2.1)
│   │       │       │   ├── Bounded Contexts
│   │       │       │   ├── Module Boundary Matrix
│   │       │       │   ├── Dependency Constraints
│   │       │       │   └── Module Ownership
│   │       │       ├── Module Internal Architecture (v2.1)
│   │       │       │   ├── Layer Structure
│   │       │       │   ├── Internal Components
│   │       │       │   ├── Communication Protocol
│   │       │       │   └── Test Strategy
│   │       │       ├── Module Implementation Deep Dive (v2.1)
│   │       │       │   ├── Peripheral Module Deep Analysis
│   │       │       │   │   ├── Dependency Implementation Details
│   │       │       │   │   ├── Data Structures
│   │       │       │   │   ├── Performance Constraints
│   │       │       │   │   └── Error Handling Strategies
│   │       │       │   ├── Interface Detailed Design
│   │       │       │   │   ├── Full Signatures
│   │       │       │   │   ├── Parameter Structures + Boundary Values
│   │       │       │   │   ├── Return Structures + Error Types
│   │       │       │   │   └── Constraints + Usage Examples
│   │       │       │   ├── Implementation Logic Design
│   │       │       │   │   ├── Core Algorithms (Pseudocode/Flow)
│   │       │       │   │   ├── Data Structures (Struct/Class)
│   │       │       │   │   ├── Critical Logic Flows (Step Sequence)
│   │       │       │   │   ├── Boundary Condition Handling
│   │       │       │   │   └ Performance Optimization Strategies
│   │       │       │   ├── Module Interaction Detailed Design
│   │       │       │   │   ├── Call Sequences
│   │       │       │   │   ├── Data Flows
│   │       │       │   │   ├── Error Propagation
│   │       │       │   │   └ Sync/Async Strategies
│   │       │       │   ├── Change Impact Analysis
│   │       │       │   │   ├── Change Impact Matrix
│   │       │       │   │   ├── Impact Assessment
│   │       │       │   │   ├── Risk Mitigation Strategies
│   │       │       │   │   └── nexus-query Dependency Validation
│   │       │       │   └── Implementation Order
│   │       │       │       ├── Dependency Graph
│   │       │       │       ├── Critical Path
│   │       │       │       ├── Parallel Development Opportunities
│   │       │       │       └── Blocker Detection
│   │       │       ├── Data Flow
│   │       │       ├── Error Handling
│   │       │       ├── Integration Points
│   │       │       ├── Implementation Plan
│   │       │       └── Verification
│   │       │
│   │       ├── plans/              # Phase 2 产出
│   │       │   └── YYYY-MM-DD-<feature>.md
│   │       │
│   │       └── reviews/            # Phase 5 产出 (OPTIMIZED: 2 merged docs)
│   │           ├── architecture_review.md  # Architecture + Requirements verification
│   │           └── code_quality_review.md  # Quality + Test coverage
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

#### Retrieval Triggers (v2.1 Enhanced)

| Phase | Trigger | Retrieved Content |
|-------|---------|------------------|
| Scene Analysis | Large feature detected | Domain knowledge, user journey patterns, use case templates |
| Understanding | Research starts | Module specs, existing code, technical docs |
| 1 | Design starts | Module specs, design patterns, domain rules, scene_analysis.md (if exists) |
| 1 (Decomposition) | Module boundary defined | nexus-query dependency analysis, module ownership rules |
| 1 (Architecture) | Module internal design | Layer patterns, component templates, test strategies |
| 1 | Interface defined | API rules, dependency module specs |
| 2 | Plan writing | Implementation rules, best practices |
| 3 | Code writing | Ownership rules, concurrency patterns, module internal architecture |
| 5 | Review | Review rules, quality standards, module decomposition specs |

#### Automatic Retrieval Process (v2.1 Large Feature)

```
User starts Scene Analysis Phase: "Order Management System"

Auto-retrieval:
1. Domain Knowledge:
   - docs/knowledge/domain/order-management.md
   - docs/knowledge/domain/payment-processing.md
   
2. Use Case Templates:
   - docs/knowledge/templates/use-case-template.md
   
3. User Journey Patterns:
   - docs/knowledge/design-patterns/user-journey.md

Output: "Based on retrieval:
- Order management follows DDD bounded context pattern
- User journey: Order → Payment → Notification
- See docs/knowledge/domain/order-management.md §2.1"
```

#### Automatic Retrieval Process (v2.0 Standard Feature)

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

**Agent should be able to answer:**
- What is the core architecture?
- What are Logger module's responsibilities and interfaces?
- What rules must I follow when designing?
- What is the current project state?

---

## Red Flags (Never Skip)

### v2.1 Red Flags (Large Features)

- ❌ **Never** skip Scene Analysis Phase for large features (complexity >= HIGH)
- ❌ **Never** proceed to Understanding without user confirming scene_analysis.md
- ❌ **Never** skip Module Decomposition Workshop for features with >3 modules
- ❌ **Never** proceed to Phase 2 without nexus-query dependency validation
- ❌ **Never** skip Module Internal Architecture Design for large features
- ❌ **Never** proceed without user confirming module internal design
- ❌ **Never** violate Bounded Context definitions during implementation

### Standard Red Flags (v2.0)

- ❌ **Never** skip Phase 1 design review
- ❌ **Never** proceed without user confirmation at each gate
- ❌ **Never** skip Constitution 合规检查 (ConstitutionEnforcer)
- ❌ **Never** ignore LoopDetection 警告 (LoopDetectionMiddleware)
- ❌ **Never** mark Phase 5 complete without all 4 artifacts
- ❌ **Never** mark Phase 5 complete without ArtifactCompleteMiddleware verification
- ❌ **Never** claim implementation complete without build passing
- ❌ **Never** skip memory persistence (Phase 6)

## Context Continuity Protocol (上下文连续性协议)

> ⚠️ **关键**: 这是解决"长会话讨论上下文丢失"问题的核心机制。

### 问题

LLM 上下文窗口有限。长会话（特别是 Phase 3 多文件开发阶段）会积累大量编辑历史，
导致早期的需求讨论、设计决策被挤出上下文窗口。当 `sdd resume` 恢复会话时，
新的 LLM 实例对之前做了什么、为什么做一无所知。

### 三层防护机制

```
Layer 1: 实时保存 (Phase 内)
    ConversationMemory 每个 checkpoint 都持久化
    ├── 需求捕获 → MemoryNode(type=REQUIREMENT)
    ├── 设计决策 → MemoryNode(type=DESIGN_DECISION)
    ├── 研究发现 → MemoryNode(type=RESEARCH_FINDING)
    ├── 约束条件 → MemoryNode(type=CONSTRAINT)
    └── 待解决问题 → MemoryNode(type=OPEN_QUESTION)

Layer 2: Phase 边界压缩 (Phase 间)
    每个 Phase 完成时生成该阶段的结构化摘要
    ├── Phase 1 结束 → 设计摘要（需求、架构、约束）
    ├── Phase 2 结束 → 计划摘要（任务、文件范围、执行方式）
    ├── Phase 3 结束 → 实现摘要（新建/修改文件列表、关键决策）
    ├── Phase 4 结束 → 测试摘要（通过/失败/跳过）
    └── Phase 5 结束 → 审查摘要（4 个制品的存在状态）

Layer 3: AGENTS.md 全量快照 (Phase 6)
    Phase 6 生成完整的 AGENTS.md
    ├── 特性状态
    ├── 全部需求
    ├── 架构设计决策
    ├── 实现文件列表
    ├── 审查制品状态
    ├── 对话记忆摘要
    └── 恢复指引
```

### Phase 边界压缩规范

**在进入下一个 Phase 之前，AI 必须将当前 Phase 的完整内容缩减为结构化摘要。**

#### 摘要格式要求

| Phase | 压缩产出 | 存储位置 |
|-------|---------|---------|
| Understanding → 1 | 研究摘要 + 关键决策 | `findings.md Phase 0 section` |
| 1 → 2 | 设计方案摘要 | `findings.md Phase 1 section` |
| 2 → 3 | 实现计划摘要 + File Changes Scope | `findings.md Phase 2 section` |
| 3 → 4 | 实际文件变更列表 | `findings.md Phase 3 section` |
| 4 → 5 | 测试结果摘要 | `findings.md Phase 4 section` |
| 5 → 6 | 审查问题清单 | `findings.md Phase 5 section` |

#### 摘要内容要求

每个摘要必须包含以下要素才能被认定为有效：

```
1. 本阶段完成了什么 (What was done)
2. 做出了什么关键决策 (Key decisions made)
3. 发现了什么问题 (Issues discovered)
4. 哪些问题留待后续解决 (Pending items)
5. 下一阶段需要注意什么 (Notes for next phase)
```

#### 执行时机

```
Phase Gate 检查通过
    ↓
用户确认进入下一 Phase
    ↓
AI 生成当前 Phase 的结构化摘要 ← 必须执行
    ↓
摘要写入对应文件 (findings.md unified document)
    ↓
ConversationMemory 同步持久化
    ↓
开始下一 Phase
```

### sdd resume 上下文恢复流程

```
sdd resume <feature>
    ↓
1. 读取 AGENTS.md (Phase 6 全量快照)
    ↓
2. 读取 ConversationMemory (结构化记忆节点)
    ↓
3. 读取 feature artifacts (task_plan / findings / progress)
    ↓
4. 组合为 injected_context 注入到 ExecutionContext
    ↓
5. LLM 获得上一会话的完整上下文
    ↓
6. 从上次中断的 Phase 继续
```

**恢复后的 LLM 应该能够回答以下问题：**
- 这个特性的目标是什么？
- 已经完成了哪些 Phase？当前在哪个 Phase？
- 做了哪些设计决策？为什么？
- 创建/修改了哪些文件？
- 有哪些未解决的问题需要关注？
- 下一步应该做什么？

### 上下文溢出主动管理

在单次会话中，ContextMonitor 自动追踪并强制执行上下文刷新：

| 信号 | 触发条件 | 动作 | 执行方式 |
|------|---------|------|---------|
| 累计编辑 >20 次 | `ContextMonitor.should_refresh()` | 打印上下文摘要到 stdout，LLM 重新获得需求/设计/约束 | 🔧 自动 |
| 完成 >3 个 task | `ContextMonitor.record_task()` | 同上 | 🔧 自动 |
| 同一文件编辑 >5 次 | LoopDetectionMiddleware 联动 | 警告 + 触发上下文刷新 | 🔧 自动 |
| 进入 Phase 3 | Phase3Orchestrator | 强制上下文刷新（确保 LLM 在大量编辑前有完整上下文） | 🔧 自动 |
| 进入 Phase 4/5 | Phase4/5Orchestrator | 检查并刷新上下文（Phase 3 可能已丢失上下文） | 🔧 自动 |
| 用户说"之前讨论的"但 AI 无法定位 | 手动 | 运行 `sdd resume` 重新注入 AGENTS.md 上下文 | 👤 手动 |

**ContextMonitor 刷新内容:**
1. 特性目标（从 task_plan.md）
2. 关键需求与约束（从 findings.md Phase 0）
3. 架构设计决策（从 design-doc.md）
4. 当前进度（从 findings.md latest phase section）
5. 高频编辑文件列表（含编辑次数）
6. 一致性检查提示："以上需求和设计决策是否仍然一致？"

**主动压缩格式** (AI 在自己思考中执行):
```
[CONTEXT COMPRESSION]
Phase: 3 (Module Development)
Progress: Task 3/7 completed
Key decisions: (列出最近 3 个决策)
Files modified: (列出最近修改的文件)
Current blocker: (如果有)
Next: Task 4 - (任务描述)
[/CONTEXT COMPRESSION]
```

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
| **planning-with-files** | 1, 2, 6 | Memory artifacts | Create/update task_plan.md, findings.md, findings.md (relevant section) |
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
│   └── planning-with-files: update findings.md (relevant section) per task
├── If executing-plans:
│   ├── using-git-worktrees: create isolated branch
│   ├── executing-plans: sequential execution
│   ├── test-driven-development: define test strategy
│   ├── rust-best-practices: Rust-specific implementation
│   ├── planning-with-files: update findings.md (relevant section) per task
│   └── systematic-debugging: if build fails
└── [GATE: Build succeeds]

PHASE 4: Integration & Testing (verification-before-completion)
├── verification-before-completion: run full test suite
├── systematic-debugging: if tests fail
├── planning-with-files: update findings.md (relevant section) with results
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
├── Finalize findings.md (relevant section)
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
- Called when creating/updating task_plan.md, findings.md, findings.md (relevant section)

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