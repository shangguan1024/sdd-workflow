"""
Writing Plans Capability
"""

from pathlib import Path
from typing import TYPE_CHECKING, List, Dict, Any

if TYPE_CHECKING:
    from ..director import ExecutionContext

from .base import Capability, CapabilityResult


class WritingPlansCapability(Capability):
    """
    Writing Plans Capability
    
    职责:
    - 分解任务为步骤
    - 估算工作量
    - 识别依赖
    - 定义文件变更范围 (file_changes)
    - 生成执行计划
    """
    
    def __init__(self):
        super().__init__("writing-plans")
    
    def execute(self, context: "ExecutionContext") -> CapabilityResult:
        """执行 Writing Plans"""
        try:
            feature_name = context.feature_name
            
            # 从 context 获取设计阶段的文件信息
            design_doc = context.artifacts.get("design-doc", "")
            
            tasks = self._create_task_list(context)
            file_changes = self._create_file_changes(context)
            milestones = self._define_milestones(context, tasks)
            
            plan_doc = self._generate_plan_doc(context, tasks, file_changes, milestones)
            
            context.metadata["writing_plans_executed"] = True
            context.metadata["tasks"] = tasks
            context.metadata["file_changes"] = file_changes
            context.metadata["milestones"] = milestones
            
            return CapabilityResult(
                success=True,
                message=f"Plan created: {len(tasks)} tasks, {len(milestones)} milestones, {len(file_changes['total_files'])} files",
                artifacts={
                    "tasks": tasks,
                    "file_changes": file_changes,
                    "milestones": milestones,
                    "plan_doc": plan_doc,
                },
            )
        except Exception as e:
            return CapabilityResult(
                success=False,
                message=f"Writing Plans failed: {e}",
            )
    
    def _create_file_changes(self, context: "ExecutionContext") -> Dict[str, Any]:
        """定义文件变更范围"""
        feature_name = context.feature_name
        
        # 默认的文件变更结构，实际应从 design doc 解析
        file_changes = {
            "new_files": [],
            "modified_files": [],
            "deleted_files": [],
            "total_files": 0,
        }
        
        # 检查 context 中是否有设计阶段定义的文件
        design_info = context.metadata.get("design_files", {})
        
        if design_info:
            file_changes["new_files"] = design_info.get("new_files", [])
            file_changes["modified_files"] = design_info.get("modified_files", [])
            file_changes["deleted_files"] = design_info.get("deleted_files", [])
        else:
            # 默认结构 - 基于 feature name 生成占位符
            file_changes["new_files"] = [
                f"src/{feature_name}/__init__.py",
                f"src/{feature_name}/core.py",
                f"src/{feature_name}/api.py",
                f"tests/test_{feature_name}.py",
            ]
            file_changes["modified_files"] = [
                "src/main.py",
                "Cargo.toml",
            ]
        
        file_changes["total_files"] = (
            len(file_changes["new_files"]) 
            + len(file_changes["modified_files"]) 
            + len(file_changes["deleted_files"])
        )
        
        return file_changes
    
    def _create_task_list(self, context: "ExecutionContext") -> List[Dict[str, Any]]:
        """创建任务列表"""
        feature_name = context.feature_name
        
        tasks = [
            {
                "id": "task-1",
                "title": f"Setup {feature_name} project structure",
                "description": "Create directories and initial files",
                "priority": "high",
                "estimated_hours": 1,
                "dependencies": [],
            },
            {
                "id": "task-2",
                "title": f"Implement core {feature_name} functionality",
                "description": "Implement main features",
                "priority": "high",
                "estimated_hours": 4,
                "dependencies": ["task-1"],
            },
            {
                "id": "task-3",
                "title": f"Add unit tests for {feature_name}",
                "description": "Write comprehensive unit tests",
                "priority": "high",
                "estimated_hours": 2,
                "dependencies": ["task-2"],
            },
            {
                "id": "task-4",
                "title": f"Implement error handling",
                "description": "Add proper error handling and logging",
                "priority": "medium",
                "estimated_hours": 1,
                "dependencies": ["task-2"],
            },
            {
                "id": "task-5",
                "title": f"Update documentation",
                "description": "Update README and inline docs",
                "priority": "low",
                "estimated_hours": 1,
                "dependencies": ["task-4"],
            },
        ]
        
        return tasks
    
    def _define_milestones(
        self,
        context: "ExecutionContext",
        tasks: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """定义里程碑"""
        feature_name = context.feature_name
        
        milestones = [
            {
                "id": "milestone-1",
                "title": f"{feature_name} MVP",
                "description": "Basic functionality ready",
                "tasks": ["task-1", "task-2"],
                "due_days": 2,
            },
            {
                "id": "milestone-2",
                "title": f"{feature_name} Tested",
                "description": "Tests written and passing",
                "tasks": ["task-3"],
                "due_days": 1,
            },
            {
                "id": "milestone-3",
                "title": f"{feature_name} Complete",
                "description": "Documentation complete, ready for review",
                "tasks": ["task-4", "task-5"],
                "due_days": 1,
            },
        ]
        
        return milestones
    
    def _generate_plan_doc(
        self,
        context: "ExecutionContext",
        tasks: List[Dict[str, Any]],
        file_changes: Dict[str, Any],
        milestones: List[Dict[str, Any]],
    ) -> str:
        """生成计划文档"""
        feature_name = context.feature_name
        total_hours = sum(t["estimated_hours"] for t in tasks)
        
        doc = f"""# Implementation Plan: {feature_name}

## Summary

- **Feature:** {feature_name}
- **Total Tasks:** {len(tasks)}
- **Total Estimated Hours:** {total_hours}
- **Milestones:** {len(milestones)}
- **Files to Change:** {file_changes['total_files']}

## File Changes Scope

> ⚠️ **Phase 5 Code Review 范围**: 仅审查以下文件变更

### New Files ({len(file_changes['new_files'])})
"""
        
        if file_changes["new_files"]:
            for f in file_changes["new_files"]:
                doc += f"- `{f}`\n"
        else:
            doc += "- None\n"
        
        doc += f"\n### Modified Files ({len(file_changes['modified_files'])})\n"
        
        if file_changes["modified_files"]:
            for f in file_changes["modified_files"]:
                doc += f"- `{f}`\n"
        else:
            doc += "- None\n"
        
        doc += f"\n### Deleted Files ({len(file_changes['deleted_files'])})\n"
        
        if file_changes["deleted_files"]:
            for f in file_changes["deleted_files"]:
                doc += f"- `{f}`\n"
        else:
            doc += "- None\n"
        
        doc += """
## Milestones

"""
        for milestone in milestones:
            doc += f"### {milestone['title']}\n"
            doc += f"{milestone['description']}\n"
            doc += f"- Due: {milestone['due_days']} days\n"
            doc += f"- Tasks: {', '.join(milestone['tasks'])}\n\n"
        
        doc += "## Tasks\n\n"
        doc += "| ID | Task | Priority | Hours | Dependencies |\n"
        doc += "|----|------|----------|-------|---------------|\n"
        
        for task in tasks:
            deps = ", ".join(task["dependencies"]) if task["dependencies"] else "None"
            doc += f"| {task['id']} | {task['title']} | {task['priority']} | {task['estimated_hours']} | {deps} |\n"
        
        doc += f"""
## Phase 5 Review Scope

> This section defines the scope for Phase 5 Code Review.
> **Only files listed above in File Changes Scope will be reviewed.**

| File Type | Count | Review Focus |
|-----------|-------|--------------|
| New Files | {len(file_changes['new_files'])} | Completeness, testability, design fit |
| Modified Files | {len(file_changes['modified_files'])} | Regression, backward compatibility |
| Deleted Files | {len(file_changes['deleted_files'])} | No breaking changes |

"""
        return doc
