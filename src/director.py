"""
SDD-Workflow Director (Layer 1)
主状态机、Gate 控制、流程编排
v2.1: ConversationMemory integration, Middleware hooks, proper QualityGate
"""

import json
import sys
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum

# 确保项目根目录在 path 中，以便导入顶层 middleware/
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
        self._memory = None
        self._session_id = str(uuid.uuid4())[:8]
        
        from .checkpoint import CheckpointManager
        self._checkpoint_manager = CheckpointManager(project_root)
        
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
            Phase.REQUIREMENTS: Phase1Orchestrator(self.capability_registry),
            Phase.PLANNING: Phase2Orchestrator(self.capability_registry),
            Phase.DEVELOPMENT: Phase3Orchestrator(self.capability_registry),
            Phase.INTEGRATION: Phase4Orchestrator(self.capability_registry),
            Phase.REVIEW: Phase5Orchestrator(self.capability_registry),
            Phase.PERSISTENCE: Phase6Orchestrator(self.capability_registry),
        }

    def _init_middleware(self):
        from middleware import (
            PhaseGateMiddleware,
            LoopDetectionMiddleware,
            ArtifactCompleteMiddleware,
            PhaseCompressionMiddleware,
        )

        const_dir = self.project_root / "CONSTITUTION"
        self._phase_gate_mw = PhaseGateMiddleware(const_dir) if const_dir.exists() else None

        config_dir = Path(__file__).parent.parent / "config"
        loop_config = config_dir / "loop_detection.yaml"
        self._loop_detection_mw = LoopDetectionMiddleware(loop_config)

        artifact_config = config_dir / "artifact_checker.yaml"
        self._artifact_mw = ArtifactCompleteMiddleware(self.project_root, artifact_config)

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
        # ContextMonitor: track edit + check for mid-phase context refresh
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
        """Find the active feature directory to build context for refresh."""
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
        """Public method for phase orchestrators to trigger context refresh."""
        self._context_monitor.force_refresh(context, reason)

    def record_task_complete(self, task_name: str = ""):
        """Called by phase orchestrators when a sub-task completes."""
        self._context_monitor.record_task(task_name)
        should_refresh, reason = self._context_monitor.should_refresh()
        if should_refresh:
            ctx = self._get_active_context()
            if ctx and ctx.feature_name:
                print(f"\n  ⚠️  {reason}\n")
                self._context_monitor.inject_refresh(ctx)

    def reset_context_monitor(self):
        """Reset context monitor for a new feature session."""
        self._context_monitor.reset()

    def initialize(self, command: InitCommand) -> Result:
        try:
            project_path = command.args.get("path") or self.project_root

            if not command.args.get("force") and self._is_initialized(project_path):
                return Result(
                    success=False,
                    message="Project already initialized. Use --force to reinitialize.",
                )

            self._create_directory_structure(project_path)
            self._initialize_config_files(project_path, command)
            self._initialize_constitution(project_path)
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
        try:
            feature_name = command.args.get("feature")
            feature_dir = self.project_root / "docs" / "features" / feature_name

            feature_dir.mkdir(parents=True, exist_ok=True)

            self._initialize_feature_artifacts(feature_dir, feature_name)
            self.reset_context_monitor()

            self._memory = self._load_or_create_memory(feature_name)
            self._memory.start_session(self._session_id)
            
            if self._checkpoint_manager:
                self._checkpoint_manager.set_memory(self._memory)
                self._checkpoint_manager.enable_realtime_sync(feature_name)
                print("✅ Real-time checkpoint sync enabled (30s interval)")

            capability_name = command.args.get("capability") or "brainstorming"
            capability = self.capability_registry.select(capability_name)

            orchestrator = self.phase_orchestrators.get(Phase.REQUIREMENTS)
            if not orchestrator:
                raise RuntimeError("Phase1 orchestrator not found")

            web_kernel_mode = self._ask_web_kernel_mode()

            print()
            print("\U0001f4da Understanding 阶段")
            print("=" * 50)
            print("在进入设计阶段之前，必须先深入理解现有系统和相关原理...")
            self._show_memory_context()

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

            self.inject_memory_context(context, feature_name)

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
                self._save_memory_silent(feature_name)
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

        except Exception as e:
            return Result(success=False, message=f"Start feature failed: {e}")

    def _show_memory_context(self):
        if self._memory and self._memory.nodes:
            unresolved = self._memory.get_unresolved_nodes()
            questions = self._memory.get_open_questions()
            if unresolved or questions:
                print()
                print("\U0001f4dd 检测到上次会话未完成的讨论:")
                for q in questions:
                    print(f"  \u2753 {q.title}: {q.content[:100]}")
                for node in unresolved:
                    if node.type.value != "open_question":
                        print(f"  \u26a0\ufe0f [{node.type.value}] {node.title}")
                print()

    def inject_memory_context(self, context: "ExecutionContext", feature_name: str, use_progressive_disclosure: bool = True):
        """
        将 ConversationMemory 上下文注入到当前会话。

        改进：使用 Progressive Disclosure（渐进式披露）
        - Layer 1: 仅注入索引（最小token）
        - Layer 2/3: 按需调用方法获取详情

        Args:
            context: 执行上下文
            feature_name: 特性名称
            use_progressive_disclosure: 是否使用渐进披露（默认True）
        """
        if use_progressive_disclosure and self._memory and self._memory.nodes:
            # 使用 Progressive Disclosure
            self._inject_with_progressive_disclosure(context, feature_name)
        else:
            # 传统方式（全量注入）
            self._inject_full_context(context, feature_name)
    
    def _inject_with_progressive_disclosure(self, context: "ExecutionContext", feature_name: str):
        """
        Progressive Disclosure 注入方式
        
        仅注入Layer 1（索引），提供方法供LLM按需调用Layer 2/3
        """
        from .memory.progressive_disclosure import ProgressiveDisclosure
        
        disclosure = ProgressiveDisclosure(self._memory)
        
        # Layer 1: 获取索引
        indices = disclosure.get_index(limit=15)
        
        # 格式化索引表
        index_table = disclosure.format_index_table(indices)
        
        # 注入到context
        context.metadata["injected_context"] = index_table
        context.metadata["context_injected"] = True
        context.metadata["progressive_disclosure_enabled"] = True
        context.metadata["progressive_disclosure_instance"] = disclosure
        
        # 注入AGENTS.md（如果存在）
        agents_file = self.project_root / "AGENTS.md"
        if agents_file.exists():
            agents_content = agents_file.read_text(encoding="utf-8")
            # 仅注入AGENTS.md的目录部分（前1000字符）
            agents_summary = agents_content[:1000]
            context.metadata["injected_context"] = f"{agents_summary}\n\n---\n\n{index_table}"
            context.metadata["agents_context_loaded"] = True
        
        # Token统计
        token_stats = disclosure.get_token_stats()
        context.metadata["progressive_disclosure_token_stats"] = token_stats
        
        # 保存到current_context.md
        feature_dir = self.project_root / "docs" / "features" / feature_name
        context_dir = feature_dir / ".sdd"
        context_dir.mkdir(parents=True, exist_ok=True)
        context_file = context_dir / "current_context.md"
        context_file.write_text(context.metadata["injected_context"], encoding="utf-8")
        
        # 记录统计
        stats = {
            "Method": "Progressive Disclosure (Layer 1)",
            "MemoryNodes": len(indices),
            "TokenEstimate": token_stats["layer1_used"],
            "Savings": token_stats["savings_estimate"],
        }
        context.metadata["context_injection_stats"] = stats
    
    def _inject_full_context(self, context: "ExecutionContext", feature_name: str):
        """
        传统全量注入方式（向后兼容）
        
        直接注入全部内容，可能消耗大量token
        """
        context_parts = []
        stats = {}

        agents_file = self.project_root / "AGENTS.md"
        if agents_file.exists():
            agents_content = agents_file.read_text(encoding="utf-8")
            context_parts.append(agents_content)
            context.metadata["agents_context_loaded"] = True
            stats["AGENTS.md"] = f"{len(agents_content)} chars"
        else:
            context.metadata["agents_context_loaded"] = False
            stats["AGENTS.md"] = "not found"

        if self._memory and self._memory.nodes:
            summary = self._memory.get_context_summary()
            if summary and summary != "No conversation memory recorded yet.":
                context_parts.append(
                    f"\n## 会话记忆 (ConversationMemory)\n\n{summary}"
                )
                stats["ConversationMemory"] = f"{len(self._memory.nodes)} nodes"
            context.metadata["conversation_memory_summary"] = summary
        else:
            stats["ConversationMemory"] = "no nodes"

        feature_dir = self.project_root / "docs" / "features" / feature_name
        if feature_dir.exists():
            for filename in ["task_plan.md", "findings.md", "progress.md"]:
                filepath = feature_dir / filename
                if filepath.exists():
                    content = filepath.read_text(encoding="utf-8")
                    context_parts.append(f"\n## {filename}\n\n{content[:2000]}")
                    stats[filename] = f"{len(content)} chars"
            context.metadata["feature_artifacts_loaded"] = True

        if context_parts:
            combined = "\n\n".join(context_parts)
            context.metadata["injected_context"] = combined
            context.metadata["context_injected"] = True

            context_dir = feature_dir / ".sdd"
            context_dir.mkdir(parents=True, exist_ok=True)
            context_file = context_dir / "current_context.md"
            context_file.write_text(combined, encoding="utf-8")
            stats["current_context.md"] = f"{len(combined)} chars written"
        else:
            context.metadata["context_injected"] = False
            stats["current_context.md"] = "empty"

        context.metadata["context_injection_stats"] = stats
    
    def get_memory_timeline(self, context: "ExecutionContext", around_id: str) -> str:
        """
        Layer 2: 获取时间线
        
        LLM可以调用此方法获取特定节点的时间上下文
        
        Args:
            context: 执行上下文
            around_id: 围绕哪个节点
        
        Returns:
            str: 时间线Markdown内容
        """
        if not context.metadata.get("progressive_disclosure_enabled"):
            return "Progressive Disclosure not enabled. Context was injected with full mode."
        
        disclosure = context.metadata.get("progressive_disclosure_instance")
        if not disclosure:
            return "Progressive Disclosure instance not found in context."
        
        timelines = disclosure.get_timeline(around_id=around_id)
        timeline_content = disclosure.format_timeline_context(timelines)
        
        # 更新token统计
        token_stats = disclosure.get_token_stats()
        context.metadata["progressive_disclosure_token_stats"] = token_stats
        
        return timeline_content
    
    def get_memory_full_details(self, context: "ExecutionContext", ids: List[str]) -> str:
        """
        Layer 3: 获取完整详情
        
        LLM可以调用此方法获取特定节点的完整内容
        
        Args:
            context: 执行上下文
            ids: 要获取的节点ID列表
        
        Returns:
            str: 完整详情Markdown内容
        """
        if not context.metadata.get("progressive_disclosure_enabled"):
            return "Progressive Disclosure not enabled. Context was injected with full mode."
        
        disclosure = context.metadata.get("progressive_disclosure_instance")
        if not disclosure:
            return "Progressive Disclosure instance not found in context."
        
        nodes = disclosure.get_full_details(ids)
        details_content = disclosure.format_full_details(nodes)
        
        # 更新token统计
        token_stats = disclosure.get_token_stats()
        context.metadata["progressive_disclosure_token_stats"] = token_stats
        
        return details_content

    def _print_context_to_stdout(self, context: "ExecutionContext", feature_name: str):
        """
        将注入的上下文输出到 stdout。

        改进：支持 Progressive Disclosure 输出
        """
        stats = context.metadata.get("context_injection_stats", {})
        injected = context.metadata.get("injected_context", "")
        progressive_enabled = context.metadata.get("progressive_disclosure_enabled", False)

        print()
        print("=" * 60)
        print("  CONTEXT RECOVERY — 跨会话上下文恢复")
        print("=" * 60)
        print()

        if stats:
            print("上下文来源:")
            for source, info in stats.items():
                print(f"   {source}: {info}")
        
        # Progressive Disclosure提示
        if progressive_enabled:
            print()
            print("[INFO] Progressive Disclosure enabled (Layer 1)")
            print()
            token_stats = context.metadata.get("progressive_disclosure_token_stats", {})
            if token_stats:
                print(f"   Token estimate: ~{token_stats.get('layer1_used', 0)} tokens")
                print(f"   Savings: {token_stats.get('savings_estimate', 'N/A')}")
            print()
            print("To view more context, use:")
            print("   - get_memory_timeline(around_id='xxx') — Layer 2")
            print("   - get_memory_full_details(ids=['xxx']) — Layer 3")

        if injected:
            print()
            print("-" * 60)
            if progressive_enabled:
                print("  INJECTED CONTEXT (Memory Index + AGENTS.md summary)")
            else:
                print("  INJECTED CONTEXT (AGENTS.md + Memory + Artifacts)")
            print("-" * 60)
            print()
            truncated = injected[:6000]
            print(truncated)
            if len(injected) > 6000:
                print()
                print(f"... (truncated, full context in .sdd/current_context.md)")
            print()
            print("-" * 60)
            print("  END OF INJECTED CONTEXT")
            print("-" * 60)

        print()
        if progressive_enabled:
            print("[INFO] 以上是Memory索引（Layer 1）。按需调用Layer 2/3获取详情。")
        else:
            print("[INFO] 以上是上一会话的完整上下文。请基于此继续开发。")
        print()

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

            self._memory = self._load_or_create_memory(feature_name)
            self._memory.start_session(self._session_id)

            if self._checkpoint_manager:
                self._checkpoint_manager.set_memory(self._memory)
                self._checkpoint_manager.enable_realtime_sync(feature_name)
                print("✅ Real-time checkpoint sync enabled (30s interval)")

            self._show_memory_context()

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

                self.inject_memory_context(context, feature_name)

                print(f"\U0001f504 从 Phase {phase_name} 恢复: {feature_name}")
                print()

                self._print_context_to_stdout(context, feature_name)

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
                print(f"\u26a0\ufe0f No orchestrator for phase '{phase_name}'. Starting from Phase 1.")
                orchestrator = self.phase_orchestrators.get(Phase.REQUIREMENTS)
                if orchestrator:
                    context = self._rebuild_context(feature_dir, feature_name, checkpoint)
                    context.metadata["session_id"] = self._session_id
                    self.inject_memory_context(context, feature_name)
                    self._print_context_to_stdout(context, feature_name)
                    orchestrator.execute(context)

            return Result(
                success=True,
                message=f"Resumed feature '{feature_name}'",
                details=[f"Resuming from Phase: {phase_name}"],
            )

        except Exception as e:
            return Result(success=False, message=f"Resume failed: {e}")

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
        status_file = feature_dir / "status.toml"
        if status_file.exists():
            try:
                import toml
                return toml.loads(status_file.read_text())
            except Exception:
                pass

        checkpoint = self._load_checkpoint(feature_dir)
        if checkpoint:
            return {
                "current_phase": checkpoint.get("phase", "1"),
                "current_task": checkpoint.get("step", ""),
                "progress": "",
            }
        return {"current_phase": "1"}

    def _load_or_create_memory(self, feature_name: str):
        from .memory.recovery import MemoryRecovery
        recovery = MemoryRecovery(self.project_root)
        return recovery.recover_or_create(feature_name)

    def _save_memory_silent(self, feature_name: str):
        if self._memory:
            try:
                from .memory.persistence import MemoryPersistence
                persistence = MemoryPersistence(self.project_root)
                persistence.save(self._memory, feature_name)
            except Exception:
                pass

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
            return Result(success=False, message=f"Status failed: {e}")

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
            return Result(success=False, message=f"Complete failed: {e}")

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

    def _is_initialized(self, path: Path) -> bool:
        return (
            (path / "CONSTITUTION").exists()
            or (path / ".sdd").exists()
            or (path / "PROJECT_STATE.md").exists()
        )

    def _create_directory_structure(self, project_root: Path):
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
        const_dir = project_root / "CONSTITUTION"
        const_dir.mkdir(parents=True, exist_ok=True)

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
            progress = feature_dir / "progress.md"
            if task_plan.exists():
                details.append(f"Task Plan: {task_plan}")
            if findings.exists():
                details.append(f"Findings: {findings}")
            if progress.exists():
                details.append(f"Progress: {progress}")

            if self._memory:
                summary = self._memory.get_context_summary()
                details.append(f"\nConversation Memory:\n{summary[:500]}")

        return {
            "title": f"Feature: {feature_name}",
            "details": details,
        }

    def _get_project_status(self, verbose: bool) -> dict:
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


class Gate:
    def evaluate(self, context: "ExecutionContext") -> "GateResult":
        raise NotImplementedError


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
