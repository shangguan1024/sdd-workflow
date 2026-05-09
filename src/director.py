"""
SDD-Workflow Director (Layer 1)
主状态机、Gate 控制、流程编排
v2.4: Refactored with extracted modules + ConfigManager
"""

import json
import re
import sys
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum

_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from .cli import (
    Command,
    InitCommand,
    StartCommand,
    ResumeCommand,
    StatusCommand,
    CompleteCommand,
    Result,
)
from .constants import REQUIRED_REVIEW_ARTIFACTS, REQUIRED_MEMORY_ARTIFACTS
from .memory_manager import MemoryManager
from .context_injector import ContextInjector
from .project_initializer import ProjectInitializer
from .config_manager import ConfigManager


class Phase(Enum):
    INIT = 0
    UNDERSTANDING = -1
    REQUIREMENTS = 1
    PLANNING = 2
    DEVELOPMENT = 3
    INTEGRATION = 4
    REVIEW = 5
    PERSISTENCE = 6
    COMPLETED = 7


class Director:
    def __init__(self, project_root: Path = Path("."), quality_profile: str = "standard"):
        self.project_root = project_root
        self.state_machine = StateMachine()
        self.gate_controller = GateController()
        self.phase_orchestrators: Dict[Phase, "PhaseOrchestrator"] = {}
        self.capability_registry = CapabilityRegistry()
        self._session_id = str(uuid.uuid4())[:8]
        
        # ConfigManager - 统一配置管理
        self._config_manager = ConfigManager(project_root)
        
        from .checkpoint import CheckpointManager
        self._checkpoint_manager = CheckpointManager(project_root)
        
        from .nexus_map import NexusMapIntegrator
        self._nexus_map_integrator = NexusMapIntegrator(project_root)
        
        # 使用ConfigManager加载配置
        from .memory.privacy_filter import PrivacyFilter, PrivacyFilterConfig
        privacy_config = self._config_manager.load("privacy_filter")
        privacy_config_path = self._config_manager.get_config_path("privacy_filter")
        self._privacy_filter = PrivacyFilter(config_path=privacy_config_path)
        
        from .error_recovery import ErrorRecoveryManager, ErrorSeverity
        self._error_recovery_manager = ErrorRecoveryManager(
            project_root,
            config_manager=self._config_manager
        )
        
        self._memory_manager = MemoryManager(project_root, self._error_recovery_manager)
        
        self._context_injector = ContextInjector(
            project_root,
            self._privacy_filter,
            self._memory_manager,
        )
        
        self._project_initializer = ProjectInitializer(project_root)
        
        self._init_phase_orchestrators()
        self._init_middleware()

        from .context_monitor import ContextMonitor
        self._context_monitor = ContextMonitor()

        from .quality import QualityHarness, get_profile
        self.quality_harness = QualityHarness(project_root, get_profile(quality_profile))
    
    def _init_phase_orchestrators(self):
        from .phases import (
            Phase1Orchestrator,
            Phase2Orchestrator,
            Phase3Orchestrator,
            Phase4Orchestrator,
            Phase5Orchestrator,
            Phase6Orchestrator,
        )
        
        self.phase_orchestrators = {
            Phase.REQUIREMENTS: Phase1Orchestrator(
                self.capability_registry,
                error_recovery_manager=self._error_recovery_manager
            ),
            Phase.PLANNING: Phase2Orchestrator(
                self.capability_registry,
                error_recovery_manager=self._error_recovery_manager
            ),
            Phase.DEVELOPMENT: Phase3Orchestrator(
                self.capability_registry,
                error_recovery_manager=self._error_recovery_manager
            ),
            Phase.INTEGRATION: Phase4Orchestrator(
                self.capability_registry,
                error_recovery_manager=self._error_recovery_manager
            ),
            Phase.REVIEW: Phase5Orchestrator(
                self.capability_registry,
                error_recovery_manager=self._error_recovery_manager
            ),
            Phase.PERSISTENCE: Phase6Orchestrator(
                self.capability_registry,
                error_recovery_manager=self._error_recovery_manager
            ),
        }

    def _init_middleware(self):
        from middleware import (
            PhaseGateMiddleware,
            LoopDetectionMiddleware,
            ArtifactCompleteMiddleware,
            PhaseCompressionMiddleware,
        )

        const_dir = self.project_root / "CONSTITUTION"
        self._phase_gate_mw = (
            PhaseGateMiddleware(const_dir, config_manager=self._config_manager) 
            if const_dir.exists() else None
        )

        self._loop_detection_mw = LoopDetectionMiddleware(
            config_manager=self._config_manager
        )

        self._artifact_mw = ArtifactCompleteMiddleware(
            self.project_root, 
            config_manager=self._config_manager
        )

        self._compression_mw = PhaseCompressionMiddleware(self.project_root)

    def run_middleware_before(self, phase: int, context: dict = None) -> "MiddlewareResult":
        from middleware import MiddlewareResult
        ctx = context or {}
        ctx["phase"] = phase

        if self._phase_gate_mw:
            result = self._phase_gate_mw.before_action(ctx)
            if not result.allowed:
                return result

        if self._compression_mw and phase > 1:
            ctx["from_phase"] = phase - 1
            result = self._compression_mw.before_action(ctx)
            if not result.allowed:
                return result

        quality_result = self._check_quality_gate(phase, ctx)
        if quality_result and not quality_result.allowed:
            return quality_result

        return MiddlewareResult(allowed=True)
    
    def _check_quality_gate(self, phase: int, ctx: dict) -> Optional["MiddlewareResult"]:
        from middleware import MiddlewareResult
        
        phase_name = self._phase_num_to_name(phase)
        
        if phase_name not in ["development", "integration", "review"]:
            return None
        
        feature_name = ctx.get("feature_name")
        if not feature_name:
            return None
        
        active_ctx = self._get_active_context()
        if not active_ctx:
            return None
        
        metrics = active_ctx.metadata.get("quality_assessment", {})
        if not metrics:
            return None
        
        from .quality.gate_engine import GateEngine
        gate_engine = GateEngine(self.project_root, self.quality_harness.profile)
        result = gate_engine.evaluate(phase_name, metrics)
        
        if not result.passed:
            failed_gates = result.details.get("gate_results", [])
            failed_names = [g["name"] for g in failed_gates if not g["passed"]]
            
            return MiddlewareResult(
                allowed=False,
                message=f"❌ Quality Gate 未通过: {', '.join(failed_names)}\n{result.message}",
                suggestion="修复质量问题后再继续下一 Phase",
                requires_confirmation=True,
                confirmation_options=["修复并重试", "跳过（不推荐）"],
            )
        
        return MiddlewareResult(allowed=True)

    def run_middleware_after(self, phase: int, context: dict = None) -> "MiddlewareResult":
        from middleware import MiddlewareResult

        if phase == 5 and self._artifact_mw:
            ctx = context or {}
            ctx["phase"] = 6
            result = self._artifact_mw.before_action(ctx)
            return result

        return MiddlewareResult(allowed=True)

    def record_edit(self, file_path: str) -> Optional["MiddlewareResult"]:
        self._context_monitor.record_edit(file_path)
        should_refresh, reason = self._context_monitor.should_refresh()
        if should_refresh:
            ctx = self._get_active_context()
            if ctx and ctx.feature_name:
                print(f"\n  ⚠️  {reason}\n")
                self._context_monitor.inject_refresh(ctx)

        if self._loop_detection_mw:
            ctx = {
                "tool_name": "edit_file",
                "file_path": file_path,
                "session_id": self._session_id,
            }
            loop_result = self._loop_detection_mw.after_action(ctx, None)
            if loop_result and loop_result.message and "编辑" in str(loop_result.message):
                print(f"\n  💡 提示: 可以手动触发上下文刷新以检查方向\n")
            return loop_result
        return None

    def _get_active_context(self) -> Optional["ExecutionContext"]:
        features_dir = self.project_root / "docs" / "features"
        if not features_dir.exists():
            return None
        for d in sorted(features_dir.iterdir(), reverse=True):
            if d.is_dir() and (d / ".sdd" / "checkpoint.json").exists():
                return ExecutionContext(
                    project_root=self.project_root,
                    feature_name=d.name,
                    feature_dir=d,
                    capability=None,
                )
        return None

    def refresh_context(self, context: "ExecutionContext", reason: str = ""):
        self._context_monitor.force_refresh(context, reason)

    def record_task_complete(self, task_name: str = ""):
        self._context_monitor.record_task(task_name)
        should_refresh, reason = self._context_monitor.should_refresh()
        if should_refresh:
            ctx = self._get_active_context()
            if ctx and ctx.feature_name:
                print(f"\n  ⚠️  {reason}\n")
                self._context_monitor.inject_refresh(ctx)

    def reset_context_monitor(self):
        self._context_monitor.reset()

    def initialize(self, command: InitCommand) -> Result:
        try:
            project_path = command.args.get("path") or self.project_root

            if not command.args.get("force") and self._project_initializer.is_initialized(project_path):
                return Result(
                    success=False,
                    message="Project already initialized. Use --force to reinitialize.",
                )

            self._project_initializer.initialize_all(project_path, command)

            return Result(
                success=True,
                message="SDD project initialized successfully",
                details=[
                    f"Project: {project_path}",
                    f"Template: {command.args.get('template')}",
                ],
            )

        except Exception as e:
            from .error_recovery import ErrorSeverity
            error_record = self._error_recovery_manager.capture_error(
                exception=e,
                operation="initialize",
                severity=ErrorSeverity.ERROR,
            )
            
            error_report = self._error_recovery_manager.generate_error_report()
            return Result(
                success=False,
                message=f"Initialization failed: {error_record.message}",
                details=[error_report]
            )

    def start_feature(self, command: StartCommand) -> Result:
        try:
            feature_name = command.args.get("feature")
            feature_dir = self.project_root / "docs" / "features" / feature_name

            feature_dir.mkdir(parents=True, exist_ok=True)

            self._project_initializer.initialize_feature_artifacts(feature_dir, feature_name)
            self.reset_context_monitor()

            self._memory_manager.load_or_create_memory(feature_name)
            self._memory_manager.start_session(self._session_id)
            
            memory = self._memory_manager.get_memory()
            
            if self._checkpoint_manager:
                self._checkpoint_manager.set_memory(memory)
                self._checkpoint_manager.enable_realtime_sync(feature_name)
                print("✅ Real-time checkpoint sync enabled (30s interval)")

            capability_name = command.args.get("capability") or "brainstorming"
            capability = self.capability_registry.select(capability_name)

            orchestrator = self.phase_orchestrators.get(Phase.REQUIREMENTS)
            if not orchestrator:
                raise RuntimeError("Phase1 orchestrator not found")

            web_kernel_mode = self._ask_web_kernel_mode()

            print()
            print("📚 Understanding 阶段")
            print("=" * 50)
            print("在进入设计阶段之前，必须先深入理解现有系统和相关原理...")
            self._memory_manager.show_memory_context()

            from .capabilities.understanding import UnderstandingCapability
            understanding_cap = UnderstandingCapability()

            context = ExecutionContext(
                project_root=self.project_root,
                feature_name=feature_name,
                feature_dir=feature_dir,
                capability=capability,
            )
            context.metadata["web_kernel_mode"] = web_kernel_mode
            context.metadata["session_id"] = self._session_id
            context.metadata["_context_monitor"] = self._context_monitor
            context.metadata["_director"] = self

            self._context_injector.inject_memory_context(context, feature_name)

            understanding_result = understanding_cap.execute(context)

            if not understanding_result.success:
                print()
                print("❌ Understanding 阶段未通过")
                print(f"原因: {understanding_result.message}")
                print()
                print("请补充研究后重新运行: sdd start " + feature_name)
                return Result(
                    success=False,
                    message="Understanding 阶段未通过",
                    details=[understanding_result.message],
                )

            print()
            print("✅ Understanding 阶段完成")
            print(f"研究报告: {context.metadata.get('research_report_path', 'N/A')}")
            print()

            print("📋 Understanding 报告已生成")
            print("请阅读报告，确认研究足够深入后再继续进入设计阶段。")
            print()

            continue_choice = input("是否继续进入 Phase 1 (设计阶段)? (Y/N): ").strip().upper()
            if continue_choice != "Y":
                print()
                self._memory_manager.save_memory_silent(feature_name)
                print("已暂停。您可以随时运行: sdd resume " + feature_name)
                return Result(
                    success=True,
                    message="Understanding 阶段完成，等待用户确认继续",
                    details=["sdd resume " + feature_name],
                )

            gate_result = self.run_middleware_before(1, {
                "feature_name": feature_name,
                "session_id": self._session_id,
                "content": str(context.metadata.get("design_content", "")),
            })
            if not gate_result.allowed:
                print(f"❌ Phase Gate blocked: {gate_result.message}")
                return Result(success=False, message=gate_result.message)

            orchestrator.execute(context)
            
            for phase_num in range(2, 7):
                phase_name = self._phase_num_to_name(phase_num)
                
                print()
                print(f"🔄 Phase {phase_num}: {phase_name}")
                print("=" * 50)
                
                continue_choice = input(f"是否继续进入 Phase {phase_num}? (Y/N): ").strip().upper()
                if continue_choice != "Y":
                    print()
                    self._memory_manager.save_memory_silent(feature_name)
                    print(f"已暂停。您可以随时运行: sdd resume {feature_name}")
                    return Result(
                        success=True,
                        message=f"Phase {phase_num - 1} 完成，等待用户确认继续",
                        details=[f"sdd resume {feature_name}"],
                    )
                
                gate_result = self.run_middleware_before(phase_num, {
                    "feature_name": feature_name,
                    "session_id": self._session_id,
                })
                if not self.gate_controller.handle_confirmation(gate_result, context):
                    print()
                    self._memory_manager.save_memory_silent(feature_name)
                    print(f"Gate blocked at Phase {phase_num}. Run: sdd resume {feature_name}")
                    return Result(
                        success=False,
                        message=f"Phase {phase_num} gate blocked",
                        details=[gate_result.message],
                    )
                
                next_orchestrator = self.phase_orchestrators.get(Phase(phase_num))
                if next_orchestrator:
                    next_orchestrator.execute(context)
                else:
                    print(f"⚠️ No orchestrator for Phase {phase_num}")
                    break
            
            print()
            print("✅ All 6 phases completed successfully")
            self._memory_manager.save_memory_silent(feature_name)
            
            return Result(
                success=True,
                message=f"Feature '{feature_name}' completed through Phase 6",
            )

        except Exception as e:
            from .error_recovery import ErrorSeverity
            error_record = self._error_recovery_manager.capture_error(
                exception=e,
                operation="start_feature",
                severity=ErrorSeverity.ERROR,
                file_path=str(feature_dir) if feature_dir else None,
            )
            
            error_report = self._error_recovery_manager.generate_error_report()
            return Result(
                success=False,
                message=f"Start feature failed: {error_record.message}",
                details=[error_report]
            )

    def get_memory_timeline(self, context: "ExecutionContext", around_id: str) -> str:
        return self._memory_manager.get_memory_timeline(context, around_id)
    
    def get_memory_full_details(self, context: "ExecutionContext", ids: List[str]) -> str:
        return self._memory_manager.get_memory_full_details(context, ids)

    def resume_feature(self, command: ResumeCommand) -> Result:
        try:
            feature_name = command.args.get("feature")

            if not feature_name:
                features = self._list_active_features()
                if not features:
                    return Result(
                        success=True,
                        message="No active features found",
                    )

                print()
                print("SDD Resume Options")
                print("=" * 50)
                print("Active Features:")
                for i, f in enumerate(features, 1):
                    status = self._read_feature_status(f)
                    phase = status.get("current_phase", "?")
                    progress = status.get("progress", "")
                    task_info = status.get("current_task", "")
                    info = f"[Phase {phase}]"
                    if task_info:
                        info += f" {task_info}"
                    if progress:
                        info += f" ({progress})"
                    print(f"{i}. {f:<20} {info}")

                print()
                print("Select feature to resume:")
                for f in features:
                    print(f"  sdd resume {f}")
                return Result(
                    success=True,
                    message="Select a feature to resume",
                    details=[f"  - {f}" for f in features],
                )

            feature_dir = self.project_root / "docs" / "features" / feature_name
            if not feature_dir.exists():
                return Result(
                    success=False,
                    message=f"Feature '{feature_name}' not found. Use 'sdd start {feature_name}'.",
                )

            self._memory_manager.load_or_create_memory(feature_name)
            self._memory_manager.start_session(self._session_id)

            memory = self._memory_manager.get_memory()

            if self._checkpoint_manager:
                self._checkpoint_manager.set_memory(memory)
                self._checkpoint_manager.enable_realtime_sync(feature_name)
                print("✅ Real-time checkpoint sync enabled (30s interval)")

            self._memory_manager.show_memory_context()

            checkpoint = self._load_checkpoint(feature_dir)

            phase_name = "1"
            if checkpoint:
                phase_name = checkpoint.get("phase", "1")
                current_phase = self._phase_name_to_enum(phase_name)
            else:
                current_phase = Phase.REQUIREMENTS

            if phase_name in ("6", "persistence") and checkpoint:
                print(f"✅ Feature '{feature_name}' was at Phase 6 (Memory Persistence).")
                print("Workflow may be complete. Check status: sdd status")
                return Result(
                    success=True,
                    message=f"Feature '{feature_name}' appears complete",
                    details=[f"Last phase: {phase_name}"],
                )

            orchestrator = self.phase_orchestrators.get(current_phase)

            if orchestrator:
                context = self._rebuild_context(feature_dir, feature_name, checkpoint)
                context.metadata["session_id"] = self._session_id
                context.metadata["resumed"] = True
                context.metadata["_context_monitor"] = self._context_monitor
                context.metadata["_director"] = self

                self._context_injector.inject_memory_context(context, feature_name)

                print(f"🔄 从 Phase {phase_name} 恢复: {feature_name}")
                print()

                self._context_injector.print_context_to_stdout(context, feature_name)

                gate_result = self.run_middleware_before(
                    self._enum_to_phase_num(current_phase),
                    {
                        "feature_name": feature_name,
                        "session_id": self._session_id,
                    },
                )
                if not gate_result.allowed:
                    print(f"⚠️ Gate check: {gate_result.message}")

                orchestrator.execute(context)
            else:
                print(f"⚠️ No orchestrator for phase '{phase_name}'. Starting from Phase 1.")
                orchestrator = self.phase_orchestrators.get(Phase.REQUIREMENTS)
                if orchestrator:
                    context = self._rebuild_context(feature_dir, feature_name, checkpoint)
                    context.metadata["session_id"] = self._session_id
                    self._context_injector.inject_memory_context(context, feature_name)
                    self._context_injector.print_context_to_stdout(context, feature_name)
                    orchestrator.execute(context)

            return Result(
                success=True,
                message=f"Resumed feature '{feature_name}'",
                details=[f"Resuming from Phase: {phase_name}"],
            )

        except Exception as e:
            from .error_recovery import ErrorSeverity
            error_record = self._error_recovery_manager.capture_error(
                exception=e,
                operation="resume_feature",
                severity=ErrorSeverity.ERROR,
            )
            
            error_report = self._error_recovery_manager.generate_error_report()
            return Result(
                success=False,
                message=f"Resume failed: {error_record.message}",
                details=[error_report]
            )

    def _phase_name_to_enum(self, name: str) -> Phase:
        mapping = {
            "1": Phase.REQUIREMENTS,
            "requirements": Phase.REQUIREMENTS,
            "2": Phase.PLANNING,
            "planning": Phase.PLANNING,
            "3": Phase.DEVELOPMENT,
            "development": Phase.DEVELOPMENT,
            "4": Phase.INTEGRATION,
            "integration": Phase.INTEGRATION,
            "5": Phase.REVIEW,
            "review": Phase.REVIEW,
            "6": Phase.PERSISTENCE,
            "persistence": Phase.PERSISTENCE,
        }
        return mapping.get(str(name).lower(), Phase.REQUIREMENTS)
    
    def _phase_num_to_name(self, phase_num: int) -> str:
        mapping = {
            1: "Requirements",
            2: "Planning",
            3: "Development",
            4: "Integration",
            5: "Review",
            6: "Persistence",
        }
        return mapping.get(phase_num, f"Phase {phase_num}")

    def _enum_to_phase_num(self, phase: Phase) -> int:
        mapping = {
            Phase.REQUIREMENTS: 1,
            Phase.PLANNING: 2,
            Phase.DEVELOPMENT: 3,
            Phase.INTEGRATION: 4,
            Phase.REVIEW: 5,
            Phase.PERSISTENCE: 6,
        }
        return mapping.get(phase, 1)

    def _read_feature_status(self, feature_name: str) -> dict:
        feature_dir = self.project_root / "docs" / "features" / feature_name
        
        checkpoint = self._load_checkpoint(feature_dir)
        if checkpoint:
            return {
                "current_phase": checkpoint.get("phase", "1"),
                "current_task": checkpoint.get("step", ""),
                "progress": "",
            }
        
        if feature_dir.exists():
            task_plan = feature_dir / "task_plan.md"
            if task_plan.exists():
                content = task_plan.read_text(encoding="utf-8")
                phase_match = re.search(r"Phase (\d+)", content)
                if phase_match:
                    return {"current_phase": phase_match.group(1)}
        
        return {"current_phase": "1"}

    def show_status(self, command: StatusCommand) -> Result:
        try:
            feature_name = command.args.get("feature")
            verbose = command.args.get("verbose", False)

            if feature_name:
                status = self._get_feature_status(feature_name, verbose)
            else:
                status = self._get_project_status(verbose)

            return Result(
                success=True,
                message=status["title"],
                details=status["details"],
            )

        except Exception as e:
            from .error_recovery import ErrorSeverity
            error_record = self._error_recovery_manager.capture_error(
                exception=e,
                operation="show_status",
                severity=ErrorSeverity.WARNING,
            )
            
            error_report = self._error_recovery_manager.generate_error_report()
            return Result(
                success=False,
                message=f"Status failed: {error_record.message}",
                details=[error_report]
            )

    def complete(self, command: CompleteCommand) -> Result:
        try:
            feature_name = command.args.get("feature")
            if not feature_name:
                features = self._list_active_features()
                if not features:
                    return Result(success=True, message="No active features")
                feature_name = features[0]

            if not self._check_review_artifacts():
                if self._artifact_mw:
                    ctx = {"phase": 5, "session_id": self._session_id}
                    result = self._artifact_mw.before_action(ctx)
                    if result.allowed and result.message:
                        print(result.message)

                still_missing = [
                    f for f in REQUIRED_REVIEW_ARTIFACTS
                    if not (self.project_root / f).exists()
                ]

                from middleware import MiddlewareResult
                if still_missing and self._artifact_mw:
                    ctx = {"phase": 6, "session_id": self._session_id}
                    check = self._artifact_mw.before_action(ctx)
                    if not check.allowed:
                        return Result(
                            success=False,
                            message=f"Phase 5 artifacts incomplete: {', '.join(still_missing)}",
                        )

            orchestrator = self.phase_orchestrators.get(Phase.PERSISTENCE)
            if orchestrator:
                context = self._get_current_context()
                orchestrator.execute(context)

            if self._checkpoint_manager and feature_name:
                self._checkpoint_manager.disable_realtime_sync(feature_name)
                print("✅ Real-time checkpoint sync stopped")

            return Result(
                success=True,
                message="Workflow completed. Ready for merge.",
            )

        except Exception as e:
            from .error_recovery import ErrorSeverity
            error_record = self._error_recovery_manager.capture_error(
                exception=e,
                operation="complete",
                severity=ErrorSeverity.ERROR,
            )
            
            error_report = self._error_recovery_manager.generate_error_report()
            return Result(
                success=False,
                message=f"Complete failed: {error_record.message}",
                details=[error_report]
            )

    def run_quality_assessment(self, feature_name: str, phase: str = "development") -> Dict[str, Any]:
        feature_dir = self.project_root / "docs" / "features" / feature_name

        context = ExecutionContext(
            project_root=self.project_root,
            feature_name=feature_name,
            feature_dir=feature_dir,
            capability=None,
        )

        return self.quality_harness.run_assessment(feature_name, phase, context)

    def check_quality_gates(self, phase_str: str) -> "GateResult":
        result = GateResult(passed=True, message="")

        if phase_str == "1" or phase_str == "requirements":
            design_docs = list((self.project_root / "docs" / "superpowers" / "specs").glob("*-design.md")
                               if (self.project_root / "docs" / "superpowers" / "specs").exists() else [])
            if not design_docs:
                return GateResult(
                    passed=False,
                    message="Phase 1 incomplete: No design document found",
                )

        elif phase_str == "3" or phase_str == "development":
            cargo_toml = self.project_root / "Cargo.toml"
            if cargo_toml.exists():
                src_dir = self.project_root / "src"
                if not src_dir.exists() or not list(src_dir.glob("*.rs")):
                    return GateResult(
                        passed=False,
                        message="Phase 3: No compiled Rust sources found",
                    )

        elif phase_str == "5" or phase_str == "review":
            missing = [f for f in REQUIRED_REVIEW_ARTIFACTS if not (self.project_root / f).exists()]
            if missing:
                return GateResult(
                    passed=False,
                    message=f"Phase 5 incomplete: Missing {len(missing)} review artifacts",
                    blockers=missing,
                )

        elif phase_str == "6" or phase_str == "persistence":
            missing = [f for f in REQUIRED_MEMORY_ARTIFACTS if not (self.project_root / f).exists()]
            if missing:
                return GateResult(
                    passed=False,
                    message=f"Phase 6 incomplete: Missing {', '.join(missing)}",
                )

        return result

    def _list_active_features(self) -> list:
        features_dir = self.project_root / "docs" / "features"
        if not features_dir.exists():
            return []

        active = []
        for feature_dir in features_dir.iterdir():
            if feature_dir.is_dir():
                checkpoint_file = feature_dir / ".sdd" / "checkpoint.json"
                if checkpoint_file.exists():
                    active.append(feature_dir.name)
                elif not (feature_dir / "COMPLETED").exists():
                    active.append(feature_dir.name)

        return active

    def _load_checkpoint(self, feature_dir: Path) -> Optional[dict]:
        checkpoint_file = feature_dir / ".sdd" / "checkpoint.json"
        if checkpoint_file.exists():
            try:
                return json.loads(checkpoint_file.read_text())
            except (json.JSONDecodeError, IOError):
                return None
        return None

    def _check_review_artifacts(self) -> bool:
        return all((self.project_root / f).exists() for f in REQUIRED_REVIEW_ARTIFACTS)

    def _get_feature_status(self, feature_name: str, verbose: bool) -> dict:
        feature_dir = self.project_root / "docs" / "features" / feature_name

        if not feature_dir.exists():
            return {
                "title": f"Feature '{feature_name}' not found",
                "details": [],
            }

        details = []

        mem_dir = feature_dir / ".sdd"
        checkpoint_file = mem_dir / "checkpoint.json"
        if checkpoint_file.exists():
            try:
                cp = json.loads(checkpoint_file.read_text())
                details.append(f"Phase: {cp.get('phase', '?')}")
                details.append(f"Step: {cp.get('step', '?')}")
                details.append(f"Last saved: {cp.get('timestamp', '?')}")
                if cp.get("conversation_memory_snapshot"):
                    nodes = cp["conversation_memory_snapshot"].get("nodes", {})
                    details.append(f"Memory nodes: {len(nodes)}")
                    reqs = sum(1 for n in nodes.values() if n.get("type") == "requirement")
                    decs = sum(1 for n in nodes.values() if n.get("type") == "design_decision")
                    details.append(f"  Requirements: {reqs}, Design Decisions: {decs}")
            except Exception:
                pass

        if verbose:
            task_plan = feature_dir / "task_plan.md"
            findings = feature_dir / "findings.md"
            design_doc = feature_dir / "design-doc.md"
            if task_plan.exists():
                details.append(f"Task Plan: {task_plan}")
            if findings.exists():
                details.append(f"Findings: {findings}")
            if design_doc.exists():
                details.append(f"Design Doc: {design_doc}")

            memory = self._memory_manager.get_memory()
            if memory:
                summary = memory.get_context_summary()
                details.append(f"\nConversation Memory:\n{summary[:500]}")

        return {
            "title": f"Feature: {feature_name}",
            "details": details,
        }

    def _get_project_status(self, verbose: bool) -> dict:
        active_features = self._list_active_features()

        details = []
        if verbose:
            if self._project_initializer.is_initialized(self.project_root):
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

    def _rebuild_context(self, feature_dir: Path, feature_name: str,
                         checkpoint: dict) -> "ExecutionContext":
        capability = self.capability_registry.select(
            checkpoint.get("capability", "brainstorming") if checkpoint else "brainstorming"
        )

        return ExecutionContext(
            project_root=self.project_root,
            feature_name=feature_name,
            feature_dir=feature_dir,
            capability=capability,
            checkpoint=checkpoint or {},
        )

    def _get_current_context(self) -> "ExecutionContext":
        return ExecutionContext(
            project_root=self.project_root,
            feature_name="",
            feature_dir=Path(""),
            capability=None,
        )

    def _ask_web_kernel_mode(self) -> bool:
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


