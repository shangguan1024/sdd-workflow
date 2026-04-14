"""
Phase 1: Requirements Analysis Orchestrator
需求分析阶段
"""

from pathlib import Path
from typing import Optional, Dict, Any, List, TYPE_CHECKING
import json
import re

if TYPE_CHECKING:
    from ..director import ExecutionContext, GateResult

from .base import PhaseOrchestrator, PhaseResult, PhaseStep, StepResult


class Phase1Orchestrator(PhaseOrchestrator):
    """
    Phase 1: Requirements Analysis
    
    职责:
    - 探索项目上下文
    - 分析存量代码
    - 收集需求
    - 生成设计方案
    - Constitution 合规检查
    - 用户审批
    """
    
    STEPS = [
        "explore_context",
        "analyze_existing_code",
        "gather_requirements",
        "web_kernel_skills",
        "generate_design",
        "impact_analysis",
        "expert_knowledge",
        "constitution_check",
        "user_approval",
    ]
    
    def __init__(self, capability_registry=None):
        super().__init__(capability_registry)
        self._init_steps()
    
    def _init_steps(self):
        """初始化 Steps"""
        self.steps = [
            StepExploreContext("explore_context"),
            StepAnalyzeExistingCode("analyze_existing_code"),
            StepGatherRequirements("gather_requirements"),
            StepWebKernelSkills("web_kernel_skills"),
            StepGenerateDesign("generate_design"),
            StepImpactAnalysis("impact_analysis"),
            StepExpertKnowledge("expert_knowledge"),
            StepConstitutionCheck("constitution_check"),
            StepUserApproval("user_approval"),
        ]
    
    def execute(self, context: "ExecutionContext") -> PhaseResult:
        """执行 Phase 1"""
        try:
            capability = context.capability
            if capability:
                result = capability.execute(context)
                if not result.success:
                    return PhaseResult(success=False, message=result.message)
            
            for step in self.steps:
                result = step.execute(context)
                if not result.success:
                    return PhaseResult(success=False, message=result.message)
                
                self._save_checkpoint(context, step.name)
            
            return PhaseResult(
                success=True,
                artifacts={"design-doc": context.artifacts.get("design-doc")},
                message="Phase 1 completed successfully",
            )
            
        except Exception as e:
            return PhaseResult(success=False, message=f"Phase 1 failed: {e}")
    
    def can_transition_to(self, context: "ExecutionContext") -> "GateResult":
        """检查是否可以进入 Phase 2"""
        required_artifacts = ["design-doc"]
        
        for artifact in required_artifacts:
            if artifact not in context.artifacts:
                return GateResult(
                    passed=False,
                    message=f"Missing required artifact: {artifact}",
                    blockers=[artifact],
                )
        
        if not context.metadata.get("design_approved"):
            return GateResult(
                passed=False,
                message="Design not approved by user",
                blockers=["user_approval"],
            )
        
        return GateResult(passed=True)


