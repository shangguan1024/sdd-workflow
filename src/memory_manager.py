"""
Memory Manager - Memory management, Progressive Disclosure, Timeline access

负责：
- Memory管理（load_or_create_memory, save_memory）
- Progressive Disclosure注入
- Memory Timeline访问

Extracted from director.py for better modularity.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .memory import ConversationMemory
    from .memory.progressive_disclosure import ProgressiveDisclosure


class MemoryManager:
    """
    Memory Manager - 管理会话记忆
    
    负责：
    1. Memory加载和保存
    2. Progressive Disclosure注入
    3. Memory Timeline访问
    """
    
    def __init__(self, project_root: Path, error_recovery_manager=None):
        self.project_root = project_root
        self._memory: Optional[ConversationMemory] = None
        self._error_recovery_manager = error_recovery_manager
    
    def load_or_create_memory(self, feature_name: str) -> Optional[ConversationMemory]:
        """
        加载或创建 Memory
        
        Args:
            feature_name: 特性名称
            
        Returns:
            ConversationMemory instance
        """
        from .memory.recovery import MemoryRecovery
        recovery = MemoryRecovery(self.project_root)
        self._memory = recovery.recover_or_create(feature_name)
        return self._memory
    
    def save_memory_silent(self, feature_name: str):
        """
        保存 Memory（静默模式，不抛出异常）
        
        Args:
            feature_name: 特性名称
        """
        if not self._memory:
            return
        
        try:
            from .memory.persistence import MemoryPersistence
            persistence = MemoryPersistence(self.project_root)
            persistence.save(self._memory, feature_name)
        except Exception as e:
            if self._error_recovery_manager:
                from .error_recovery import ErrorSeverity
                self._error_recovery_manager.capture_error(
                    exception=e,
                    operation="save_memory_silent",
                    severity=ErrorSeverity.WARNING,
                    file_path=feature_name,
                )
    
    def show_memory_context(self):
        """
        显示 Memory上下文（未解决的讨论）
        
        在会话恢复时显示上次未完成的内容
        """
        if not self._memory or not self._memory.nodes:
            return
        
        unresolved = self._memory.get_unresolved_nodes()
        questions = self._memory.get_open_questions()
        
        if not unresolved and not questions:
            return
        
        print()
        print("📝 检测到上次会话未完成的讨论:")
        for q in questions:
            print(f"  ❓ {q.title}: {q.content[:100]}")
        for node in unresolved:
            if node.type.value != "open_question":
                print(f"  ⚠️ [{node.type.value}] {node.title}")
        print()
    
    def get_memory_timeline(self, context, around_id: str) -> str:
        """
        Layer 2: 获取时间线
        
        LLM可以调用此方法获取特定节点的时间上下文
        
        Args:
            context: 执行上下文
            around_id: 围绕哪个节点
        
        Returns:
            str: 时间线Markdown内容
        """
        if not context.metadata.get("progressive_disclosure_enabled"):
            return "Progressive Disclosure not enabled. Context was injected with full mode."
        
        disclosure = context.metadata.get("progressive_disclosure_instance")
        if not disclosure:
            return "Progressive Disclosure instance not found in context."
        
        timelines = disclosure.get_timeline(around_id=around_id)
        timeline_content = disclosure.format_timeline_context(timelines)
        
        token_stats = disclosure.get_token_stats()
        context.metadata["progressive_disclosure_token_stats"] = token_stats
        
        return timeline_content
    
    def get_memory_full_details(self, context, ids: List[str]) -> str:
        """
        Layer 3: 获取完整详情
        
        LLM可以调用此方法获取特定节点的完整内容
        
        Args:
            context: 执行上下文
            ids: 要获取的节点ID列表
        
        Returns:
            str: 完整详情Markdown内容
        """
        if not context.metadata.get("progressive_disclosure_enabled"):
            return "Progressive Disclosure not enabled. Context was injected with full mode."
        
        disclosure = context.metadata.get("progressive_disclosure_instance")
        if not disclosure:
            return "Progressive Disclosure instance not found in context."
        
        nodes = disclosure.get_full_details(ids)
        details_content = disclosure.format_full_details(nodes)
        
        token_stats = disclosure.get_token_stats()
        context.metadata["progressive_disclosure_token_stats"] = token_stats
        
        return details_content
    
    def get_memory(self) -> Optional[ConversationMemory]:
        """
        获取当前 Memory实例
        
        Returns:
            ConversationMemory instance or None
        """
        return self._memory
    
    def set_memory(self, memory: ConversationMemory):
        """
        设置 Memory实例
        
        Args:
            memory: ConversationMemory instance
        """
        self._memory = memory
    
    def start_session(self, session_id: str):
        """
        开始会话
        
        Args:
            session_id: 会话ID
        """
        if self._memory:
            self._memory.start_session(session_id)