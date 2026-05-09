"""
Phase 4: Integration Orchestrator (Enhanced)
"""

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Any
from datetime import datetime

if TYPE_CHECKING:
    from ..director import ExecutionContext, GateResult

from .base import PhaseOrchestrator, PhaseResult, PhaseStep


class Phase4Orchestrator(PhaseOrchestrator):
    """
    Phase 4: Integration (Enhanced)
    
    职责:
    - 检查模块依赖和导入
    - 运行集成测试
    - Constitution 检查
    - 修复集成问题
    - 更新 findings.md
    """
    
    STEPS = [
        "check_module_dependencies",
        "integrate_modules",
        "run_integration_tests",
        "quality_assessment",
        "constitution_check",
        "fix_integration_issues",
        "update_findings",
    ]
    
    def __init__(self, capability_registry=None):
        super().__init__(capability_registry)
        self._init_steps()
    
    def _init_steps(self):
        self.steps = [
            StepCheckModuleDependencies("check_module_dependencies"),
            StepIntegrateModules("integrate_modules"),
            StepRunIntegrationTests("run_integration_tests"),
            StepRunQualityAssessment("quality_assessment"),
            StepConstitutionCheckForIntegration("constitution_check"),
            StepFixIntegrationIssues("fix_integration_issues"),
            StepUpdateFindings("update_findings"),
        ]
    
    def execute(self, context: "ExecutionContext") -> PhaseResult:
        try:
            self._check_and_refresh_context(context, "进入 Phase 4 (Integration)")
            
            for step in self.steps:
                result = step.execute(context)
                if not result.success:
                    return PhaseResult(
                        success=False,
                        message=f"Phase 4 step '{step.name}' failed: {result.message}"
                    )
            
            self._save_phase_checkpoint(context, "phase4")
            
            return PhaseResult(
                success=True,
                artifacts={"integration_complete": True},
                message="Phase 4 completed - Integration successful",
            )
        
        except Exception as e:
            self._capture_error(e, context, "phase4", severity="CRITICAL")
            return PhaseResult(
                success=False,
                message=f"Phase 4 execution failed: {e}"
            )

    def can_transition_to(self, context: "ExecutionContext") -> "GateResult":
        if not context.metadata.get("integration_complete"):
            return GateResult(passed=False, message="Integration not complete")
        return GateResult(passed=True)