class StepExploreContext(PhaseStep):
    """Step 1: 探索项目上下文"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        """探索项目上下文"""
        project_root = context.project_root
        
        context_info = {
            "root": str(project_root),
            "structure": self._scan_structure(project_root),
            "config_files": self._find_config_files(project_root),
            "existing_features": self._find_existing_features(project_root),
        }
        
        context.metadata["project_context"] = context_info
        context.metadata["explore_context_completed"] = True
        
        return StepResult(
            success=True,
            message="Context explored",
            details={"structure": context_info["structure"]},
        )
    
    def _scan_structure(self, root: Path) -> Dict[str, Any]:
        """扫描项目结构"""
        structure = {
            "dirs": [],
            "file_types": {},
        }
        
        if not root.exists():
            return structure
        
        for item in root.rglob("*"):
            if item.is_dir():
                rel_path = item.relative_to(root)
                depth = len(rel_path.parts)
                if depth <= 3:
                    structure["dirs"].append(str(rel_path))
            else:
                ext = item.suffix.lower()
                structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
        
        return structure
    
    def _find_config_files(self, root: Path) -> List[str]:
        """查找配置文件"""
        config_patterns = [
            "*.json", "*.yaml", "*.yml", "*.toml",
            "*.ini", "*.cfg", "*.conf",
            "package.json", "Cargo.toml", "setup.py",
            "pyproject.toml", "Makefile", "CMakeLists.txt",
        ]
        
        configs = []
        for pattern in config_patterns:
            configs.extend([str(p.relative_to(root)) for p in root.glob(pattern)])
        
        return configs[:20]
    
    def _find_existing_features(self, root: Path) -> List[str]:
        """查找已存在的特性"""
        features_dir = root / "docs" / "features"
        if not features_dir.exists():
            return []
        
        return [d.name for d in features_dir.iterdir() if d.is_dir()]


class StepAnalyzeExistingCode(PhaseStep):
    """Step 2: 分析存量代码"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        """分析存量代码，识别可复用组件"""
        project_root = context.project_root
        
        analysis = {
            "modules": self._identify_modules(project_root),
            "dependencies": self._analyze_dependencies(project_root),
            "patterns": self._find_patterns(project_root),
        }
        
        context.metadata["existing_code_analysis"] = analysis
        context.metadata["existing_code_analysis_completed"] = True
        
        return StepResult(
            success=True,
            message="Existing code analyzed",
            details={"modules_found": len(analysis["modules"])},
        )
    
    def _identify_modules(self, root: Path) -> List[Dict[str, str]]:
        """识别项目模块"""
        modules = []
        
        patterns = ["**/module*.py", "**/modules/**/*.py", "**/src/**/*.py"]
        
        for pattern in patterns:
            for py_file in root.glob(pattern):
                if "test_" in py_file.name or "__pycache__" in str(py_file):
                    continue
                
                rel_path = py_file.relative_to(root)
                modules.append({
                    "path": str(rel_path),
                    "name": py_file.stem,
                })
        
        return modules[:50]
    
    def _analyze_dependencies(self, root: Path) -> Dict[str, List[str]]:
        """分析依赖关系"""
        deps = {}
        
        dep_files = [
            ("requirements.txt", "pip"),
            ("package.json", "npm"),
            ("Cargo.toml", "cargo"),
            ("go.mod", "go"),
            ("pyproject.toml", "python"),
        ]
        
        for filename, dep_type in dep_files:
            dep_file = root / filename
            if dep_file.exists():
                deps[dep_type] = self._parse_deps(dep_file)
        
        return deps
    
    def _parse_deps(self, dep_file: Path) -> List[str]:
        """解析依赖文件"""
        try:
            content = dep_file.read_text(encoding="utf-8")
            lines = []
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    if "==" in line:
                        line = line.split("==")[0].strip()
                    elif ">=" in line:
                        line = line.split(">=")[0].strip()
                    lines.append(line)
            return lines[:20]
        except:
            return []
    
    def _find_patterns(self, root: Path) -> Dict[str, int]:
        """查找代码模式"""
        patterns = {
            "classes": r"^class\s+\w+",
            "functions": r"^def\s+\w+",
            "async_functions": r"^async\s+def\s+\w+",
            "imports": r"^import\s+|^from\s+",
        }
        
        counts = {}
        
        for py_file in root.rglob("*.py"):
            if "test_" in py_file.name:
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                for pattern_name, pattern in patterns.items():
                    counts[pattern_name] = counts.get(pattern_name, 0) + len(re.findall(pattern, content, re.MULTILINE))
            except:
                pass
        
        return counts


class StepGatherRequirements(PhaseStep):
    """Step 3: 收集需求"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        """收集需求"""
        feature_name = context.feature_name
        
        requirements = context.metadata.get("gathered_requirements", [])
        if not requirements:
            requirements = self._extract_from_context(context)
        
        categorized = self._categorize_requirements(requirements)
        
        context.metadata["requirements"] = requirements
        context.metadata["requirements_categorized"] = categorized
        context.metadata["requirements_collected"] = True
        
        return StepResult(
            success=True,
            message="Requirements gathered",
            details={"count": len(requirements), "categories": list(categorized.keys())},
        )
    
    def _extract_from_context(self, context: "ExecutionContext") -> List[str]:
        """从上下文提取需求"""
        requirements = []
        
        if "user_input" in context.metadata:
            requirements.append(context.metadata["user_input"])
        
        if "feature_description" in context.metadata:
            requirements.append(context.metadata["feature_description"])
        
        if not requirements:
            requirements = [f"Feature: {context.feature_name}"]
        
        return requirements
    
    def _categorize_requirements(self, requirements: List[str]) -> Dict[str, List[str]]:
        """分类需求"""
        categories = {
            "functional": [],
            "non_functional": [],
            "constraints": [],
        }
        
        keywords = {
            "functional": ["shall", "must", "should", "allow", "enable", "provide", "support"],
            "non_functional": ["performance", "scalability", "reliability", "security", "usability"],
            "constraints": ["only", "must not", "cannot", "limit", "maximum", "minimum"],
        }
        
        for req in requirements:
            req_lower = req.lower()
            categorized = False
            
            for cat, kws in keywords.items():
                if any(kw in req_lower for kw in kws):
                    categories[cat].append(req)
                    categorized = True
                    break
            
            if not categorized:
                categories["functional"].append(req)
        
        return categories


class StepWebKernelSkills(PhaseStep):
    """Step 4: Web Kernel Skills 询问"""
    
    WEB_KERNEL_SKILLS = [
        {
            "name": "requirement-web-kernel-clarifier",
            "description": "Clarify underspecified Servo/web-platform requirements",
            "use_when": "Requirement is unclear or needs platform behavior clarification",
        },
        {
            "name": "requirement-standards-check",
            "description": "Map requirements to Web standards (WHATWG, W3C, etc.)",
            "use_when": "Task involves DOM, CSS, HTML, Fetch, URL, or other web specs",
        },
        {
            "name": "requirement-reference-implementation",
            "description": "Analyze Chromium/WebKit/Gecko implementations",
            "use_when": "Need design reference from mature browser engine implementations",
        },
    ]
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        """询问是否加载 Web Kernel Skills"""
        web_kernel_mode = context.metadata.get("web_kernel_mode", False)
        
        if not web_kernel_mode:
            context.metadata["web_kernel_skills_enabled"] = []
            context.metadata["web_kernel_skills_completed"] = True
            return StepResult(
                success=True,
                message="Web Kernel Skills skipped (non-web-kernel task)",
                details={"web_kernel_mode": False},
            )
        
        print()
        print("🌐 Web Kernel Skills Available")
        print("=" * 50)
        print("For Web Kernel development, you can use these skills to enhance requirements analysis:")
        print()
        
        for i, skill in enumerate(self.WEB_KERNEL_SKILLS, 1):
            print(f"{i}. {skill['name']}")
            print(f"   Description: {skill['description']}")
            print(f"   Use when: {skill['use_when']}")
            print()
        
        print("Available options:")
        print("  [1] Load all 3 skills")
        print("  [2] Select specific skills")
        print("  [3] Skip - Proceed without Web Kernel Skills")
        print()
        
        choice = input("Select option (1/2/3): ").strip()
        
        skills_to_load = []
        
        if choice == "1":
            skills_to_load = [s["name"] for s in self.WEB_KERNEL_SKILLS]
        elif choice == "2":
            print()
            print("Enter skill numbers to load (e.g., 1,3 for clarifier and reference): ")
            selection = input("Selection: ").strip()
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(",")]
                skills_to_load = [
                    self.WEB_KERNEL_SKILLS[i]["name"] 
                    for i in indices 
                    if 0 <= i < len(self.WEB_KERNEL_SKILLS)
                ]
            except ValueError:
                print("Invalid selection. Proceeding without Web Kernel Skills.")
                skills_to_load = []
        else:
            skills_to_load = []
        
        context.metadata["web_kernel_skills_enabled"] = skills_to_load
        context.metadata["web_kernel_skills_completed"] = True
        
        if skills_to_load:
            print()
            print("✅ Web Kernel Skills enabled:")
            for skill in skills_to_load:
                print(f"   - {skill}")
            print()
            print("💡 To use these skills during requirements analysis, load them with:")
            print("   /skill <skill-name>")
            print()
        else:
            print()
            print("⏭️  Skipped Web Kernel Skills. You can load them manually if needed.")
            print()
        
        return StepResult(
            success=True,
            message="Web Kernel Skills selection completed",
            details={
                "web_kernel_mode": True,
                "skills_enabled": skills_to_load,
            },
        )
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        """生成设计方案"""
        feature_name = context.feature_name
        requirements = context.metadata.get("requirements", [])
        categorized = context.metadata.get("requirements_categorized", {})
        context_info = context.metadata.get("project_context", {})
        
        design_doc = self._create_design_doc(
            feature_name,
            requirements,
            categorized,
            context_info,
        )
        
        feature_dir = context.feature_dir
        design_file = feature_dir / "specs" / f"2026-04-11-{feature_name}-design.md"
        design_file.parent.mkdir(parents=True, exist_ok=True)
        design_file.write_text(design_doc, encoding="utf-8")
        
        context.artifacts["design-doc"] = design_doc
        context.artifacts["design-file"] = str(design_file)
        
        return StepResult(
            success=True,
            message="Design generated",
            details={"file": str(design_file)},
        )
    
    def _create_design_doc(
        self,
        feature_name: str,
        requirements: List[str],
        categorized: Dict[str, List[str]],
        context_info: Dict[str, Any],
    ) -> str:
        """创建设计文档"""
        modules = context_info.get("structure", {}).get("dirs", [])[:10]
        
        doc = f"""# Design: {feature_name}

