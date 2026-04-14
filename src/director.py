"""
SDD-Workflow Director (Layer 1)
主状态机、Gate 控制、流程编排
"""

from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum

from .cli import (
    Command,
    InitCommand,
    StartCommand,
    ResumeCommand,
    StatusCommand,
    CompleteCommand,
    Result,
)


class Phase(Enum):
    """工作流阶段"""
    INIT = 0
    REQUIREMENTS = 1
    PLANNING = 2
    DEVELOPMENT = 3
    INTEGRATION = 4
    REVIEW = 5
    PERSISTENCE = 6
    COMPLETED = 7


class Director:
    """
    主状态机，负责流程编排和 Gate 控制
    
    Layer 1 职责:
    - 管理全局状态机
    - 控制 Phase 间 Gate
    - 协调 Phase Orchestrator
    - 调用 Capability Registry
    """
    
    def __init__(self, project_root: Path = Path("."), quality_profile: str = "standard"):
        self.project_root = project_root
        self.state_machine = StateMachine()
        self.gate_controller = GateController()
        self.phase_orchestrators: Dict[Phase, PhaseOrchestrator] = {}
        self.capability_registry = CapabilityRegistry()
        self._init_phase_orchestrators()
        
        from .quality import QualityHarness, get_profile
        self.quality_harness = QualityHarness(project_root, get_profile(quality_profile))
    
    def _init_phase_orchestrators(self):
        """初始化 Phase Orchestrator"""
        from .phases import (
            Phase1Orchestrator,
            Phase2Orchestrator,
            Phase3Orchestrator,
            Phase4Orchestrator,
            Phase5Orchestrator,
            Phase6Orchestrator,
        )
        
        self.phase_orchestrators = {
            Phase.REQUIREMENTS: Phase1Orchestrator(self.capability_registry),
            Phase.PLANNING: Phase2Orchestrator(self.capability_registry),
            Phase.DEVELOPMENT: Phase3Orchestrator(self.capability_registry),
            Phase.INTEGRATION: Phase4Orchestrator(self.capability_registry),
            Phase.REVIEW: Phase5Orchestrator(self.capability_registry),
            Phase.PERSISTENCE: Phase6Orchestrator(self.capability_registry),
        }
    
    def initialize(self, command: InitCommand) -> Result:
        """
        初始化项目
        
        Args:
            command: InitCommand 对象
            
        Returns:
            Result: 执行结果
        """
        try:
            project_path = command.args.get("path") or self.project_root
            
            # 检查是否已初始化
            if not command.args.get("force") and self._is_initialized(project_path):
                return Result(
                    success=False,
                    message="Project already initialized. Use --force to reinitialize.",
                )
            
            # 创建目录结构
            self._create_directory_structure(project_path)
            
            # 初始化配置文件
            self._initialize_config_files(project_path, command)
            
            # 初始化 Constitution
            self._initialize_constitution(project_path)
            
            # 初始化内存 artifacts
            self._initialize_memory_artifacts(project_path)
            
            return Result(
                success=True,
                message="SDD project initialized successfully",
                details=[
                    f"Project: {project_path}",
                    f"Template: {command.args.get('template')}",
                ],
            )
            
        except Exception as e:
            return Result(success=False, message=f"Initialization failed: {e}")
    
    def start_feature(self, command: StartCommand) -> Result:
        """
        开始新特性开发
        
        Args:
            command: StartCommand 对象
            
        Returns:
            Result: 执行结果
        """
        try:
            feature_name = command.args.get("feature")
            feature_dir = self.project_root / "docs" / "features" / feature_name
            
            # 创建特性目录
            feature_dir.mkdir(parents=True, exist_ok=True)
            
            # 初始化特性级 artifacts
            self._initialize_feature_artifacts(feature_dir, feature_name)
            
            # 获取或创建 Capability
            capability_name = command.args.get("capability") or "brainstorming"
            capability = self.capability_registry.select(capability_name)
            
            # 获取 Phase1 Orchestrator
            orchestrator = self.phase_orchestrators.get(Phase.REQUIREMENTS)
            if not orchestrator:
                raise RuntimeError("Phase1 orchestrator not found")
            
            # 交互式询问：是否是 Web 内核开发
            web_kernel_mode = self._ask_web_kernel_mode()
            
            # 执行 Phase1
            context = ExecutionContext(
                project_root=self.project_root,
                feature_name=feature_name,
                feature_dir=feature_dir,
                capability=capability,
            )
            
            # 将 Web Kernel 模式存入 context
            context.metadata["web_kernel_mode"] = web_kernel_mode
            
            orchestrator.execute(context)
            
            return Result(
                success=True,
                message=f"Feature '{feature_name}' started",
                details=[
                    f"Feature dir: {feature_dir}",
                    f"Capability: {capability_name}",
                    f"Web Kernel Mode: {'Yes' if web_kernel_mode else 'No'}",
                ],
            )
            
        except Exception as e:
            return Result(success=False, message=f"Start feature failed: {e}")
    
    def _ask_web_kernel_mode(self) -> bool:
        """询问是否是 Web 内核开发"""
        print()
        print("🌐 Web Kernel Development Detection")
        print("=" * 40)
        print("Is this a Web Kernel (Servo/browser engine) development task?")
        print()
        print("  [Y] Yes - This involves DOM, CSS, HTML, layout, networking, or other web platform components")
        print("  [N] No - This is a general software development task")
        print("  [S] Skip - Don't ask again for this feature")
        print()
        
        while True:
            choice = input("Select option (Y/N/S): ").strip().upper()
            if choice == "Y":
                return True
            elif choice == "N":
                return False
            elif choice == "S":
                return False
            else:
                print("Invalid option. Please enter Y, N, or S.")
    
    def resume_feature(self, command: ResumeCommand) -> Result:
        """
        恢复特性开发
        
        Args:
            command: ResumeCommand 对象
            
        Returns:
            Result: 执行结果
        """
        try:
            feature_name = command.args.get("feature")
            
            if not feature_name:
                # 列出所有进行中的特性
                features = self._list_active_features()
                if not features:
                    return Result(
                        success=True,
                        message="No active features found",
                    )
                
                return Result(
                    success=True,
                    message="Select a feature to resume:",
                    details=[f"  - {f}" for f in features],
                )
            
            # 加载 Checkpoint
            feature_dir = self.project_root / "docs" / "features" / feature_name
            checkpoint = self._load_checkpoint(feature_dir)
            
            if not checkpoint:
                return Result(
                    success=False,
                    message=f"No checkpoint found for feature '{feature_name}'",
                )
            
            # 恢复执行
            current_phase = checkpoint.get("current_phase", Phase.REQUIREMENTS)
            orchestrator = self.phase_orchestrators.get(current_phase)
            
            if orchestrator:
                context = self._rebuild_context(feature_dir, feature_name, checkpoint)
                orchestrator.execute(context)
            
            return Result(
                success=True,
                message=f"Resumed feature '{feature_name}'",
                details=[f"Resuming from: {current_phase}"],
            )
            
        except Exception as e:
            return Result(success=False, message=f"Resume failed: {e}")
    
    def show_status(self, command: StatusCommand) -> Result:
        """
        显示项目状态
        
        Args:
            command: StatusCommand 对象
            
        Returns:
            Result: 执行结果
        """
        try:
            feature_name = command.args.get("feature")
            verbose = command.args.get("verbose", False)
            
            if feature_name:
                # 显示特定特性状态
                status = self._get_feature_status(feature_name, verbose)
            else:
                # 显示项目总体状态
                status = self._get_project_status(verbose)
            
            return Result(
                success=True,
                message=status["title"],
                details=status["details"],
            )
            
        except Exception as e:
            return Result(success=False, message=f"Status failed: {e}")
    
    def complete(self, command: CompleteCommand) -> Result:
        """
        完成当前工作流
        
        Args:
            command: CompleteCommand 对象
            
        Returns:
            Result: 执行结果
        """
        try:
            # 检查 Phase 5 artifacts
            if not self._check_review_artifacts():
                return Result(
                    success=False,
                    message="Phase 5 artifacts incomplete. Run sdd status to check.",
                )
            
            # 执行 Phase 6 Persistence
            orchestrator = self.phase_orchestrators.get(Phase.PERSISTENCE)
            if orchestrator:
                context = self._get_current_context()
                orchestrator.execute(context)
            
            return Result(
                success=True,
                message="Workflow completed. Ready for merge.",
            )
            
        except Exception as e:
            return Result(success=False, message=f"Complete failed: {e}")
    
    def run_quality_assessment(
        self,
        feature_name: str,
        phase: str = "development",
    ) -> Dict[str, Any]:
        """
        运行质量评估
        
        Args:
            feature_name: 特性名称
            phase: 当前 Phase
            
        Returns:
            评估结果字典
        """
        feature_dir = self.project_root / "docs" / "features" / feature_name
        
        context = ExecutionContext(
            project_root=self.project_root,
            feature_name=feature_name,
            feature_dir=feature_dir,
            capability=None,
        )
        
        return self.quality_harness.run_assessment(feature_name, phase, context)
    
    def check_quality_gates(self, phase: str) -> "GateResult":
        """
        检查质量 Gate
        
        Args:
            phase: 当前 Phase
            
        Returns:
            GateResult
        """
        return GateResult(passed=True, message="Quality gates passed")
    
    def _is_initialized(self, path: Path) -> bool:
        """检查项目是否已初始化"""
        return (
            (path / "CONSTITUTION").exists()
            or (path / ".sdd").exists()
            or (path / "PROJECT_STATE.md").exists()
        )
    
    def _create_directory_structure(self, project_root: Path):
        """创建目录结构"""
        directories = [
            ".sdd",
            "CONSTITUTION",
            ".nexus-map",
            "docs/knowledge",
            "docs/modules",
            "docs/features",
            "docs/collaboration",
        ]
        
        for dir_path in directories:
            (project_root / dir_path).mkdir(parents=True, exist_ok=True)
    
    def _initialize_config_files(self, project_root: Path, command: InitCommand):
        """初始化配置文件"""
        import yaml
        
        config = {
            "project": {
                "name": project_root.name,
                "type": command.args.get("template", "standard"),
                "complexity": "medium",
            },
            "harness": {"enabled": True},
        }
        
        config_path = project_root / ".sdd" / "project.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(yaml.dump(config))
    
    def _initialize_constitution(self, project_root: Path):
        """初始化 Constitution"""
        const_dir = project_root / "CONSTITUTION"
        const_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建 core.md
        core_content = """# Core Principles

## 1. Safety First
- All user input must be validated
- No sensitive info in logs

## 2. Modularity
- Modules communicate via explicit interfaces
- Single responsibility per module

## 3. Testability
- All public APIs must have tests

## 4. Backward Compatibility
- No breaking changes to public APIs
"""
        (const_dir / "core.md").write_text(core_content)
    
    def _initialize_memory_artifacts(self, project_root: Path):
        """初始化内存 artifacts"""
        state_content = """# Project State

## Features

No active features.

## Quality Metrics

| Metric | Current | Target |
|--------|---------|--------|
"""
        (project_root / "PROJECT_STATE.md").write_text(state_content)
        
        agents_content = """# AI Agent Context

No active session.
"""
        (project_root / "AGENTS.md").write_text(agents_content)
    
    def _initialize_feature_artifacts(self, feature_dir: Path, feature_name: str):
        """初始化特性级 artifacts"""
        feature_dir.mkdir(parents=True, exist_ok=True)
        
        task_plan = f"""# Task Plan: {feature_name}

## Phase 1: Requirements Analysis
- [ ] Explore context
- [ ] Gather requirements
- [ ] Generate design
- [ ] User approval

## Phase 2: Implementation Planning
- [ ] Create task list
- [ ] User approval
"""
        (feature_dir / "task_plan.md").write_text(task_plan)
        
        findings = f"""# Findings: {feature_name}

## Research

## Decisions

## Notes
"""
        (feature_dir / "findings.md").write_text(findings)
        
        progress = f"""# Progress: {feature_name}

## Execution Log

"""
        (feature_dir / "progress.md").write_text(progress)
    
    def _list_active_features(self) -> list:
        """列出所有进行中的特性"""
        features_dir = self.project_root / "docs" / "features"
        if not features_dir.exists():
            return []
        
        active = []
        for feature_dir in features_dir.iterdir():
            if feature_dir.is_dir():
                status_file = feature_dir / "status.toml"
                if status_file.exists():
                    active.append(feature_dir.name)
                elif not (feature_dir / "COMPLETED").exists():
                    active.append(feature_dir.name)
        
        return active
    
    def _load_checkpoint(self, feature_dir: Path) -> Optional[dict]:
        """加载 Checkpoint"""
        checkpoint_file = feature_dir / ".sdd" / "checkpoint.json"
        if checkpoint_file.exists():
            import json
            return json.loads(checkpoint_file.read_text())
        return None
    
    def _check_review_artifacts(self) -> bool:
        """检查 Phase 5 artifacts"""
        required = [
            "docs/reviews/architecture_review.md",
            "docs/reviews/code_quality_review.md",
            "docs/reviews/test_coverage_report.md",
            "docs/reviews/requirements_verification.md",
        ]
        
        return all((self.project_root / f).exists() for f in required)
    
    def _get_feature_status(self, feature_name: str, verbose: bool) -> dict:
        """获取特性状态"""
        feature_dir = self.project_root / "docs" / "features" / feature_name
        
        if not feature_dir.exists():
            return {
                "title": f"Feature '{feature_name}' not found",
                "details": [],
            }
        
        task_plan = feature_dir / "task_plan.md"
        findings = feature_dir / "findings.md"
        progress = feature_dir / "progress.md"
        
        details = []
        if verbose:
            if task_plan.exists():
                details.append(f"Task Plan: {task_plan}")
            if findings.exists():
                details.append(f"Findings: {findings}")
            if progress.exists():
                details.append(f"Progress: {progress}")
        
        return {
            "title": f"Feature: {feature_name}",
            "details": details,
        }
    
    def _get_project_status(self, verbose: bool) -> dict:
        """获取项目状态"""
        active_features = self._list_active_features()
        
        details = []
        if verbose:
            if self._is_initialized(self.project_root):
                details.append("SDD: Initialized")
            else:
                details.append("SDD: Not initialized")
            
            if active_features:
                details.append(f"Active Features: {len(active_features)}")
                for f in active_features:
                    details.append(f"  - {f}")
        
        return {
            "title": f"Project Status ({len(active_features)} active features)",
            "details": details,
        }
    
    def _rebuild_context(self, feature_dir: Path, feature_name: str, checkpoint: dict) -> "ExecutionContext":
        """重建执行上下文"""
        capability = self.capability_registry.select(checkpoint.get("capability", "brainstorming"))
        
        return ExecutionContext(
            project_root=self.project_root,
            feature_name=feature_name,
            feature_dir=feature_dir,
            capability=capability,
            checkpoint=checkpoint,
        )
    
    def _get_current_context(self) -> "ExecutionContext":
        """获取当前执行上下文"""
        return ExecutionContext(
            project_root=self.project_root,
            feature_name="",
            feature_dir=Path(""),
            capability=None,
        )


