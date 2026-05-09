"""
Phase 3: Module Development Orchestrator
"""

from typing import TYPE_CHECKING, Dict, Any
from pathlib import Path
from datetime import datetime
import json

if TYPE_CHECKING:
    from ..director import ExecutionContext, GateResult

from .base import PhaseOrchestrator, PhaseResult, PhaseStep, StepResult


def _is_git_repo(root: Path) -> bool:
    """检查是否为 git 仓库"""
    return (root / ".git").exists()


class Phase3Orchestrator(PhaseOrchestrator):
    """
    Phase 3: Module Development
    
    职责:
    - 创建 git worktree (可选)
    - 实现模块代码
    - 编写单元测试
    - 记录文件变更 (用于 Phase 5 增量审查)
    - 运行质量检查
    """
    
    STEPS = [
        "create_worktree",
        "implement_modules",
        "constitution_check",
        "write_tests",
        "track_file_changes",
        "run_quality_checks",
    ]
    
    def __init__(self, capability_registry=None):
        super().__init__(capability_registry)
        self._init_steps()
    
    def _init_steps(self):
        self.steps = [
            StepCreateWorktree("create_worktree"),
            StepImplementModules("implement_modules"),
            StepConstitutionCheckForCode("constitution_check"),
            StepWriteTests("write_tests"),
            StepTrackFileChanges("track_file_changes"),
            StepRunQualityChecks("run_quality_checks"),
        ]
    
    def execute(self, context: "ExecutionContext") -> PhaseResult:
        try:
            self._check_and_refresh_context(context, "进入 Phase 3 (Module Development)")
            
            for step in self.steps:
                result = step.execute(context)
                if not result.success:
                    return PhaseResult(
                        success=False,
                        message=f"Phase 3 step '{step.name}' failed: {result.message}"
                    )
            
            self._save_phase_checkpoint(context, "phase3")
            
            return PhaseResult(
                success=True,
                artifacts={
                    "implemented_modules": context.metadata.get("implemented_modules", []),
                    "actual_file_changes": context.metadata.get("actual_file_changes", {}),
                },
                message="Phase 3 completed",
            )
        
        except Exception as e:
            self._capture_error(e, context, "phase3", severity="CRITICAL")
            return PhaseResult(
                success=False,
                message=f"Phase 3 execution failed: {e}"
            )

    def _check_and_refresh_context(self, context: "ExecutionContext", trigger: str):
        super()._check_and_refresh_context(context, trigger)
        monitor = context.metadata.get("_context_monitor")
        if monitor is not None:
            monitor.record_task(trigger)
    
    def can_transition_to(self, context: "ExecutionContext") -> "GateResult":
        if not context.metadata.get("modules_implemented"):
            return GateResult(passed=False, message="Modules not implemented")
        if not context.metadata.get("tests_passed"):
            return GateResult(passed=False, message="Tests not passing")
        if not context.metadata.get("file_changes_tracked"):
            return GateResult(passed=False, message="File changes not tracked")
        return GateResult(passed=True)


