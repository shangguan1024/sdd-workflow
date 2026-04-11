r"""
YAML Rule Parser
YAML 格式规则解析器
"""

from pathlib import Path
from typing import Optional, List

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from .models import Rule, RuleSet, RuleType, Severity


class YamlRuleParser:
    r"""
    YAML 规则解析器
    
    支持格式:
    ```yaml
    id: my-rules
    name: My Rules
    version: 1.0
    description: Custom coding rules
    scope: "**/*.py"
    
    rules:
      - id: no-print
        name: No Print Statements
        description: Do not use print in production
        type: coding_convention
        severity: error
        patterns:
          - 'print\s*\('
          - 'console\.log'
        fix: Use logging instead
    ```
    """
    
    def parse(self, file_path: Path) -> Optional[RuleSet]:
        """
        解析 YAML 规则文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            RuleSet 对象或 None
        """
        if not YAML_AVAILABLE:
            return None
        
        try:
            content = file_path.read_text(encoding="utf-8")
            data = yaml.safe_load(content)
        except (IOError, UnicodeDecodeError, Exception):
            return None
        
        if not data:
            return None
        
        rules = []
        for rule_data in data.get("rules", []):
            rule = self._parse_rule(rule_data)
            if rule:
                rules.append(rule)
        
        ruleset = RuleSet(
            id=data.get("id", file_path.stem),
            name=data.get("name", file_path.stem),
            version=data.get("version", "1.0"),
            description=data.get("description", ""),
            scope=data.get("scope", "**/*"),
            tags=data.get("tags", []),
            rules=rules,
        )
        
        return ruleset if rules else None
    
    def _parse_rule(self, data: dict) -> Optional[Rule]:
        """解析规则数据"""
        if not data or not data.get("id"):
            return None
        
        return Rule(
            id=data["id"],
            name=data.get("name", data["id"]),
            description=data.get("description", ""),
            type=self._parse_rule_type(data.get("type", "")),
            severity=self._parse_severity(data.get("severity", "")),
            patterns=data.get("patterns", []),
            fix_suggestion=data.get("fix", ""),
            metadata=data.get("metadata", {}),
        )
    
    def _parse_rule_type(self, type_str: str) -> RuleType:
        """解析规则类型"""
        type_map = {
            "coding_convention": RuleType.CODING_CONVENTION,
            "architecture": RuleType.ARCHITECTURE,
            "testing": RuleType.TESTING,
            "documentation": RuleType.DOCUMENTATION,
            "security": RuleType.SECURITY,
            "performance": RuleType.PERFORMANCE,
        }
        return type_map.get(type_str.lower(), RuleType.CODING_CONVENTION)
    
    def _parse_severity(self, severity_str: str) -> Severity:
        """解析严重程度"""
        severity_map = {
            "error": Severity.ERROR,
            "warning": Severity.WARNING,
            "info": Severity.INFO,
        }
        return severity_map.get(severity_str.lower(), Severity.WARNING)
