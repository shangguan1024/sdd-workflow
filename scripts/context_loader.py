"""
ContextLoader: 自动加载项目上下文
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml


@dataclass
class ModuleSpec:
    name: str
    owner: str
    responsibility: str
    public_apis: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    file_path: str = ""
    summary: str = ""


@dataclass
class ProjectContext:
    project_root: Path
    constitution: dict[str, str] = field(default_factory=dict)
    modules: dict[str, ModuleSpec] = field(default_factory=dict)
    knowledge: dict[str, list[str]] = field(default_factory=dict)
    project_state: str = ""
    task_plan: str = ""
    feature_matrix: str = ""


class ModuleResolver:
    """确定与任务相关的模块"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def resolve(self, task: str, context: dict = None) -> list[str]:
        """返回与任务相关的模块列表"""

        modules = self._from_feature_matrix(task)
        if modules:
            return modules

        modules = self._from_code_analysis(task)
        if modules:
            return modules

        modules = self._from_task_context(task, context)
        if modules:
            return modules

        return []

    def _from_feature_matrix(self, task: str) -> list[str]:
        """从 feature-matrix.md 查找"""
        matrix_path = self.project_root / "docs" / "collaboration" / "feature-matrix.md"

        if not matrix_path.exists():
            return []

        content = matrix_path.read_text()
        lines = content.split("\n")

        modules = []
        for line in lines:
            if task in line:
                parts = line.split("|")
                if len(parts) > 2:
                    for part in parts[2:-1]:
                        if "✓" in part or "△" in part:
                            module_name = parts[1].strip() if parts[1] else ""
                            if module_name:
                                modules.append(module_name)

        return list(set(modules))

    def _from_code_analysis(self, task: str) -> list[str]:
        """用关键词分析推断相关模块"""
        modules_dir = self.project_root / "docs" / "modules"

        if not modules_dir.exists():
            return []

        modules = []
        for module_dir in modules_dir.iterdir():
            if not module_dir.is_dir():
                continue

            spec_path = module_dir / "SPEC.md"
            if spec_path.exists():
                content = spec_path.read_text().lower()
                if any(keyword in content for keyword in task.lower().split()):
                    modules.append(module_dir.name)

        return modules

    def _from_task_context(self, task: str, context: dict = None) -> list[str]:
        """从 task_plan 推断"""
        if not context:
            return []

        return context.get("modules", [])