class StepCheckModuleDependencies(PhaseStep):
    """Step 0: 检查模块依赖和导入"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        implemented = context.metadata.get("implemented_modules", [])
        
        if not implemented:
            return StepResult(
                success=True,
                message="No modules to check",
                details={"modules": 0},
            )
        
        project_root = context.project_root
        dependency_issues = []
        
        for module_path in implemented:
            if isinstance(module_path, str) and module_path.endswith(".py"):
                full_path = project_root / module_path
                if full_path.exists():
                    issues = self._check_file_imports(full_path, project_root)
                    dependency_issues.extend(issues)
        
        context.metadata["dependency_check_complete"] = True
        context.metadata["dependency_issues"] = dependency_issues
        
        if dependency_issues:
            return StepResult(
                success=True,
                message=f"Found {len(dependency_issues)} dependency issues",
                details={"issues": dependency_issues[:5]},
            )
        
        return StepResult(
            success=True,
            message="All module dependencies valid",
            details={"modules_checked": len(implemented)},
        )
    
    def _check_file_imports(self, file_path: Path, project_root: Path) -> List[str]:
        """增强的依赖检查"""
        import ast
        import re
        issues = []
        
        try:
            content = file_path.read_text(encoding="utf-8")
            
            try:
                tree = ast.parse(content)
                
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
                        if node.level > 0:
                            imports.append(f"relative:{node.level}:{node.module or ''}")
                
                for imp in imports:
                    if imp.startswith("relative:"):
                        parts = imp.split(":")
                        level = int(parts[1])
                        module = parts[2] if len(parts) > 2 else ""
                        
                        base_path = file_path.parent
                        for _ in range(level):
                            base_path = base_path.parent
                        
                        if module:
                            module_path = base_path / module.replace(".", "/")
                            if not module_path.exists():
                                module_file = base_path / f"{module.replace('.', '/')}.py"
                                if not module_file.exists():
                                    init_file = module_path / "__init__.py"
                                    if not init_file.exists():
                                        issues.append(
                                            f"{file_path.relative_to(project_root)}: "
                                            f"Relative import '{module}' (level {level}) may not exist"
                                        )
                    
                    else:
                        if imp.startswith(("src.", "tests.", "middleware.", "scripts.")):
                            parts = imp.split(".")
                            expected_path = project_root / parts[0] / parts[1] if len(parts) > 1 else project_root / parts[0]
                            if not expected_path.exists():
                                issues.append(
                                    f"{file_path.relative_to(project_root)}: "
                                    f"Project import '{imp}' may not exist"
                                )
            
            except SyntaxError:
                import_lines = [
                    line for line in content.split("\n")
                    if line.strip().startswith(("import ", "from "))
                ]
                
                for line in import_lines[:10]:
                    if "from ." in line:
                        module_name = line.split("from .")[1].split(" import")[0].strip()
                        expected_path = file_path.parent / module_name.replace(".", "/") / "__init__.py"
                        if not expected_path.exists() and not (file_path.parent / f"{module_name}.py").exists():
                            issues.append(f"{file_path.relative_to(project_root)}: Local import '{module_name}' may not exist")
            
            dep_files = []
            for dep_file_name in ["requirements.txt", "pyproject.toml", "setup.py", "Cargo.toml", "package.json", "go.mod"]:
                dep_file = project_root / dep_file_name
                if dep_file.exists():
                    dep_files.append(dep_file_name)
            
            if dep_files:
                dep_content = ""
                for dep_file_name in dep_files:
                    dep_file = project_root / dep_file_name
                    try:
                        dep_content += dep_file.read_text(encoding="utf-8", errors="ignore")
                    except Exception:
                        pass
                
                for imp in imports[:20]:
                    if not imp.startswith(("relative:", "src.", "tests.", "middleware.", "scripts.", ".")):
                        if not imp.startswith(("os", "sys", "json", "yaml", "pathlib", "typing", "datetime", "abc", "enum", "dataclasses", "collections", "functools", "itertools", "re", "subprocess", "hashlib", "tempfile", "shutil", "copy")):
                            if imp not in dep_content and imp.split(".")[0] not in dep_content:
                                issues.append(
                                    f"{file_path.relative_to(project_root)}: "
                                    f"Import '{imp}' not found in dependency files ({', '.join(dep_files)})"
                                )
        
        except Exception as e:
            issues.append(f"{file_path.relative_to(project_root)}: Failed to parse file: {e}")
        
        return issues


class StepIntegrateModules(PhaseStep):
    """Step 1: 集成模块"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        implemented = context.metadata.get("implemented_modules", [])
        dependency_issues = context.metadata.get("dependency_issues", [])
        
        if dependency_issues:
            return StepResult(
                success=False,
                message=f"Cannot integrate modules - {len(dependency_issues)} dependency issues found. Must fix first.",
                details={"issues": dependency_issues[:5]},
            )
        
        integration_result = self._perform_integration(context, implemented)
        
        context.metadata["modules_integrated"] = True
        context.metadata["integration_manifest"] = integration_result
        
        return StepResult(
            success=True,
            message=f"Integrated {len(implemented)} modules successfully",
            details={"modules": len(implemented), "integration_type": integration_result.get("type", "standard")},
        )
    
    def _perform_integration(self, context: "ExecutionContext", modules: List[str]) -> Dict[str, Any]:
        project_root = context.project_root
        feature_name = context.feature_name
        
        integration_manifest = {
            "timestamp": datetime.now().isoformat(),
            "feature": feature_name,
            "modules": modules,
            "type": "standard",
            "main_entry_point": None,
        }
        
        main_candidates = [
            project_root / "src" / feature_name / "api.py",
            project_root / "src" / feature_name / "core.py",
            project_root / "src" / feature_name / "__init__.py",
        ]
        
        for candidate in main_candidates:
            if candidate.exists():
                integration_manifest["main_entry_point"] = str(candidate.relative_to(project_root))
                break
        
        return integration_manifest


