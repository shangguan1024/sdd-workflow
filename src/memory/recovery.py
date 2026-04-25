"""
Memory Recovery: restore conversation memory from persistence and merge sessions.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from .conversation import ConversationMemory
from .persistence import MemoryPersistence


class MemoryRecovery:
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.persistence = MemoryPersistence(project_root)

    def recover(self, feature_name: str) -> Optional[ConversationMemory]:
        snapshot = self.persistence.load(feature_name)
        if not snapshot:
            return self._create_empty(feature_name)

        memory = ConversationMemory.from_snapshot(snapshot, self.project_root)
        return memory

    def recover_or_create(self, feature_name: str) -> ConversationMemory:
        memory = self.recover(feature_name)
        if memory is None:
            memory = self._create_empty(feature_name)
        return memory

    def merge_sessions(self, feature_name: str,
                       additional_snapshot: dict) -> ConversationMemory:
        existing = self.recover_or_create(feature_name)

        for nid, node_data in additional_snapshot.get("nodes", {}).items():
            if nid in existing.nodes:
                existing_node = existing.nodes[nid]
                if node_data.get("updated_at", "") > existing_node.updated_at:
                    existing.update_node(nid,
                                         content=node_data.get("content", ""),
                                         rationale=node_data.get("rationale", ""),
                                         updated_at=node_data.get("updated_at", ""),
                                         resolved=node_data.get("resolved", False))
            else:
                from .conversation import MemoryNode
                existing.nodes[nid] = MemoryNode.from_dict(node_data)

        for cid, chain_nodes in additional_snapshot.get("decision_chains", {}).items():
            if cid not in existing.decision_chains:
                from .conversation import DecisionChain
                chain = DecisionChain(cid)
                for node_data in chain_nodes:
                    chain.nodes.append(
                        existing.nodes.get(node_data["id"])
                        or MemoryNode.from_dict(node_data)
                    )
                existing.decision_chains[cid] = chain

        return existing

    def get_memory_summary(self, feature_name: str) -> str:
        memory = self.recover(feature_name)
        if not memory:
            return f"No conversation memory found for feature '{feature_name}'."

        sections = []
        sections.append(f"# Conversation Memory: {feature_name}")
        sections.append(f"Last saved: {datetime.now().isoformat()}")
        sections.append(f"Total memory nodes: {len(memory.nodes)}")
        sections.append(f"Open questions: {len(memory.get_open_questions())}")
        sections.append(f"Unresolved items: {len(memory.get_unresolved_nodes())}")
        sections.append("")

        sections.append("## Requirements")
        sections.append(f"Count: {len(memory.get_requirements())}")
        for r in memory.get_requirements():
            sections.append(f"  - [{r.priority}] {r.title}")

        sections.append("")
        sections.append("## Design Decisions")
        for d in memory.get_design_decisions():
            sections.append(f"  - {d.title} (session: {d.source_session})")

        sections.append("")
        sections.append("## Rejected Alternatives")
        for r in memory.get_rejected_alternatives():
            sections.append(f"  - {r.title}")

        sections.append("")
        sections.append("## Open Questions")
        for q in memory.get_open_questions():
            sections.append(f"  - {q.title}: {q.content}")

        sections.append("")
        sections.append("## Decision Chains")
        for cid, chain in memory.decision_chains.items():
            sections.append(f"  ### Chain: {cid}")
            sections.append(f"  Nodes: {len(chain.nodes)}")
            latest = chain.latest()
            if latest:
                sections.append(f"  Latest: {latest.title} -> {latest.content[:100]}")

        return "\n".join(sections)

    def _create_empty(self, feature_name: str) -> ConversationMemory:
        return ConversationMemory(feature_name, self.project_root)