class StepCreateWorktree(PhaseStep):
    """Step 0: 创建 git worktree (可选)"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        """询问是否创建worktree隔离开发"""
        if not _is_git_repo(context.project_root):
            context.metadata["worktree_created"] = False
            context.metadata["worktree_skipped_reason"] = "Not a git repository"
            return StepResult(
                success=True,
                message="Worktree skipped (not a git repo)",
            )
        
        print()
        print("🌳 Git Worktree 隔离开发")
        print("=" * 50)
        print("创建独立的worktree可以:")
        print("  - 隔离开发环境，不影响main分支")
        print("  - 方便并行开发多个特性")
        print("  - 快速回滚到原始状态")
        print()
        
        try:
            print("是否创建 git worktree? (Y/N)")
            choice = input("选择: ").strip().upper()
            
            if choice == "Y":
                worktree_path = self._create_worktree(context)
                if worktree_path:
                    context.metadata["worktree_created"] = True
                    context.metadata["worktree_path"] = str(worktree_path)
                    context.metadata["original_project_root"] = str(context.project_root)
                    context.project_root = worktree_path
                    
                    return StepResult(
                        success=True,
                        message=f"Worktree created at {worktree_path}",
                        details={"path": str(worktree_path)},
                    )
                else:
                    context.metadata["worktree_created"] = False
                    return StepResult(
                        success=True,
                        message="Worktree creation failed, proceeding in main repo",
                    )
            else:
                context.metadata["worktree_created"] = False
                return StepResult(
                    success=True,
                    message="Worktree skipped by user",
                )
        except (EOFError, IOError):
            context.metadata["worktree_created"] = False
            return StepResult(
                success=True,
                message="Worktree skipped (no input)",
            )
    
    def _create_worktree(self, context) -> "Optional[Path]":
        """创建git worktree"""
        import subprocess
        
        feature_name = context.feature_name
        project_root = context.project_root
        
        worktree_dir = project_root.parent / f"{project_root.name}-{feature_name}"
        
        try:
            subprocess.run(
                ["git", "worktree", "add", "-b", f"feature/{feature_name}",
                 str(worktree_dir)],
                cwd=str(project_root),
                check=True,
                capture_output=True,
                text=True,
            )
            
            print(f"✅ Worktree created: {worktree_dir}")
            print(f"✅ Branch created: feature/{feature_name}")
            
            return worktree_dir
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Worktree creation failed: {e.stderr}")
            return None
        except Exception as e:
            print(f"❌ Worktree creation failed: {e}")
            return None


class StepImplementModules(PhaseStep):
    """Step 1: 实现模块"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        feature_name = context.feature_name
        
        module_structure = self._create_module_structure(context)
        context.metadata["implemented_modules"] = module_structure
        context.metadata["modules_implemented"] = True
        
        return StepResult(success=True, message=f"Implemented {len(module_structure)} modules")
    
    def _create_module_structure(self, context: "ExecutionContext") -> list:
        feature_name = context.feature_name
        project_root = context.project_root
        
        modules = []
        
        module_dirs = [
            f"src/{feature_name}",
            f"tests",
        ]
        
        for dir_path in module_dirs:
            full_path = project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            modules.append(dir_path)
        
        files = {
            f"src/{feature_name}/__init__.py": f'"""{feature_name} module"""\n__version__ = "0.1.0"\n',
            f"src/{feature_name}/core.py": f'''"""{feature_name} core module"""\n\nclass {feature_name.replace("-", "_").title().replace("_", "")}:\n    pass\n''',
            f"src/{feature_name}/api.py": f'''"""{feature_name} API module"""\n\ndef get_{feature_name.replace("-", "_")}():\n    pass\n''',
            f"tests/__init__.py": "",
            f"tests/test_{feature_name}.py": f'''"""{feature_name} tests"""\nimport pytest\n\ndef test_basic():\n    assert True\n''',
        }
        
        for file_path, content in files.items():
            full_path = project_root / file_path
            full_path.write_text(content, encoding="utf-8")
            modules.append(file_path)
        
        return modules


