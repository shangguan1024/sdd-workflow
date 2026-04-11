"""
Brainstorming Capability
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..director import ExecutionContext

from .base import Capability, CapabilityResult


class BrainstormingCapability(Capability):
    """
    Brainstorming Capability
    
    职责:
    - 探索问题空间
    - 生成潜在解决方案
    - 收集用户输入
    - 触发进一步分析
    """
    
    def __init__(self):
        super().__init__("brainstorming")
    
    def execute(self, context: "ExecutionContext") -> CapabilityResult:
        """执行 Brainstorming"""
        try:
            feature_name = context.feature_name
            
            ideas = self._generate_ideas(context)
            alternatives = self._explore_alternatives(context)
            
            context.metadata["brainstorming_executed"] = True
            context.metadata["brainstorming_ideas"] = ideas
            context.metadata["brainstorming_alternatives"] = alternatives
            
            return CapabilityResult(
                success=True,
                message=f"Brainstorming completed: {len(ideas)} ideas generated",
                artifacts={
                    "ideas": ideas,
                    "alternatives": alternatives,
                },
            )
        except Exception as e:
            return CapabilityResult(
                success=False,
                message=f"Brainstorming failed: {e}",
            )
    
    def _generate_ideas(self, context: "ExecutionContext") -> list:
        """生成想法"""
        ideas = []
        feature_name = context.feature_name
        
        ideas.append({
            "id": "idea-1",
            "title": f"Basic implementation for {feature_name}",
            "description": "Start with a simple, straightforward implementation",
            "complexity": "low",
            "risk": "low",
        })
        
        ideas.append({
            "id": "idea-2",
            "title": f"Modular architecture for {feature_name}",
            "description": "Design with separation of concerns in mind",
            "complexity": "medium",
            "risk": "medium",
        })
        
        ideas.append({
            "id": "idea-3",
            "title": f"Extensible design for {feature_name}",
            "description": "Build with plugin/extension support",
            "complexity": "high",
            "risk": "high",
        })
        
        if context.project_root.exists():
            existing_features = self._find_related_features(context)
            if existing_features:
                ideas.append({
                    "id": "idea-4",
                    "title": "Integration with existing features",
                    "description": f"Build on top of: {', '.join(existing_features[:3])}",
                    "complexity": "medium",
                    "risk": "medium",
                })
        
        return ideas
    
    def _explore_alternatives(self, context: "ExecutionContext") -> list:
        """探索替代方案"""
        alternatives = []
        feature_name = context.feature_name
        
        alternatives.append({
            "approach": "in-process",
            "description": "Implement as part of existing module",
            "pros": ["Simpler deployment", "Lower latency"],
            "cons": ["Tighter coupling", "Larger codebase"],
        })
        
        alternatives.append({
            "approach": "microservice",
            "description": "Deploy as separate service",
            "pros": ["Loose coupling", "Independent scaling"],
            "cons": ["More complexity", "Network latency"],
        })
        
        alternatives.append({
            "approach": "serverless",
            "description": "Use serverless functions",
            "pros": ["No server management", "Automatic scaling"],
            "cons": ["Cold starts", "Vendor lock-in"],
        })
        
        return alternatives
    
    def _find_related_features(self, context: "ExecutionContext") -> list:
        """查找相关特性"""
        project_root = context.project_root
        features_dir = project_root / "docs" / "features"
        
        if not features_dir.exists():
            return []
        
        feature_name = context.feature_name.lower()
        related = []
        
        for feature_dir in features_dir.iterdir():
            if feature_dir.is_dir() and feature_dir.name != feature_name:
                if self._is_related(feature_name, feature_dir.name):
                    related.append(feature_dir.name)
        
        return related[:5]
    
    def _is_related(self, name1: str, name2: str) -> bool:
        """检查两个特性是否相关"""
        words1 = set(name1.replace("-", " ").replace("_", " ").split())
        words2 = set(name2.replace("-", " ").replace("_", " ").split())
        
        common = words1 & words2
        return len(common) > 0
