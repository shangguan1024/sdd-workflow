"""
Phase Orchestrator 基类
v2.1: ConversationMemory integrated into checkpoints
"""

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..director import ExecutionContext, GateResult


class PhaseOrchestrator(ABC):
    def __init__(self, capability_registry=None):
        self.capability_registry = capability_registry
        self.steps = []

    @abstractmethod
    def execute(self, context: ExecutionContext) -> PhaseResult:
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


class PhaseStep(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute(self, context: ExecutionContext) -> StepResult:
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