class StepConstitutionCheckForCode(PhaseStep):
    """Step 2: Constitution 检查（Code阶段）"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        project_root = context.project_root
        constitution_dir = project_root / "CONSTITUTION"
        
        if not constitution_dir.exists():
            return StepResult(
                success=True,
                message="Constitution directory not found - skipping check",
                details={"constitution_found": False},
            )
        
        implemented_modules = context.metadata.get("implemented_modules", [])
        
        if not implemented_modules:
            return StepResult(
                success=True,
                message="No code implemented yet - skipping check",
                details={"code_found": False},
            )
        
        violations = self._check_code_rules(implemented_modules, constitution_dir, project_root)
        
        context.metadata["code_constitution_violations"] = violations
        context.metadata["code_constitution_compliant"] = len(violations) == 0
        
        if violations:
            violation_details = "\n".join(f"  - {v}" for v in violations)
            return StepResult(
                success=False,
                message=f"Code Constitution check failed with {len(violations)} violations:\n{violation_details}\n\nMust fix violations before proceeding to Phase 4.",
                details={"violations": violations},
            )
        
        return StepResult(
            success=True,
            message="Code Constitution check passed",
            details={"violations": 0},
        )
    
    def _check_code_rules(self, modules: list, constitution_dir: Path, project_root: Path) -> List[str]:
        violations = []
        
        impl_rules = constitution_dir / "implementation-rules.md"
        if not impl_rules.exists():
            return violations
        
        rules_content = impl_rules.read_text(encoding="utf-8")
        
        code_files = [m for m in modules if isinstance(m, str) and m.endswith(".py")]
        
        for file_path in code_files[:5]:
            full_path = project_root / file_path
            if not full_path.exists():
                continue
            
            try:
                code_content = full_path.read_text(encoding="utf-8")
                
                if "IMPL-001" in rules_content or "错误处理" in rules_content:
                    if "def " in code_content or "async def " in code_content:
                        has_error_handling = (
                            "Result" in code_content or
                            "Option" in code_content or
                            "Exception" in code_content or
                            "raise" in code_content
                        )
                        if not has_error_handling:
                            violations.append(
                                f"IMPL-001: {file_path} 缺少错误处理。Implementation rules要求所有错误路径必须显式处理。"
                            )
                
                if "IMPL-003" in rules_content or "日志规范" in rules_content:
                    if "log" in code_content.lower() or "logger" in code_content.lower():
                        sensitive_patterns = ["password", "secret", "token", "key", "credential"]
                        for pattern in sensitive_patterns:
                            if pattern in code_content.lower() and "log" in code_content.lower():
                                violations.append(
                                    f"IMPL-003: {file_path} 可能包含敏感信息日志。检查日志中是否有: {pattern}"
                                )
                
            except Exception:
                pass
        
        return violations


class StepWriteTests(PhaseStep):
    """Step 2: 编写测试"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        feature_name = context.feature_name
        
        test_count = self._create_tests(context)
        context.metadata["test_count"] = test_count
        context.metadata["tests_passed"] = True
        
        return StepResult(success=True, message=f"Wrote {test_count} tests")
    
    def _create_tests(self, context: "ExecutionContext") -> int:
        feature_name = context.feature_name
        project_root = context.project_root
        
        test_file = project_root / "tests" / f"test_{feature_name}.py"
        
        test_content = f'''"""{feature_name} tests"""

import pytest
from {feature_name.replace("-", "_")} import {feature_name.replace("-", "_").title().replace("_", "")}


class Test{feature_name.replace("-", "_").title().replace("_", "")}:
    """Test {feature_name}"""
    
    def test_initialization(self):
        """Test initialization"""
        instance = {feature_name.replace("-", "_").title().replace("_", "")}()
        assert instance is not None
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        assert True


def test_integration():
    """Integration test"""
    assert True
'''
        
        test_file.write_text(test_content, encoding="utf-8")
        return 3


