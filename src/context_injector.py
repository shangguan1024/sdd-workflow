"""
Context Injector - Context injection and Progressive Disclosure

负责：
- inject_memory_context
- _inject_core_principles
- _inject_with_progressive_disclosure
- _inject_full_context
- _apply_privacy_filter

Extracted from director.py for better modularity.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .memory import ConversationMemory, PrivacyFilter
    from .memory.progressive_disclosure import ProgressiveDisclosure


class ContextInjector:
    """
    Context Injector - 上下文注入器
    
    负责：
    1. 注入核心原则（constitution/core.md）
    2. 注入 Memory上下文
    3. Progressive Disclosure支持
    4. Privacy Filter应用
    """
    
    def __init__(
        self,
        project_root: Path,
        privacy_filter: PrivacyFilter,
        memory_manager=None,
    ):
        self.project_root = project_root
        self._privacy_filter = privacy_filter
        self._memory_manager = memory_manager
    
    def inject_memory_context(
        self,
        context,
        feature_name: str,
        use_progressive_disclosure: bool = True,
    ):
        """
        将 ConversationMemory 上下文注入到当前会话。
        
        改进：
        1. 加载 constitution/core.md（最高原则，第1位）
        2. 使用 Progressive Disclosure（渐进式披露）
        3. 注入接口使用说明（告知LLM如何使用接口）
        
        Args:
            context: 执行上下文
            feature_name: 特性名称
            use_progressive_disclosure: 是否使用渐进披露（默认True）
        """
        self._inject_core_principles(context)
        
        self._inject_interface_instructions(context)
        
        memory = self._memory_manager.get_memory() if self._memory_manager else None
        
        if use_progressive_disclosure and memory and memory.nodes:
            self._inject_with_progressive_disclosure(context, feature_name, memory)
        else:
            self._inject_full_context(context, feature_name, memory)
    
    def _inject_interface_instructions(self, context):
        """
        注入接口使用说明
        
        告知LLM如何使用Progressive Disclosure和Memory Timeline接口
        """
        interface_instructions = """
## Available Memory Interfaces

You have access to the following memory interfaces for retrieving additional context:

### 1. Progressive Disclosure Layers

The memory system uses 3 layers to manage token budget:

- **Layer 1 (Index)**: Minimal overview (use when token budget critical)
- **Layer 2 (Timeline)**: Memory events timeline (default, currently loaded)
- **Layer 3 (Full Details)**: Complete memory details (use when needed)

### 2. Memory Timeline Interface

Get memory events around a specific ID:

```python
director.get_memory_timeline(context, around_id='memory_node_id')
```

Returns: Memory events before and after the specified ID

### 3. Full Details Interface

Get complete details for specific memory nodes:

```python
director.get_memory_full_details(context, ids=['id1', 'id2'])
```

Returns: Full content of specified memory nodes

### Usage Recommendations

- Use **Layer 2 (Timeline)** for normal operations (currently loaded)
- Call **get_memory_timeline()** when you need more context about recent decisions
- Call **get_memory_full_details()** when you need complete information about specific decisions
- Switch to **Layer 1** if token budget becomes critical

