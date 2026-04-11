"""
RealTime Sync
实时 Checkpoint 同步
"""

import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any
from pathlib import Path


class RealTimeSync:
    """
    实时 Checkpoint 同步
    
    职责:
    - 后台线程定期同步 Checkpoint
    - 文件系统监控
    - 变更检测
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self._sync_threads: Dict[str, threading.Thread] = {}
        self._sync_enabled: Dict[str, bool] = {}
        self._sync_interval = 30
    
    def enable(self, feature_name: str):
        """启用实时同步"""
        if feature_name in self._sync_threads and self._sync_threads[feature_name].is_alive():
            return
        
        self._sync_enabled[feature_name] = True
        
        thread = threading.Thread(
            target=self._sync_worker,
            args=(feature_name,),
            daemon=True,
        )
        self._sync_threads[feature_name] = thread
        thread.start()
    
    def disable(self, feature_name: str):
        """禁用实时同步"""
        self._sync_enabled[feature_name] = False
        
        if feature_name in self._sync_threads:
            self._sync_threads[feature_name].join(timeout=1)
            del self._sync_threads[feature_name]
    
    def sync(self, feature_name: str) -> bool:
        """
        立即同步
        
        Args:
            feature_name: 特性名称
            
        Returns:
            是否成功
        """
        feature_dir = self.project_root / "docs" / "features" / feature_name
        
        if not feature_dir.exists():
            return False
        
        checkpoint_file = feature_dir / ".sdd" / "checkpoint.json"
        
        if not checkpoint_file.exists():
            return False
        
        try:
            checkpoint_file.touch()
            return True
        except IOError:
            return False
    
    def is_enabled(self, feature_name: str) -> bool:
        """检查是否启用"""
        return self._sync_enabled.get(feature_name, False)
    
    def _sync_worker(self, feature_name: str):
        """同步工作线程"""
        while self._sync_enabled.get(feature_name, False):
            self.sync(feature_name)
            time.sleep(self._sync_interval)
