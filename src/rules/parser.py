"""
Rule Parser
规则解析器
"""

from pathlib import Path
from typing import Dict, Any, Optional

from .md_parser import MarkdownRuleParser
from .yaml_parser import YamlRuleParser
from .models import RuleSet


class RuleParser:
    """
    规则解析器
    
    支持:
    - Markdown 格式规则 (.md)
    - YAML 格式规则 (.yaml, .yml)
    """
    
    def __init__(self):
        self.md_parser = MarkdownRuleParser()
        self.yaml_parser = YamlRuleParser()
    
    def parse(self, file_path: Path) -> Optional[RuleSet]:
        """
        解析规则文件
        
        Args:
            file_path: 规则文件路径
            
        Returns:
            RuleSet 对象或 None
        """
        if not file_path.exists():
            return None
        
        suffix = file_path.suffix.lower()
        
        if suffix in [".md", ".markdown"]:
            return self.md_parser.parse(file_path)
        elif suffix in [".yaml", ".yml"]:
            return self.yaml_parser.parse(file_path)
        else:
            return None
    
    def parse_multiple(self, file_paths: list) -> Dict[str, RuleSet]:
        """
        解析多个规则文件
        
        Args:
            file_paths: 规则文件路径列表
            
        Returns:
            文件路径到 RuleSet 的字典
        """
        results = {}
        
        for file_path in file_paths:
            ruleset = self.parse(file_path)
            if ruleset:
                results[str(file_path)] = ruleset
        
        return results


def parse_rule_file(file_path: Path) -> Optional[RuleSet]:
    """
    便捷函数：解析规则文件
    
    Args:
        file_path: 规则文件路径
        
    Returns:
        RuleSet 对象或 None
    """
    parser = RuleParser()
    return parser.parse(file_path)
