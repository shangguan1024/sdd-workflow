"""
SDD-Workflow 测试脚本

用于验证工作流的完整性和正确性
"""

import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import yaml


@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    details: str = ""


class SDDWorkflowTester:
    """SDD-Workflow 工作流测试器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results: list[TestResult] = []

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("SDD-Workflow 测试开始")
        print("=" * 60)

        tests = [
            ("目录结构测试", self.test_directory_structure),
            ("初始化测试", self.test_initialization),
            ("特性目录创建测试", self.test_feature_directory_creation),
            ("Phase 产物测试", self.test_phase_artifacts),
            ("Constitution 检查测试", self.test_constitution_enforcer),
            ("制品完整性测试", self.test_artifact_completeness),
            ("状态聚合测试", self.test_status_aggregation),
            ("多特性隔离测试", self.test_multi_feature_isolation),
        ]

        for name, test_fn in tests:
            print(f"\n[测试] {name}...")
            try:
                result = test_fn()
                self.results.append(result)
                if result.passed:
                    print(f"  ✅ 通过: {result.message}")
                else:
                    print(f"  ❌ 失败: {result.message}")
            except Exception as e:
                result = TestResult(
                    name=name, passed=False, message=f"测试异常: {str(e)}", details=""
                )
                self.results.append(result)
                print(f"  ❌ 异常: {str(e)}")

        return self.results

    def test_directory_structure(self) -> TestResult:
        """测试目录结构是否符合规范"""
        expected_dirs = [
            "CONSTITUTION",
            ".nexus-map",
            "docs/knowledge",
            "docs/modules",
            "docs/features",
            "docs/collaboration",
        ]

        missing = []
        for d in expected_dirs:
            if not (self.project_root / d).exists():
                missing.append(d)

        if missing:
            return TestResult(
                name="目录结构测试",
                passed=False,
                message=f"缺少目录: {', '.join(missing)}",
            )

        return TestResult(name="目录结构测试", passed=True, message="所有必需目录存在")

    def test_initialization(self) -> TestResult:
        """测试项目初始化"""
        required_files = [
            "PROJECT_STATE.md",
            "AGENTS.md",
            "CONSTITUTION/core.md",
        ]

        missing = []
        for f in required_files:
            if not (self.project_root / f).exists():
                missing.append(f)

        if missing:
            return TestResult(
                name="初始化测试",
                passed=False,
                message=f"缺少文件: {', '.join(missing)}",
            )

        return TestResult(name="初始化测试", passed=True, message="初始化文件完整")

    def test_feature_directory_creation(self) -> TestResult:
        """测试特性目录创建"""
        features_dir = self.project_root / "docs" / "features"

        if not features_dir.exists():
            return TestResult(
                name="特性目录创建测试", passed=False, message="features 目录不存在"
            )

        feature_dirs = list(features_dir.iterdir())
        if not feature_dirs:
            return TestResult(
                name="特性目录创建测试", passed=False, message="没有找到任何特性目录"
            )

        # 检查第一个特性目录结构
        feature_dir = feature_dirs[0]
        required_feature_files = [
            "status.toml",
            "task_plan.md",
            "findings.md",
            "progress.md",
        ]

        missing = []
        for f in required_feature_files:
            if not (feature_dir / f).exists():
                missing.append(f)

        if missing:
            return TestResult(
                name="特性目录创建测试",
                passed=False,
                message=f"特性 {feature_dir.name} 缺少: {', '.join(missing)}",
            )

        return TestResult(
            name="特性目录创建测试",
            passed=True,
            message=f"特性目录 {feature_dir.name} 结构正确",
        )

    def test_phase_artifacts(self) -> TestResult:
        """测试 Phase 产物"""
        features_dir = self.project_root / "docs" / "features"
        feature_dirs = list(features_dir.iterdir())

        if not feature_dirs:
            return TestResult(
                name="Phase 产物测试", passed=False, message="没有特性目录"
            )

        issues = []
        for feature_dir in feature_dirs:
            if not feature_dir.is_dir():
                continue

            # Phase 1: specs/
            specs_dir = feature_dir / "specs"
            if not specs_dir.exists() or not list(specs_dir.glob("*.md")):
                issues.append(f"{feature_dir.name}/specs/ 缺失或为空")

            # Phase 2: plans/
            plans_dir = feature_dir / "plans"
            if not plans_dir.exists() or not list(plans_dir.glob("*.md")):
                issues.append(f"{feature_dir.name}/plans/ 缺失或为空")

            # Phase 5: reviews/
            reviews_dir = feature_dir / "reviews"
            if not reviews_dir.exists():
                issues.append(f"{feature_dir.name}/reviews/ 缺失")

        if issues:
            return TestResult(
                name="Phase 产物测试", passed=False, message="; ".join(issues)
            )

        return TestResult(
            name="Phase 产物测试", passed=True, message="所有 Phase 产物存在"
        )

    def test_constitution_enforcer(self) -> TestResult:
        """测试 ConstitutionEnforcer 配置"""
        # 优先使用 sdd-workflow 目录下的配置
        skill_dir = Path(__file__).parent.parent
        config_path = skill_dir / "config" / "constitution_enforcer.yaml"

        if not config_path.exists():
            # 回退到项目根目录
            config_path = self.project_root / "config" / "constitution_enforcer.yaml"

        if not config_path.exists():
            return TestResult(
                name="Constitution 检查测试",
                passed=False,
                message="constitution_enforcer.yaml 不存在",
            )

        if not config_path.exists():
            return TestResult(
                name="Constitution 检查测试",
                passed=False,
                message="constitution_enforcer.yaml 不存在",
            )

        with open(config_path) as f:
            config = yaml.safe_load(f)

        design_rules = config.get("enforcer", {}).get("design_rules", [])
        impl_rules = config.get("enforcer", {}).get("implementation_rules", [])

        if not design_rules:
            return TestResult(
                name="Constitution 检查测试", passed=False, message="没有设计规则"
            )

        return TestResult(
            name="Constitution 检查测试",
            passed=True,
            message=f"包含 {len(design_rules)} 个设计规则, {len(impl_rules)} 个实现规则",
        )

    def test_artifact_completeness(self) -> TestResult:
        """测试制品完整性"""
        features_dir = self.project_root / "docs" / "features"
        feature_dirs = list(features_dir.iterdir())

        required_reviews = [
            "architecture_review.md",
            "code_quality_review.md",
            "test_coverage_report.md",
            "requirements_verification.md",
        ]

        issues = []
        for feature_dir in feature_dirs:
            if not feature_dir.is_dir():
                continue

            reviews_dir = feature_dir / "reviews"
            for review_file in required_reviews:
                if not (reviews_dir / review_file).exists():
                    issues.append(f"{feature_dir.name}/{review_file} 缺失")

        if issues:
            return TestResult(
                name="制品完整性测试", passed=False, message="; ".join(issues)
            )

        return TestResult(
            name="制品完整性测试",
            passed=True,
            message=f"所有 {len(feature_dirs)} 个特性的制品完整",
        )

    def test_status_aggregation(self) -> TestResult:
        """测试状态聚合"""
        project_state = self.project_root / "PROJECT_STATE.md"

        if not project_state.exists():
            return TestResult(
                name="状态聚合测试", passed=False, message="PROJECT_STATE.md 不存在"
            )

        content = project_state.read_text()

        # 检查是否包含特性信息
        features_dir = self.project_root / "docs" / "features"
        feature_names = [d.name for d in features_dir.iterdir() if d.is_dir()]

        missing_features = []
        for name in feature_names:
            if name not in content:
                missing_features.append(name)

        if missing_features:
            return TestResult(
                name="状态聚合测试",
                passed=False,
                message=f"PROJECT_STATE.md 缺少: {', '.join(missing_features)}",
            )

        return TestResult(
            name="状态聚合测试",
            passed=True,
            message="PROJECT_STATE.md 正确聚合所有特性",
        )

    def test_multi_feature_isolation(self) -> TestResult:
        """测试多特性隔离"""
        features_dir = self.project_root / "docs" / "features"
        feature_dirs = [d for d in features_dir.iterdir() if d.is_dir()]

        if len(feature_dirs) < 2:
            return TestResult(
                name="多特性隔离测试",
                passed=True,
                message="只有单个特性，跳过多特性测试",
            )

        # 检查每个特性的 task_plan.md 内容是否独立
        task_plans = {}
        for feature_dir in feature_dirs:
            task_plan = feature_dir / "task_plan.md"
            if task_plan.exists():
                task_plans[feature_dir.name] = task_plan.read_text()[:100]

        # 简单的隔离检查：不同特性的 task_plan 应该内容不同
        unique_contents = set(task_plans.values())
        if len(unique_contents) < len(task_plans):
            return TestResult(
                name="多特性隔离测试", passed=False, message="特性之间可能存在内容重复"
            )

        return TestResult(
            name="多特性隔离测试",
            passed=True,
            message=f"{len(feature_dirs)} 个特性隔离正确",
        )

    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "=" * 60)
        print("测试结果摘要")
        print("=" * 60)

        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)

        print(f"\n通过: {passed}/{len(self.results)}")
        print(f"失败: {failed}/{len(self.results)}")

        if failed > 0:
            print("\n失败测试:")
            for r in self.results:
                if not r.passed:
                    print(f"  ❌ {r.name}: {r.message}")

        return failed == 0


def create_mock_project(root: Path) -> Path:
    """创建模拟项目用于测试"""

    # 创建目录结构
    dirs = [
        "CONSTITUTION",
        ".nexus-map",
        "docs/knowledge",
        "docs/modules",
        "docs/features/mock-feature",
        "docs/collaboration",
    ]

    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)

    # 创建 Constitution 文件
    (root / "CONSTITUTION" / "core.md").write_text("# Core Principles\n")
    (root / "CONSTITUTION" / "design-rules.md").write_text("# Design Rules\n")
    (root / "CONSTITUTION" / "implementation-rules.md").write_text(
        "# Implementation Rules\n"
    )

    # 创建初始化文件
    (root / "PROJECT_STATE.md").write_text(
        "# Project State\n\n## Features\n- mock-feature: Phase 6\n"
    )
    (root / "AGENTS.md").write_text("# AGENTS.md\n")

    # 创建模拟特性
    feature_dir = root / "docs" / "features" / "mock-feature"

    # status.toml
    (feature_dir / "status.toml").write_text("""[feature]
