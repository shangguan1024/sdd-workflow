# SDD-Workflow

面向开发者的 AI 辅助软件开发生命周期管理工具。

## 开发者如何使用

### 1. 启动功能开发

```bash
sdd start <feature-name>
```

AI Agent 自动执行 6 阶段流程，每阶段等待开发者确认。

### 2. 中断后继续

```bash
sdd resume
```

从上次中断的阶段继续开发。

### 3. 查看开发状态

```bash
sdd status
```

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
├── CONSTITUTION/           # 项目准则（架构、设计、编码规则）
├── .nexus-map/            # 架构知识图谱
├── docs/
│   ├── modules/           # 模块规格说明
│   ├── features/          # 功能规格说明
│   ├── superpowers/       # SDD 工作流文档
│   └── collaboration/     # 团队协作文档
├── PROJECT_STATE.md       # 项目当前状态
├── AGENTS.md             # AI 持久化上下文
├── task_plan.md          # 任务进度跟踪
├── findings.md           # 研究发现
└── progress.md          # 开发日志
```

## 安装

```bash
git clone git@github.com:shangguan1024/sdd-workflow.git ~/.config/opencode/skills/sdd-workflow
```

opencode 会自动加载该技能。
