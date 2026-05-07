"""
CheckpointManager 测试

验证 checkpoint 持久化、恢复、realtime sync 功能
"""

import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.checkpoint.manager import CheckpointManager


def test_checkpoint_manager_init():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        manager = CheckpointManager(project_root)
        
        assert manager.project_root == project_root
        assert manager._memory is None
        assert manager.persistence is not None
        assert manager.recovery is not None
        assert manager.realtime is not None
        
        print("[PASS] CheckpointManager initialization")


def test_save_checkpoint():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        manager = CheckpointManager(project_root)
        
        feature_name = "test_feature"
        feature_dir = project_root / "docs" / "features" / feature_name
        feature_dir.mkdir(parents=True, exist_ok=True)
        
        from src.director import ExecutionContext, CapabilityRegistry
        registry = CapabilityRegistry()
        capability = registry.select("brainstorming")
        
        context = ExecutionContext(
            project_root=project_root,
            feature_name=feature_name,
            feature_dir=feature_dir,
            capability=capability,
        )
        context.metadata["session_id"] = "test_session"
        context.metadata["progress"] = 50
        
        checkpoint_path = manager.save(
            feature_name=feature_name,
            phase="1",
            step="design",
            context=context,
        )
        
        assert checkpoint_path.exists()
        
        loaded_data = manager.load(feature_name)
        assert loaded_data["version"] == "2.1"
        assert loaded_data["feature_name"] == feature_name
        
        print("[PASS] Checkpoint saved successfully")


def test_load_checkpoint():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        manager = CheckpointManager(project_root)
        
        feature_name = "test_feature"
        feature_dir = project_root / "docs" / "features" / feature_name
        feature_dir.mkdir(parents=True, exist_ok=True)
        
        from src.director import ExecutionContext, CapabilityRegistry
        registry = CapabilityRegistry()
        capability = registry.select("brainstorming")
        
        context = ExecutionContext(
            project_root=project_root,
            feature_name=feature_name,
            feature_dir=feature_dir,
            capability=capability,
        )
        
        manager.save(
            feature_name=feature_name,
            phase="3",
            step="implement_modules",
            context=context,
        )
        
        loaded = manager.load(feature_name)
        
        assert loaded is not None
        assert loaded["version"] == "2.1"
        assert loaded["phase"] == "3"
        
        print("[PASS] Checkpoint loaded successfully")


def test_load_checkpoint_missing():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        manager = CheckpointManager(project_root)
        
        loaded = manager.load("nonexistent_feature")
        
        assert loaded is None
        
        print("[PASS] Missing checkpoint returns None")


def test_set_memory():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        manager = CheckpointManager(project_root)
        
        from src.memory import ConversationMemory
        memory = ConversationMemory(feature_name="test", project_root=project_root)
        
        manager.set_memory(memory)
        
        assert manager._memory == memory
        
        print("[PASS] Memory set successfully")


def test_realtime_sync_enable():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        manager = CheckpointManager(project_root)
        
        feature_name = "test_feature"
        
        manager.enable_realtime_sync(feature_name)
        
        assert manager.realtime._sync_enabled.get(feature_name, False) == True
        
        manager.disable_realtime_sync(feature_name)
        
        assert manager.realtime._sync_enabled.get(feature_name, False) == False
        
        print("[PASS] Realtime sync enabled/disabled")


def test_checkpoint_update_metadata():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        manager = CheckpointManager(project_root)
        
        feature_name = "test_feature"
        feature_dir = project_root / "docs" / "features" / feature_name
        feature_dir.mkdir(parents=True, exist_ok=True)
        
        from src.director import ExecutionContext, CapabilityRegistry
        registry = CapabilityRegistry()
        capability = registry.select("brainstorming")
        
        context = ExecutionContext(
            project_root=project_root,
            feature_name=feature_name,
            feature_dir=feature_dir,
            capability=capability,
        )
        context.metadata["progress"] = 50
        
        manager.save(feature_name, "1", "initial", context)
        
        context.metadata["progress"] = 60
        manager.save(feature_name, "2", "planning", context)
        
        loaded = manager.load(feature_name)
        assert loaded["phase"] == "2"
        assert loaded["metadata"]["progress"] == 60
        
        print("[PASS] Checkpoint metadata updated")


