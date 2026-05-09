"""
Phase 2: Implementation Planning Orchestrator (Optimized)
"""

from typing import TYPE_CHECKING, List, Dict, Any
from datetime import datetime

if TYPE_CHECKING:
    from ..director import ExecutionContext, GateResult

from .base import PhaseOrchestrator, PhaseResult, PhaseStep


class Phase2Orchestrator(PhaseOrchestrator):
    """
    Phase 2: Implementation Planning (Optimized)
    
    职责:
    - 创建详细任务列表
    - 估算工作量
    - 识别依赖关系
    - 用户审批
    
    优化：合并 plan-doc.md 到 findings.md + task_plan.md
    """
    
    STEPS = [
        "create_task_list",
        "constitution_check",
        "estimate_effort",
        "identify_dependencies",
        "append_to_documents",
        "user_approval",
    ]
    
    def __init__(self, capability_registry=None):
        super().__init__(capability_registry)
        self._init_steps()
    
    def _init_steps(self):
        self.steps = [
            StepCreateTaskList("create_task_list"),
            StepConstitutionCheckForPlan("constitution_check"),
            StepEstimateEffort("estimate_effort"),
            StepIdentifyDependencies("identify_dependencies"),
            StepAppendToDocuments("append_to_documents"),
            StepPlanningUserApproval("user_approval"),
        ]
    
    def execute(self, context: "ExecutionContext") -> PhaseResult:
        try:
            capability = context.capability
            if capability:
                result = capability.execute(context)
                if not result.success:
                    return PhaseResult(
                        success=False,
                        message=f"Phase 2 capability failed: {result.message}"
                    )
            
            for step in self.steps:
                result = step.execute(context)
                if not result.success:
                    return PhaseResult(
                        success=False,
                        message=f"Phase 2 step '{step.name}' failed: {result.message}"
                    )
            
            self._save_phase_checkpoint(context, "phase2")
            
            return PhaseResult(
                success=True,
                artifacts={"plan-merged": True},
                message="Phase 2 completed - Plan merged into findings.md + task_plan.md",
            )
        
        except Exception as e:
            self._capture_error(e, context, "phase2", severity="CRITICAL")
            return PhaseResult(
                success=False,
                message=f"Phase 2 execution failed: {e}"
            )
    
    def can_transition_to(self, context: "ExecutionContext") -> "GateResult":
        if "tasks" not in context.metadata:
            return GateResult(passed=False, message="Tasks not created")
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


