"""
Progressive Disclosure - 渐进式上下文披露

三层检索机制：
Layer 1: Index（索引层）- 最小信息，快速浏览
Layer 2: Timeline（时间线层）- 时间上下文，因果关系
Layer 3: Full Details（完整详情层）- 深入查看，完整决策

v1.0: 基础实现
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from .conversation import MemoryNode, ConversationMemory


@dataclass
class MemoryIndex:
    """
    Layer 1: 索引层
    
    最小信息，用于快速浏览和定位
    Token消耗: ~50-100 tokens/节点
    """
    id: str
    type: str
    title: str
    created_at: str
    priority: str
    resolved: bool
    
    def to_markdown(self) -> str:
        """转换为Markdown格式（用于注入上下文）"""
        status = "[OK]" if self.resolved else "[...]"
        return f"| {self.id[:8]} | {self.type:<20} | {self.title:<40} | {self.priority:<6} | {status} |"
    
    def estimate_tokens(self) -> int:
        """估算token消耗"""
        # 简单估算：每个字符约0.25 tokens
        text = f"{self.id} {self.type} {self.title} {self.priority}"
        return len(text) // 4 + 10  # 加10 tokens for formatting


@dataclass
class MemoryTimeline:
    """
    Layer 2: 时间线层
    
    时间序列上下文，用于理解因果关系
    Token消耗: ~200-300 tokens/节点
    """
    id: str
    type: str
    title: str
    content_summary: str  # 前200字符摘要
    created_at: str
    related_ids: List[str]
    session_id: str
    
    def to_markdown(self) -> str:
        """转换为Markdown格式"""
        lines = [
            f"### {self.title}",
            f"- ID: {self.id[:8]}",
            f"- Type: {self.type}",
            f"- Time: {self.created_at}",
            f"- Session: {self.session_id}",
            "",
            f"**Summary:** {self.content_summary}",
        ]
        
        if self.related_ids:
            lines.append(f"- Related: {', '.join(self.related_ids[:3])}")
        
        return "\n".join(lines)
    
    def estimate_tokens(self) -> int:
        """估算token消耗"""
        text = f"{self.title} {self.content_summary} {self.session_id}"
        return len(text) // 4 + 20


class ProgressiveDisclosure:
    """
    Progressive Disclosure - 渐进式上下文披露
    
    核心机制：
    1. get_index() - 获取索引层（最小token）
    2. get_timeline() - 获取时间线层（中等token）
    3. get_full_details() - 获取完整详情（最大token）
    
    每层提供token成本估算，用户可以控制预算
    """
    
    def __init__(self, memory: ConversationMemory):
        self.memory = memory
        
        # Token统计
        self._token_stats = {
            "layer1_used": 0,
            "layer2_used": 0,
            "layer3_used": 0,
            "total_used": 0,
        }
    
    def get_index(
        self,
        filter_type: Optional[str] = None,
        filter_resolved: Optional[bool] = None,
        limit: int = 20,
        priority_threshold: Optional[str] = None,
    ) -> List[MemoryIndex]:
        """
        Layer 1: 获取索引
        
        仅返回ID + 基本信息，最小token消耗
        ~50-100 tokens/result
        
        Args:
            filter_type: 按类型过滤（REQUIREMENT/DESIGN_DECISION/etc）
            filter_resolved: 按是否已解决过滤
            limit: 最大返回数量
            priority_threshold: 优先级阈值（high/medium/low）
        
        Returns:
            List[MemoryIndex]: 索引列表
        """
        nodes = list(self.memory.nodes.values())
        
        # 过滤
        if filter_type:
            from .conversation import MemoryType
            nodes = [n for n in nodes if n.type.value == filter_type]
        
        if filter_resolved is not None:
            nodes = [n for n in nodes if n.resolved == filter_resolved]
        
        if priority_threshold:
            priority_order = {"high": 3, "medium": 2, "low": 1}
            threshold_level = priority_order.get(priority_threshold, 0)
            nodes = [
                n for n in nodes 
                if priority_order.get(n.priority, 0) >= threshold_level
            ]
        
        # 按优先级和时间排序
        def sort_key(n):
            priority_order = {"high": 0, "medium": 1, "low": 2}
            return (priority_order.get(n.priority, 99), n.created_at)
        
        sorted_nodes = sorted(nodes, key=sort_key, reverse=True)
        
        # 生成索引
        indices = []
        for node in sorted_nodes[:limit]:
            indices.append(MemoryIndex(
                id=node.id,
                type=node.type.value,
                title=node.title[:50] if len(node.title) > 50 else node.title,
                created_at=node.created_at[:16] if len(node.created_at) > 16 else node.created_at,
                priority=node.priority,
                resolved=node.resolved,
            ))
        
        # 更新token统计
        total_tokens = sum(idx.estimate_tokens() for idx in indices)
        self._token_stats["layer1_used"] += total_tokens
        self._token_stats["total_used"] += total_tokens
        
        return indices
    
    def get_timeline(
        self,
        around_id: Optional[str] = None,
        before: int = 3,
        after: int = 3,
        feature_name: Optional[str] = None,
    ) -> List[MemoryTimeline]:
        """
        Layer 2: 获取时间线
        
        返回时间序列上下文，中等token消耗
        ~200-300 tokens/result
        
        Args:
            around_id: 围绕哪个节点（中心节点）
            before: 之前多少个节点
            after: 之后多少个节点
            feature_name: 按特性过滤
        
        Returns:
            List[MemoryTimeline]: 时间线列表
        """
        all_nodes = sorted(
            self.memory.nodes.values(),
            key=lambda n: n.created_at
        )
        
        # 按特性过滤
        if feature_name:
            all_nodes = [
                n for n in all_nodes 
                if feature_name in n.source_session or feature_name in n.id
            ]
        
        if not around_id:
            # 没有指定中心节点，返回最近的节点
            recent_nodes = all_nodes[-(before + after):] if len(all_nodes) > before + after else all_nodes
            return self._nodes_to_timeline(recent_nodes)
        
        # 找到around_id的位置
        target_index = None
        for i, node in enumerate(all_nodes):
            if node.id == around_id or node.id.startswith(around_id):
                target_index = i
                break
        
        if target_index is None:
            # 未找到，返回最近的节点
            recent_nodes = all_nodes[-(before + after):]
            return self._nodes_to_timeline(recent_nodes)
        
        # 获取前后节点
        start = max(0, target_index - before)
        end = min(len(all_nodes), target_index + after + 1)
        
        timeline_nodes = all_nodes[start:end]
        
        return self._nodes_to_timeline(timeline_nodes)
    
    def get_full_details(
        self,
        ids: List[str],
        include_alternatives: bool = True,
        include_rationale: bool = True,
    ) -> List[MemoryNode]:
        """
        Layer 3: 获取完整详情
        
        仅获取指定ID的完整内容
        ~500-1000 tokens/result
        
        ⚠️ 必须先通过Layer 1/2筛选后再调用
        
        Args:
            ids: 要获取的节点ID列表
            include_alternatives: 是否包含备选方案
            include_rationale: 是否包含决策理由
        
        Returns:
            List[MemoryNode]: 完整节点列表
        """
        nodes = []
        
        for id in ids:
            # 支持短ID匹配
            matched_node = None
            for node_id, node in self.memory.nodes.items():
                if node_id == id or node_id.startswith(id):
                    matched_node = node
                    break
            
            if matched_node:
                nodes.append(matched_node)
        
        # 更新token统计
        for node in nodes:
            text_length = len(node.content) + len(node.rationale)
            node_tokens = text_length // 4 + 30
            self._token_stats["layer3_used"] += node_tokens
            self._token_stats["total_used"] += node_tokens
        
        return nodes
    
    def _nodes_to_timeline(self, nodes: List[MemoryNode]) -> List[MemoryTimeline]:
        """从节点生成时间线"""
        timelines = []
        
        for node in nodes:
            summary_parts = [node.content]
            if node.rationale and len(node.rationale) > 0:
                summary_parts.append(node.rationale)
            
            full_summary = " | ".join(summary_parts)
            content_summary = full_summary[:200] if len(full_summary) > 200 else full_summary
            
            timelines.append(MemoryTimeline(
                id=node.id,
                type=node.type.value,
                title=node.title,
                content_summary=content_summary,
                created_at=node.created_at,
                related_ids=node.related_ids[:3] if node.related_ids else [],
                session_id=node.source_session,
            ))
        
        total_tokens = sum(t.estimate_tokens() for t in timelines)
        self._token_stats["layer2_used"] += total_tokens
        self._token_stats["total_used"] += total_tokens
        
        return timelines
    
    def get_token_stats(self) -> Dict[str, Any]:
        """获取token使用统计"""
        return {
            "layer1_used": self._token_stats["layer1_used"],
            "layer2_used": self._token_stats["layer2_used"],
            "layer3_used": self._token_stats["layer3_used"],
            "total_used": self._token_stats["total_used"],
            "savings_estimate": self._estimate_savings(),
        }
    
    def _estimate_savings(self) -> str:
        """估算节省的token（对比全量注入）"""
        # 假设全量注入会加载所有节点
        full_load_estimate = sum(
            len(n.content) // 4 + len(n.rationale) // 4 + 20
            for n in self.memory.nodes.values()
        )
        
        used = self._token_stats["total_used"]
        
        if full_load_estimate == 0:
            return "N/A"
        
        savings_percent = (1 - used / full_load_estimate) * 100
        
        return f"{savings_percent:.1f}% saved ({used}/{full_load_estimate} tokens)"
    
    def format_index_table(self, indices: List[MemoryIndex]) -> str:
        """格式化索引为Markdown表格"""
        lines = [
            "## Memory Index (Layer 1)",
            "",
            "| ID | Type | Title | Priority | Status |",
            "|------|------|------|----------|--------|",
        ]
        
        for idx in indices:
            lines.append(idx.to_markdown())
        
        # 添加token成本提示
        total_tokens = sum(idx.estimate_tokens() for idx in indices)
        lines.extend([
            "",
            f"> **Token cost:** ~{total_tokens} tokens",
            f"> **Savings:** ~{self._estimate_savings()}",
            "",
            "**Next steps:**",
            "- Use `get_timeline(around_id='xxx')` to see context around specific node",
            "- Use `get_full_details(ids=['xxx', 'yyy'])` to fetch full details",
        ])
        
        return "\n".join(lines)
    
    def format_timeline_context(self, timelines: List[MemoryTimeline]) -> str:
        """格式化时间线为Markdown"""
        lines = [
            "## Memory Timeline (Layer 2)",
            "",
            f"Showing {len(timelines)} nodes in chronological order:",
            "",
        ]
        
        for t in timelines:
            lines.append(t.to_markdown())
            lines.append("")
        
        total_tokens = sum(t.estimate_tokens() for t in timelines)
        lines.extend([
            "---",
            "",
            f"> **Token cost:** ~{total_tokens} tokens",
            "",
            "**Next step:**",
            "- Use `get_full_details(ids=[...])` to fetch full details for interesting nodes",
        ])
        
        return "\n".join(lines)
    
    def format_full_details(self, nodes: List[MemoryNode]) -> str:
        """格式化完整详情为Markdown"""
        lines = [
            "## Memory Full Details (Layer 3)",
            "",
        ]
        
        for node in nodes:
            lines.extend([
                f"### {node.title}",
                "",
                f"- **ID:** {node.id}",
                f"- **Type:** {node.type.value}",
                f"- **Priority:** {node.priority}",
                f"- **Created:** {node.created_at}",
                f"- **Session:** {node.source_session}",
                f"- **Resolved:** {'Yes' if node.resolved else 'No'}",
                "",
                "**Content:**",
                "",
                node.content,
                "",
                "**Rationale:**",
                "",
                node.rationale,
                "",
            ])
            
            if node.alternatives:
                lines.extend([
                    "**Alternatives considered:**",
                    "",
                ])
                for alt in node.alternatives[:3]:
                    lines.append(f"- {alt}")
                lines.append("")
            
            if node.related_ids:
                lines.extend([
                    "**Related nodes:**",
                    "",
                ])
                for rid in node.related_ids[:3]:
                    lines.append(f"- {rid}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        total_tokens = sum(
            len(n.content) // 4 + len(n.rationale) // 4 + 30
            for n in nodes
        )
        lines.extend([
            f"> **Token cost:** ~{total_tokens} tokens",
            "",
        ])
        
        return "\n".join(lines)