# SDD-Workflow v2.0 改造设计

**Version:** 1.0  
**Date:** 2026-04-11  
**Author:** SDD-Workflow Team  
**Status:** Approved

---

## 1. 概述

### 1.1 背景

当前 SDD-Workflow v1.0 存在以下问题：

- `workflow_coordinator.py` 单文件 1207 行，职责混杂
- Checkpoint 机制缺失或简单，无法有效恢复长会话
- Quality Gate 功能基础，缺乏完整的质量保障体系
- 规则系统扩展性差，难以适应不同团队需求

### 1.2 目标

将 SDD-Workflow 重构为分层架构，提高可维护性、可扩展性和质量保障能力。

### 1.3 改造原则

- **自顶向下**：先完成整体架构设计，再逐步实现各层
- **改造现有代码**：基于现有代码演进，而非推倒重来
- **保持兼容性**：确保现有命令和接口不变

---

## 2. 分层架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      SDD-Workflow v2.0                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 0: CLI Entry (cli.py)                               │
│  └── 命令行解析、用户交互                                    │
│                                                              │
│  Layer 1: Director (director.py)                             │
│  └── 状态机管理、Gate 控制、流程编排                          │
│                                                              │
│  Layer 2: Phase Orchestrators (phases/)                     │
│  └── 每个 Phase 的标准流程定义                               │
│                                                              │
│  Layer 3: Capability Registry (capabilities/)                │
│  └── 可插拔的能力模块注册与发现                              │
│                                                              │
│  Supporting:                                                 │
│  ├── checkpoint/ (多层持久化)                               │
│  ├── harness/ (质量保障)                                   │
│  └── rules/ (规则扩展)                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 目录结构

```
sdd-workflow/
├── SKILL.yaml                 # Skill 元数据
├── SKILL.md                   # 主文档
├── bin/                       # CLI 入口脚本
│   ├── sdd.ps1
│   ├── sdd.cmd
│   └── sdd.bat
│
├── src/                       # 源代码 (新增)
│   ├── __init__.py
│   ├── cli.py                # Layer 0: CLI 入口
│   ├── director.py            # Layer 1: 主状态机
│   │
│   ├── phases/               # Layer 2: Phase Orchestrator
│   │   ├── __init__.py
│   │   ├── base.py           # 基类 PhaseOrchestrator
│   │   ├── phase1.py         # Requirements Analysis
│   │   ├── phase2.py         # Implementation Planning
│   │   ├── phase3.py         # Module Development
│   │   ├── phase4.py         # Integration & Testing
│   │   ├── phase5.py         # Code Quality Review
│   │   └── phase6.py         # Memory Persistence
│   │
│   ├── checkpoint/            # 多层 Checkpoint 机制
│   │   ├── __init__.py
│   │   ├── manager.py        # Checkpoint 管理器
│   │   ├── persistence.py   # 持久化
│   │   └── recovery.py       # 恢复机制
│   │
│   ├── harness/              # Quality Harness
│   │   ├── __init__.py
│   │   ├── collectors.py     # 指标收集器
│   │   ├── analyzers.py      # 分析引擎
│   │   ├── gate_engine.py   # 门禁判定
│   │   └── reporters.py      # 报告生成
│   │
│   ├── capabilities/         # Capability Registry
│   │   ├── __init__.py
│   │   ├── registry.py       # 注册发现
│   │   └── selection.py      # 选择引擎
│   │
│   └── rules/                # 规则扩展
│       ├── __init__.py
│       ├── parser_md.py      # MD 解析器
│       ├── parser_yaml.py    # YAML 解析器
│       └── checker.py        # 规则检查器
│
├── scripts/                   # 现有脚本 (保留)
│   ├── workflow_coordinator.py
│   └── ...
│
├── middleware/                 # 中间件 (保留)
│   └── __init__.py
│
├── config/                     # 配置 (扩展)
│   └── harness_gates.yaml     # Quality Gate 配置
│
└── docs/                       # 文档 (新增)
    └── specs/
        └── 2026-04-11-sdd-workflow-v2-redesign.md
```

---

## 3. 各层详细设计

### 3.1 Layer 0: CLI Entry

