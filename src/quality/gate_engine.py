"""
Gate Engine
质量 Gate 评估引擎
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod


class Gate(ABC):
    """Gate 基类"""
    
    def __init__(self, name: str, threshold: float):
        self.name = name
        self.threshold = threshold
    
    @abstractmethod
    def evaluate(self, metrics: Dict[str, Any]) -> "GateResult":
        """评估 Gate"""
        pass


class GateResult:
    """Gate 评估结果"""
    
    def __init__(
        self,
        passed: bool,
        gate_name: str,
        message: str = "",
        details: Dict[str, Any] = None,
    ):
        self.passed = passed
        self.gate_name = gate_name
        self.message = message
        self.details = details or {}


class CodeQualityGate(Gate):
    """代码质量 Gate"""
    
    def evaluate(self, metrics: Dict[str, Any]) -> GateResult:
        """评估代码质量"""
        code_metrics = metrics.get("code_metrics", {})
        convention = metrics.get("convention", {})
        
        score = code_metrics.get("score", 0)
        convention_score = convention.get("score", 0)
        
        avg_score = (score + convention_score) / 2
        
        passed = avg_score >= self.threshold
        
        return GateResult(
            passed=passed,
            gate_name=self.name,
            message=f"Code quality: {avg_score:.1f}% (threshold: {self.threshold}%)",
            details={
                "code_score": score,
                "convention_score": convention_score,
                "threshold": self.threshold,
            },
        )


class TestCoverageGate(Gate):
    """测试覆盖率 Gate"""
    
    def evaluate(self, metrics: Dict[str, Any]) -> GateResult:
        """评估测试覆盖率"""
        coverage = metrics.get("test_coverage", {})
        
        coverage_percent = coverage.get("metrics", {}).get("coverage_percent", 0)
        
        passed = coverage_percent >= self.threshold
        
        return GateResult(
            passed=passed,
            gate_name=self.name,
            message=f"Test coverage: {coverage_percent:.1f}% (threshold: {self.threshold}%)",
            details={
                "coverage_percent": coverage_percent,
                "threshold": self.threshold,
            },
        )


class ComplexityGate(Gate):
    """复杂度 Gate"""
    
    def evaluate(self, metrics: Dict[str, Any]) -> GateResult:
        """评估代码复杂度"""
        complexity = metrics.get("complexity", {})
        
        avg_complexity = complexity.get("metrics", {}).get("avg_complexity", 0)
        
        passed = avg_complexity <= self.threshold
        
        return GateResult(
            passed=passed,
            gate_name=self.name,
            message=f"Avg complexity: {avg_complexity:.1f} (threshold: {self.threshold})",
            details={
                "avg_complexity": avg_complexity,
                "threshold": self.threshold,
            },
        )


class GateEngine:
    """
    Gate 评估引擎
    
    职责:
    - 管理 Gate 列表
    - 协调 Gate 评估
    - 汇总评估结果
    """
    
    def __init__(self, project_root: Path, profile: "QualityProfile"):
        self.project_root = project_root
        self.profile = profile
        self.gates: List[Gate] = []
        self._init_gates()
    
    def _init_gates(self):
        """初始化 Gates"""
        self.gates = [
            CodeQualityGate("code_quality", self.profile.get_threshold("code_quality")),
            TestCoverageGate("test_coverage", self.profile.get_threshold("test_coverage")),
            ComplexityGate("complexity", self.profile.get_threshold("complexity")),
        ]
    
    def evaluate(
        self,
        phase: str,
        metrics: Dict[str, Any],
    ) -> GateResult:
        """
        评估所有 Gate
        
        Args:
            phase: 当前 Phase
            metrics: 指标数据
            
        Returns:
            Gate 评估结果
        """
        phase_gates = self._get_gates_for_phase(phase)
        
        if not phase_gates:
            return GateResult(
                passed=True,
                gate_name="default",
                message="No gates defined for this phase",
            )
        
        all_passed = True
        results = []
        
        for gate in phase_gates:
            result = gate.evaluate(metrics)
            results.append(result)
            if not result.passed:
                all_passed = False
        
        failed_gates = [r.gate_name for r in results if not r.passed]
        
        return GateResult(
            passed=all_passed,
            gate_name="phase_gate",
            message="All gates passed" if all_passed else f"Failed gates: {', '.join(failed_gates)}",
            details={
                "phase": phase,
                "gate_results": [
                    {"name": r.gate_name, "passed": r.passed, "message": r.message}
                    for r in results
                ],
            },
        )
    
    def _get_gates_for_phase(self, phase: str) -> List[Gate]:
        """获取 Phase 对应的 Gate"""
        if phase in ["development", "integration"]:
            return self.gates
        elif phase == "review":
            return [g for g in self.gates if g.name != "complexity"]
        else:
            return []
    
    def add_gate(self, gate: Gate):
        """添加 Gate"""
        self.gates.append(gate)
    
    def remove_gate(self, gate_name: str):
        """移除 Gate"""
        self.gates = [g for g in self.gates if g.name != gate_name]