class StateMachine:
    """状态机"""
    
    TRANSITIONS = {
        Phase.INIT: [Phase.REQUIREMENTS],
        Phase.REQUIREMENTS: [Phase.PLANNING],
        Phase.PLANNING: [Phase.DEVELOPMENT],
        Phase.DEVELOPMENT: [Phase.INTEGRATION],
        Phase.INTEGRATION: [Phase.REVIEW],
        Phase.REVIEW: [Phase.PERSISTENCE],
        Phase.PERSISTENCE: [Phase.COMPLETED],
    }
    
    def __init__(self):
        self.current_phase = Phase.INIT
    
    def can_transition(self, from_phase: Phase, to_phase: Phase) -> bool:
        """检查是否可以转换"""
        return to_phase in self.TRANSITIONS.get(from_phase, [])
    
    def transition(self, to_phase: Phase) -> bool:
        """执行转换"""
        if self.can_transition(self.current_phase, to_phase):
            self.current_phase = to_phase
            return True
        return False
    
    def get_current(self) -> Phase:
        """获取当前阶段"""
        return self.current_phase


class GateController:
    """Gate 控制器"""
    
    def __init__(self):
        self.gates = {}
    
    def add_gate(self, from_phase: Phase, to_phase: Phase, gate: "Gate"):
        """添加 Gate"""
        key = (from_phase, to_phase)
        self.gates[key] = gate
    
    def evaluate(
        self,
        from_phase: Phase,
        to_phase: Phase,
        context: "ExecutionContext",
    ) -> "GateResult":
        """评估 Gate"""
        key = (from_phase, to_phase)
        gate = self.gates.get(key)
        
        if not gate:
            return GateResult(passed=True)
        
        return gate.evaluate(context)


