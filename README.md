# SDD-Workflow

面向开发者的 AI 辅助软件开发生命周期管理工具。

## 开发者如何使用

### 1. 初始化项目（每个项目只执行一次）

```bash
sdd init
```

创建项目目录结构、初始化内存制品、建立架构知识图谱。

**检查初始化状态：**
```bash
sdd check-init
```

### 2. 启动功能开发

```bash
sdd start <feature-name>
```

AI Agent 自动执行 6 阶段流程，每阶段等待开发者确认。

### 3. 中断后继续

```bash
sdd resume                    # 继续上一个特性
sdd resume <feature-name>     # 继续指定特性
```

从上次中断的阶段继续开发。如果不指定特性名，显示所有进行中的特性列表供选择。

### 4. 查看开发状态

```bash
sdd status
```

显示所有 6 个阶段的完成状态。

### 5. 查看知识图谱

```bash
sdd graph
```

显示现有知识图谱结构，或生成新的 .nexus-map/ 目录。

### 6. 多特性开发

可以同时开发多个特性，每个特性独立跟踪：

```bash
sdd start feature-a      # 开发者 A 开始特性 A
sdd start feature-b      # 开发者 B 开始特性 B
sdd resume feature-a     # 继续特性 A
sdd status               # 查看所有特性进度
```

**多开发者支持**：
- 每个特性有独立的 `status.toml` 记录开发者
- 每个特性有独立的内存制品（task_plan.md, findings.md, progress.md）
- 不同开发者可以同时开发不同特性，互不干扰
- `PROJECT_STATE.md` 聚合所有特性状态

**状态示例**：
```toml
# docs/features/custom-format/status.toml
[feature]
name = "custom-format"
developer = "@zhangsan"
current_phase = 3
```

### 7. 完成 workflow

```bash
sdd complete
```

强制执行 Phase 5 Review 和 Phase 6 Persistence，用于结束开发分支。

### 8. 查看帮助

```bash
sdd help
```

显示所有可用命令的说明。

## 开发者关注点

### 每个阶段的确认门控

开发者在每个阶段结束时需要做决定：

| 阶段 | 开发者需要确认的内容 |
|------|---------------------|
| **Phase 1** | Review 设计文档，确认 "Design approved, proceed to Phase 2" |
| **Phase 2** | Review 实现计划，选择执行模式（subagent-driven 或 sequential），确认 "Plan approved, proceed to Phase 3" |
| **Phase 3** | 确认编译通过和单元测试完成，确认 "Phase 3 complete, proceed to Phase 4" |
| **Phase 4** | 确认集成测试通过（或同意跳过），确认 "Phase 4 complete, proceed to Phase 5" |
| **Phase 5** | Review 代码审查报告，确认 "Phase 5 complete, proceed to Phase 6" |
| **Phase 6** | 自动完成，无需干预 |

### 开发者职责

- **提供需求**: 清晰描述要开发的功能
- **Review 设计**: Phase 1 结束时审查 AI 生成的设计文档
- **Review 计划**: Phase 2 结束时审查实现计划
- **做决定**: 在每个门控点明确批准或要求修改
- **最终验收**: 功能开发完成后进行最终确认

### 开发者不需要关注

- 代码编写细节（AI 自动完成）
- 项目结构创建（自动初始化）
- 文档生成（自动维护）
- 代码审查报告（自动生成 4 个制品）

## 6 阶段流程

```
用户需求 → Phase 1 设计 → Phase 2 规划 → Phase 3 开发 
        → Phase 4 测试 → Phase 5 审查 → Phase 6 归档
```

### Phase 1: 需求分析
AI 通过提问理解需求，生成设计文档。

**开发者**: 回答问题，review 并批准设计

### Phase 2: 实现规划
AI 生成详细的实现计划，包括任务拆分。

**开发者**: 选择执行模式（并行/串行），review 并批准计划

### Phase 3: 模块开发
AI 按计划执行代码编写，使用 git worktree 隔离。

**开发者**: 确认编译成功和单元测试通过

### Phase 4: 集成测试
AI 运行完整测试套件。

**开发者**: 确认测试通过（或同意环境限制导致的跳过）

### Phase 5: 代码审查
AI 自动生成 4 个审查制品。

**开发者**: review 审查报告，确认开发质量

### Phase 6: 记忆持久化
AI 自动更新项目状态和知识图谱。

**开发者**: 无需干预

## 项目文件结构

