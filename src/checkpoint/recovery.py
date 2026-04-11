"""
Checkpoint Recovery
从 Checkpoint 恢复执行上下文
"""

from pathlib import Path
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..director import ExecutionContext

class CheckpointRecovery:
    """
    Checkpoint 恢复
    
    职责:
    - 从 Checkpoint 数据重建 ExecutionContext
    - 查找最新 Checkpoint
    - 验证 Checkpoint 完整性
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def rebuild_context(self, checkpoint: Dict[str, Any]) -> "ExecutionContext":
        """
        从 Checkpoint 重建 ExecutionContext
        
        Args:
            checkpoint: Checkpoint 数据
            
        Returns:
            ExecutionContext 对象
        """
        from ..director import ExecutionContext, CapabilityRegistry
        
        feature_name = checkpoint.get("feature_name", "")
        feature_dir = self.project_root / "docs" / "features" / feature_name
        
        registry = CapabilityRegistry()
        capability_name = checkpoint.get("metadata", {}).get("capability", "brainstorming")
        capability = registry.select(capability_name)
        
        context = ExecutionContext(
            project_root=self.project_root,
            feature_name=feature_name,
            feature_dir=feature_dir,
            capability=capability,
            checkpoint=checkpoint,
        )
        
        context.metadata = checkpoint.get("metadata", {}).copy()
        context.artifacts = checkpoint.get("artifacts", {}).copy()
        
        return context
    
    def find_latest_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        查找最新的 Checkpoint
        
        Returns:
            最新 Checkpoint 数据或 None
        """
        features_dir = self.project_root / "docs" / "features"
        
        if not features_dir.exists():
            return None
        
        latest_checkpoint = None
        latest_time = None
        
        for feature_dir in features_dir.iterdir():
            if not feature_dir.is_dir():
                continue
            
            checkpoint_file = feature_dir / ".sdd" / "checkpoint.json"
            if not checkpoint_file.exists():
                continue
            
            try:
                import json
                with open(checkpoint_file, "r", encoding="utf-8") as f:
                    checkpoint = json.load(f)
                
                timestamp = checkpoint.get("timestamp", "")
                if not latest_time or timestamp > latest_time:
                    latest_time = timestamp
                    latest_checkpoint = checkpoint
                    
            except (json.JSONDecodeError, IOError):
                continue
        
        return latest_checkpoint
    
    def validate_checkpoint(self, checkpoint: Dict[str, Any]) -> bool:
        """
        验证 Checkpoint 完整性
        
        Args:
            checkpoint: Checkpoint 数据
            
        Returns:
            是否有效
        """
        required_fields = [
            "version",
            "timestamp",
            "feature_name",
            "phase",
            "step",
        ]
        
        for field in required_fields:
            if field not in checkpoint:
                return False
        
        if checkpoint.get("version") != "2.0":
            return False
        
        return True
    
    def get_recovery_point(self, checkpoint: Dict[str, Any]) -> Dict[str, str]:
        """
        获取恢复点信息
        
        Args:
            checkpoint: Checkpoint 数据
            
        Returns:
            恢复点信息字典
        """
        return {
            "feature_name": checkpoint.get("feature_name", ""),
            "phase": checkpoint.get("phase", ""),
            "step": checkpoint.get("step", ""),
            "timestamp": checkpoint.get("timestamp", ""),
        }
