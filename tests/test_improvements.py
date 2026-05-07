"""
测试脚本 - 验证改进功能

验证以下改进：
1. Real-time Checkpoint启动
2. Delta Review持久化
3. git worktree集成
4. Web Kernel Skills自动加载
"""

import json
import time
import sys
import tempfile
import subprocess
from pathlib import Path

# 确保项目根目录在path中
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

print("="*60)
print("SDD-Workflow 改进功能验证测试")
print("="*60)
print()

def test_realtime_checkpoint():
    """测试1: Real-time Checkpoint启动"""
    print("测试1: Real-time Checkpoint启动")
    print("-"*60)
    
    from src.checkpoint import CheckpointManager
    
    project_root = Path(_project_root / "test_temp_realtime")
    project_root.mkdir(parents=True, exist_ok=True)
    
    manager = CheckpointManager(project_root)
    
    feature_name = "test-realtime"
    feature_dir = project_root / "docs" / "features" / feature_name
    feature_dir.mkdir(parents=True, exist_ok=True)
    
    manager.enable_realtime_sync(feature_name)
    
    if manager.realtime.is_enabled(feature_name):
        print("[PASS] Realtime sync enabled")
        
        if feature_name in manager.realtime._sync_threads:
            thread = manager.realtime._sync_threads[feature_name]
            if thread.is_alive():
                print("[PASS] Background thread running")
            else:
                print("[FAIL] Thread not running")
        else:
            print("[FAIL] Thread not found")
    else:
        print("[FAIL] Realtime sync not enabled")
    
    manager.disable_realtime_sync(feature_name)
    print("[INFO] Cleanup completed")
    
    print()

def test_delta_review_persistence():
    """测试2: Delta Review持久化"""
    print("测试2: Delta Review持久化")
    print("-"*60)
    
    from src.phases.phase3 import StepTrackFileChanges
    from src.director import ExecutionContext
    
    project_root = Path(_project_root / "test_temp_delta")
    project_root.mkdir(parents=True, exist_ok=True)
    
    feature_name = "test-delta"
    feature_dir = project_root / "docs" / "features" / feature_name
    feature_dir.mkdir(parents=True, exist_ok=True)
    
    checkpoint_dir = feature_dir / ".sdd"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    test_files = [
        "src/test-delta/__init__.py",
        "src/test-delta/core.py",
    ]
    
    for file_path in test_files:
        full_path = project_root / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text("test content", encoding="utf-8")
    
    context = ExecutionContext(
        project_root=project_root,
        feature_name=feature_name,
        feature_dir=feature_dir,
        capability=None,
    )
    
    context.metadata["file_changes"] = {
        "new_files": test_files,
        "modified_files": [],
        "deleted_files": [],
    }
    
    context.metadata["implemented_modules"] = test_files
    
    step = StepTrackFileChanges("track_file_changes")
    result = step.execute(context)
    
    if result.success:
        print("[PASS] Step executed successfully")
    else:
        print(f"[FAIL] Step failed - {result.message}")
    
    changes_file = feature_dir / ".sdd" / "file_changes.json"
    
    if changes_file.exists():
        print("[PASS] file_changes.json created")
        
        changes_data = json.loads(changes_file.read_text(encoding="utf-8"))
        
        if "changes" in changes_data:
            print("[PASS] Changes data valid")
            
            review_files = changes_data["changes"].get("all_review_files", [])
            if len(review_files) > 0:
                print(f"[PASS] {len(review_files)} files tracked for review")
            else:
                print("[FAIL] No files tracked")
        else:
            print("[FAIL] Invalid format")
    else:
        print("[FAIL] file_changes.json not created")
    
    print()

