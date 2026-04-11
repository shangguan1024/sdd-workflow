"""
Quality Harness
主质量评估协调器
"""

from pathlib import Path
from typing import Dict, Any, List, Optional

from .collectors import (
    CodeMetricsCollector,
    TestCoverageCollector,
    ComplexityCollector,
    ConventionCollector,
)
from .gate_engine import GateEngine
from .reporter import QualityReporter
from .profile import QualityProfile


class QualityHarness:
    """
    Quality Harness
    
    职责:
    - 协调各 Collector 收集质量数据
    - 调用 GateEngine 评估质量 Gate
    - 生成质量报告
    - 提供质量评分
    """
    
    def __init__(self, project_root: Path, profile: Optional[QualityProfile] = None):
        self.project_root = project_root
        self.profile = profile or get_profile("standard")
        
        self.collectors = {
            "code_metrics": CodeMetricsCollector(project_root),
            "test_coverage": TestCoverageCollector(project_root),
            "complexity": ComplexityCollector(project_root),
            "convention": ConventionCollector(project_root),
        }
        
        self.gate_engine = GateEngine(project_root, self.profile)
        self.reporter = QualityReporter(project_root)
    
    def run_assessment(
        self,
        feature_name: str,
        phase: str,
        context: "ExecutionContext",
    ) -> Dict[str, Any]:
        """
        运行质量评估
        
        Args:
            feature_name: 特性名称
            phase: 当前 Phase
            context: 执行上下文
            
        Returns:
            评估结果字典
        """
        results = {}
        
        for name, collector in self.collectors.items():
            try:
                result = collector.collect(feature_name, context)
                results[name] = result
            except Exception as e:
                results[name] = {
                    "success": False,
                    "error": str(e),
                    "metrics": {},
                }
        
        gate_result = self.gate_engine.evaluate(phase, results)
        
        report = self.reporter.generate(
            feature_name=feature_name,
            phase=phase,
            collector_results=results,
            gate_result=gate_result,
        )
        
        return {
            "success": gate_result.passed,
            "metrics": results,
            "gate": gate_result,
            "report": report,
        }
    
    def run_phase_assessment(
        self,
        feature_name: str,
        phase: str,
        context: "ExecutionContext",
    ) -> Dict[str, Any]:
        """
        运行 Phase 级质量评估
        
        Args:
            feature_name: 特性名称
            phase: 当前 Phase
            context: 执行上下文
            
        Returns:
            Phase 评估结果
        """
        return self.run_assessment(feature_name, phase, context)
    
    def get_quality_score(self, results: Dict[str, Any]) -> float:
        """
        计算质量分数
        
        Args:
            results: 评估结果
            
        Returns:
            质量分数 (0-100)
        """
        total_weight = 0
        weighted_sum = 0
        
        for collector_name, result in results.get("metrics", {}).items():
            if not result.get("success", False):
                continue
            
            weight = self.profile.get_weight(collector_name)
            score = result.get("score", 0)
            
            weighted_sum += weight * score
            total_weight += weight
        
        if total_weight == 0:
            return 0
        
        return weighted_sum / total_weight
    
    def add_collector(self, name: str, collector):
        """添加自定义 Collector"""
        self.collectors[name] = collector
    
    def remove_collector(self, name: str):
        """移除 Collector"""
        if name in self.collectors:
            del self.collectors[name]
    
    def set_profile(self, profile: QualityProfile):
        """设置质量配置"""
        self.profile = profile
        self.gate_engine.profile = profile
