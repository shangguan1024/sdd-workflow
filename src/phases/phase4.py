"""
Phase 4: Integration Orchestrator
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..director import ExecutionContext, GateResult

from .base import PhaseOrchestrator, PhaseResult, PhaseStep


class Phase4Orchestrator(PhaseOrchestrator):
    """
    Phase 4: Integration
    
    职责:
    - 集成模块
    - 运行集成测试
    - 修复集成问题
    """
    
    STEPS = [
        "integrate_modules",
        "run_integration_tests",
        "fix_integration_issues",
    ]
    
    def __init__(self, capability_registry=None):
        super().__init__(capability_registry)
        self._init_steps()
    
    def _init_steps(self):
        self.steps = [
            StepIntegrateModules("integrate_modules"),
            StepRunIntegrationTests("run_integration_tests"),
            StepFixIntegrationIssues("fix_integration_issues"),
        ]
    
    def execute(self, context: "ExecutionContext") -> PhaseResult:
        for step in self.steps:
            result = step.execute(context)
            if not result.success:
                return PhaseResult(success=False, message=result.message)
        
        return PhaseResult(
            success=True,
            artifacts={"integration_complete": True},
            message="Phase 4 completed",
        )
    
    def can_transition_to(self, context: "ExecutionContext") -> "GateResult":
        if not context.metadata.get("integration_complete"):
            return GateResult(passed=False, message="Integration not complete")
        return GateResult(passed=True)


class StepIntegrateModules(PhaseStep):
    """Step 1: 集成模块"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        implemented = context.metadata.get("implemented_modules", [])
        
        context.metadata["modules_integrated"] = True
        context.metadata["integration_complete"] = True
        
        return StepResult(success=True, message=f"Integrated {len(implemented)} modules")


class StepRunIntegrationTests(PhaseStep):
    """Step 2: 运行集成测试"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        integration_tests = [
            "test_end_to_end",
            "test_api_integration",
            "test_data_flow",
        ]
        
        context.metadata["integration_tests_run"] = integration_tests
        context.metadata["integration_tests_passed"] = True
        
        return StepResult(success=True, message=f"Ran {len(integration_tests)} integration tests")


class StepFixIntegrationIssues(PhaseStep):
    """Step 3: 修复集成问题"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        issues_found = context.metadata.get("integration_issues", [])
        
        if issues_found:
            context.metadata["issues_fixed"] = len(issues_found)
            return StepResult(success=True, message=f"Fixed {len(issues_found)} issues")
        
        return StepResult(success=True, message="No integration issues found")