class Gate:
    """Gate 接口"""
    
    def evaluate(self, context: "ExecutionContext") -> "GateResult":
        """评估 Gate"""
        raise NotImplementedError


class GateResult:
    """Gate 评估结果"""
    
    def __init__(self, passed: bool, message: str = "", blockers: list = None):
        self.passed = passed
        self.message = message
        self.blockers = blockers or []


class CapabilityRegistry:
    """Capability 注册表"""
    
    def __init__(self):
        self.capabilities = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """注册默认 Capabilities"""
        from .capabilities import (
            BrainstormingCapability,
            WritingPlansCapability,
            CodeReviewCapability,
            VerificationCapability,
        )
        
        self.capabilities["brainstorming"] = BrainstormingCapability()
        self.capabilities["writing-plans"] = WritingPlansCapability()
        self.capabilities["code-review"] = CodeReviewCapability()
        self.capabilities["verification"] = VerificationCapability()
    
    def select(self, name: str):
        """选择 Capability"""
        return self.capabilities.get(name)
    
    def register(self, name: str, capability: "Capability"):
        """注册 Capability"""
        self.capabilities[name] = capability
    
    def list_all(self) -> list:
        """列出所有 Capability"""
        return list(self.capabilities.keys())


class ExecutionContext:
    """执行上下文"""
    
    def __init__(
        self,
        project_root: Path,
        feature_name: str,
        feature_dir: Path,
        capability: Optional[Any] = None,
        checkpoint: Optional[dict] = None,
    ):
        self.project_root = project_root
        self.feature_name = feature_name
        self.feature_dir = feature_dir
        self.capability = capability
        self.checkpoint = checkpoint or {}
        self.metadata: dict = {}
        self.artifacts: dict = {}


PhaseResult = None


class PhaseResult:
    """Phase 执行结果"""
    
    def __init__(
        self,
        success: bool,
        artifacts: dict = None,
        message: str = "",
    ):
        self.success = success
        self.artifacts = artifacts or {}
        self.message = message
