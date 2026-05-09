"""
Phase Orchestrator 基类
v2.3: ConversationMemory integrated into checkpoints + Error Recovery support
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..director import ExecutionContext, GateResult
    from ..error_recovery import ErrorRecoveryManager


class PhaseOrchestrator(ABC):
    def __init__(self, capability_registry=None, error_recovery_manager=None):
        self.capability_registry = capability_registry
        self.steps = []
        self._error_recovery_manager: Optional[ErrorRecoveryManager] = error_recovery_manager
    
    def set_error_recovery_manager(self, manager: ErrorRecoveryManager):
        """设置Error Recovery Manager"""
        self._error_recovery_manager = manager

    @abstractmethod
    def execute(self, context: "ExecutionContext") -> "PhaseResult":
        pass

    def can_transition_to(self, context: ExecutionContext) -> GateResult:
        return GateResult(passed=True)

    def _execute_steps(self, context: ExecutionContext) -> PhaseResult:
        for step in self.steps:
            result = step.execute(context)
            if not result.success:
                return result

        return PhaseResult(success=True)

    def _save_checkpoint(self, context: ExecutionContext, step_name: str):
        import json
        from pathlib import Path

        checkpoint_dir = context.feature_dir / ".sdd"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        checkpoint = {
            "feature_name": context.feature_name,
            "step": step_name,
            "metadata": context.metadata,
            "session_id": context.metadata.get("session_id", ""),
        }

        (checkpoint_dir / "checkpoint.json").write_text(
            json.dumps(checkpoint, indent=2, ensure_ascii=False)
        )

    def _save_phase_checkpoint(self, context: ExecutionContext, phase_name: str):
        """保存Phase级别的checkpoint
        
        Args:
            context: 执行上下文
            phase_name: Phase名称（如"phase2"）
        """
        import json
        from pathlib import Path
        from datetime import datetime
        
        checkpoint_dir = context.feature_dir / ".sdd"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        checkpoint_data = {
            "version": "2.2",
            "timestamp": datetime.now().isoformat(),
            "phase": phase_name,
            "feature_name": context.feature_name,
            "session_id": context.metadata.get("session_id", ""),
            "metadata": context.metadata.copy() if hasattr(context.metadata, 'copy') else dict(context.metadata),
            "artifacts": dict(context.artifacts) if hasattr(context, 'artifacts') else {},
        }
        
        checkpoint_file = checkpoint_dir / f"{phase_name}_checkpoint.json"
        checkpoint_file.write_text(
            json.dumps(checkpoint_data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        main_checkpoint_file = checkpoint_dir / "checkpoint.json"
        main_checkpoint_file.write_text(
            json.dumps(checkpoint_data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        print(f"[Checkpoint] Phase {phase_name} saved to {checkpoint_file}")

    def _save_memory_checkpoint(self, context: ExecutionContext, phase_name: str,
                                director=None, memory=None):
        if director is None:
            self._save_checkpoint(context, f"{phase_name}_entry")
            return

        if memory is None:
            memory = director._memory

        checkpoint_dir = context.feature_dir / ".sdd"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        if memory:
            from ..memory.persistence import MemoryPersistence
            mem_persistence = MemoryPersistence(context.project_root)
            mem_persistence.save(memory, context.feature_name)

            checkpoint_data = {
                "version": "2.1",
                "phase": phase_name,
                "feature_name": context.feature_name,
                "session_id": context.metadata.get("session_id", ""),
                "conversation_memory_snapshot": memory.get_memory_snapshot(),
            }

            from datetime import datetime
            checkpoint_data["timestamp"] = datetime.now().isoformat()

            checkpoint_file = checkpoint_dir / "checkpoint.json"
            with open(checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        else:
            self._save_checkpoint(context, f"{phase_name}_entry")

    def _check_and_refresh_context(self, context: "ExecutionContext", trigger: str):
        """Check ContextMonitor thresholds and refresh if needed.

        Shared by all phase orchestrators to prevent context loss
        during long phases (especially Phase 3 development).
        """
        monitor = context.metadata.get("_context_monitor")
        if monitor is None:
            return
        should_refresh, reason = monitor.should_refresh()
        if should_refresh:
            monitor.inject_refresh(context)
    
    def _capture_error(
        self,
        exception: Exception,
        context: "ExecutionContext",
        phase_name: str,
        step_name: str = "",
        severity: str = "ERROR"
    ):
        """捕获并记录错误
        
        Args:
            exception: 异常对象
            context: 执行上下文
            phase_name: Phase名称
            step_name: Step名称（可选）
            severity: 错误严重程度（ERROR/WARNING/CRITICAL）
        """
        if not self._error_recovery_manager:
            return
        
        from ..error_recovery import ErrorSeverity
        
        severity_enum = ErrorSeverity.ERROR
        if severity == "WARNING":
            severity_enum = ErrorSeverity.WARNING
        elif severity == "CRITICAL":
            severity_enum = ErrorSeverity.CRITICAL
        
        operation = f"{phase_name}.{step_name}" if step_name else phase_name
        
        self._error_recovery_manager.capture_error(
            exception=exception,
            operation=operation,
            severity=severity_enum,
            file_path=str(context.feature_dir),
            context={
                "phase": phase_name,
                "step": step_name,
                "feature_name": context.feature_name,
            },
        )


class PhaseStep(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute(self, context: "ExecutionContext") -> "StepResult":
        pass


class StepResult:
    def __init__(self, success: bool, message: str = "", details: dict = None):
        self.success = success
        self.message = message
        self.details = details or {}


class PhaseResult:
    def __init__(self, success: bool, artifacts: dict = None, message: str = ""):
        self.success = success
        self.artifacts = artifacts or {}
        self.message = message
