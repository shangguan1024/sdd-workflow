"""
Multi-Agent Coordinator with conflict detection.
Skeleton implementation for parallel agent task management.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgentTask:
    task_id: str
    description: str
    files_owned: list[str] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)
    assigned_agent: str = ""
    status: str = "pending"
    dependencies: list[str] = field(default_factory=list)


@dataclass
class Conflict:
    conflict_type: str
    description: str
    files: list[str]
    tasks: list[str]
    suggested_resolution: str = ""


class CoordinatorAgent:
    def __init__(self):
        self.tasks: dict[str, AgentTask] = {}
        self.file_ownership: dict[str, str] = {}
        self.conflicts: list[Conflict] = []

    def assign_task(self, task_id: str, description: str,
                    files: list[str], agent: str,
                    dependencies: list[str] = None) -> bool:
        conflicts = self._detect_file_overlap(task_id, files)
        if conflicts:
            self.conflicts.append(Conflict(
                conflict_type="same_file_modified",
                description=f"Task {task_id} overlaps with: {conflicts}",
                files=list(conflicts),
                tasks=[task_id, self.file_ownership.get(conflicts[0], "unknown")],
                suggested_resolution="Sequential edits or reassign file ownership",
            ))
            return False

        task = AgentTask(
            task_id=task_id,
            description=description,
            files_owned=files,
            assigned_agent=agent,
            dependencies=dependencies or [],
        )
        self.tasks[task_id] = task
        for f in files:
            self.file_ownership[f] = task_id
        return True

    def check_interface_consistency(self, frozen_interfaces: dict,
                                    current_interfaces: dict) -> list[Conflict]:
        conflicts = []
        for name, expected in frozen_interfaces.items():
            if name not in current_interfaces:
                conflicts.append(Conflict(
                    conflict_type="missing_interface",
                    description=f"Interface '{name}' was frozen but not found",
                    files=[],
                    tasks=[],
                    suggested_resolution=f"Implement interface: {name}",
                ))
            elif expected != current_interfaces[name]:
                conflicts.append(Conflict(
                    conflict_type="interface_changed",
                    description=f"Interface '{name}' changed from frozen version",
                    files=[],
                    tasks=[],
                    suggested_resolution="Coordinate interface change via Coordinator",
                ))
        return conflicts

    def detect_conflicts(self) -> list[Conflict]:
        all_conflicts = list(self.conflicts)

        file_to_tasks: dict[str, list[str]] = {}
        for task_id, task in self.tasks.items():
            for f in task.files_modified:
                file_to_tasks.setdefault(f, []).append(task_id)

        for file_path, task_ids in file_to_tasks.items():
            if len(task_ids) > 1:
                all_conflicts.append(Conflict(
                    conflict_type="same_file_modified",
                    description=f"File '{file_path}' modified by {task_ids}",
                    files=[file_path],
                    tasks=task_ids,
                    suggested_resolution="Sequential tasks or split file responsibility",
                ))

        return all_conflicts

    def resolve_conflicts(self) -> dict:
        unresolved = []
        resolved = []

        for conflict in self.conflicts:
            if conflict.conflict_type == "same_file_modified":
                owner_task = self.file_ownership.get(conflict.files[0])
                if owner_task:
                    for task_id in conflict.tasks:
                        if task_id != owner_task:
                            task = self.tasks.get(task_id)
                            if task:
                                task.files_modified = [
                                    f for f in task.files_modified
                                    if f not in conflict.files
                                ]
                    resolved.append(conflict)

        self.conflicts = unresolved
        return {"resolved": len(resolved), "unresolved": len(unresolved)}

    def get_ready_tasks(self) -> list[AgentTask]:
        ready = []
        for task in self.tasks.values():
            if task.status != "pending":
                continue
            deps_met = all(
                self.tasks.get(dep, AgentTask("", "", status="completed")).status == "completed"
                for dep in task.dependencies
            )
            if deps_met:
                ready.append(task)
        return ready

    def mark_complete(self, task_id: str):
        if task_id in self.tasks:
            self.tasks[task_id].status = "completed"

    def summary(self) -> dict:
        return {
            "total_tasks": len(self.tasks),
            "completed": sum(1 for t in self.tasks.values() if t.status == "completed"),
            "in_progress": sum(1 for t in self.tasks.values() if t.status == "in_progress"),
            "pending": sum(1 for t in self.tasks.values() if t.status == "pending"),
            "conflicts": len(self.conflicts),
        }

    def _detect_file_overlap(self, task_id: str, files: list[str]) -> set[str]:
        conflicts = set()
        for f in files:
            owner = self.file_ownership.get(f)
            if owner and owner != task_id:
                conflicts.add(f)
        return conflicts
