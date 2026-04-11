"""
Checkpoint Manager
全局 Checkpoint 管理器
"""

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .persistence import CheckpointPersistence
from .recovery import CheckpointRecovery
from .realtime import RealTimeSync
from .phase_level import PhaseLevelCheckpoints


class CheckpointManager:
    """
    Checkpoint 管理器
    
    职责:
    - 管理项目级和特性级 Checkpoint
    - 协调持久化、恢复、实时同步
    - 提供 Checkpoint 查询接口
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.persistence = CheckpointPersistence(project_root)
        self.recovery = CheckpointRecovery(project_root)
        self.realtime = RealTimeSync(project_root)
        self.phase_checkpoints = PhaseLevelCheckpoints(project_root)
        
        self._current_checkpoint: Optional[Dict[str, Any]] = None
    
    def save(
        self,
        feature_name: str,
        phase: str,
        step: str,
        context: "ExecutionContext",
        artifacts: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """
        保存 Checkpoint
        
        Args:
            feature_name: 特性名称
            phase: 当前 Phase
            step: 当前 Step
            context: 执行上下文
            artifacts: 产物字典
            
        Returns:
            Checkpoint 文件路径
        """
        checkpoint_data = {
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "feature_name": feature_name,
            "phase": phase,
            "step": step,
            "metadata": context.metadata.copy() if context.metadata else {},
            "artifacts": artifacts or {},
            "project_root": str(self.project_root),
        }
        
        self._current_checkpoint = checkpoint_data
        
        feature_dir = self.project_root / "docs" / "features" / feature_name
        return self.persistence.save(feature_dir, checkpoint_data)
    
    def load(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """
        加载 Checkpoint
        
        Args:
            feature_name: 特性名称
            
        Returns:
            Checkpoint 数据或 None
        """
        feature_dir = self.project_root / "docs" / "features" / feature_name
        return self.persistence.load(feature_dir)
    
    def load_latest(self) -> Optional[Dict[str, Any]]:
        """
        加载最新的 Checkpoint
        
        Returns:
            最新的 Checkpoint 数据或 None
        """
        return self.recovery.find_latest_checkpoint()
    
    def recover(self, feature_name: str) -> Optional["ExecutionContext"]:
        """
        恢复执行上下文
        
        Args:
            feature_name: 特性名称
            
        Returns:
            恢复的 ExecutionContext 或 None
        """
        checkpoint = self.load(feature_name)
        if not checkpoint:
            return None
        
        return self.recovery.rebuild_context(checkpoint)
    
    def list_checkpoints(self, feature_name: str) -> list:
        """
        列出特性的所有 Checkpoint
        
        Args:
            feature_name: 特性名称
            
        Returns:
            Checkpoint 列表
        """
        feature_dir = self.project_root / "docs" / "features" / feature_name
        return self.persistence.list_all(feature_dir)
    
    def delete(self, feature_name: str) -> bool:
        """
        删除 Checkpoint
        
        Args:
            feature_name: 特性名称
            
        Returns:
            是否成功删除
        """
        feature_dir = self.project_root / "docs" / "features" / feature_name
        return self.persistence.delete(feature_dir)
    
    def enable_realtime_sync(self, feature_name: str):
        """启用实时同步"""
        self.realtime.enable(feature_name)
    
    def disable_realtime_sync(self, feature_name: str):
        """禁用实时同步"""
        self.realtime.disable(feature_name)
    
    def sync_now(self, feature_name: str) -> bool:
        """立即同步"""
        return self.realtime.sync(feature_name)
