"""
Phase 6: Persistence Orchestrator
"""

from typing import TYPE_CHECKING
from pathlib import Path
from datetime import datetime

if TYPE_CHECKING:
    from ..director import ExecutionContext, GateResult

from .base import PhaseOrchestrator, PhaseResult, PhaseStep


class Phase6Orchestrator(PhaseOrchestrator):
    """
    Phase 6: Persistence
    
    职责:
    - 保存制品到文件
    - 更新项目状态
    - 清理临时文件
    """
    
    STEPS = [
        "save_artifacts",
        "update_project_state",
        "cleanup_temp_files",
    ]
    
    def __init__(self, capability_registry=None):
        super().__init__(capability_registry)
        self._init_steps()
    
    def _init_steps(self):
        self.steps = [
            StepSaveArtifacts("save_artifacts"),
            StepUpdateProjectState("update_project_state"),
            StepCleanupTempFiles("cleanup_temp_files"),
        ]
    
    def execute(self, context: "ExecutionContext") -> PhaseResult:
        for step in self.steps:
            result = step.execute(context)
            if not result.success:
                return PhaseResult(success=False, message=result.message)
        
        return PhaseResult(
            success=True,
            artifacts={"persistence_complete": True},
            message="Phase 6 completed - All artifacts persisted",
        )
    
    def can_transition_to(self, context: "ExecutionContext") -> "GateResult":
        return GateResult(passed=True)


class StepSaveArtifacts(PhaseStep):
    """Step 1: 保存制品"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        feature_name = context.feature_name
        feature_dir = context.feature_dir
        
        artifacts_saved = []
        
        if "design-doc" in context.artifacts:
            design_file = feature_dir / "specs" / f"2026-04-11-{feature_name}-design.md"
            design_file.parent.mkdir(parents=True, exist_ok=True)
            design_file.write_text(context.artifacts["design-doc"], encoding="utf-8")
            artifacts_saved.append(str(design_file))
        
        if "plan-doc" in context.artifacts:
            plan_file = context.artifacts["plan-doc"]
            if Path(plan_file).exists():
                artifacts_saved.append(plan_file)
        
        context.metadata["artifacts_saved"] = artifacts_saved
        context.metadata["persistence_complete"] = True
        
        return StepResult(success=True, message=f"Saved {len(artifacts_saved)} artifacts")


class StepUpdateProjectState(PhaseStep):
    """Step 2: 更新项目状态"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        project_root = context.project_root
        feature_name = context.feature_name
        
        state_file = project_root / "PROJECT_STATE.md"
        
        if state_file.exists():
            content = state_file.read_text(encoding="utf-8")
        else:
            content = "# Project State\n\n## Features\n\n"
        
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        if f"- {feature_name}:" not in content:
            content += f"- {feature_name}: Phase 6 (Completed) [{timestamp}]\n"
        else:
            content = content.replace(
                f"- {feature_name}:",
                f"- {feature_name}: Phase 6 (Completed) [{timestamp}]"
            )
        
        state_file.write_text(content, encoding="utf-8")
        
        context.metadata["project_state_updated"] = True
        
        return StepResult(success=True, message="Project state updated")


class StepCleanupTempFiles(PhaseStep):
    """Step 3: 清理临时文件"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        feature_dir = context.feature_dir
        
        temp_patterns = ["*.tmp", "*.bak", "__pycache__", ".pytest_cache"]
        cleaned = []
        
        for pattern in temp_patterns:
            for temp_file in feature_dir.rglob(pattern):
                try:
                    if temp_file.is_file():
                        temp_file.unlink()
                    elif temp_file.is_dir():
                        import shutil
                        shutil.rmtree(temp_file)
                    cleaned.append(str(temp_file))
                except:
                    pass
        
        context.metadata["temp_files_cleaned"] = len(cleaned)
        
        return StepResult(success=True, message=f"Cleaned {len(cleaned)} temp files")
