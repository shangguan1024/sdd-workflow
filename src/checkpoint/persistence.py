"""
Checkpoint Persistence
Checkpoint 持久化存储
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime


class CheckpointPersistence:
    """
    Checkpoint 持久化
    
    支持:
    - JSON 文件存储
    - Checkpoint 历史管理
    - 原子写入
    """
    
    CHECKPOINT_DIR = ".sdd"
    CHECKPOINT_FILE = "checkpoint.json"
    HISTORY_DIR = "history"
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def save(
        self,
        feature_dir: Path,
        checkpoint_data: Dict[str, Any],
    ) -> Path:
        """
        保存 Checkpoint
        
        Args:
            feature_dir: 特性目录
            checkpoint_data: Checkpoint 数据
            
        Returns:
            保存的文件路径
        """
        checkpoint_dir = feature_dir / self.CHECKPOINT_DIR
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        checkpoint_path = checkpoint_dir / self.CHECKPOINT_FILE
        
        backup_path = None
        if checkpoint_path.exists():
            backup_path = checkpoint_dir / f"checkpoint.backup.json"
            checkpoint_path.rename(backup_path)
        
        try:
            with open(checkpoint_path, "w", encoding="utf-8") as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
            
            self._save_to_history(checkpoint_dir, checkpoint_data)
            
            if backup_path and backup_path.exists():
                backup_path.unlink()
            
        except Exception as e:
            if backup_path and backup_path.exists():
                backup_path.rename(checkpoint_path)
            raise e
        
        return checkpoint_path
    
    def load(self, feature_dir: Path) -> Optional[Dict[str, Any]]:
        """
        加载 Checkpoint
        
        Args:
            feature_dir: 特性目录
            
        Returns:
            Checkpoint 数据或 None
        """
        checkpoint_path = feature_dir / self.CHECKPOINT_DIR / self.CHECKPOINT_FILE
        
        if not checkpoint_path.exists():
            return None
        
        try:
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def load_backup(self, feature_dir: Path) -> Optional[Dict[str, Any]]:
        """
        加载备份 Checkpoint
        
        Args:
            feature_dir: 特性目录
            
        Returns:
            备份 Checkpoint 数据或 None
        """
        backup_path = feature_dir / self.CHECKPOINT_DIR / "checkpoint.backup.json"
        
        if not backup_path.exists():
            return None
        
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def list_all(self, feature_dir: Path) -> List[Dict[str, Any]]:
        """
        列出所有历史 Checkpoint
        
        Args:
            feature_dir: 特性目录
            
        Returns:
            Checkpoint 列表
        """
        history_dir = feature_dir / self.CHECKPOINT_DIR / self.HISTORY_DIR
        
        if not history_dir.exists():
            return []
        
        checkpoints = []
        for checkpoint_file in history_dir.glob("checkpoint_*.json"):
            try:
                with open(checkpoint_file, "r", encoding="utf-8") as f:
                    checkpoints.append(json.load(f))
            except (json.JSONDecodeError, IOError):
                continue
        
        checkpoints.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return checkpoints
    
    def delete(self, feature_dir: Path) -> bool:
        """
        删除 Checkpoint
        
        Args:
            feature_dir: 特性目录
            
        Returns:
            是否成功删除
        """
        checkpoint_dir = feature_dir / self.CHECKPOINT_DIR
        
        if not checkpoint_dir.exists():
            return True
        
        try:
            import shutil
            shutil.rmtree(checkpoint_dir)
            return True
        except Exception:
            return False
    
    def _save_to_history(
        self,
        checkpoint_dir: Path,
        checkpoint_data: Dict[str, Any],
    ):
        """保存到历史记录"""
        history_dir = checkpoint_dir / self.HISTORY_DIR
        history_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = history_dir / f"checkpoint_{timestamp}.json"
        
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        
        self._cleanup_old_history(history_dir)
    
    def _cleanup_old_history(self, history_dir: Path, max_count: int = 50):
        """清理旧的历史记录"""
        checkpoints = sorted(
            history_dir.glob("checkpoint_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        
        for old_checkpoint in checkpoints[max_count:]:
            old_checkpoint.unlink()