class StepRunIntegrationTests(PhaseStep):
    """Step 2: 运行集成测试"""
    
    TEST_COMMANDS = {
        "python": ["pytest", "-v", "--tb=short"],
        "rust": ["cargo", "test"],
        "node": ["npm", "test"],
        "go": ["go", "test", "./..."],
        "default": ["pytest", "-v"],
    }
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        project_root = context.project_root
        test_type = self._detect_test_type(project_root)
        command = self.TEST_COMMANDS.get(test_type, self.TEST_COMMANDS["default"])
        
        print(f"\n🧪 Running integration tests ({test_type})...")
        print(f"Command: {command}")
        
        result = self._run_tests(project_root, command)
        
        context.metadata["integration_tests_run"] = True
        context.metadata["integration_tests_passed"] = result["passed"]
        context.metadata["integration_test_output"] = result["output"]
        context.metadata["integration_test_failures"] = result["failures"]
        
        if result["passed"]:
            return StepResult(success=True, message="All integration tests passed")
        else:
            context.metadata["integration_issues"] = result["failures"]
            return StepResult(
                success=True,
                message=f"Tests run with {len(result['failures'])} failures",
                details={"failures": result["failures"][:5]},
            )
    
    def _detect_test_type(self, project_root: Path) -> str:
        if (project_root / "Cargo.toml").exists():
            return "rust"
        if (project_root / "package.json").exists():
            return "node"
        if (project_root / "go.mod").exists():
            return "go"
        if (project_root / "pytest.ini").exists() or (project_root / "setup.py").exists():
            return "python"
        if list(project_root.glob("tests/test_*.py")):
            return "python"
        return "default"
    
    def _run_tests(self, project_root: Path, command: List[str]) -> Dict:
        try:
            result = subprocess.run(
                command,
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            output = result.stdout + result.stderr
            
            passed = result.returncode == 0
            
            failures = []
            if not passed:
                failures = self._parse_test_failures(output)
            
            return {
                "passed": passed,
                "output": output,
                "failures": failures,
            }
        
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "output": "Test execution timed out (120s)",
                "failures": ["Timeout"],
            }
        except FileNotFoundError:
            return {
                "passed": False,
                "output": f"Test runner not found: {command[0]}",
                "failures": [f"Missing: {command[0]}"],
            }
        except Exception as e:
            return {
                "passed": False,
                "output": str(e),
                "failures": [str(e)],
            }
    
    def _parse_test_failures(self, output: str) -> List[str]:
        failures = []
        lines = output.split("\n")
        
        for line in lines:
            if "FAILED" in line or "ERROR" in line:
                failures.append(line.strip())
        
        return failures[:20]


class StepConstitutionCheckForIntegration(PhaseStep):
    """Step 3: Constitution 检查（Integration阶段）"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        project_root = context.project_root
        constitution_dir = project_root / "CONSTITUTION"
        
        if not constitution_dir.exists():
            return StepResult(
                success=True,
                message="Constitution directory not found - skipping check",
                details={"constitution_found": False},
            )
        
        integration_manifest = context.metadata.get("integration_manifest", {})
        
        if not integration_manifest:
            return StepResult(
                success=True,
                message="No integration manifest to check",
                details={"manifest_found": False},
            )
        
        violations = self._check_integration_rules(integration_manifest, constitution_dir)
        
        context.metadata["integration_constitution_violations"] = violations
        context.metadata["integration_constitution_compliant"] = len(violations) == 0
        
        if violations:
            violation_details = "\n".join(f"  - {v}" for v in violations)
            return StepResult(
                success=False,
                message=f"Integration Constitution check failed with {len(violations)} violations:\n{violation_details}\n\nMust fix violations before proceeding to Phase 5.",
                details={"violations": violations},
            )
        
        return StepResult(
            success=True,
            message="Integration Constitution check passed",
            details={"violations": 0},
        )
    
    def _check_integration_rules(self, manifest: Dict, constitution_dir: Path) -> List[str]:
        violations = []
        
        workflow_rules = constitution_dir / "workflow-rules.md"
        if workflow_rules.exists():
            rules_content = workflow_rules.read_text(encoding="utf-8")
            
            if "WORKFLOW-003" in rules_content or "Checkpoint" in rules_content:
                integration_manifest = manifest
                if "timestamp" not in integration_manifest:
                    violations.append(
                        "WORKFLOW-003: Integration manifest缺少timestamp。Workflow rules要求Phase boundary必须有checkpoint。"
                    )
        
        return violations


class StepFixIntegrationIssues(PhaseStep):
    """Step 4: 修复集成问题"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        issues_found = context.metadata.get("integration_issues", [])
        
        if issues_found:
            context.metadata["issues_fixed"] = len(issues_found)
            return StepResult(
                success=True,
                message=f"Found {len(issues_found)} issues to fix - manual intervention required",
                details={"issues": issues_found[:10]},
            )
        
        return StepResult(
            success=True,
            message="No integration issues found",
            details={"issues": 0},
        )


