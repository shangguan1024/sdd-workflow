# SDD-Workflow v2.0 实现计划

**Version:** 1.0  
**Date:** 2026-04-11  
**Based on:** `2026-04-11-sdd-workflow-v2-redesign.md`  
**Status:** Draft

---

## 1. 概述

### 1.1 目标

将 SDD-Workflow 从单文件架构重构为分层模块化架构。

### 1.2 改造范围

- 创建 `src/` 目录结构
- 实现 Layer 0-3 核心模块
- 实现 Checkpoint 机制
- 实现 Quality Harness
- 实现规则扩展系统
- 迁移现有逻辑

---

## 2. 任务分解

### 2.1 Phase 1: 基础架构

| ID | 任务 | 文件变更 | 依赖 |
|----|------|----------|------|
| T1.1 | 创建 src/ 目录结构 | `src/__init__.py`, `src/phases/__init__.py`, etc. | - |
| T1.2 | 实现 Layer 0: CLI | `src/cli.py` | T1.1 |
| T1.3 | 实现 Layer 1: Director | `src/director.py` | T1.1 |
| T1.4 | 实现 PhaseOrchestrator 基类 | `src/phases/base.py` | T1.3 |
| T1.5 | 实现 StateMachine | `src/state_machine.py` | T1.3 |
| T1.6 | 实现 GateController | `src/gate_controller.py` | T1.3 |

### 2.2 Phase 2: Checkpoint 机制

| ID | 任务 | 文件变更 | 依赖 |
|----|------|----------|------|
| T2.1 | 实现 CheckpointManager | `src/checkpoint/manager.py` | T1.3 |
| T2.2 | 实现 Persistence | `src/checkpoint/persistence.py` | T2.1 |
| T2.3 | 实现 Recovery | `src/checkpoint/recovery.py` | T2.2 |
| T2.4 | 实现 RealTimeCheckpoint | `src/checkpoint/real_time.py` | T2.1 |
| T2.5 | 实现 PhaseLevelCheckpoint | `src/checkpoint/phase_level.py` | T2.1 |

### 2.3 Phase 3: Quality Harness

| ID | 任务 | 文件变更 | 依赖 |
|----|------|----------|------|
| T3.1 | 实现 Collector 基类 | `src/harness/collectors.py` | T1.3 |
| T3.2 | 实现 CoverageCollector | `src/harness/collectors/coverage.py` | T3.1 |
| T3.3 | 实现 ComplexityCollector | `src/harness/collectors/complexity.py` | T3.1 |
| T3.4 | 实现 GateEngine | `src/harness/gate_engine.py` | T3.1 |
| T3.5 | 实现 Reporter | `src/harness/reporters.py` | T3.4 |
| T3.6 | 创建 harness_gates.yaml | `config/harness_gates.yaml` | T3.4 |

### 2.4 Phase 4: Capability Registry

| ID | 任务 | 文件变更 | 依赖 |
|----|------|----------|------|
| T4.1 | 实现 CapabilityRegistry | `src/capabilities/registry.py` | T1.3 |
| T4.2 | 实现 CapabilitySelection | `src/capabilities/selection.py` | T4.1 |
| T4.3 | 实现 BaseCapability | `src/capabilities/base.py` | T4.1 |

### 2.5 Phase 5: 规则扩展

| ID | 任务 | 文件变更 | 依赖 |
|----|------|----------|------|
| T5.1 | 实现 MarkdownRuleParser | `src/rules/parser_md.py` | T1.3 |
| T5.2 | 实现 YamlRuleParser | `src/rules/parser_yaml.py` | T5.1 |
| T5.3 | 实现 RuleChecker | `src/rules/checker.py` | T5.1 |
| T5.4 | 创建示例规则文件 | `config/rules_example.md` | T5.1 |

### 2.6 Phase 6: Phase 实现

| ID | 任务 | 文件变更 | 依赖 |
|----|------|----------|------|
| T6.1 | 实现 Phase1Orchestrator | `src/phases/phase1.py` | T1.4 |
| T6.2 | 实现 Phase2Orchestrator | `src/phases/phase2.py` | T1.4 |
| T6.3 | 实现 Phase3Orchestrator | `src/phases/phase3.py` | T1.4 |
| T6.4 | 实现 Phase4Orchestrator | `src/phases/phase4.py` | T1.4 |
| T6.5 | 实现 Phase5Orchestrator | `src/phases/phase5.py` | T1.4 |
| T6.6 | 实现 Phase6Orchestrator | `src/phases/phase6.py` | T1.4 |