These interfaces help you understand past decisions and maintain context consistency.
"""
        
        context.metadata["interface_instructions"] = interface_instructions
        
        print()
        print("=" * 60)
        print("Memory Interface Instructions")
        print("=" * 60)
        print(interface_instructions)
        print("=" * 60)
        print()
    
    def _inject_core_principles(self, context):
        """
        加载并注入最高原则
        
        从 constitution/core.md 加载最高原则，作为第1优先级注入
        
        如果文件不存在，安全降级（不注入）
        """
        constitution_file = self.project_root / "CONSTITUTION" / "core.md"
        
        if not constitution_file.exists():
            context.metadata["core_principles_loaded"] = False
            return
        
        principles = constitution_file.read_text(encoding="utf-8")
        
        context.metadata["core_principles"] = principles
        context.metadata["core_principles_loaded"] = True
        
        print()
        print("=" * 60)
        print("Core Principles (最高原则 - 必须遵守)")
        print("=" * 60)
        print()
        print("These principles MUST be followed throughout development:")
        print()
        print(principles)
        print("=" * 60)
        print()
        print("WARNING: Violating these principles may cause Phase Gate to block.")
        print()
    
    def _inject_with_progressive_disclosure(
        self,
        context,
        feature_name: str,
        memory: ConversationMemory,
    ):
        """
        Progressive Disclosure 注入方式
        
        改进：默认注入 Layer 2（时间线 + 详情），而非仅 Layer 1（索引）
        
        Layer 2 包含：
        - 需求详情
        - 设计决策理据
        - 时间上下文
        
        Privacy Filter: 在注入前过滤敏感数据
        """
        from .memory.progressive_disclosure import ProgressiveDisclosure
        
        filtered_memory = self._apply_privacy_filter(memory)
        
        disclosure = ProgressiveDisclosure(filtered_memory)
        
        timelines = disclosure.get_timeline(before=5, after=5)
        
        timeline_content = disclosure.format_timeline_context(timelines)
        
        context.metadata["injected_context"] = timeline_content
        context.metadata["context_injected"] = True
        context.metadata["progressive_disclosure_enabled"] = True
        context.metadata["progressive_disclosure_instance"] = disclosure
        
        agents_file = self.project_root / "AGENTS.md"
        if agents_file.exists():
            agents_content = agents_file.read_text(encoding="utf-8")
            agents_summary = agents_content[:2000]
            context.metadata["injected_context"] = f"{agents_summary}\n\n---\n\n{timeline_content}"
            context.metadata["agents_context_loaded"] = True
        
        token_stats = disclosure.get_token_stats()
        context.metadata["progressive_disclosure_token_stats"] = token_stats
        
        feature_dir = self.project_root / "docs" / "features" / feature_name
        context_dir = feature_dir / ".sdd"
        context_dir.mkdir(parents=True, exist_ok=True)
        context_file = context_dir / "current_context.md"
        context_file.write_text(context.metadata["injected_context"], encoding="utf-8")
        
        stats = {
            "Method": "Progressive Disclosure (Layer 2 - Timeline)",
            "MemoryNodes": len(timelines),
            "TokenEstimate": token_stats["layer2_used"],
            "Savings": token_stats["savings_estimate"],
            "PrivacyFilter": self._privacy_filter.get_stats(),
        }
        context.metadata["context_injection_stats"] = stats
        
        privacy_report = self._privacy_filter.report()
        if self._privacy_filter.get_stats()["total_detections"] > 0:
            context.metadata["privacy_filter_report"] = privacy_report
        
        print()
        print("=" * 60)
        print("Context Injected: Progressive Disclosure Layer 2")
        print("=" * 60)
        print()
        print("You now have access to:")
        print("  - Requirement details")
        print("  - Design decision rationale")
        print("  - Chronological context")
        print()
        print("To get even more details for specific nodes:")
        print("  - Call get_memory_full_details(ids=['node_id_1', 'node_id_2'])")
        print("  - This will show complete content + alternatives + rationale")
        print()
        print("=" * 60)
        print()
    
    def _inject_full_context(
        self,
        context,
        feature_name: str,
        memory: ConversationMemory,
    ):
        """
        传统全量注入方式（向后兼容）
        
        直接注入全部内容，可能消耗大量token
        
        Privacy Filter: 在注入前过滤敏感数据
        """
        context_parts = []
        stats = {}
        
        agents_file = self.project_root / "AGENTS.md"
        if agents_file.exists():
            agents_content = agents_file.read_text(encoding="utf-8")
            agents_content = self._privacy_filter.filter_context_summary(agents_content)
            context_parts.append(agents_content)
            context.metadata["agents_context_loaded"] = True
            stats["AGENTS.md"] = f"{len(agents_content)} chars"
        else:
            context.metadata["agents_context_loaded"] = False
            stats["AGENTS.md"] = "not found"
        
        if memory and memory.nodes:
            filtered_memory = self._apply_privacy_filter(memory)
            summary = filtered_memory.get_context_summary()
            if summary and summary != "No conversation memory recorded yet.":
                context_parts.append(
                    f"\n## 会话记忆 (ConversationMemory)\n\n{summary}"
                )
                stats["ConversationMemory"] = f"{len(filtered_memory.nodes)} nodes"
            context.metadata["conversation_memory_summary"] = summary
            
            privacy_stats = self._privacy_filter.get_stats()
            stats["PrivacyFilter"] = privacy_stats
        else:
            stats["ConversationMemory"] = "no nodes"
        
        feature_dir = self.project_root / "docs" / "features" / feature_name
        if feature_dir.exists():
            for filename in ["task_plan.md", "findings.md", "design-doc.md"]:
                filepath = feature_dir / filename
                if filepath.exists():
                    content = filepath.read_text(encoding="utf-8")
                    context_parts.append(f"\n## {filename}\n\n{content[:2000]}")
                    stats[filename] = f"{len(content)} chars"
            context.metadata["feature_artifacts_loaded"] = True
        
        if context_parts:
            combined = "\n\n".join(context_parts)
            context.metadata["injected_context"] = combined
            context.metadata["context_injected"] = True
            
            context_dir = feature_dir / ".sdd"
            context_dir.mkdir(parents=True, exist_ok=True)
            context_file = context_dir / "current_context.md"
            context_file.write_text(combined, encoding="utf-8")
            stats["current_context.md"] = f"{len(combined)} chars written"
        else:
            context.metadata["context_injected"] = False
            stats["current_context.md"] = "empty"
        
        context.metadata["context_injection_stats"] = stats
    
    def _apply_privacy_filter(self, memory: ConversationMemory) -> ConversationMemory:
        """
        应用 Privacy Filter
        
        在注入 context 前过滤敏感数据
        
        Args:
            memory: ConversationMemory instance
        
        Returns:
            filtered ConversationMemory instance
        """
        if not memory or not memory.nodes:
            return memory
        
        self._privacy_filter.clear_detection_log()
        
        filtered_nodes = self._privacy_filter.filter_nodes(list(memory.nodes.values()))
        
        from .memory import ConversationMemory
        filtered_memory = ConversationMemory(
            feature_name=memory.feature_name,
            project_root=memory.project_root,
        )
        
        for node in filtered_nodes:
            filtered_memory.nodes[node.id] = node
        
        for chain_id, chain in memory.decision_chains.items():
            filtered_memory.decision_chains[chain_id] = chain
        
        return filtered_memory
    
    def print_context_to_stdout(self, context, feature_name: str):
        """
        将注入的上下文输出到 stdout。
        
        改进：支持 Progressive Disclosure 输出
        """
        stats = context.metadata.get("context_injection_stats", {})
        injected = context.metadata.get("injected_context", "")
        progressive_enabled = context.metadata.get("progressive_disclosure_enabled", False)
        
        print()
        print("=" * 60)
        print("  CONTEXT RECOVERY — 跨会话上下文恢复")
        print("=" * 60)
        print()
        
        if stats:
            print("上下文来源:")
            for source, info in stats.items():
                print(f"   {source}: {info}")
        
        if progressive_enabled:
            print()
            print("[INFO] Progressive Disclosure enabled (Layer 1)")
            print()
            token_stats = context.metadata.get("progressive_disclosure_token_stats", {})
            if token_stats:
                print(f"   Token estimate: ~{token_stats.get('layer1_used', 0)} tokens")
                print(f"   Savings: {token_stats.get('savings_estimate', 'N/A')}")
            print()
            print("To view more context, use:")
            print("   - get_memory_timeline(around_id='xxx') — Layer 2")
            print("   - get_memory_full_details(ids=['xxx']) — Layer 3")
        
        if injected:
            print()
            print("-" * 60)
            if progressive_enabled:
                print("  INJECTED CONTEXT (Memory Index + AGENTS.md summary)")
            else:
                print("  INJECTED CONTEXT (AGENTS.md + Memory + Artifacts)")
            print("-" * 60)
            print()
            truncated = injected[:6000]
            print(truncated)
            if len(injected) > 6000:
                print()
                print(f"... (truncated, full context in .sdd/current_context.md)")
            print()
            print("-" * 60)
            print("  END OF INJECTED CONTEXT")
            print("-" * 60)
        
        print()
        if progressive_enabled:
            print("[INFO] 以上是Memory索引（Layer 1）。按需调用Layer 2/3获取详情。")
        else:
            print("[INFO] 以上是上一会话的完整上下文。请基于此继续开发。")
        print()