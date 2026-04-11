"""
Rule Models
规则数据模型
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class RuleType(Enum):
    """规则类型"""
    CODING_CONVENTION = "coding_convention"
    ARCHITECTURE = "architecture"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    PERFORMANCE = "performance"


class Severity(Enum):
    """严重程度"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Rule:
    """
    规则定义
    
    Attributes:
        id: 规则唯一标识
        name: 规则名称
        description: 规则描述
        type: 规则类型
        severity: 严重程度
        patterns: 匹配模式列表
        fix_suggestion: 修复建议
        metadata: 额外元数据
    """
    id: str
    name: str
    description: str
    type: RuleType = RuleType.CODING_CONVENTION
    severity: Severity = Severity.WARNING
    patterns: List[str] = field(default_factory=list)
    fix_suggestion: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def matches(self, content: str) -> List[Dict[str, Any]]:
        """
        检查内容是否匹配规则
        
        Args:
            content: 待检查内容
            
        Returns:
            匹配结果列表
        """
        import re
        
        matches = []
        for pattern in self.patterns:
            try:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    matches.append({
                        "rule_id": self.id,
                        "rule_name": self.name,
                        "match": match.group(),
                        "line": content[:match.start()].count('\n') + 1,
                        "position": match.start(),
                    })
            except re.error:
                continue
        
        return matches


@dataclass
class RuleSet:
    """
    规则集
    
    Attributes:
        id: 规则集唯一标识
        name: 规则集名称
        version: 版本
        description: 描述
        rules: 规则列表
        scope: 适用范围 (e.g., "*.py", "src/**")
        tags: 标签
    """
    id: str
    name: str
    version: str = "1.0"
    description: str = ""
    rules: List[Rule] = field(default_factory=list)
    scope: str = "**/*"
    tags: List[str] = field(default_factory=list)
    
    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """获取规则"""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None
    
    def filter_by_type(self, rule_type: RuleType) -> List[Rule]:
        """按类型筛选规则"""
        return [r for r in self.rules if r.type == rule_type]
    
    def filter_by_severity(self, severity: Severity) -> List[Rule]:
        """按严重程度筛选规则"""
        return [r for r in self.rules if r.severity == severity]
    
    def add_rule(self, rule: Rule):
        """添加规则"""
        if not self.get_rule(rule.id):
            self.rules.append(rule)
    
    def remove_rule(self, rule_id: str):
        """移除规则"""
        self.rules = [r for r in self.rules if r.id != rule_id]