### 2.7 Phase 7: 迁移与集成

| ID | 任务 | 文件变更 | 依赖 |
|----|------|----------|------|
| T7.1 | 迁移 workflow_coordinator.py 逻辑 | - | T1-T6 |
| T7.2 | 更新 bin/ 脚本 | `bin/sdd.ps1`, `bin/sdd.cmd` | T7.1 |
| T7.3 | 更新 SKILL.md | `SKILL.md` | T7.1 |
| T7.4 | 更新 USAGE.md | `USAGE.md` | T7.1 |

---

## 3. 执行计划

### 3.1 执行顺序

```
Week 1: Phase 1 (基础架构)
├── Day 1-2: T1.1-T1.3 (目录结构, CLI, Director)
└── Day 3-5: T1.4-T1.6 (PhaseOrchestrator, StateMachine, GateController)

Week 2: Phase 2 (Checkpoint)
├── Day 1-3: T2.1-T2.3 (Manager, Persistence, Recovery)
└── Day 4-5: T2.4-T2.5 (RealTime, PhaseLevel)

Week 3: Phase 3 (Quality Harness)
├── Day 1-2: T3.1 (Collector 基类)
├── Day 3-4: T3.2-T3.3 (Coverage, Complexity)
└── Day 5: T3.4-T3.6 (GateEngine, Reporter, 配置)

Week 4: Phase 4-5 (Capability & 规则)
├── Day 1-2: T4.1-T4.3 (Capability Registry)
└── Day 3-5: T5.1-T5.4 (规则扩展)

Week 5: Phase 6 (Phase 实现)
└── Day 1-5: T6.1-T6.6 (各 Phase Orchestrator)

Week 6: Phase 7 (迁移与集成)
├── Day 1-2: T7.1 (迁移逻辑)
├── Day 3-4: T7.2-T7.3 (更新脚本和文档)
└── Day 5: T7.4 (最终更新)
```

### 3.2 里程碑

| Milestone | 完成条件 | 目标日期 |
|-----------|----------|----------|
| M1: 基础架构完成 | Layer 0-1 可用 | Week 1 末 |
| M2: Checkpoint 完成 | 可保存和恢复 | Week 2 末 |
| M3: Harness 完成 | Quality Gate 可用 | Week 3 末 |
| M4: 功能完整 | 所有模块可用 | Week 5 末 |
| M5: 发布 v2.0 | 文档更新，测试通过 | Week 6 末 |

---

## 4. 验证计划

### 4.1 构建验证

```bash
# 验证 Python 语法
python -m py_compile src/**/*.py

# 验证导入
python -c "from src import CLI, Director"
```

### 4.2 功能验证

| 测试 | 命令 | 预期结果 |
|------|------|----------|
| CLI 帮助 | `sdd help` | 显示帮助信息 |
| 状态检测 | `sdd status` | 显示当前状态 |
| Phase 检测 | Python 测试 | 正确识别 Phase |

### 4.3 回归验证

确保现有命令不受影响：
- `sdd init`
- `sdd start <feature>`
- `sdd resume [feature]`
- `sdd status`
- `sdd complete`

---

## 5. 风险与缓解

| 风险 | 影响 | 概率 | 缓解 |
|------|------|------|------|
| 改造破坏现有功能 | 高 | 中 | 分阶段验证，每阶段测试 |
| 进度延迟 | 中 | 高 | 预留 buffer，定期检查 |
| 复杂度超预期 | 中 | 中 | 遇到复杂点及时沟通 |

---

## 6. 资源需求

| 资源 | 数量 | 说明 |
|------|------|------|
| 开发时间 | 6 周 | 每周约 20 小时 |
| 代码审查 | 2 人 | 每周 1 次 |
| 测试环境 | 1 | 独立测试项目 |

---

*计划版本: 1.0 | 状态: Ready for Approval*