## Overview

**Feature:** {feature_name}  
**Date:** 2026-04-11  
**Status:** Draft

## Requirements

### Functional Requirements

"""
        for req in categorized.get("functional", requirements):
            doc += f"- {req}\n"
        
        doc += "\n### Non-Functional Requirements\n\n"
        for req in categorized.get("non_functional", []):
            doc += f"- {req}\n"
        
        doc += "\n### Constraints\n\n"
        for req in categorized.get("constraints", []):
            doc += f"- {req}\n"
        
        doc += "\n## Architecture\n\n"
        doc += "### Project Structure\n\n"
        for module in modules:
            doc += f"- `{module}`\n"
        
        doc += "\n### Module Design\n\n"
        doc += "```\n"
        doc += f"{feature_name}/\n"
        doc += f"├── src/\n"
        doc += f"│   └── {feature_name}/\n"
        doc += f"│       ├── __init__.py\n"
        doc += f"│       ├── core.py       # Core functionality\n"
        doc += f"│       └── api.py       # Public API\n"
        doc += f"└── tests/\n"
        doc += f"    └── test_{feature_name}.py\n"
        doc += "```\n"
        
        doc += "\n## Implementation Plan\n\n"
        doc += "| Step | Task | Priority |\n"
        doc += "|------|------|----------|\n"
        doc += "| 1 | Create module structure | High |\n"
        doc += "| 2 | Implement core functionality | High |\n"
        doc += "| 3 | Add tests | High |\n"
        doc += "| 4 | Documentation | Medium |\n"
        
        doc += "\n## Verification\n\n"
        doc += "- [ ] Code compiles/runs without errors\n"
        doc += "- [ ] Unit tests pass\n"
        doc += "- [ ] Integration tests pass\n"
        doc += "- [ ] Documentation complete\n"
        
        return doc


class StepImpactAnalysis(PhaseStep):
    """Step 5: 影响分析"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        """分析设计变更对系统的影响"""
        feature_name = context.feature_name
        
        impact = {
            "affected_modules": self._find_affected_modules(context),
            "risk_level": self._assess_risk(context),
            "regression_tests": self._identify_regression_tests(context),
        }
        
        context.metadata["impact_analysis"] = impact
        context.metadata["impact_analysis_completed"] = True
        
        return StepResult(
            success=True,
            message="Impact analysis completed",
            details={"affected_modules": len(impact["affected_modules"]), "risk": impact["risk_level"]},
        )
    
    def _find_affected_modules(self, context: "ExecutionContext") -> List[str]:
        """查找受影响的模块"""
        analysis = context.metadata.get("existing_code_analysis", {})
        modules = analysis.get("modules", [])
        
        return [m["name"] for m in modules[:5]]
    
    def _assess_risk(self, context: "ExecutionContext") -> str:
        """评估风险等级"""
        requirements = context.metadata.get("requirements", [])
        
        if len(requirements) > 10:
            return "High"
        elif len(requirements) > 5:
            return "Medium"
        else:
            return "Low"
    
    def _identify_regression_tests(self, context: "ExecutionContext") -> List[str]:
        """识别回归测试"""
        return ["test_existing_functionality", "test_integration"]


class StepExpertKnowledge(PhaseStep):
    """Step 6: 专家经验融入"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        """融入专家经验和最佳实践"""
        feature_name = context.feature_name
        
        knowledge = {
            "design_patterns": self._suggest_patterns(context),
            "best_practices": self._get_best_practices(context),
            "common_pitfalls": self._warn_pitfalls(context),
        }
        
        context.metadata["expert_knowledge"] = knowledge
        context.metadata["expert_knowledge_integrated"] = True
        
        return StepResult(
            success=True,
            message="Expert knowledge integrated",
            details={"patterns_suggested": len(knowledge["design_patterns"])},
        )
    
    def _suggest_patterns(self, context: "ExecutionContext") -> List[str]:
        """建议设计模式"""
        patterns = []
        
        requirements = context.metadata.get("requirements", [])
        categorized = context.metadata.get("requirements_categorized", {})
        
        if categorized.get("functional"):
            patterns.append("Strategy Pattern - for varying behaviors")
        if len(requirements) > 5:
            patterns.append("Factory Pattern - for complex object creation")
        if any("api" in r.lower() for r in requirements):
            patterns.append("Facade Pattern - for simplified interface")
        
        return patterns if patterns else ["Module Pattern - for encapsulation"]
    
    def _get_best_practices(self, context: "ExecutionContext") -> List[str]:
        """获取最佳实践"""
        return [
            "Use type hints for better IDE support",
            "Write docstrings for all public APIs",
            "Keep functions small and focused",
            "Separate concerns between modules",
            "Use dependency injection for testability",
        ]
    
    def _warn_pitfalls(self, context: "ExecutionContext") -> List[str]:
        """警告常见陷阱"""
        return [
            "Avoid premature optimization",
            "Do not over-engineer - keep it simple",
            "Avoid circular dependencies",
            "Do not ignore error handling",
        ]


class StepConstitutionCheck(PhaseStep):
    """Step 7: Constitution 检查"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        """检查设计是否符合 Constitution"""
        project_root = context.project_root
        
        constitution_dir = project_root / "CONSTITUTION"
        violations = []
        
        if constitution_dir.exists():
            violations = self._check_constitution_rules(context, constitution_dir)
        else:
            violations = self._check_default_rules(context)
        
        context.metadata["constitution_violations"] = violations
        context.metadata["constitution_compliant"] = len(violations) == 0
        
        if violations:
            return StepResult(
                success=True,
                message="Constitution check passed with warnings",
                details={"violations": len(violations)},
            )
        
        return StepResult(
            success=True,
            message="Constitution check passed",
            details={"violations": 0},
        )
    
    def _check_constitution_rules(self, context: "ExecutionContext", const_dir: Path) -> List[str]:
        """检查 Constitution 规则"""
        violations = []
        
        design_file = context.artifacts.get("design-file")
        if design_file and Path(design_file).exists():
            design_content = Path(design_file).read_text(encoding="utf-8")
            
            rule_files = list(const_dir.glob("*.md"))
            for rule_file in rule_files:
                rule_content = rule_file.read_text(encoding="utf-8")
                
                if "test" in rule_file.name.lower() and "test" not in design_content.lower():
                    violations.append(f"Rule violation: {rule_file.name} requires tests")
        
        return violations
    
    def _check_default_rules(self, context: "ExecutionContext") -> List[str]:
        """检查默认规则"""
        violations = []
        
        design_doc = context.artifacts.get("design-doc", "")
        
        if "test" not in design_doc.lower():
            violations.append("Design should include testing strategy")
        
        if "doc" not in design_doc.lower() and "document" not in design_doc.lower():
            violations.append("Design should include documentation plan")
        
        return violations


class StepUserApproval(PhaseStep):
    """Step 8: 用户审批"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        """等待用户审批"""
        if context.metadata.get("design_approved"):
            return StepResult(success=True, message="Design approved")
        
        context.metadata["awaiting_user_approval"] = True
        
        design_file = context.artifacts.get("design-file", "design document")
        
        return StepResult(
            success=True,
            message=f"Design ready for user approval. Review: {design_file}",
            details={"approval_required": True},
        )