```python
# src/cli.py

class CLI:
    """CLI 入口，负责命令解析和用户交互"""
    
    COMMANDS = ["init", "start", "resume", "status", "complete", "help"]
    
    def parse(self, args: list[str]) -> Command:
        """解析命令行参数"""
        ...
    
    def execute(self, command: Command) -> Result:
        """执行命令"""
        ...
```

**职责：**
- 解析 `sdd init/start/resume/status/complete` 命令
- 调用 Director 执行相应逻辑
- 格式化输出结果

### 3.2 Layer 1: Director

```python
# src/director.py

class Director:
    """主状态机，负责流程编排和 Gate 控制"""
    
    def __init__(self, project_root: Path):
        self.state_machine = StateMachine()
        self.gate_controller = GateController()
        self.phase_orchestrators = self._init_phase_orchestrators()
    
    def execute_feature_workflow(self, feature: str) -> WorkflowResult:
        """执行完整的特性工作流"""
        ...
    
    def transition_to_phase(self, phase: Phase) -> TransitionResult:
        """Phase 转换，执行 Gate 检查"""
        ...
```

**职责：**
- 管理全局状态机
- 控制 Phase 间 Gate
- 协调 Phase Orchestrator
- 调用 Capability Registry

### 3.3 Layer 2: Phase Orchestrator

```python
# src/phases/base.py

class PhaseOrchestrator(ABC):
    """Phase Orchestrator 基类"""
    
    @abstractmethod
    def execute(self, context: ExecutionContext) -> PhaseResult:
        """执行 Phase"""
        pass
    
    @abstractmethod
    def can_transition_to(self, context: ExecutionContext) -> TransitionCheck:
        """检查是否可以进入下一 Phase"""
        pass

# src/phases/phase1.py

class Phase1Requirements(PhaseOrchestrator):
    """Phase 1: Requirements Analysis"""
    
    STEPS = [
        "explore_context",
        "analyze_existing_code",
        "gather_requirements",
        "generate_design",
        "impact_analysis",
        "expert_knowledge",
        "constitution_check",
        "user_approval",
    ]
    
    def __init__(self, capability: BrainstormCapability):
        self.capability = capability
        self.checkpoint_manager = CheckpointManager()
```

**职责：**
- 定义每个 Phase 的标准流程
- 管理 Phase 内的 Step
- 调用 Capability 执行具体任务
- 触发 Checkpoint

### 3.4 Layer 3: Capability Registry

```python
# src/capabilities/registry.py

class CapabilityRegistry:
    """可插拔能力模块注册表"""
    
    def __init__(self, skills_dir: Path):
        self.capabilities = {}
        self.load_all(skills_dir)
    
    def register(self, capability: Capability):
        """注册 Capability"""
        self.capabilities[capability.id] = capability
    
    def select(self, rules: SelectionRules) -> Capability:
        """根据规则选择 Capability"""
        ...
    
    def list_by_type(self, cap_type: CapabilityType) -> list[CapabilityMeta]:
        """列出指定类型的所有 Capability"""
        ...
```

**职责：**
- 管理 Capability 注册与发现
- 根据规则选择合适的 Capability
- 支持 Capability 热插拔

### 3.5 Checkpoint 机制

```python
# src/checkpoint/manager.py

class CheckpointManager:
    """多层 Checkpoint 管理器"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.real_time = RealTimeCheckpoint()
        self.phase_level = PhaseLevelCheckpoint()
        self.feature_level = FeatureLevelCheckpoint()
    
    def save(
        self,
        checkpoint_type: CheckpointType,
        context: ExecutionContext,
    ):
        """保存 Checkpoint"""
        ...
    
    def recover(self, checkpoint_id: str) -> ExecutionContext:
        """从 Checkpoint 恢复"""
        ...

class RealTimeCheckpoint:
    """实时层：每轮对话、每个用户决策自动保存"""
    
    def save(self, context: ExecutionContext):
        """保存到 AGENTS.md"""
        ...

class PhaseLevelCheckpoint:
    """阶段层：每个 Step 完成时保存"""
    
    def save(self, feature: str, phase: Phase, step: str):
        """保存到 feature/.sdd/checkpoints/"""
        ...

class FeatureLevelCheckpoint:
    """持久层：Phase 完成、特性完成时保存"""
    
    def save(self, feature: str, artifacts: dict):
        """保存到 PROJECT_STATE.md"""
        ...
```

