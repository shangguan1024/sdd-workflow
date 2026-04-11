"""
Phase Level Checkpoints
Phase 级 Checkpoint 支持
"""

from pathlib import Path
from typing import Optional, Dict, Any, List


class PhaseLevelCheckpoints:
    """
    Phase 级 Checkpoint
    
    职责:
    - 管理每个 Phase 的入口/出口 Checkpoint
    - Phase 间状态传递
    - Gate 决策支持
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def save_phase_entry(
        self,
        feature_name: str,
        phase: str,
        context: "ExecutionContext",
    ) -> Path:
        """
        保存 Phase 入口 Checkpoint
        
        Args:
            feature_name: 特性名称
            phase: Phase 名称
            context: 执行上下文
            
        Returns:
            Checkpoint 文件路径
        """
        feature_dir = self.project_root / "docs" / "features" / feature_name
        phase_checkpoint_dir = feature_dir / ".sdd" / "phases"
        phase_checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        import json
        from datetime import datetime
        
        checkpoint_data = {
            "type": "phase_entry",
            "phase": phase,
            "timestamp": datetime.now().isoformat(),
            "feature_name": feature_name,
            "context": {
                "metadata": context.metadata.copy() if context.metadata else {},
                "artifacts": context.artifacts.copy() if context.artifacts else {},
            },
        }
        
        checkpoint_file = phase_checkpoint_dir / f"{phase}_entry.json"
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        
        return checkpoint_file
    
    def save_phase_exit(
        self,
        feature_name: str,
        phase: str,
        context: "ExecutionContext",
        gate_result: "GateResult",
    ) -> Path:
        """
        保存 Phase 出口 Checkpoint
        
        Args:
            feature_name: 特性名称
            phase: Phase 名称
            context: 执行上下文
            gate_result: Gate 评估结果
            
        Returns:
            Checkpoint 文件路径
        """
        feature_dir = self.project_root / "docs" / "features" / feature_name
        phase_checkpoint_dir = feature_dir / ".sdd" / "phases"
        phase_checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        import json
        from datetime import datetime
        
        checkpoint_data = {
            "type": "phase_exit",
            "phase": phase,
            "timestamp": datetime.now().isoformat(),
            "feature_name": feature_name,
            "gate_passed": gate_result.passed if gate_result else True,
            "gate_message": gate_result.message if gate_result else "",
            "context": {
                "metadata": context.metadata.copy() if context.metadata else {},
                "artifacts": context.artifacts.copy() if context.artifacts else {},
            },
        }
        
        checkpoint_file = phase_checkpoint_dir / f"{phase}_exit.json"
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        
        return checkpoint_file
    
    def load_phase_checkpoint(
        self,
        feature_name: str,
        phase: str,
        checkpoint_type: str = "exit",
    ) -> Optional[Dict[str, Any]]:
        """
        加载 Phase Checkpoint
        
        Args:
            feature_name: 特性名称
            phase: Phase 名称
            checkpoint_type: Checkpoint 类型 (entry/exit)
            
        Returns:
            Checkpoint 数据或 None
        """
        feature_dir = self.project_root / "docs" / "features" / feature_name
        checkpoint_file = feature_dir / ".sdd" / "phases" / f"{phase}_{checkpoint_type}.json"
        
        if not checkpoint_file.exists():
            return None
        
        try:
            import json
            with open(checkpoint_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def get_phase_history(self, feature_name: str) -> List[Dict[str, Any]]:
        """
        获取 Phase 执行历史
        
        Args:
            feature_name: 特性名称
            
        Returns:
            Phase 历史列表
        """
        feature_dir = self.project_root / "docs" / "features" / feature_name
        phase_checkpoint_dir = feature_dir / ".sdd" / "phases"
        
        if not phase_checkpoint_dir.exists():
            return []
        
        history = []
        
        for checkpoint_file in phase_checkpoint_dir.glob("*_exit.json"):
            try:
                import json
                with open(checkpoint_file, "r", encoding="utf-8") as f:
                    history.append(json.load(f))
            except (json.JSONDecodeError, IOError):
                continue
        
        history.sort(key=lambda x: x.get("timestamp", ""))
        return history
    
    def verify_phase_sequence(
        self,
        feature_name: str,
        expected_sequence: List[str],
    ) -> Dict[str, Any]:
        """
        验证 Phase 执行顺序
        
        Args:
            feature_name: 特性名称
            expected_sequence: 期望的 Phase 顺序
            
        Returns:
            验证结果
        """
        history = self.get_phase_history(feature_name)
        
        if not history:
            return {
                "valid": False,
                "message": "No phase history found",
                "actual_sequence": [],
            }
        
        actual_sequence = [h.get("phase") for h in history]
        
        for i, expected_phase in enumerate(expected_sequence):
            if i >= len(actual_sequence):
                return {
                    "valid": False,
                    "message": f"Missing phase: {expected_phase}",
                    "actual_sequence": actual_sequence,
                    "expected_sequence": expected_sequence,
                }
            
            if actual_sequence[i] != expected_phase:
                return {
                    "valid": False,
                    "message": f"Phase mismatch at position {i}: expected {expected_phase}, got {actual_sequence[i]}",
                    "actual_sequence": actual_sequence,
                    "expected_sequence": expected_sequence,
                }
        
        return {
            "valid": True,
            "message": "Phase sequence is valid",
            "actual_sequence": actual_sequence,
            "expected_sequence": expected_sequence,
        }