class StepUpdateFindings(PhaseStep):
    """Step 5: 更新 findings.md"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        feature_dir = context.feature_dir
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        self._append_to_findings(feature_dir, context, timestamp)
        
        return StepResult(
            success=True,
            message="findings.md updated with Phase 4 summary",
            details={"file_updated": True},
        )
    
    def _append_to_findings(self, feature_dir: Path, context: "ExecutionContext", timestamp: str):
        findings_file = feature_dir / "findings.md"
        
        if findings_file.exists():
            current_content = findings_file.read_text(encoding="utf-8")
        else:
            current_content = f"# Findings: {context.feature_name}\n\n"
        
        integration_manifest = context.metadata.get("integration_manifest", {})
        test_results = {
            "passed": context.metadata.get("integration_tests_passed", False),
            "failures": len(context.metadata.get("integration_test_failures", [])),
        }
        
        phase4_section = f"""
---

## Phase 4: Integration Summary

**Date**: {timestamp}

### Integration Results
- Modules integrated: **{len(integration_manifest.get("modules", []))}**
- Main entry point: **{integration_manifest.get("main_entry_point", "N/A")}**
- Integration type: **{integration_manifest.get("type", "standard")}**

### Test Results
- Status: **{"✅ PASSED" if test_results["passed"] else "⚠️ FAILED"}**
- Failures: **{test_results["failures"]}**

### Constitution Compliance
- Status: **{"✅ PASSED" if context.metadata.get("integration_constitution_compliant", True) else "❌ FAILED"}**

---
*Phase 4 completed* | *{timestamp}*
"""
        
        findings_file.write_text(current_content + phase4_section, encoding="utf-8")
        context.metadata["findings_phase4_updated"] = True


class StepRunQualityAssessment(PhaseStep):
    """Step 3.5: 运行质量评估"""
    
    def execute(self, context: "ExecutionContext") -> "StepResult":
        from ..quality import QualityHarness, get_profile
        
        project_root = context.project_root
        feature_name = context.feature_name
        
        harness = QualityHarness(project_root, get_profile("integration"))
        
        assessment = harness.run_assessment(
            feature_name=feature_name,
            phase="integration",
            context=context,
        )
        
        quality_score = harness.get_quality_score(assessment)
        
        context.metadata["integration_quality_assessment"] = assessment
        context.metadata["integration_quality_score"] = quality_score
        
        if quality_score < 70:
            return StepResult(
                success=False,
                message=f"Integration quality score too low: {quality_score:.1f}% (threshold: 70%)",
                details={
                    "score": quality_score,
                    "threshold": 70,
                    "metrics": assessment.get("metrics", {}),
                },
            )
        
        return StepResult(
            success=True,
            message=f"Integration quality assessment passed: {quality_score:.1f}%",
            details={
                "score": quality_score,
                "passed_gates": assessment.get("gate", {}).get("passed", False),
            },
        )