```
project/
├── CONSTITUTION/                     # Layer 1: 最高准则
│   ├── README.md                    # Constitution 索引
│   ├── core.md                      # 核心原则（不可变更）
│   ├── module-ownership.md         # 模块所有权定义
│   ├── design-rules.md              # 设计规则
│   ├── implementation-rules.md      # 实现规则
│   ├── review-rules.md              # 审查规则
│   ├── communication-protocols.md   # 开发者沟通协议
│   └── decision-records/            # 架构决策记录
│
├── .nexus-map/                      # Layer 2: 架构知识（AI 自动加载）
│   ├── INDEX.md                    # 架构索引
│   ├── systems.md                  # 系统概览
│   ├── concept_model.json          # 概念模型（机器可读）
│   ├── module-graph.md             # 模块依赖图
│   └── module-specs/               # 模块规格
│
├── docs/
│   ├── knowledge/                   # Layer 3: 知识库
│   │   ├── rust-best-practices/   # Rust 最佳实践
│   │   ├── design-patterns/        # 设计模式
│   │   ├── security/              # 安全规则
│   │   ├── performance/           # 性能规则
│   │   └── domain/               # 领域规则
│   │
│   ├── modules/                    # Layer 4: 模块设计
│   │   ├── README.md
│   │   └── [module-name]/
│   │       ├── SPEC.md           # 模块规格
│   │       ├── IMPLEMENTATION.md # 实现细节
│   │       ├── TESTS.md          # 测试策略
│   │       └── OWNERS.md         # 模块负责人
│   │
│   ├── features/                   # Layer 5: 功能设计
│   │   ├── README.md
│   │   └── [feature-name]/
│   │       ├── SPEC.md           # 功能规格
│   │       ├── MODULES.md        # 模块变更
│   │       ├── API-CHANGES.md   # API 变更
│   │       ├── DEPENDENCIES.md  # 依赖
│   │       ├── REVIEW.md        # 设计审查
│   │       ├── status.toml      # 特性状态（Phase、开发者）
│   │       ├── task_plan.md     # 特性任务进度
│   │       ├── findings.md      # 特性研究发现
│   │       ├── progress.md      # 特性执行日志
│   │       └── reviews/         # 审查报告
│   │           ├── architecture_review.md
│   │           ├── code_quality_review.md
│   │           ├── test_coverage_report.md
│   │           └── requirements_verification.md
│   │
│   ├── superpowers/                # Layer 6: SDD 工作流文档
│   │   ├── specs/                # Phase 1 产出
│   │   └── plans/                # Phase 2 产出
│   │
│   └── collaboration/             # Layer 7: 团队协作
│       ├── feature-matrix.md     # 特性-模块矩阵
│       ├── module-owners.md      # 模块负责人列表
│       └── decision-log.md       # 决策日志
│
├── PROJECT_STATE.md                 # 项目当前状态（所有特性聚合）
└── AGENTS.md                       # AI 持久化上下文（当前特性）
```

### 层级说明

| Layer | 目录 | 用途 |
|-------|------|------|
| 1 | `CONSTITUTION/` | 最高准则，所有阶段必须遵守 |
| 2 | `.nexus-map/` | AI 自动加载的架构知识 |
| 3 | `docs/knowledge/` | 可检索的知识库 |
| 4 | `docs/modules/` | 模块规格和实现 |
| 5 | `docs/features/<f>/` | **特性级别**：规格、进度、制品 |
| 6 | `docs/superpowers/` | SDD 工作流产出 |
| 7 | `docs/collaboration/` | 团队协作文档 |
| - | `PROJECT_STATE.md` | 项目级聚合视图 |
| - | `AGENTS.md` | 当前特性 AI 上下文 |
| 7 | `docs/collaboration/` | 团队协作文档 |

## 核心机制

### Constitution（项目准则）

项目根目录的 `CONSTITUTION/` 定义了所有设计、实现必须遵守的规则：

| 文件 | 内容 |
|------|------|
| `core.md` | 核心原则（不可变更） |
| `module-ownership.md` | 模块所有权定义 |
| `design-rules.md` | 设计阶段规则 |
| `implementation-rules.md` | 实现阶段规则 |
| `review-rules.md` | 审查规则 |

**合规检查**: AI 在 Phase 1、2、3 会自动检查设计与代码是否符合 Constitution 规则。

### 知识检索

AI 在各阶段会自动检索相关文档：

| 阶段 | 触发时机 | 检索内容 |
|------|---------|---------|
| Phase 1 | 设计开始 | 模块规格、设计模式、领域规则 |
| Phase 2 | 编写计划 | 实现规则、最佳实践 |
| Phase 3 | 编写代码 | 所有权规则、并发模式 |
| Phase 5 | 代码审查 | 审查规则、质量标准 |

### 特性-模块矩阵

`docs/collaboration/feature-matrix.md` 记录特性与模块的映射关系：

| 特性 | 模块 A | 模块 B | 模块 C |
|------|--------|--------|--------|
| feature-a | ✓ | ✓ | - |
| feature-b | - | △ | ✓ |

### 模块所有权

每个模块有明确的 owner 和职责边界。模块规格定义在 `docs/modules/<name>/SPEC.md`。

### 内存制品

Phase 6 自动维护的 5 个核心文件：

| 文件 | 描述 |
|------|------|
| `PROJECT_STATE.md` | 项目当前状态 |
| `AGENTS.md` | AI 持久化上下文 |
| `task_plan.md` | 任务进度跟踪 |
| `findings.md` | 研究发现和决策 |
| `progress.md` | 开发执行日志 |

### 审查制品

Phase 5 自动生成的 4 个审查报告：

| 文件 | 描述 |
|------|------|
| `docs/reviews/architecture_review.md` | 架构合规性审查 |
| `docs/reviews/code_quality_review.md` | 代码质量审查 |
| `docs/reviews/test_coverage_report.md` | 测试覆盖率报告 |
| `docs/reviews/requirements_verification.md` | 需求验证报告 |

## 安装

```bash
git clone git@github.com:shangguan1024/sdd-workflow.git ~/.config/opencode/skills/sdd-workflow
```

opencode 会自动加载该技能。