class ContextLoader:
    """上下文加载器"""

    def __init__(self, project_root: Path, config_path: Path = None):
        self.project_root = project_root
        self.config_path = (
            config_path
            or Path(__file__).parent.parent / "config" / "context_loader.yaml"
        )
        self.config = self._load_config()
        self.module_resolver = ModuleResolver(project_root)

    def _load_config(self) -> dict:
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return {
            "context_loader": {
                "enabled": True,
                "max_tokens": 100000,
                "module_load_limit": 10,
            }
        }

    def load(self, task: str, phase: int, context: dict = None) -> ProjectContext:
        """加载项目上下文"""

        cfg = self.config.get("context_loader", {})
        if not cfg.get("enabled", True):
            return ProjectContext(project_root=self.project_root)

        project_context = ProjectContext(project_root=self.project_root)

        project_context.constitution = self._load_constitution(phase)

        modules = self.module_resolver.resolve(task, context)
        project_context.modules = self._load_modules(modules, phase)

        project_context.knowledge = self._load_knowledge(phase)

        project_context.project_state = self._load_file("PROJECT_STATE.md")
        project_context.task_plan = self._load_file("task_plan.md")
        project_context.feature_matrix = self._load_file(
            "docs/collaboration/feature-matrix.md"
        )

        return project_context

    def _load_constitution(self, phase: int) -> dict[str, str]:
        """根据 phase 加载 Constitution"""
        constitution = {}

        phase_contexts = self.config.get("context_loader", {}).get("phase_contexts", {})
        phase_cfg = phase_contexts.get(phase, {})

        constitution_files = phase_cfg.get("constitution", ["core.md"])

        const_dir = self.project_root / "CONSTITUTION"
        if not const_dir.exists():
            const_dir = self.project_root.parent / "CONSTITUTION"

        if const_dir.exists():
            for filename in constitution_files:
                file_path = const_dir / filename
                if file_path.exists():
                    constitution[filename] = file_path.read_text()

        return constitution

    def _load_modules(self, modules: list[str], phase: int) -> dict[str, ModuleSpec]:
        """加载相关模块规格"""
        module_specs = {}

        cfg = self.config.get("context_loader", {})
        load_limit = cfg.get("module_load_limit", 10)

        modules_dir = self.project_root / "docs" / "modules"

        for i, module_name in enumerate(modules[:load_limit]):
            module_dir = modules_dir / module_name
            if not module_dir.exists():
                continue

            spec_path = module_dir / "SPEC.md"
            if spec_path.exists():
                content = spec_path.read_text()

                module_specs[module_name] = ModuleSpec(
                    name=module_name,
                    owner=self._extract_owner(content),
                    responsibility=self._extract_responsibility(content),
                    file_path=str(spec_path),
                    summary=self._create_summary(content),
                )

        return module_specs

    def _load_knowledge(self, phase: int) -> dict[str, list[str]]:
        """加载知识库"""
        knowledge = {}

        phase_contexts = self.config.get("context_loader", {}).get("phase_contexts", {})
        phase_cfg = phase_contexts.get(phase, {})

        knowledge_dirs = phase_cfg.get("knowledge", [])

        knowledge_base = self.project_root / "docs" / "knowledge"

        for dir_name in knowledge_dirs:
            dir_path = knowledge_base / dir_name
            if dir_path.exists():
                files = []
                for f in dir_path.glob("*.md"):
                    files.append(f.read_text())
                knowledge[dir_name] = files

        return knowledge

    def _load_file(self, relative_path: str) -> str:
        """加载项目文件"""
        file_path = self.project_root / relative_path
        if file_path.exists():
            return file_path.read_text()
        return ""

    def _extract_owner(self, content: str) -> str:
        """提取模块 owner"""
        import re

        match = re.search(r"Owner[:\s]+@?(\w+)", content, re.IGNORECASE)
        return match.group(1) if match else "unknown"

    def _extract_responsibility(self, content: str) -> str:
        """提取模块职责"""
        import re

        match = re.search(r"Responsibility[:\s]+([^\n]+)", content, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _create_summary(self, content: str, max_length: int = 500) -> str:
        """创建模块规格摘要"""
        if len(content) <= max_length:
            return content

        return content[:max_length] + "..."


class ContextFormatter:
    """上下文格式化器"""

    @staticmethod
    def format(context: ProjectContext, task: str, phase: int) -> str:
        """格式化项目上下文为 markdown"""

        lines = [
            "# 项目上下文",
            "",
            f"## 当前任务",
            f"- 任务描述: {task}",
            f"- 当前阶段: Phase {phase}",
            "",
        ]

        if context.constitution:
            lines.extend(["## CONSTITUTION (项目准则)", ""])
            for filename, content in context.constitution.items():
                lines.extend([f"### {filename}", "", f"```", content[:500], "```", ""])

        if context.modules:
            lines.extend(["## 相关模块规格", ""])
            for name, spec in context.modules.items():
                lines.extend(
                    [
                        f"### {name}",
                        f"**负责人**: {spec.owner}",
                        f"**职责**: {spec.responsibility}",
                        f"**规格摘要**: {spec.summary[:200]}..."
                        if len(spec.summary) > 200
                        else f"**规格**: {spec.summary}",
                        "",
                    ]
                )

        if context.project_state:
            lines.extend(["## 项目状态", "", context.project_state[:500], ""])

        if context.task_plan:
            lines.extend(["## 任务进度", "", context.task_plan[:500], ""])

        lines.extend(["---", f"请基于以上上下文执行 Phase {phase} 任务。"])

        return "\n".join(lines)