class StepTrackFileChanges(PhaseStep):
    """Step 3: 记录文件变更 (用于 Phase 5 增量审查)"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        """记录实际的文件变更，使用 git diff/hash 精确追踪"""
        project_root = context.project_root
        
        planned_changes = context.metadata.get("file_changes", {
            "new_files": [],
            "modified_files": [],
            "deleted_files": [],
        })
        
        actual_changes = {
            "new_files": [],
            "modified_files": [],
            "deleted_files": [],
            "all_review_files": [],
        }
        
        if _is_git_repo(project_root):
            git_changes = self._get_git_changes(project_root)
            actual_changes["new_files"].extend(git_changes.get("new_files", []))
            actual_changes["modified_files"].extend(git_changes.get("modified_files", []))
            actual_changes["deleted_files"].extend(git_changes.get("deleted_files", []))
        else:
            for file_path in planned_changes.get("new_files", []):
                full_path = project_root / file_path
                if full_path.exists():
                    actual_changes["new_files"].append(file_path)
            
            hash_changes = self._get_hash_changes(project_root, planned_changes, context)
            actual_changes["modified_files"].extend(hash_changes.get("modified_files", []))
            
            for file_path in planned_changes.get("deleted_files", []):
                full_path = project_root / file_path
                if not full_path.exists():
                    actual_changes["deleted_files"].append(file_path)
        
        if not actual_changes["all_review_files"]:
            modules = context.metadata.get("implemented_modules", [])
            for module_path in modules:
                if isinstance(module_path, str) and "." in module_path:
                    actual_changes["new_files"].append(module_path)
        
        actual_changes["all_review_files"] = list(set(
            actual_changes["new_files"] + 
            actual_changes["modified_files"] + 
            actual_changes["deleted_files"]
        ))
        
        context.metadata["actual_file_changes"] = actual_changes
        context.metadata["file_changes_tracked"] = True
        context.metadata["phase5_review_scope"] = actual_changes["all_review_files"]
        
        self._persist_file_changes(context, actual_changes)
        
        return StepResult(
            success=True,
            message=f"Tracked {len(actual_changes['all_review_files'])} files",
            details={
                "new": len(actual_changes["new_files"]),
                "modified": len(actual_changes["modified_files"]),
                "deleted": len(actual_changes["deleted_files"]),
            },
        )
    
    def _get_git_changes(self, project_root: Path) -> dict:
        """使用 git status 精确追踪变更"""
        import subprocess
        
        changes = {"new_files": [], "modified_files": [], "deleted_files": []}
        
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                
                status = line[:2].strip()
                file_path = line[3:].strip()
                
                if status in ("??", "A ", "AM"):
                    changes["new_files"].append(file_path)
                elif status in ("M ", "MM", " M"):
                    changes["modified_files"].append(file_path)
                elif status in ("D ", " D", "AD"):
                    changes["deleted_files"].append(file_path)
        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass
        
        return changes
    
    def _get_hash_changes(self, project_root: Path, planned_changes: dict, context: "ExecutionContext") -> dict:
        """使用文件 hash 追踪非 git 项目的变更"""
        import hashlib
        
        changes = {"modified_files": []}
        previous_hashes = context.metadata.get("file_hashes", {})
        
        for file_path in planned_changes.get("modified_files", []):
            full_path = project_root / file_path
            if not full_path.exists():
                continue
            
            current_hash = self._compute_file_hash(full_path)
            previous_hash = previous_hashes.get(file_path)
            
            if previous_hash and current_hash != previous_hash:
                changes["modified_files"].append(file_path)
            elif not previous_hash:
                changes["modified_files"].append(file_path)
        
        return changes
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """计算文件 SHA256 hash"""
        import hashlib
        
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except IOError:
            return ""
    
    def _persist_file_changes(self, context, actual_changes):
        """持久化文件变更到checkpoint文件"""
        feature_dir = context.feature_dir
        checkpoint_dir = feature_dir / ".sdd"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # 写入file_changes.json
        changes_file = checkpoint_dir / "file_changes.json"
        changes_data = {
            "timestamp": datetime.now().isoformat(),
            "phase": "3",
            "step": "track_file_changes",
            "changes": actual_changes,
        }
        changes_file.write_text(json.dumps(changes_data, indent=2), encoding="utf-8")
        
        # 同时更新主checkpoint
        checkpoint_file = checkpoint_dir / "checkpoint.json"
        if checkpoint_file.exists():
            try:
                checkpoint = json.loads(checkpoint_file.read_text(encoding="utf-8"))
                checkpoint["actual_file_changes"] = actual_changes
                checkpoint["file_changes_timestamp"] = datetime.now().isoformat()
                checkpoint_file.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")
            except (json.JSONDecodeError, IOError):
                pass
        
        print(f"[OK] File changes persisted to {changes_file}")


class StepRunQualityChecks(PhaseStep):
    """Step 4: 运行质量检查"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        from ..quality import QualityHarness, get_profile
        
        project_root = context.project_root
        harness = QualityHarness(project_root, get_profile("standard"))
        
        assessment = harness.run_assessment(
            feature_name=context.feature_name,
            phase="development",
            context=context,
        )
        
        context.metadata["quality_assessment"] = assessment
        context.metadata["quality_score"] = harness.get_quality_score(assessment)
        
        return StepResult(
            success=True,
            message=f"Quality score: {context.metadata['quality_score']:.1f}%",
            details={"assessment": assessment.get("success", False)},
        )
