"""
ContextLoader: load project context + conversation memory for agent injection.
v2.1: Supports feedback loop — writing decisions back to knowledge base.
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
    conversation_memory_summary: str = ""
    findings: str = ""
    progress: str = ""


class ModuleResolver:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def resolve(self, task: str, context: dict = None) -> list[str]:
        modules = self._from_feature_matrix(task)
        if modules:
            return modules
        modules = self._from_code_analysis(task)
        if modules:
            return modules
        modules = self._from_task_context(task, context)
        return modules or []

    def _from_feature_matrix(self, task: str) -> list[str]:
        matrix_path = self.project_root / "docs" / "collaboration" / "feature-matrix.md"
        if not matrix_path.exists():
            return []
        content = matrix_path.read_text()
        modules = []
        for line in content.split("\n"):
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
        if not context:
            return []
        return context.get("modules", [])


class ContextLoader:
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

    def load(self, task: str, phase: int,
             context: dict = None,
             conversation_memory=None) -> ProjectContext:
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
        project_context.findings = self._load_file("findings.md")
        project_context.progress = self._load_file("progress.md")
        project_context.feature_matrix = self._load_file(
            "docs/collaboration/feature-matrix.md"
        )

        if conversation_memory:
            try:
                project_context.conversation_memory_summary = (
                    conversation_memory.get_context_summary()
                )
            except Exception:
                project_context.conversation_memory_summary = ""
        elif isinstance(context, dict) and "feature_name" in context:
            from ..src.memory.recovery import MemoryRecovery
            recovery = MemoryRecovery(self.project_root)
            memory = recovery.recover(context["feature_name"])
            if memory:
                project_context.conversation_memory_summary = (
                    memory.get_context_summary()
                )

        return project_context

    def load_with_memory(self, task: str, phase: int,
                         feature_name: str = "",
                         context: dict = None) -> ProjectContext:
        memory = None
        if feature_name:
            from ..src.memory.recovery import MemoryRecovery
            recovery = MemoryRecovery(self.project_root)
            memory = recovery.recover(feature_name)

        return self.load(task, phase, context=context, conversation_memory=memory)

    def write_back(self, feature_name: str, memory, category: str,
                   title: str, content: str) -> bool:
        """Feedback loop: write new knowledge back to the project's knowledge base."""
        write_back_config = (
            self.config.get("context_loader", {}).get("write_back", {})
        )
        if not write_back_config.get("enabled", True):
            return False

        knowledge_dir = self.project_root / "docs" / "knowledge"
        knowledge_dir.mkdir(parents=True, exist_ok=True)

        category_map = {
            "requirement": "domain",
            "design_decision": "design-patterns",
            "research_finding": "domain",
            "constraint": "domain",
            "discussion": "domain",
        }
        subdir = category_map.get(category, "domain")
        target_dir = knowledge_dir / subdir
        target_dir.mkdir(parents=True, exist_ok=True)

        feature_file = target_dir / f"{feature_name}-insights.md"

        now_str = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"""### {title}
**Category**: {category}
**Added**: {now_str}

{content}

---

"""

        existing = ""
        if feature_file.exists():
            existing = feature_file.read_text()

        feature_file.write_text(existing + entry)
        return True

    def write_back_decisions(self, feature_name: str, memory) -> int:
        """Write all design decisions from memory back to knowledge base."""
        if memory is None:
            return 0

        count = 0
        for node in memory.get_design_decisions():
            if self.write_back(feature_name, memory,
                               "design_decision", node.title,
                               f"**决策**: {node.content}\n**理据**: {node.rationale}"):
                count += 1

        for node in memory.get_requirements():
            if self.write_back(feature_name, memory,
                               "requirement", node.title,
                               f"[{node.priority}] {node.content}"):
                count += 1

        return count

    def _load_constitution(self, phase: int) -> dict[str, str]:
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
        file_path = self.project_root / relative_path
        if file_path.exists():
            return file_path.read_text()
        return ""

    def _extract_owner(self, content: str) -> str:
        import re
        match = re.search(r"Owner[:\s]+@?(\w+)", content, re.IGNORECASE)
        return match.group(1) if match else "unknown"

    def _extract_responsibility(self, content: str) -> str:
        import re
        match = re.search(r"Responsibility[:\s]+([^\n]+)", content, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _create_summary(self, content: str, max_length: int = 500) -> str:
        return content if len(content) <= max_length else content[:max_length] + "..."


class ContextFormatter:
    @staticmethod
    def format(context: ProjectContext, task: str, phase: int) -> str:
        lines = [
            "# 项目上下文",
            "",
            f"## 当前任务",
            f"- 任务描述: {task}",
            f"- 当前阶段: Phase {phase}",
            "",
        ]

        if context.conversation_memory_summary:
            lines.extend([
                "## 对话记忆 (跨会话持久化)",
                "",
                context.conversation_memory_summary,
                "",
                "---",
                "",
            ])

        if context.constitution:
            lines.extend(["## CONSTITUTION (项目准则)", ""])
            for filename, content in context.constitution.items():
                lines.extend([f"### {filename}", "", f"```", content[:500], "```", ""])

        if context.modules:
            lines.extend(["## 相关模块规格", ""])
            for name, spec in context.modules.items():
                lines.extend([
                    f"### {name}",
                    f"**负责人**: {spec.owner}",
                    f"**职责**: {spec.responsibility}",
                    f"**规格摘要**: {spec.summary[:200]}..."
                    if len(spec.summary) > 200
                    else f"**规格**: {spec.summary}",
                    "",
                ])

        if context.project_state:
            lines.extend(["## 项目状态", "", context.project_state[:500], ""])
        if context.task_plan:
            lines.extend(["## 任务进度", "", context.task_plan[:500], ""])

        if context.findings:
            lines.extend(["## 研究发现", "", context.findings[:500], ""])

        lines.extend(["---", f"请基于以上上下文执行 Phase {phase} 任务。"])

        return "\n".join(lines)