class StepConstitutionCheckForPlan(PhaseStep):
    """Step 2: Constitution 检查（Plan阶段）"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        project_root = context.project_root
        constitution_dir = project_root / "CONSTITUTION"
        
        if not constitution_dir.exists():
            return StepResult(
                success=True,
                message="Constitution directory not found - skipping check",
                details={"constitution_found": False},
            )
        
        plan_content = context.metadata.get("plan_doc", "")
        tasks = context.metadata.get("tasks", [])
        
        if not plan_content and not tasks:
            return StepResult(
                success=True,
                message="No plan content to check",
                details={"plan_content_found": False},
            )
        
        violations = self._check_plan_rules(plan_content, tasks, constitution_dir)
        
        context.metadata["plan_constitution_violations"] = violations
        context.metadata["plan_constitution_compliant"] = len(violations) == 0
        
        if violations:
            violation_details = "\n".join(f"  - {v}" for v in violations)
            return StepResult(
                success=False,
                message=f"Plan Constitution check failed with {len(violations)} violations:\n{violation_details}\n\nMust fix violations before proceeding to Phase 3.",
                details={"violations": violations},
            )
        
        return StepResult(
            success=True,
            message="Plan Constitution check passed",
            details={"violations": 0},
        )
    
    def _check_plan_rules(self, plan_content: str, tasks: List[Dict], constitution_dir) -> List[str]:
        violations = []
        
        impl_rules = constitution_dir / "implementation-rules.md"
        if impl_rules.exists():
            rules_content = impl_rules.read_text(encoding="utf-8")
            
            if "IMPL-001" in rules_content or "错误处理" in rules_content:
                has_error_handling = any(
                    "error" in str(t).lower() or "exception" in str(t).lower()
                    for t in tasks
                )
                if not has_error_handling and len(tasks) > 3:
                    violations.append(
                        "IMPL-001: Plan缺少错误处理任务。Implementation rules要求所有错误路径必须显式处理。"
                    )
            
            if "IMPL-002" in rules_content or "测试覆盖" in rules_content:
                has_test_tasks = any(
                    "test" in str(t).lower() for t in tasks
                )
                if not has_test_tasks:
                    violations.append(
                        "IMPL-002: Plan缺少测试任务。Implementation rules要求新代码必须有单元测试。"
                    )
        
        return violations


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


class StepAppendToDocuments(PhaseStep):
    """Step 4: 追加计划内容到 findings.md + task_plan.md"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        feature_dir = context.feature_dir
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        self._append_to_findings(feature_dir, context, timestamp)
        self._append_to_task_plan(feature_dir, context, timestamp)
        
        return StepResult(success=True, message="Plan content merged into findings.md + task_plan.md")
    
    def _append_to_findings(self, feature_dir, context: "ExecutionContext", timestamp: str):
        """追加 Phase 2 内容到 findings.md"""
        findings_file = feature_dir / "findings.md"
        
        if findings_file.exists():
            current_content = findings_file.read_text(encoding="utf-8")
        else:
            current_content = f"# Findings: {context.feature_name}\n\n"
        
        tasks = context.metadata.get("tasks", [])
        total_hours = context.metadata.get("total_effort_hours", 0)
        effort_breakdown = context.metadata.get("effort_breakdown", {})
        execution_mode = context.metadata.get("execution_mode", "subagent-driven")
        
        phase2_section = f"""
---

## Phase 2: Plan Summary

**Date**: {timestamp}

### Execution Mode
- Selected: **{execution_mode}**

### Tasks Overview
- Total tasks: **{len(tasks)}**
- Estimated effort: **{total_hours} hours**

### Effort Breakdown
- High priority: {effort_breakdown.get('high_priority', 0)} hours
- Medium priority: {effort_breakdown.get('medium_priority', 0)} hours
- Low priority: {effort_breakdown.get('low_priority', 0)} hours

### Task List
{self._format_task_list(tasks)}

---
*Phase 2 completed* | *{timestamp}*
"""
        
        findings_file.write_text(current_content + phase2_section, encoding="utf-8")
        context.metadata["findings_updated"] = True
    
    def _append_to_task_plan(self, feature_dir, context: "ExecutionContext", timestamp: str):
        """追加 Phase 2 任务到 task_plan.md"""
        task_plan_file = feature_dir / "task_plan.md"
        
        if task_plan_file.exists():
            current_content = task_plan_file.read_text(encoding="utf-8")
        else:
            current_content = f"# Task Plan: {context.feature_name}\n\n"
        
        tasks = context.metadata.get("tasks", [])
        execution_mode = context.metadata.get("execution_mode", "subagent-driven")
        
        phase2_tasks = f"""
---

## Phase 2: Implementation Tasks [COMPLETED ✅]

### Execution Mode
- {execution_mode}

### Task Table

| ID | Task | Priority | Est. Hours | Dependencies |
|----|------|----------|-----------|-------------|
{self._format_task_table(tasks)}

---
*Phase 2 completed* | *{timestamp}*
"""
        
        task_plan_file.write_text(current_content + phase2_tasks, encoding="utf-8")
        context.metadata["task_plan_updated"] = True
    
    def _format_task_list(self, tasks: List[Dict]) -> str:
        """格式化任务列表"""
        parts = []
        for i, task in enumerate(tasks[:10], 1):
            task_name = task.get("name", task.get("description", "Unknown"))
            priority = task.get("priority", "Medium")
            parts.append(f"- Task {i}: {task_name} ({priority})")
        return "\n".join(parts)
    
    def _format_task_table(self, tasks: List[Dict]) -> str:
        """格式化任务表格"""
        parts = []
        for i, task in enumerate(tasks[:10], 1):
            task_name = task.get("name", task.get("description", "Unknown"))
            priority = task.get("priority", "Medium")
            hours = task.get("estimated_hours", 0)
            deps = ", ".join(task.get("dependencies", [])) if task.get("dependencies") else "None"
            parts.append(f"| {i} | {task_name} | {priority} | {hours}h | {deps} |")
        return "\n".join(parts)


class StepPlanningUserApproval(PhaseStep):
    """Step 4: 用户审批"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        if context.metadata.get("plan_approved"):
            return StepResult(success=True, message="Plan approved")
        
        context.metadata["awaiting_plan_approval"] = True
        return StepResult(success=True, message="Plan ready for approval")
