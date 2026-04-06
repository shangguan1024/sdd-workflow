"""
ConstitutionEnforcer: 自动检查设计/计划/代码是否符合 Constitution
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable
import re
import yaml


@dataclass
class Violation:
    rule_id: str
    rule_name: str
    description: str
    location: str
    suggestion: str


@dataclass
class CheckResult:
    passed: bool
    violations: list[Violation] = field(default_factory=list)


class Rule:
    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        severity: str,
        check_fn: Callable[[str], list[Violation]],
    ):
        self.id = rule_id
        self.name = name
        self.description = description
        self.severity = severity
        self.check_fn = check_fn

    def evaluate(self, content: str) -> CheckResult:
        violations = self.check_fn(content)
        return CheckResult(passed=len(violations) == 0, violations=violations)


class ConstitutionEnforcer:
    def __init__(self, constitution_dir: Path, config_path: Path | None = None):
        self.constitution_dir = constitution_dir
        self.config_path = (
            config_path
            or Path(__file__).parent.parent / "config" / "constitution_enforcer.yaml"
        )
        self.config = self._load_config()
        self.design_rules = self._load_design_rules()
        self.implementation_rules = self._load_implementation_rules()

    def _load_config(self) -> dict:
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return {
            "enforcer": {
                "enabled": True,
                "design_rules": [],
                "implementation_rules": [],
            }
        }

    def check_design(self, design_content: str) -> CheckResult:
        """检查设计文档是否符合 Constitution"""
        all_violations = []

        for rule in self.design_rules:
            if not rule.severity or rule.severity == "disabled":
                continue
            result = rule.evaluate(design_content)
            all_violations.extend(result.violations)

        return CheckResult(passed=len(all_violations) == 0, violations=all_violations)

    def check_plan(self, plan_content: str) -> CheckResult:
        """检查实现计划是否符合 Constitution"""
        all_violations = []

        for rule in self.implementation_rules:
            if not rule.severity or rule.severity == "disabled":
                continue
            result = rule.evaluate(plan_content)
            all_violations.extend(result.violations)

        return CheckResult(passed=len(all_violations) == 0, violations=all_violations)

    def check_code(self, code_content: str) -> CheckResult:
        """检查代码是否符合 Constitution"""
        return self.check_plan(code_content)

    def _load_design_rules(self) -> list[Rule]:
        rules = []

        config_rules = self.config.get("enforcer", {}).get("design_rules", [])

        for cfg in config_rules:
            rule_id = cfg.get("id", "")

            if rule_id == "DESIGN-001":
                rules.append(
                    Rule(
                        rule_id="DESIGN-001",
                        name=cfg.get("name", "单一职责"),
                        description=cfg.get("description", ""),
                        severity=cfg.get("severity", "error"),
                        check_fn=self._check_single_responsibility,
                    )
                )
            elif rule_id == "DESIGN-002":
                rules.append(
                    Rule(
                        rule_id="DESIGN-002",
                        name=cfg.get("name", "接口分离"),
                        description=cfg.get("description", ""),
                        severity=cfg.get("severity", "warning"),
                        check_fn=self._create_interface_check(cfg.get("threshold", 10)),
                    )
                )
            elif rule_id == "DESIGN-003":
                rules.append(
                    Rule(
                        rule_id="DESIGN-003",
                        name=cfg.get("name", "依赖方向"),
                        description=cfg.get("description", ""),
                        severity=cfg.get("severity", "error"),
                        check_fn=self._check_dependency_direction,
                    )
                )
            elif rule_id == "DESIGN-004":
                rules.append(
                    Rule(
                        rule_id="DESIGN-004",
                        name=cfg.get("name", "循环依赖"),
                        description=cfg.get("description", ""),
                        severity=cfg.get("severity", "error"),
                        check_fn=self._check_no_circular_dependency,
                    )
                )
            elif rule_id == "DESIGN-005":
                rules.append(
                    Rule(
                        rule_id="DESIGN-005",
                        name=cfg.get("name", "公开 API 文档化"),
                        description=cfg.get("description", ""),
                        severity=cfg.get("severity", "warning"),
                        check_fn=self._check_api_documented,
                    )
                )

        return rules

    def _load_implementation_rules(self) -> list[Rule]:
        rules = []

        config_rules = self.config.get("enforcer", {}).get("implementation_rules", [])

        for cfg in config_rules:
            rule_id = cfg.get("id", "")

            if rule_id == "IMPL-001":
                rules.append(
                    Rule(
                        rule_id="IMPL-001",
                        name=cfg.get("name", "错误处理"),
                        description=cfg.get("description", ""),
                        severity=cfg.get("severity", "error"),
                        check_fn=self._check_error_handling,
                    )
                )
            elif rule_id == "IMPL-002":
                rules.append(
                    Rule(
                        rule_id="IMPL-002",
                        name=cfg.get("name", "无裸 await"),
                        description=cfg.get("description", ""),
                        severity=cfg.get("severity", "error"),
                        check_fn=self._check_no_bare_await,
                    )
                )
            elif rule_id == "IMPL-003":
                rules.append(
                    Rule(
                        rule_id="IMPL-003",
                        name=cfg.get("name", "测试覆盖"),
                        description=cfg.get("description", ""),
                        severity=cfg.get("severity", "warning"),
                        check_fn=self._check_test_coverage,
                    )
                )
            elif rule_id == "IMPL-004":
                rules.append(
                    Rule(
                        rule_id="IMPL-004",
                        name=cfg.get("name", "日志规范"),
                        description=cfg.get("description", ""),
                        severity=cfg.get("severity", "error"),
                        check_fn=self._create_logging_check(
                            cfg.get("sensitive_patterns", [])
                        ),
                    )
                )

        return rules

    def _check_single_responsibility(self, content: str) -> list[Violation]:
        violations = []

        module_patterns = [
            r"Module\s+(\w+)\s+handles?\s+(.+?)(?=\nModule|\Z)",
        ]

        for pattern in module_patterns:
            for match in re.finditer(pattern, content, re.DOTALL | re.IGNORECASE):
                module_name = match.group(1)
                responsibilities = match.group(2)

                handles_parts = re.split(r"\band\b|,|;", responsibilities)
                handles_count = len([p for p in handles_parts if p.strip()])

                if handles_count > 2:
                    violations.append(
                        Violation(
                            rule_id="DESIGN-001",
                            rule_name="单一职责",
                            description=f"Module {module_name} 负责 {handles_count} 个不同领域",
                            location=f"Module {module_name} definition",
                            suggestion="拆分模块，每个模块只负责一个功能领域",
                        )
                    )

        return violations

    def _create_interface_check(self, threshold: int):
        def check(content: str) -> list[Violation]:
            violations = []

            interface_pattern = r"(?:interface|trait|class)\s+(\w+)[^{]*?{([^}]+)}"

            for match in re.finditer(interface_pattern, content, re.DOTALL):
                interface_name = match.group(1)
                body = match.group(2)

                method_count = len(re.findall(r"(?:fn|def|func|method)\s+\w+", body))

                if method_count > threshold:
                    violations.append(
                        Violation(
                            rule_id="DESIGN-002",
                            rule_name="接口分离",
                            description=f"{interface_name} 包含 {method_count} 个方法，超过阈值 {threshold}",
                            location=f"{interface_name} definition",
                            suggestion=f"将 {interface_name} 拆分为多个小接口",
                        )
                    )

            return violations

        return check

    def _check_dependency_direction(self, content: str) -> list[Violation]:
        violations = []

        direct_dep_pattern = (
            r"(\w+)\s+(?:depends on|imports|uses)\s+(\w+)(?:Direct|Impl)"
        )

        for match in re.finditer(direct_dep_pattern, content, re.IGNORECASE):
            from_module = match.group(1)
            to_module = match.group(2)

            violations.append(
                Violation(
                    rule_id="DESIGN-003",
                    rule_name="依赖方向",
                    description=f"{from_module} 直接依赖 {to_module} 的具体实现",
                    location=f"{from_module} depends on {to_module}",
                    suggestion=f"依赖抽象接口而非具体实现，使用 trait 或 interface",
                )
            )

        return violations

    def _check_no_circular_dependency(self, content: str) -> list[Violation]:
        violations = []

        deps = {}
        dep_pattern = r"(\w+)\s+(?:depends on|imports)\s+(\w+)"

        for match in re.finditer(dep_pattern, content, re.IGNORECASE):
            module = match.group(1)
            dep = match.group(2)
            deps.setdefault(module, []).append(dep)

        def has_cycle(node, visited, stack):
            visited.add(node)
            stack.add(node)

            for neighbor in deps.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, stack):
                        return True
                elif neighbor in stack:
                    return True

            stack.remove(node)
            return False

        visited = set()
        stack = set()

        for node in deps:
            if node not in visited:
                if has_cycle(node, visited, stack):
                    violations.append(
                        Violation(
                            rule_id="DESIGN-004",
                            rule_name="循环依赖",
                            description=f"检测到模块之间的循环依赖",
                            location=f"Module: {node}",
                            suggestion="使用 trait 抽象解耦，或将共享类型移到独立模块",
                        )
                    )

        return violations

    def _check_api_documented(self, content: str) -> list[Violation]:
        violations = []

        public_api_pattern = r"(?:pub\s+)?(?:fn|def|func)\s+(\w+)\s*\([^)]*\)"

        for match in re.finditer(public_api_pattern, content):
            func_name = match.group(1)
            func_start = match.start()

            context_start = max(0, func_start - 200)
            context = content[context_start:func_start]

            doc_pattern = r"(///|##|/\*\*|///)"
            if not re.search(doc_pattern, context):
                violations.append(
                    Violation(
                        rule_id="DESIGN-005",
                        rule_name="公开 API 文档化",
                        description=f"函数 {func_name} 缺少文档说明",
                        location=f"Function: {func_name}",
                        suggestion=f"为 {func_name} 添加文档注释",
                    )
                )

        return violations

    def _check_error_handling(self, content: str) -> list[Violation]:
        violations = []

        func_pattern = r"(?:pub\s+)?(?:fn|func)\s+(\w+)\s*\([^)]*\)\s*->\s*(\w+)"

        for match in re.finditer(func_pattern, content):
            func_name = match.group(1)
            return_type = match.group(2)

            if return_type not in ["Result", "Option", "()", "void", "None", "void"]:
                if not return_type.startswith("Vec") and not return_type.startswith(
                    "Option"
                ):
                    violations.append(
                        Violation(
                            rule_id="IMPL-001",
                            rule_name="错误处理",
                            description=f"函数 {func_name} 返回类型 {return_type} 不是 Result 或 Option",
                            location=f"Function: {func_name}",
                            suggestion=f"考虑返回 Result<T, E> 或 Option<T> 以正确处理错误",
                        )
                    )

        return violations

    def _check_no_bare_await(self, content: str) -> list[Violation]:
        violations = []

        bare_await_pattern = r"\.\s*await\s*(?!\()"

        for match in re.finditer(bare_await_pattern, content):
            violations.append(
                Violation(
                    rule_id="IMPL-002",
                    rule_name="无裸 await",
                    description="检测到可能的裸 await 表达式",
                    location=f"Position {match.start()}",
                    suggestion="确保 await 正确用于 Future，不应有额外操作符",
                )
            )

        return violations

    def _check_test_coverage(self, content: str) -> list[Violation]:
        violations = []

        test_pattern = r"#\[test\]|#\[cfg\(test\)\]|def test_|\.test\("
        tests_found = len(re.findall(test_pattern, content))

        func_pattern = r"(?:pub\s+)?(?:fn|func)\s+(\w+)\s*\("
        funcs_found = len(re.findall(func_pattern, content))

        if funcs_found > 5 and tests_found == 0:
            violations.append(
                Violation(
                    rule_id="IMPL-003",
                    rule_name="测试覆盖",
                    description=f"代码中有 {funcs_found} 个函数但没有找到测试",
                    location="Test coverage",
                    suggestion="为新功能添加对应的测试",
                )
            )

        return violations

    def _create_logging_check(self, sensitive_patterns: list):
        def check(content: str) -> list[Violation]:
            violations = []

            logging_pattern = r"(?:log|info|warn|error|debug|trace)\s*\([^)]+\)"

            for match in re.finditer(logging_pattern, content):
                log_call = match.group(0)

                for pattern in sensitive_patterns:
                    if re.search(pattern, log_call, re.IGNORECASE):
                        violations.append(
                            Violation(
                                rule_id="IMPL-004",
                                rule_name="日志规范",
                                description=f"日志中包含敏感关键词: {pattern}",
                                location=f"Log call: {log_call[:50]}...",
                                suggestion="不要在日志中记录敏感信息",
                            )
                        )
                        break

            return violations

        return check


class ViolationFormatter:
    @staticmethod
    def format(result: CheckResult) -> str:
        if result.passed:
            return "✅ Constitution 合规检查通过"

        lines = ["## ❌ Constitution 合规检查失败", ""]
        lines.append(f"发现 {len(result.violations)} 条违规:")
        lines.append("")

        for v in result.violations:
            lines.extend(
                [
                    f"### {v.rule_id}: {v.rule_name}",
                    f"**位置**: {v.location}",
                    f"**问题**: {v.description}",
                    f"**建议**: {v.suggestion}",
                    "",
                ]
            )

        lines.append("---")
        lines.append("**必须修复以上违规才能进入下一阶段**")

        return "\n".join(lines)