name = "mock-feature"
developer = "@testuser"
current_phase = 6
""")

    # task_plan.md
    (feature_dir / "task_plan.md").write_text(
        "# Task Plan for mock-feature\n- Task 1: Done\n- Task 2: Done\n"
    )

    # findings.md
    (feature_dir / "findings.md").write_text("# Findings for mock-feature\n")

    # progress.md
    (feature_dir / "progress.md").write_text("# Progress for mock-feature\n")

    # specs/
    (feature_dir / "specs").mkdir(exist_ok=True)
    (feature_dir / "specs" / "2026-04-06-mock-feature-design.md").write_text(
        "# Design\n"
    )

    # plans/
    (feature_dir / "plans").mkdir(exist_ok=True)
    (feature_dir / "plans" / "2026-04-06-mock-feature.md").write_text("# Plan\n")

    # reviews/
    (feature_dir / "reviews").mkdir(exist_ok=True)
    (feature_dir / "reviews" / "architecture_review.md").write_text(
        "# Architecture Review\n"
    )
    (feature_dir / "reviews" / "code_quality_review.md").write_text(
        "# Code Quality Review\n"
    )
    (feature_dir / "reviews" / "test_coverage_report.md").write_text(
        "# Test Coverage Report\n"
    )
    (feature_dir / "reviews" / "requirements_verification.md").write_text(
        "# Requirements Verification\n"
    )

    return root


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="SDD-Workflow 测试脚本")
    parser.add_argument("--project", type=str, help="项目根目录路径")
    parser.add_argument("--mock", action="store_true", help="使用模拟项目测试")
    args = parser.parse_args()

    if args.mock:
        # 创建临时目录进行测试
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "mock-project"
            project_root.mkdir()
            create_mock_project(project_root)

            print(f"模拟项目创建于: {project_root}")

            tester = SDDWorkflowTester(project_root)
            tester.run_all_tests()
            success = tester.print_summary()

            sys.exit(0 if success else 1)
    elif args.project:
        project_root = Path(args.project)
        if not project_root.exists():
            print(f"错误: 项目目录不存在: {project_root}")
            sys.exit(1)

        tester = SDDWorkflowTester(project_root)
        tester.run_all_tests()
        success = tester.print_summary()

        sys.exit(0 if success else 1)
    else:
        # 检查 sdd-workflow 目录本身
        skill_dir = Path(__file__).parent.parent
        config_dir = skill_dir / "config"

        print("检查 sdd-workflow 目录...")

        results = []

        # 检查配置文件
        config_files = [
            "constitution_enforcer.yaml",
            "artifact_checker.yaml",
            "loop_detection.yaml",
            "context_loader.yaml",
            "trace_analysis.yaml",
        ]

        print("\n配置文件检查:")
        for f in config_files:
            path = config_dir / f
            if path.exists():
                print(f"  ✅ {f}")
            else:
                print(f"  ❌ {f} 缺失")
                results.append(False)

        # 检查脚本
        scripts_dir = skill_dir / "scripts"
        script_files = [
            "constitution_enforcer.py",
            "artifact_checker.py",
            "context_loader.py",
            "trace_collector.py",
        ]

        print("\n脚本文件检查:")
        for f in script_files:
            path = scripts_dir / f
            if path.exists():
                print(f"  ✅ {f}")
            else:
                print(f"  ❌ {f} 缺失")
                results.append(False)

        # 检查 middleware
        middleware_dir = skill_dir / "middleware"
        middleware_files = ["__init__.py"]

        print("\nMiddleware 检查:")
        for f in middleware_files:
            path = middleware_dir / f
            if path.exists():
                print(f"  ✅ {f}")
            else:
                print(f"  ❌ {f} 缺失")
                results.append(False)

        sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
