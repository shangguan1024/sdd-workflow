"""
SDD-Workflow 开发者模拟测试

使用子 agent 模拟开发者行为，测试工作流的问题
"""

import asyncio
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
import json


@dataclass
class SimulatedAction:
    phase: int
    action: str
    developer_decision: str
    ai_response: str
    timestamp: str
    issues: Optional[List[str]] = None


@dataclass
class TestIssue:
    severity: str  # critical, high, medium, low
    phase: int
    description: str
    suggestion: str


class DeveloperSimulator:
    """
    模拟开发者行为

    模拟场景：
    1. 开发者发起需求
    2. AI 执行 Phase 1-6
    3. 开发者做出决策
    4. 记录所有问题和异常
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.actions: list[SimulatedAction] = []
        self.issues: list[TestIssue] = []
        self.current_phase = 0
        self.feature_name = "test-feature"

    async def simulate_developer_start_feature(self):
        """模拟开发者开始一个特性"""
        print(f"\n{'=' * 60}")
        print(f"模拟开发者开始特性: {self.feature_name}")
        print(f"{'=' * 60}")

        # 模拟开发者输入需求
        developer_input = "添加一个自定义日志格式功能，支持用户自定义时间格式和字段"

        self.actions.append(
            SimulatedAction(
                phase=0,
                action="sdd start",
                developer_decision=developer_input,
                ai_response="开始执行 Phase 1: 需求分析",
                timestamp="2026-04-06T10:00:00Z",
                issues=[],
            )
        )

        print(f"\n开发者输入: {developer_input}")
        print(f"AI 响应: 开始执行 Phase 1: 需求分析")

        self.current_phase = 1

    async def simulate_phase_1(self):
        """模拟 Phase 1: 需求分析"""
        print(f"\n--- Phase 1: 需求分析 ---")

        # 模拟 AI 提问
        ai_questions = [
            "请问自定义日志格式的主要使用场景是什么？",
            "您希望支持哪些时间格式？",
            "是否需要支持结构化日志输出？",
        ]

        for q in ai_questions:
            print(f"\nAI: {q}")
            print("开发者: [模拟回答]")

        # 模拟开发者批准设计
        print(f"\n--- Phase 1 Gate ---")
        print("AI: 设计文档已生成，请审查")
        print("开发者: 查看设计文档...")

        # 检查设计文档是否存在
        design_path = (
            self.project_root / "docs" / "features" / self.feature_name / "specs"
        )
        if not design_path.exists():
            issue = TestIssue(
                severity="high",
                phase=1,
                description="Phase 1 完成后设计文档未生成",
                suggestion="检查 brainstorming skill 是否正确输出设计文档",
            )
            self.issues.append(issue)
            print(f"❌ 问题: {issue.description}")

        # 模拟开发者决策
        developer_decision = "Design approved, proceed to Phase 2"
        self.actions.append(
            SimulatedAction(
                phase=1,
                action="review design",
                developer_decision=developer_decision,
                ai_response="进入 Phase 2: 实现规划",
                timestamp="2026-04-06T10:15:00Z",
                issues=[],
            )
        )

        print(f"\n开发者决策: {developer_decision}")
        self.current_phase = 2

    async def simulate_phase_2(self):
        """模拟 Phase 2: 实现规划"""
        print(f"\n--- Phase 2: 实现规划 ---")

        print("AI: 正在生成实现计划...")

        # 检查计划文档
        plan_path = (
            self.project_root / "docs" / "features" / self.feature_name / "plans"
        )
        if not plan_path.exists():
            issue = TestIssue(
                severity="high",
                phase=2,
                description="Phase 2 完成后实现计划未生成",
                suggestion="检查 writing-plans skill 是否正确输出计划",
            )
            self.issues.append(issue)
            print(f"❌ 问题: {issue.description}")

        # 模拟开发者选择执行模式
        print(f"\n--- Phase 2 Gate ---")
        print("AI: 请选择执行模式: subagent-driven 或 sequential")

        developer_decision = "subagent-driven"
        self.actions.append(
            SimulatedAction(
                phase=2,
                action="select mode",
                developer_decision=developer_decision,
                ai_response="使用 subagent-driven 模式开始 Phase 3",
                timestamp="2026-04-06T10:30:00Z",
                issues=[],
            )
        )

        print(f"开发者决策: {developer_decision}")
        self.current_phase = 3

    async def simulate_phase_3(self):
        """模拟 Phase 3: 模块开发"""
        print(f"\n--- Phase 3: 模块开发 ---")

        print("AI: 开始执行任务...")

        # 模拟 LoopDetectionMiddleware
        edit_count = 0
        for i in range(1, 6):
            print(f"AI: Task {i}/5 执行中...")
            edit_count += 1

            if edit_count == 5:
                print("⚠️ LoopDetectionMiddleware: 已编辑 5 次，添加警告")
                issue = TestIssue(
                    severity="medium",
                    phase=3,
                    description="同一文件编辑次数达到警告阈值",
                    suggestion="检查 LoopDetectionMiddleware 是否正确触发",
                )
                self.issues.append(issue)

        # 检查 task_plan.md
        task_plan_path = (
            self.project_root / "docs" / "features" / self.feature_name / "task_plan.md"
        )
        if not task_plan_path.exists():
            issue = TestIssue(
                severity="high",
                phase=3,
                description="task_plan.md 未生成",
                suggestion="检查 planning-with-files skill 是否正确更新",
            )
            self.issues.append(issue)

        # 检查 progress.md
        progress_path = (
            self.project_root / "docs" / "features" / self.feature_name / "progress.md"
        )
        if not progress_path.exists():
            issue = TestIssue(
                severity="medium",
                phase=3,
                description="progress.md 未生成",
                suggestion="检查 planning-with-files skill 是否正确更新",
            )
            self.issues.append(issue)

        print(f"\n--- Phase 3 Gate ---")
        print("AI: 编译成功，单元测试通过")

        developer_decision = "Phase 3 complete, proceed to Phase 4"
        self.actions.append(
            SimulatedAction(
                phase=3,
                action="confirm build",
                developer_decision=developer_decision,
                ai_response="进入 Phase 4: 集成测试",
                timestamp="2026-04-06T11:00:00Z",
                issues=[],
            )
        )

        print(f"开发者决策: {developer_decision}")
        self.current_phase = 4

    async def simulate_phase_4(self):
        """模拟 Phase 4: 集成测试"""
        print(f"\n--- Phase 4: 集成测试 ---")

        print("AI: 运行集成测试...")
        print("⚠️ 测试环境问题: getrandom 依赖缺失")

        issue = TestIssue(
            severity="low",
            phase=4,
            description="测试被环境问题阻断",
            suggestion="检查 verification-before-completion skill 是否正确处理环境问题",
        )
        self.issues.append(issue)

        print(f"\n--- Phase 4 Gate ---")
        print("AI: 测试因环境问题无法运行")

        developer_decision = "Proceed despite test block"
        self.actions.append(
            SimulatedAction(
                phase=4,
                action="approve skip",
                developer_decision=developer_decision,
                ai_response="进入 Phase 5: 代码审查",
                timestamp="2026-04-06T11:15:00Z",
                issues=[],
            )
        )

        print(f"开发者决策: {developer_decision}")
        self.current_phase = 5

    async def simulate_phase_5(self):
        """模拟 Phase 5: 代码审查"""
        print(f"\n--- Phase 5: 代码审查 ---")

        print("AI: 正在生成审查制品...")

        # 检查 ArtifactCompleteMiddleware
        reviews_path = (
            self.project_root / "docs" / "features" / self.feature_name / "reviews"
        )
        required_reviews = [
            "architecture_review.md",
            "code_quality_review.md",
            "test_coverage_report.md",
            "requirements_verification.md",
        ]

        missing_reviews = []
        for r in required_reviews:
            if not (reviews_path / r).exists():
                missing_reviews.append(r)

        if missing_reviews:
            issue = TestIssue(
                severity="high",
                phase=5,
                description=f"Phase 5 缺少制品: {', '.join(missing_reviews)}",
                suggestion="检查 ArtifactCompleteMiddleware 是否正确生成制品",
            )
            self.issues.append(issue)
            print(f"❌ 问题: {issue.description}")
        else:
            print("✅ 所有 4 个审查制品已生成")

        print(f"\n--- Phase 5 Gate ---")
        print("AI: 请审查代码质量报告")

        developer_decision = "Phase 5 complete, proceed to Phase 6"
        self.actions.append(
            SimulatedAction(
                phase=5,
                action="review artifacts",
                developer_decision=developer_decision,
                ai_response="进入 Phase 6: 记忆持久化",
                timestamp="2026-04-06T11:30:00Z",
                issues=[],
            )
        )

        print(f"开发者决策: {developer_decision}")
        self.current_phase = 6

    async def simulate_phase_6(self):
        """模拟 Phase 6: 记忆持久化"""
        print(f"\n--- Phase 6: 记忆持久化 ---")

        print("AI: 自动更新项目状态...")

        # 检查 PROJECT_STATE.md
        project_state = self.project_root / "PROJECT_STATE.md"
        if not project_state.exists():
            issue = TestIssue(
                severity="high",
                phase=6,
                description="PROJECT_STATE.md 未更新",
                suggestion="检查 Phase 6 是否正确更新项目状态",
            )
            self.issues.append(issue)

        # 检查 AGENTS.md
        agents_md = self.project_root / "AGENTS.md"
        if not agents_md.exists():
            issue = TestIssue(
                severity="medium",
                phase=6,
                description="AGENTS.md 未更新",
                suggestion="检查 Phase 6 是否正确更新 AI 上下文",
            )
            self.issues.append(issue)

        print("✅ Phase 6 完成")

        self.actions.append(
            SimulatedAction(
                phase=6,
                action="complete",
                developer_decision="N/A",
                ai_response="SDD Workflow 完成",
                timestamp="2026-04-06T11:35:00Z",
                issues=[],
            )
        )

    async def run_full_simulation(self):
        """运行完整模拟"""
        print("\n" + "=" * 60)
        print("SDD-Workflow 开发者模拟测试")
        print("=" * 60)

        await self.simulate_developer_start_feature()
        await self.simulate_phase_1()
        await self.simulate_phase_2()
        await self.simulate_phase_3()
        await self.simulate_phase_4()
        await self.simulate_phase_5()
        await self.simulate_phase_6()

        self.print_summary()

    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "=" * 60)
        print("测试结果摘要")
        print("=" * 60)

        print(f"\n执行的动作数: {len(self.actions)}")

        if self.issues:
            print(f"\n发现的问题数: {len(self.issues)}")

            # 按严重程度分组
            by_severity = {"critical": [], "high": [], "medium": [], "low": []}
            for issue in self.issues:
                by_severity[issue.severity].append(issue)

            for severity in ["critical", "high", "medium", "low"]:
                issues = by_severity[severity]
                if issues:
                    print(f"\n【{severity.upper()}】({len(issues)} 个)")
                    for i, issue in enumerate(issues, 1):
                        print(f"  {i}. Phase {issue.phase}: {issue.description}")
                        print(f"     建议: {issue.suggestion}")
        else:
            print("\n✅ 未发现问题")

        # 打印动作时间线
        print(f"\n--- 动作时间线 ---")
        for action in self.actions:
            print(
                f"Phase {action.phase}: {action.action} - {action.developer_decision[:30]}..."
            )

    def save_report(self, output_path: Path):
        """保存测试报告"""
        report = {
            "test_type": "developer_simulation",
            "feature": self.feature_name,
            "actions": [
                {
                    "phase": a.phase,
                    "action": a.action,
                    "developer_decision": a.developer_decision,
                    "ai_response": a.ai_response,
                    "timestamp": a.timestamp,
                    "issues": a.issues,
                }
                for a in self.actions
            ],
            "issues": [
                {
                    "severity": i.severity,
                    "phase": i.phase,
                    "description": i.description,
                    "suggestion": i.suggestion,
                }
                for i in self.issues
            ],
        }

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n报告已保存到: {output_path}")


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="SDD-Workflow 开发者模拟测试")
    parser.add_argument("--project", type=str, required=True, help="项目根目录路径")
    parser.add_argument("--output", type=str, help="报告输出路径")
    args = parser.parse_args()

    project_root = Path(args.project)
    if not project_root.exists():
        print(f"错误: 项目目录不存在: {project_root}")
        sys.exit(1)

    simulator = DeveloperSimulator(project_root)
    await simulator.run_full_simulation()

    if args.output:
        simulator.save_report(Path(args.output))


if __name__ == "__main__":
    asyncio.run(main())