### 3.6 Quality Harness

```python
# src/harness/collectors.py

class Collector(ABC):
    """指标收集器基类"""
    
    @abstractmethod
    async def collect(self, context: CollectionContext) -> MetricData:
        pass

class CoverageCollector(Collector):
    """覆盖率收集器"""

class ComplexityCollector(Collector):
    """复杂度收集器"""

class SecurityCollector(Collector):
    """安全扫描收集器"""

# src/harness/gate_engine.py

class GateEngine:
    """门禁判定引擎"""
    
    def __init__(self, config: GatesConfig):
        self.rules = self._load_rules(config)
    
    def evaluate(self, phase: Phase, metrics: list[MetricData]) -> GateResult:
        """评估门禁"""
        ...
```

### 3.7 规则扩展

```python
# src/rules/parser_md.py

class MarkdownRuleParser:
    """Markdown 规则解析器"""
    
    def parse(self, content: str) -> ParsedRules:
        """解析 Markdown 格式的规则"""
        # 1. 解析 frontmatter
        # 2. 解析表格定义的规则
        # 3. 解析代码块中的 YAML
        ...

# src/rules/checker.py

class RuleChecker:
    """规则检查器"""
    
    def __init__(self, rules: list[Rule]):
        self.rules = rules
    
    def check(self, code: str, context: CodeContext) -> list[Finding]:
        """检查代码是否符合规则"""
        ...
```

---

## 4. 改造顺序

### Phase 1: 基础架构 (优先级最高)
1. 创建 `src/` 目录结构
2. 实现 Layer 0: CLI
3. 实现 Layer 1: Director
4. 实现 Layer 2: PhaseOrchestrator 基类

### Phase 2: Checkpoint 机制
5. 实现 `checkpoint/manager.py`
6. 实现 `checkpoint/persistence.py`
7. 实现 `checkpoint/recovery.py`

### Phase 3: Quality Harness
8. 实现 `harness/collectors.py`
9. 实现 `harness/analyzers.py`
10. 实现 `harness/gate_engine.py`
11. 创建 `config/harness_gates.yaml`

### Phase 4: Capability Registry
12. 实现 `capabilities/registry.py`
13. 实现 `capabilities/selection.py`

### Phase 5: 规则扩展
14. 实现 `rules/parser_md.py`
15. 实现 `rules/parser_yaml.py`
16. 实现 `rules/checker.py`

### Phase 6: 迁移与集成
17. 迁移现有 `workflow_coordinator.py` 逻辑到各层
18. 更新 `bin/` 脚本调用新架构
19. 更新文档

---

## 5. 兼容性保证

### 5.1 命令兼容性

所有现有命令保持不变：
- `sdd init`
- `sdd start <feature>`
- `sdd resume [feature]`
- `sdd status`
- `sdd complete`

### 5.2 配置兼容性

现有配置文件继续有效：
- `SKILL.yaml`
- `config/*.yaml`

### 5.3 目录结构兼容性

现有目录结构保持不变：
- `CONSTITUTION/`
- `.nexus-map/`
- `docs/features/`
- `PROJECT_STATE.md`
- `AGENTS.md`

---

## 6. 验收标准

### 6.1 功能验收

- [ ] 所有现有命令正常工作
- [ ] 分层架构正确实现
- [ ] Checkpoint 可保存和恢复
- [ ] Quality Gate 正确判定
- [ ] 规则可正确加载和检查

### 6.2 质量验收

- [ ] `workflow_coordinator.py` 拆分为独立模块
- [ ] 每个模块职责单一
- [ ] 模块间通过接口通信
- [ ] 单元测试覆盖关键逻辑

---

## 7. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 改造过程中功能退化 | 高 | 分阶段改造，每阶段验证 |
| 现有逻辑丢失 | 高 | 保留原文件，逐步迁移 |
| 性能下降 | 中 | 优化模块间调用 |

---

*文档版本: 1.0 | 状态: Approved*