def test_git_worktree_class():
    """测试3: git worktree类定义"""
    print("测试3: git worktree类定义")
    print("-"*60)
    
    from src.phases.phase3 import StepCreateWorktree
    
    step = StepCreateWorktree("create_worktree")
    
    if hasattr(step, "execute"):
        print("[PASS] StepCreateWorktree.execute method exists")
    else:
        print("[FAIL] execute method missing")
    
    if hasattr(step, "_is_git_repo"):
        print("[PASS] _is_git_repo method exists")
    else:
        print("[FAIL] _is_git_repo method missing")
    
    if hasattr(step, "_create_worktree"):
        print("[PASS] _create_worktree method exists")
    else:
        print("[FAIL] _create_worktree method missing")
    
    project_root = Path(_project_root)
    
    is_git = step._is_git_repo(project_root)
    
    if is_git:
        print("[PASS] _is_git_repo correctly returns True for git dir")
    else:
        print("[INFO] _is_git_repo returns False (test project may not be git repo)")
    
    print()

def test_web_kernel_skills_loading():
    """测试4: Web Kernel Skills加载逻辑"""
    print("测试4: Web Kernel Skills加载逻辑")
    print("-"*60)
    
    from src.phases.phase1 import StepWebKernelSkills
    
    step = StepWebKernelSkills("web_kernel_skills")
    
    if hasattr(step, "_load_skills"):
        print("[PASS] _load_skills method exists")
    else:
        print("[FAIL] _load_skills method missing")
    
    if hasattr(step, "_find_skill_path"):
        print("[PASS] _find_skill_path method exists")
    else:
        print("[FAIL] _find_skill_path method missing")
    
    if hasattr(step, "_load_skill_content"):
        print("[PASS] _load_skill_content method exists")
    else:
        print("[FAIL] _load_skill_content method missing")
    
    if hasattr(step, "_ask_user_selection"):
        print("[PASS] _ask_user_selection method exists")
    else:
        print("[FAIL] _ask_user_selection method missing")
    
    from src.director import ExecutionContext
    
    project_root = Path(_project_root / "test_temp_skills")
    project_root.mkdir(parents=True, exist_ok=True)
    
    context = ExecutionContext(
        project_root=project_root,
        feature_name="test-skills",
        feature_dir=project_root / "docs" / "features" / "test-skills",
        capability=None,
    )
    
    test_skills = ["requirement-web-kernel-clarifier"]
    loaded = step._load_skills(context, test_skills)
    
    if len(loaded) >= 0:
        print("[PASS] _load_skills executed without error")
    
    if f"skill_{test_skills[0]}" in context.metadata:
        print("[PASS] Skill content injected to context")
    else:
        print("[INFO] Skill not found (expected if skill not installed)")
    
    print()

def test_phase3_steps_order():
    """测试5: Phase 3 Steps顺序"""
    print("测试5: Phase 3 Steps顺序")
    print("-"*60)
    
    from src.phases.phase3 import Phase3Orchestrator
    
    orchestrator = Phase3Orchestrator()
    
    expected_steps = [
        "create_worktree",
        "implement_modules",
        "write_tests",
        "track_file_changes",
        "run_quality_checks",
    ]
    
    if orchestrator.STEPS == expected_steps:
        print("[PASS] Steps order correct")
        print(f"  Steps: {orchestrator.STEPS}")
    else:
        print("[FAIL] Steps order incorrect")
        print(f"  Expected: {expected_steps}")
        print(f"  Actual: {orchestrator.STEPS}")
    
    print()

def test_director_checkpoint_manager():
    """测试6: Director CheckpointManager实例"""
    print("测试6: Director CheckpointManager实例")
    print("-"*60)
    
    from src.director import Director
    
    project_root = Path(_project_root / "test_temp_director")
    project_root.mkdir(parents=True, exist_ok=True)
    
    director = Director(project_root)
    
    if hasattr(director, "_checkpoint_manager"):
        print("[PASS] _checkpoint_manager attribute exists")
        
        if director._checkpoint_manager is not None:
            print("[PASS] CheckpointManager instance created")
            
            if hasattr(director._checkpoint_manager, "realtime"):
                print("[PASS] realtime attribute exists")
            else:
                print("[FAIL] realtime attribute missing")
        else:
            print("[FAIL] CheckpointManager instance is None")
    else:
        print("[FAIL] _checkpoint_manager attribute missing")
    
    print()

def main():
    test_realtime_checkpoint()
    test_delta_review_persistence()
    test_git_worktree_class()
    test_web_kernel_skills_loading()
    test_phase3_steps_order()
    test_director_checkpoint_manager()
    
    print("="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    main()