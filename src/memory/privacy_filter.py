"""
Privacy Filter - 敏感数据过滤机制

在将 memory context 注入到 LLM 之前，自动检测和过滤敏感数据。

v1.0: 基础实现
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, TYPE_CHECKING, Set
from pathlib import Path
import yaml

if TYPE_CHECKING:
    from .conversation import MemoryNode


@dataclass
class PrivacyFilterConfig:
    """
    Privacy Filter 配置
    
    定义敏感关键词、检测模式、处理策略
    """
    enabled: bool = True
    sensitive_patterns: List[str] = None
    replacement_template: str = "[REDACTED]"
    log_detection: bool = True
    whitelist: List[str] = None
    
    def __post_init__(self):
        if self.sensitive_patterns is None:
            self.sensitive_patterns = self._get_default_patterns()
        if self.whitelist is None:
            self.whitelist = []
    
    def _get_default_patterns(self) -> List[str]:
        """
        默认敏感关键词列表
        
        包括:
        - API keys
        - Tokens
        - Passwords
        - Secrets
        - Credentials
        """
        return [
            "api_key",
            "apikey",
            "api-key",
            "token",
            "access_token",
            "auth_token",
            "bearer",
            "password",
            "passwd",
            "pwd",
            "secret",
            "secret_key",
            "private_key",
            "credential",
            "credentials",
            "authorization",
            "auth",
            "session_id",
            "session_token",
            "refresh_token",
            "client_secret",
            "client_id",
            "database_password",
            "db_password",
            "redis_password",
            "mongo_password",
        ]


@dataclass
class DetectionResult:
    """
    检测结果
    
    记录检测到的敏感数据位置和类型
    """
    detected: bool
    pattern_matched: str
    original_value: str
    redacted_value: str
    location: str  # "title", "content", "rationale", etc.
    node_id: str = ""


class PrivacyFilter:
    """
    Privacy Filter 主类
    
    功能:
    1. 检测敏感数据（关键词匹配 + 正则表达式）
    2. 替换敏感数据为 [REDACTED]
    3. 记录检测结果（可选）
    4. 支持白名单（某些关键词可豁免）
    """
    
    def __init__(self, config: PrivacyFilterConfig = None, config_path: Path = None):
        if config_path and config_path.exists():
            self.config = self._load_config(config_path)
        else:
            self.config = config or PrivacyFilterConfig()
        
        self._detection_log: List[DetectionResult] = []
        self._build_regex_patterns()
    
    def _load_config(self, config_path: Path) -> PrivacyFilterConfig:
        """从 YAML 文件加载配置"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            
            privacy_config = data.get("privacy_filter", {})
            
            return PrivacyFilterConfig(
                enabled=privacy_config.get("enabled", True),
                sensitive_patterns=privacy_config.get("sensitive_patterns"),
                replacement_template=privacy_config.get("replacement_template", "[REDACTED]"),
                log_detection=privacy_config.get("log_detection", True),
                whitelist=privacy_config.get("whitelist", []),
            )
        except Exception:
            return PrivacyFilterConfig()
    
    def _build_regex_patterns(self):
        """
        构建正则表达式模式
        
        检测以下格式:
        - key=value
        - key: value
        - key = "value"
        - key: "value"
        - Authorization: Bearer <token>
        - X-API-Key: <key>
        """
        self._regex_patterns = []
        
        for pattern in self.config.sensitive_patterns:
            # 白名单检查
            if pattern in self.config.whitelist:
                continue
            
            # 多种常见格式
            regex_patterns = [
                # key=value (JSON-like)
                rf'{pattern}\s*=\s*["\']?([^"\s,\}}\]]+)["\']?',
                # key: value (YAML-like)
                rf'{pattern}\s*:\s*["\']?([^"\s,\}}\]]+)["\']?',
                # Authorization: Bearer <token>
                rf'Authorization\s*:\s*Bearer\s+([^\s]+)',
                # X-API-Key: <key>
                rf'X-.*-Key\s*:\s*([^\s]+)',
                # Generic header
                rf'{pattern}\s*[=:]\s*([^\s]+)',
            ]
            
            for regex in regex_patterns:
                try:
                    self._regex_patterns.append((pattern, re.compile(regex, re.IGNORECASE)))
                except re.error:
                    pass
    
    def filter_node(self, node: "MemoryNode") -> "MemoryNode":
        """
        过滤单个 MemoryNode
        
        检查并替换 title, content, rationale 中的敏感数据
        
        Returns:
            过滤后的 MemoryNode（不会修改原节点）
        """
        if not self.config.enabled:
            return node
        
        # 创建副本
        filtered_node = self._clone_node(node)
        
        # 过滤各个字段
        for field_name in ["title", "content", "rationale"]:
            original_value = getattr(filtered_node, field_name, "")
            if original_value:
                filtered_value, detections = self._filter_text(
                    original_value, 
                    field_name, 
                    node.id
                )
                setattr(filtered_node, field_name, filtered_value)
                
                # 记录检测结果
                if self.config.log_detection and detections:
                    self._detection_log.extend(detections)
        
        return filtered_node
    
    def _clone_node(self, node: "MemoryNode") -> "MemoryNode":
        """创建节点副本"""
        from .conversation import MemoryNode
        return MemoryNode(
            id=node.id,
            type=node.type,
            title=node.title,
            content=node.content,
            rationale=node.rationale,
            alternatives=node.alternatives.copy(),
            source_session=node.source_session,
            created_at=node.created_at,
            updated_at=node.updated_at,
            resolved=node.resolved,
            priority=node.priority,
            tags=node.tags.copy(),
            related_ids=node.related_ids.copy(),
            decision_chain_id=node.decision_chain_id,
        )
    
    def _filter_text(
        self, 
        text: str, 
        location: str, 
        node_id: str
    ) -> tuple[str, List[DetectionResult]]:
        """
        过滤文本
        
        Returns:
            (filtered_text, detection_results)
        """
        detections = []
        filtered_text = text
        
        for pattern_name, regex in self._regex_patterns:
            matches = regex.finditer(text)
            
            for match in matches:
                original_value = match.group(1) if len(match.groups()) > 0 else match.group(0)
                
                # 确认是真正的敏感数据（不是占位符）
                placeholder_patterns = [
                    "<", ">", "your_", "placeholder", "example", "xxx",
                    "[REDACTED]", "xxx-xxx", "test", "demo", "sample",
                    "[", "]", "{", "}",  # 方括号和花括号通常是占位符
                ]
                
                is_placeholder = any(p in original_value.lower() for p in placeholder_patterns)
                
                if not is_placeholder and len(original_value) > 3:
                    # 替换
                    redacted_value = self.config.replacement_template
                    filtered_text = filtered_text.replace(original_value, redacted_value)
                    
                    # 记录
                    detections.append(DetectionResult(
                        detected=True,
                        pattern_matched=pattern_name,
                        original_value=original_value[:20] + "..." if len(original_value) > 20 else original_value,
                        redacted_value=redacted_value,
                        location=location,
                        node_id=node_id,
                    ))
        
        return filtered_text, detections
    
    def filter_nodes(self, nodes: List["MemoryNode"]) -> List["MemoryNode"]:
        """
        过滤节点列表
        
        Returns:
            过滤后的节点列表
        """
        return [self.filter_node(node) for node in nodes]
    
    def filter_context_summary(self, summary: str) -> str:
        """
        过滤 context summary
        
        在注入前过滤整个 summary 文本
        """
        if not self.config.enabled:
            return summary
        
        filtered_summary, detections = self._filter_text(summary, "context_summary", "")
        
        if self.config.log_detection and detections:
            self._detection_log.extend(detections)
        
        return filtered_summary
    
    def get_detection_log(self) -> List[DetectionResult]:
        """获取检测日志"""
        return self._detection_log.copy()
    
    def clear_detection_log(self):
        """清空检测日志"""
        self._detection_log.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            {
                "total_detections": int,
                "patterns_detected": dict,
                "locations": dict,
            }
        """
        if not self._detection_log:
            return {
                "total_detections": 0,
                "patterns_detected": {},
                "locations": {},
            }
        
        patterns_count: Dict[str, int] = {}
        locations_count: Dict[str, int] = {}
        
        for detection in self._detection_log:
            patterns_count[detection.pattern_matched] = patterns_count.get(detection.pattern_matched, 0) + 1
            locations_count[detection.location] = locations_count.get(detection.location, 0) + 1
        
        return {
            "total_detections": len(self._detection_log),
            "patterns_detected": patterns_count,
            "locations": locations_count,
            "config_enabled": self.config.enabled,
            "whitelist_size": len(self.config.whitelist),
        }
    
    def report(self) -> str:
        """
        生成检测报告
        
        Returns:
            Markdown 格式的报告
        """
        stats = self.get_stats()
        
        lines = []
        lines.append("## Privacy Filter Detection Report")
        lines.append("")
        
        if stats["total_detections"] == 0:
            lines.append("No sensitive data detected.")
            return "\n".join(lines)
        
        lines.append(f"**Total detections:** {stats['total_detections']}")
        lines.append("")
        
        lines.append("**Patterns detected:**")
        for pattern, count in sorted(stats["patterns_detected"].items(), key=lambda x: -x[1]):
            lines.append(f"  - `{pattern}`: {count} times")
        lines.append("")
        
        lines.append("**Locations:**")
        for location, count in sorted(stats["locations"].items(), key=lambda x: -x[1]):
            lines.append(f"  - {location}: {count} times")
        lines.append("")
        
        if self._detection_log:
            lines.append("**Recent detections:**")
            for detection in self._detection_log[:5]:
                lines.append(f"  - Node `{detection.node_id[:8]}`: `{detection.pattern_matched}` in {detection.location}")
        
        return "\n".join(lines)


def create_default_config_file(config_path: Path):
    """
    创建默认配置文件
    
    用于首次使用时生成配置文件模板
    """
    default_config = {
        "privacy_filter": {
            "enabled": True,
            "sensitive_patterns": [
                "api_key", "apikey", "api-key",
                "token", "access_token", "auth_token",
                "password", "passwd", "pwd",
                "secret", "secret_key", "private_key",
                "credential", "credentials",
                "authorization", "auth",
            ],
            "replacement_template": "[REDACTED]",
            "log_detection": True,
            "whitelist": [],
        }
    }
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)