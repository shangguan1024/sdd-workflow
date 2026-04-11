r"""
Markdown Rule Parser
Markdown 格式规则解析器
"""

from pathlib import Path
from typing import Optional, Dict, Any
import re

from .models import Rule, RuleSet, RuleType, Severity


class MarkdownRuleParser:
    r"""
    Markdown 规则解析器
    
    支持格式:
    ```yaml
    ---
    ruleset:
      id: my-rules
      name: My Rules
      version: 1.0
    ---
    
    ## Rule: no-print-statements
    
    **Type:** coding_convention
    **Severity:** error
    
    **Description:**
    Do not use print statements in production code.
    
    **Patterns:**
    - `print\s*\(`  # noqa: W605
    - `console\.log`  # noqa: W605
    
    **Fix:**
    Use proper logging instead.
    ```
    """
    
    FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    RULESET_HEADER = re.compile(r"^##\s+Rule:\s+(.+)$", re.MULTILINE)
    METADATA_PATTERN = re.compile(r"^\*\*(\w+):\*\*\s*(.+)$", re.MULTILINE)
    
    def parse(self, file_path: Path) -> Optional[RuleSet]:
        """
        解析 Markdown 规则文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            RuleSet 对象或 None
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except (IOError, UnicodeDecodeError):
            return None
        
        ruleset = self._parse_frontmatter(content)
        
        if not ruleset:
            ruleset = RuleSet(
                id=file_path.stem,
                name=file_path.stem.replace("-", " ").replace("_", " ").title(),
            )
        
        rules = self._extract_rules(content)
        for rule in rules:
            ruleset.add_rule(rule)
        
        return ruleset if ruleset.rules else None
    
    def _parse_frontmatter(self, content: str) -> Optional[RuleSet]:
        """解析 YAML Frontmatter"""
        match = self.FRONTMATTER_PATTERN.search(content)
        
        if not match:
            return None
        
        import yaml
        
        try:
            data = yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return None
        
        if not data or "ruleset" not in data:
            return None
        
        rs_data = data["ruleset"]
        
        return RuleSet(
            id=rs_data.get("id", ""),
            name=rs_data.get("name", ""),
            version=rs_data.get("version", "1.0"),
            description=rs_data.get("description", ""),
            scope=rs_data.get("scope", "**/*"),
            tags=rs_data.get("tags", []),
        )
    
    def _extract_rules(self, content: str) -> list:
        """提取规则"""
        rules = []
        
        rule_sections = self.RULESET_HEADER.split(content)
        
        for section in rule_sections[1:]:
            rule = self._parse_rule_section(section)
            if rule:
                rules.append(rule)
        
        return rules
    
    def _parse_rule_section(self, section: str) -> Optional[Rule]:
        """解析单个规则章节"""
        lines = section.strip().split("\n")
        
        if not lines:
            return None
        
        rule_name = lines[0].strip()
        rule_id = self._to_rule_id(rule_name)
        
        metadata = {}
        description_lines = []
        in_description = False
        patterns = []
        fix_suggestion = ""
        
        for line in lines[1:]:
            meta_match = self.METADATA_PATTERN.match(line.strip())
            if meta_match:
                key = meta_match.group(1).lower()
                value = meta_match.group(2).strip()
                
                if key == "patterns":
                    in_description = False
                    continue
                elif key == "fix":
                    in_description = False
                    fix_suggestion = value
                    continue
                elif key in ["type", "severity"]:
                    metadata[key] = value
                else:
                    metadata[key] = value
            elif line.strip().startswith("- `"):
                pattern = line.strip()[3:line.strip().rfind("`")]
                patterns.append(pattern)
            elif line.strip() and not in_description:
                in_description = True
                description_lines.append(line.strip())
            elif in_description:
                description_lines.append(line.strip())
        
        rule_type = self._parse_rule_type(metadata.get("type", ""))
        severity = self._parse_severity(metadata.get("severity", ""))
        
        return Rule(
            id=rule_id,
            name=rule_name,
            description=" ".join(description_lines),
            type=rule_type,
            severity=severity,
            patterns=patterns,
            fix_suggestion=fix_suggestion,
            metadata=metadata,
        )
    
    def _to_rule_id(self, name: str) -> str:
        """将名称转换为规则 ID"""
        return re.sub(r"[^\w]+", "-", name.lower()).strip("-")
    
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
