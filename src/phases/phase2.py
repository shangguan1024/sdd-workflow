"""
Phase 2: Implementation Planning Orchestrator
"""

from typing import TYPE_CHECKING, List, Dict, Any

if TYPE_CHECKING:
    from ..director import ExecutionContext, GateResult

from .base import PhaseOrchestrator, PhaseResult, PhaseStep


class Phase2Orchestrator(PhaseOrchestrator):
    """
    Phase 2: Implementation Planning
    
    职责:
    - 创建详细任务列表
    - 估算工作量
    - 识别依赖关系
    - 用户审批
    """
    
    STEPS = [
        "create_task_list",
        "estimate_effort",
        "identify_dependencies",
        "user_approval",
    ]
    
    def __init__(self, capability_registry=None):
        super().__init__(capability_registry)
        self._init_steps()
    
    def _init_steps(self):
        self.steps = [
            StepCreateTaskList("create_task_list"),
            StepEstimateEffort("estimate_effort"),
            StepIdentifyDependencies("identify_dependencies"),
            StepPlanningUserApproval("user_approval"),
        ]
    
    def execute(self, context: "ExecutionContext") -> PhaseResult:
        capability = context.capability
        if capability:
            result = capability.execute(context)
            if not result.success:
                return PhaseResult(success=False, message=result.message)
        
        for step in self.steps:
            result = step.execute(context)
            if not result.success:
                return PhaseResult(success=False, message=result.message)
        
        plan_file = context.feature_dir / "plans" / f"2026-04-11-{context.feature_name}-plan.md"
        plan_file.parent.mkdir(parents=True, exist_ok=True)
        plan_file.write_text(context.metadata.get("plan_doc", "# Implementation Plan\n"), encoding="utf-8")
        
        context.artifacts["plan-doc"] = str(plan_file)
        
        return PhaseResult(
            success=True,
            artifacts={"plan-doc": str(plan_file)},
            message="Phase 2 completed",
        )
    
    def can_transition_to(self, context: "ExecutionContext") -> "GateResult":
        if "plan_doc" not in context.metadata:
            return GateResult(passed=False, message="Plan not created")
        if not context.metadata.get("plan_approved"):
            return GateResult(passed=False, message="Plan not approved")
        return GateResult(passed=True)


class StepCreateTaskList(PhaseStep):
    """Step 1: 创建任务列表"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        from ..capabilities import WritingPlansCapability
        
        capability = WritingPlansCapability()
        result = capability.execute(context)
        
        if result.success:
            context.metadata["tasks"] = result.artifacts.get("tasks", [])
            context.metadata["plan_doc"] = result.artifacts.get("plan_doc", "")
        
        return StepResult(success=True, message=f"Created {len(context.metadata.get('tasks', []))} tasks")


class StepEstimateEffort(PhaseStep):
    """Step 2: 估算工作量"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        tasks = context.metadata.get("tasks", [])
        
        total_hours = sum(t.get("estimated_hours", 0) for t in tasks)
        
        context.metadata["total_effort_hours"] = total_hours
        context.metadata["effort_breakdown"] = {
            "high_priority": sum(t.get("estimated_hours", 0) for t in tasks if t.get("priority") == "high"),
            "medium_priority": sum(t.get("estimated_hours", 0) for t in tasks if t.get("priority") == "medium"),
            "low_priority": sum(t.get("estimated_hours", 0) for t in tasks if t.get("priority") == "low"),
        }
        
        return StepResult(success=True, message=f"Total effort: {total_hours} hours")


class StepIdentifyDependencies(PhaseStep):
    """Step 3: 识别依赖"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        tasks = context.metadata.get("tasks", [])
        
        dependencies = {}
        for task in tasks:
            deps = task.get("dependencies", [])
            if deps:
                dependencies[task["id"]] = deps
        
        context.metadata["task_dependencies"] = dependencies
        
        critical_path = self._find_critical_path(tasks, dependencies)
        context.metadata["critical_path"] = critical_path
        
        return StepResult(success=True, message=f"Identified {len(dependencies)} dependency chains")
    
    def _find_critical_path(self, tasks: list, deps: dict) -> List[str]:
        task_map = {t["id"]: t for t in tasks}
        path = []
        
        for task in tasks:
            if task["id"] not in deps or not deps[task["id"]]:
                if not path or task_map.get(task["id"], {}).get("estimated_hours", 0) > 0:
                    path.append(task["id"])
        
        return path[:5]


class StepPlanningUserApproval(PhaseStep):
    """Step 4: 用户审批"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        if context.metadata.get("plan_approved"):
            return StepResult(success=True, message="Plan approved")
        
        context.metadata["awaiting_plan_approval"] = True
        return StepResult(success=True, message="Plan ready for approval")