class StateMachine:
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
        return to_phase in self.TRANSITIONS.get(from_phase, [])

    def transition(self, to_phase: Phase) -> bool:
        if self.can_transition(self.current_phase, to_phase):
            self.current_phase = to_phase
            return True
        return False

    def get_current(self) -> Phase:
        return self.current_phase


class GateController:
    def __init__(self):
        self.gates = {}

    def add_gate(self, from_phase: Phase, to_phase: Phase, gate: "Gate"):
        key = (from_phase, to_phase)
        self.gates[key] = gate

    def evaluate(self, from_phase: Phase, to_phase: Phase,
                 context: "ExecutionContext") -> "GateResult":
        key = (from_phase, to_phase)
        gate = self.gates.get(key)

        if not gate:
            return GateResult(passed=True)

        return gate.evaluate(context)
    
    def handle_confirmation(self, result: "MiddlewareResult", context: "ExecutionContext") -> bool:
        if result.allowed:
            return True
        
        if result.requires_confirmation and result.confirmation_options:
            print(f"\n⚠️ Gate Warning: {result.message}")
            print("\nOptions:")
            for i, option in enumerate(result.confirmation_options, 1):
                print(f"  {i}. {option}")
            print()
            
            try:
                choice = input("Select option (or 'N' to abort): ").strip().upper()
                
                if choice == "N":
                    return False
                
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(result.confirmation_options):
                        print(f"\n✅ Selected: {result.confirmation_options[idx]}")
                        return True
                
                print("Invalid choice. Gate blocked.")
                return False
            
            except (EOFError, IOError):
                print("No input. Gate blocked.")
                return False
        
        print(f"\n❌ Gate Blocked: {result.message}")
        return False


class Gate(ABC):
    @abstractmethod
    def evaluate(self, context: "ExecutionContext") -> "GateResult":
        pass


class GateResult:
    def __init__(self, passed: bool, message: str = "", blockers: list = None,
                 gate_name: str = "", details: dict = None):
        self.passed = passed
        self.message = message
        self.blockers = blockers or []
        self.gate_name = gate_name
        self.details = details or {}


class CapabilityRegistry:
    def __init__(self):
        self.capabilities = {}
        self._register_defaults()

    def _register_defaults(self):
        from .capabilities import (
            BrainstormingCapability,
            WritingPlansCapability,
            UnderstandingCapability,
            ThinkBeforeCodingCapability,
        )

        self.capabilities["brainstorming"] = BrainstormingCapability()
        self.capabilities["writing-plans"] = WritingPlansCapability()
        self.capabilities["understanding"] = UnderstandingCapability()
        self.capabilities["think-before-coding"] = ThinkBeforeCodingCapability()

    def select(self, name: str):
        return self.capabilities.get(name)

    def register(self, name: str, capability: "Capability"):
        self.capabilities[name] = capability

    def list_all(self) -> list:
        return list(self.capabilities.keys())


class ExecutionContext:
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