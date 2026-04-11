"""
Quality Reporter
质量报告生成器
"""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class QualityReporter:
    """
    质量报告生成器
    
    职责:
    - 生成 Markdown 格式质量报告
    - 保存报告到文件
    - 提供摘要信息
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def generate(
        self,
        feature_name: str,
        phase: str,
        collector_results: Dict[str, Any],
        gate_result: "GateResult",
    ) -> str:
        """
        生成质量报告
        
        Args:
            feature_name: 特性名称
            phase: 当前 Phase
            collector_results: Collector 结果
            gate_result: Gate 评估结果
            
        Returns:
            Markdown 格式报告
        """
        report_lines = [
            f"# Quality Report: {feature_name}",
            f"\n**Phase:** {phase}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\n---\n",
            f"\n## Summary",
            f"\n**Status:** {'✅ PASSED' if gate_result.passed else '❌ FAILED'}",
            f"\n**Message:** {gate_result.message}",
        ]
        
        report_lines.extend(self._generate_metrics_section(collector_results))
        report_lines.extend(self._generate_gate_details(gate_result))
        
        report = "\n".join(report_lines)
        
        self._save_report(feature_name, phase, report)
        
        return report
    
    def _generate_metrics_section(self, results: Dict[str, Any]) -> list:
        """生成指标部分"""
        lines = [
            "\n---\n",
            "\n## Metrics",
            "\n| Collector | Score | Status |",
            "|------------|-------|--------|",
        ]
        
        for name, result in results.items():
            score = result.get("score", 0)
            status = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
            lines.append(f"| {name} | {score:.1f}% | {status} |")
        
        return lines
    
    def _generate_gate_details(self, gate_result: "GateResult") -> list:
        """生成 Gate 详情"""
        lines = [
            "\n---\n",
            "\n## Gate Details",
        ]
        
        if "gate_results" in gate_result.details:
            for gr in gate_result.details["gate_results"]:
                status = "✅" if gr["passed"] else "❌"
                lines.append(f"\n### {status} {gr['name']}")
                lines.append(f"\n{gr['message']}")
        
        return lines
    
    def _save_report(self, feature_name: str, phase: str, report: str):
        """保存报告到文件"""
        report_dir = self.project_root / "docs" / "features" / feature_name / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"quality_report_{phase}_{timestamp}.md"
        
        report_file.write_text(report, encoding="utf-8")
    
    def generate_summary(
        self,
        feature_name: str,
        overall_score: float,
        gate_passed: bool,
    ) -> Dict[str, Any]:
        """
        生成摘要信息
        
        Args:
            feature_name: 特性名称
            overall_score: 总体分数
            gate_passed: Gate 是否通过
            
        Returns:
            摘要字典
        """
        return {
            "feature_name": feature_name,
            "overall_score": overall_score,
            "gate_passed": gate_passed,
            "timestamp": datetime.now().isoformat(),
            "grade": self._score_to_grade(overall_score),
        }
    
    def _score_to_grade(self, score: float) -> str:
        """分数转等级"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