def test_checkpoint_history():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        manager = CheckpointManager(project_root)
        
        feature_name = "test_feature"
        feature_dir = project_root / "docs" / "features" / feature_name
        feature_dir.mkdir(parents=True, exist_ok=True)
        
        from src.director import ExecutionContext, CapabilityRegistry
        registry = CapabilityRegistry()
        capability = registry.select("brainstorming")
        
        context = ExecutionContext(
            project_root=project_root,
            feature_name=feature_name,
            feature_dir=feature_dir,
            capability=capability,
        )
        
        manager.save(feature_name, "1", "design", context)
        manager.save(feature_name, "2", "planning", context)
        
        # Verify latest checkpoint
        loaded = manager.load(feature_name)
        assert loaded is not None
        
        print("[PASS] Checkpoint history saved")


def test_recovery_from_checkpoint():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        manager = CheckpointManager(project_root)
        
        feature_name = "test_feature"
        feature_dir = project_root / "docs" / "features" / feature_name
        feature_dir.mkdir(parents=True, exist_ok=True)
        
        from src.director import ExecutionContext, CapabilityRegistry
        registry = CapabilityRegistry()
        capability = registry.select("brainstorming")
        
        context = ExecutionContext(
            project_root=project_root,
            feature_name=feature_name,
            feature_dir=feature_dir,
            capability=capability,
        )
        context.metadata["modules_implemented"] = ["module1", "module2"]
        context.metadata["tests_passed"] = True
        
        manager.save(feature_name, "3", "implement_modules", context)
        
        recovered_context = manager.recover(feature_name)
        
        assert recovered_context is not None
        assert recovered_context.metadata.get("modules_implemented") == ["module1", "module2"]
        
        print("[PASS] Recovery from checkpoint works")


def test_multiple_features():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        manager = CheckpointManager(project_root)
        
        features = ["feature1", "feature2", "feature3"]
        
        from src.director import ExecutionContext, CapabilityRegistry
        registry = CapabilityRegistry()
        capability = registry.select("brainstorming")
        
        for feature_name in features:
            feature_dir = project_root / "docs" / "features" / feature_name
            feature_dir.mkdir(parents=True, exist_ok=True)
            
            context = ExecutionContext(
                project_root=project_root,
                feature_name=feature_name,
                feature_dir=feature_dir,
                capability=capability,
            )
            
            manager.save(feature_name, "1", "design", context)
        
        for feature_name in features:
            loaded = manager.load(feature_name)
            assert loaded is not None
            assert loaded["feature_name"] == feature_name
        
        print("[PASS] Multiple features handled correctly")


def test_checkpoint_cleanup():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        manager = CheckpointManager(project_root)
        
        feature_name = "test_feature"
        feature_dir = project_root / "docs" / "features" / feature_name
        feature_dir.mkdir(parents=True, exist_ok=True)
        
        from src.director import ExecutionContext, CapabilityRegistry
        registry = CapabilityRegistry()
        capability = registry.select("brainstorming")
        
        context = ExecutionContext(
            project_root=project_root,
            feature_name=feature_name,
            feature_dir=feature_dir,
            capability=capability,
        )
        
        manager.save(feature_name, "1", "design", context)
        
        success = manager.delete(feature_name)
        assert success == True
        
        loaded = manager.load(feature_name)
        assert loaded is None
        
        print("[PASS] Checkpoint cleanup works")


def run_all_tests():
    print("\n" + "=" * 60)
    print("CheckpointManager Test Suite")
    print("=" * 60 + "\n")
    
    test_checkpoint_manager_init()
    test_save_checkpoint()
    test_load_checkpoint()
    test_load_checkpoint_missing()
    test_set_memory()
    test_realtime_sync_enable()
    test_checkpoint_update_metadata()
    test_checkpoint_history()
    test_recovery_from_checkpoint()
    test_multiple_features()
    test_checkpoint_cleanup()
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_tests()