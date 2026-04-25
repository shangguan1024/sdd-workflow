"""
Checkpoint Manager
全局 Checkpoint 管理器
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from .persistence import CheckpointPersistence
from .recovery import CheckpointRecovery
from .realtime import RealTimeSync
from .phase_level import PhaseLevelCheckpoints


class CheckpointManager:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.persistence = CheckpointPersistence(project_root)
        self.recovery = CheckpointRecovery(project_root)
        self.realtime = RealTimeSync(project_root)
        self.phase_checkpoints = PhaseLevelCheckpoints(project_root)
        self._memory = None
        self._current_checkpoint: Optional[Dict[str, Any]] = None

    def set_memory(self, memory):
        self._memory = memory

    def save(
        self,
        feature_name: str,
        phase: str,
        step: str,
        context: "ExecutionContext",
        artifacts: Optional[Dict[str, Any]] = None,
    ) -> Path:
        checkpoint_data = {
            "version": "2.1",
            "timestamp": datetime.now().isoformat(),
            "feature_name": feature_name,
            "phase": phase,
            "step": step,
            "metadata": context.metadata.copy() if context.metadata else {},
            "artifacts": artifacts or {},
            "project_root": str(self.project_root),
            "conversation_memory_snapshot": (
                self._memory.get_memory_snapshot() if self._memory else None
            ),
        }

        self._current_checkpoint = checkpoint_data

        feature_dir = self.project_root / "docs" / "features" / feature_name
        checkpoint_path = self.persistence.save(feature_dir, checkpoint_data)

        if self._memory:
            from ..memory.persistence import MemoryPersistence
            mem_persistence = MemoryPersistence(self.project_root)
            mem_persistence.save(self._memory, feature_name)

        return checkpoint_path

    def load(self, feature_name: str) -> Optional[Dict[str, Any]]:
        feature_dir = self.project_root / "docs" / "features" / feature_name
        return self.persistence.load(feature_dir)

    def load_latest(self) -> Optional[Dict[str, Any]]:
        return self.recovery.find_latest_checkpoint()

    def recover(self, feature_name: str) -> Optional["ExecutionContext"]:
        checkpoint = self.load(feature_name)
        if not checkpoint:
            return None

        context = self.recovery.rebuild_context(checkpoint)

        if checkpoint.get("conversation_memory_snapshot"):
            from ..memory.conversation import ConversationMemory
            self._memory = ConversationMemory.from_snapshot(
                checkpoint["conversation_memory_snapshot"],
                self.project_root,
            )
        else:
            from ..memory.recovery import MemoryRecovery
            recovery = MemoryRecovery(self.project_root)
            self._memory = recovery.recover_or_create(feature_name)

        return context

    def recover_memory(self, feature_name: str):
        checkpoint = self.load(feature_name)
        if checkpoint and checkpoint.get("conversation_memory_snapshot"):
            from ..memory.conversation import ConversationMemory
            self._memory = ConversationMemory.from_snapshot(
                checkpoint["conversation_memory_snapshot"],
                self.project_root,
            )
            return self._memory

        from ..memory.recovery import MemoryRecovery
        recovery = MemoryRecovery(self.project_root)
        self._memory = recovery.recover_or_create(feature_name)
        return self._memory

    def get_memory(self):
        return self._memory

    def list_checkpoints(self, feature_name: str) -> list:
        feature_dir = self.project_root / "docs" / "features" / feature_name
        return self.persistence.list_all(feature_dir)

    def get_session_context(self, feature_name: str) -> Optional[Dict[str, Any]]:
        checkpoint = self.load(feature_name)
        if not checkpoint:
            return None

        return {
            "feature_name": checkpoint.get("feature_name", ""),
            "phase": checkpoint.get("phase", ""),
            "step": checkpoint.get("step", ""),
            "timestamp": checkpoint.get("timestamp", ""),
            "has_memory": checkpoint.get("conversation_memory_snapshot") is not None,
            "memory_node_count": (
                len(checkpoint.get("conversation_memory_snapshot", {}).get("nodes", {}))
                if checkpoint.get("conversation_memory_snapshot")
                else 0
            ),
            "metadata": checkpoint.get("metadata", {}),
        }

    def delete(self, feature_name: str) -> bool:
        feature_dir = self.project_root / "docs" / "features" / feature_name
        return self.persistence.delete(feature_dir)

    def enable_realtime_sync(self, feature_name: str):
        self.realtime.enable(feature_name)

    def disable_realtime_sync(self, feature_name: str):
        self.realtime.disable(feature_name)

    def sync_now(self, feature_name: str) -> bool:
        return self.realtime.sync(feature_name)

    def get_all_session_checkpoints(self, feature_name: str) -> List[Dict[str, Any]]:
        feature_dir = self.project_root / "docs" / "features" / feature_name
        checkpoints = self.persistence.list_all(feature_dir)

        results = []
        for cp in checkpoints:
            results.append({
                "timestamp": cp.get("timestamp", ""),
                "phase": cp.get("phase", ""),
                "step": cp.get("step", ""),
                "has_memory": cp.get("conversation_memory_snapshot") is not None,
                "artifact_count": len(cp.get("artifacts", {})),
            })

        return sorted(results, key=lambda r: r["timestamp"])

    def export_session_summary(self, feature_name: str) -> str:
        checkpoint = self.load(feature_name)
        if not checkpoint:
            return f"No checkpoint found for '{feature_name}'"

        lines = [
            f"# Session Summary: {feature_name}",
            f"Last Phase: {checkpoint.get('phase', 'unknown')}",
            f"Last Step: {checkpoint.get('step', 'unknown')}",
            f"Timestamp: {checkpoint.get('timestamp', 'unknown')}",
            f"Version: {checkpoint.get('version', 'unknown')}",
            "",
            "## Artifacts",
        ]

        for name, value in checkpoint.get("artifacts", {}).items():
            lines.append(f"  - {name}: {str(value)[:100]}")

        if checkpoint.get("conversation_memory_snapshot"):
            memory = checkpoint["conversation_memory_snapshot"]
            nodes = memory.get("nodes", {})
            lines.append("")
            lines.append(f"## Conversation Memory ({len(nodes)} nodes)")

            for nid, node in nodes.items():
                lines.append(
                    f"  [{node.get('type', '?')}] {node.get('title', nid)}"
                )

        lines.append("")
        lines.append("## Metadata")
        for key, value in checkpoint.get("metadata", {}).items():
            lines.append(f"  {key}: {str(value)[:100]}")

        return "\n".join(lines)
