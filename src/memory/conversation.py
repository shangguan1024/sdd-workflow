"""
ConversationMemory: structured capture of multi-turn dialogue context.
Preserves key requirements, design decisions, and rationale across sessions.
"""

import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class MemoryType(Enum):
    REQUIREMENT = "requirement"
    DESIGN_DECISION = "design_decision"
    RESEARCH_FINDING = "research_finding"
    DISCUSSION_POINT = "discussion_point"
    CONSTRAINT = "constraint"
    ASSUMPTION = "assumption"
    REJECTED_ALTERNATIVE = "rejected_alternative"
    OPEN_QUESTION = "open_question"
    CHANGE_LOG = "change_log"


@dataclass
class MemoryNode:
    id: str
    type: MemoryType
    title: str
    content: str
    rationale: str = ""
    alternatives: list = field(default_factory=list)
    source_session: str = ""
    created_at: str = ""
    updated_at: str = ""
    resolved: bool = False
    priority: str = "medium"
    tags: list = field(default_factory=list)
    related_ids: list = field(default_factory=list)
    decision_chain_id: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "content": self.content,
            "rationale": self.rationale,
            "alternatives": self.alternatives,
            "source_session": self.source_session,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "resolved": self.resolved,
            "priority": self.priority,
            "tags": self.tags,
            "related_ids": self.related_ids,
            "decision_chain_id": self.decision_chain_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryNode":
        return cls(
            id=data["id"],
            type=MemoryType(data["type"]),
            title=data["title"],
            content=data["content"],
            rationale=data.get("rationale", ""),
            alternatives=data.get("alternatives", []),
            source_session=data.get("source_session", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            resolved=data.get("resolved", False),
            priority=data.get("priority", "medium"),
            tags=data.get("tags", []),
            related_ids=data.get("related_ids", []),
            decision_chain_id=data.get("decision_chain_id", ""),
        )


class DecisionChain:
    """Tracks how decisions evolve across multiple sessions."""

    def __init__(self, root_id: str):
        self.nodes: list[MemoryNode] = []
        self.root_id = root_id

    def add(self, node: MemoryNode):
        self.nodes.append(node)

    def trace(self) -> list[dict]:
        """Return a human-readable trace of the decision chain."""
        result = []
        for node in sorted(self.nodes, key=lambda n: n.created_at):
            result.append({
                "title": node.title,
                "decision": node.content,
                "rationale": node.rationale,
                "changed_at": node.created_at,
                "changed_in_session": node.source_session,
            })
        return result

    def latest(self) -> Optional[MemoryNode]:
        return self.nodes[-1] if self.nodes else None


class ConversationMemory:
    """
    Persistent conversation memory across sessions.
    
    Captures:
    - Requirements and their evolution
    - Design decisions with rationale
    - Research findings
    - Discussion points and open questions
    - Rejected alternatives (why certain paths were not taken)
    - Constraints and assumptions
    """

    def __init__(self, feature_name: str, project_root: Path):
        self.feature_name = feature_name
        self.project_root = Path(project_root)
        self.nodes: dict[str, MemoryNode] = {}
        self.decision_chains: dict[str, DecisionChain] = {}
        self.session_id: str = ""
        self._edited_nodes: set = set()
        self._new_nodes: set = set()

    def start_session(self, session_id: str):
        self.session_id = session_id
        self._edited_nodes.clear()
        self._new_nodes.clear()

    def add_requirement(self, title: str, content: str, priority: str = "medium",
                        tags: list = None, related_ids: list = None) -> MemoryNode:
        return self._add_node(MemoryType.REQUIREMENT, title, content,
                              priority=priority, tags=tags, related_ids=related_ids)

    def add_design_decision(self, title: str, content: str, rationale: str = "",
                            alternatives: list = None, tags: list = None,
                            decision_chain_id: str = None) -> MemoryNode:
        node = self._add_node(MemoryType.DESIGN_DECISION, title, content,
                              rationale=rationale, alternatives=alternatives or [],
                              tags=tags, decision_chain_id=decision_chain_id or "")

        if decision_chain_id:
            if decision_chain_id not in self.decision_chains:
                self.decision_chains[decision_chain_id] = DecisionChain(decision_chain_id)
            self.decision_chains[decision_chain_id].add(node)

        return node

    def add_research_finding(self, title: str, content: str, tags: list = None,
                             related_ids: list = None) -> MemoryNode:
        return self._add_node(MemoryType.RESEARCH_FINDING, title, content,
                              tags=tags, related_ids=related_ids)

    def add_discussion_point(self, title: str, content: str, resolved: bool = False,
                             tags: list = None) -> MemoryNode:
        return self._add_node(MemoryType.DISCUSSION_POINT, title, content,
                              resolved=resolved, tags=tags)

    def add_constraint(self, title: str, content: str, priority: str = "high",
                       tags: list = None) -> MemoryNode:
        return self._add_node(MemoryType.CONSTRAINT, title, content,
                              priority=priority, tags=tags)

    def add_assumption(self, title: str, content: str, validated: bool = False,
                       tags: list = None) -> MemoryNode:
        node = self._add_node(MemoryType.ASSUMPTION, title, content, tags=tags)
        if validated:
            node.resolved = True
        return node

    def add_rejected_alternative(self, title: str, content: str, rejection_reason: str,
                                 tags: list = None) -> MemoryNode:
        return self._add_node(MemoryType.REJECTED_ALTERNATIVE, title,
                              f"方案: {content}\n\n拒绝原因: {rejection_reason}",
                              tags=tags)

    def add_open_question(self, title: str, content: str, resolved: bool = False,
                          tags: list = None) -> MemoryNode:
        return self._add_node(MemoryType.OPEN_QUESTION, title, content,
                              resolved=resolved, tags=tags)

    def add_change_log(self, title: str, content: str, tags: list = None) -> MemoryNode:
        return self._add_node(MemoryType.CHANGE_LOG, title, content, tags=tags)

    def resolve_question(self, node_id: str, answer: str) -> bool:
        node = self.nodes.get(node_id)
        if not node or node.type != MemoryType.OPEN_QUESTION:
            return False
        node.resolved = True
        node.rationale = answer
        node.updated_at = datetime.now().isoformat()
        self._edited_nodes.add(node_id)
        return True

    def update_node(self, node_id: str, **kwargs) -> bool:
        node = self.nodes.get(node_id)
        if not node:
            return False
        for key, value in kwargs.items():
            if hasattr(node, key):
                setattr(node, key, value)
        node.updated_at = datetime.now().isoformat()
        self._edited_nodes.add(node_id)
        return True

    def delete_node(self, node_id: str) -> bool:
        if node_id in self.nodes:
            del self.nodes[node_id]
            return True
        return False

    def get_by_type(self, mem_type: MemoryType) -> list[MemoryNode]:
        return [n for n in self.nodes.values() if n.type == mem_type]

    def get_requirements(self) -> list[MemoryNode]:
        return self.get_by_type(MemoryType.REQUIREMENT)

    def get_design_decisions(self) -> list[MemoryNode]:
        return self.get_by_type(MemoryType.DESIGN_DECISION)

    def get_open_questions(self) -> list[MemoryNode]:
        return [n for n in self.get_by_type(MemoryType.OPEN_QUESTION) if not n.resolved]

    def get_rejected_alternatives(self) -> list[MemoryNode]:
        return self.get_by_type(MemoryType.REJECTED_ALTERNATIVE)

    def get_unresolved_nodes(self) -> list[MemoryNode]:
        return [n for n in self.nodes.values() if not n.resolved]

    def get_decision_chain(self, chain_id: str) -> Optional[DecisionChain]:
        return self.decision_chains.get(chain_id)

    def search(self, keyword: str) -> list[MemoryNode]:
        keyword_lower = keyword.lower()
        results = []
        for node in self.nodes.values():
            if (keyword_lower in node.title.lower()
                    or keyword_lower in node.content.lower()
                    or keyword_lower in node.rationale.lower()
                    or any(keyword_lower in t.lower() for t in node.tags)):
                results.append(node)
        return results

    def get_context_summary(self) -> str:
        """Generate a comprehensive context summary for injection into new sessions."""

        sections = []

        requirements = self.get_requirements()
        if requirements:
            sections.append("## 已捕获的需求\n")
            for r in sorted(requirements, key=lambda n: n.created_at):
                sections.append(f"### [{r.priority.upper()}] {r.title}")
                sections.append(f"{r.content}\n")

        decisions = self.get_design_decisions()
        if decisions:
            sections.append("## 已作出的设计决策\n")
            for d in sorted(decisions, key=lambda n: n.created_at, reverse=True):
                sections.append(f"### {d.title}")
                sections.append(f"**决策**: {d.content}")
                if d.rationale:
                    sections.append(f"**理据**: {d.rationale}")
                if d.alternatives:
                    sections.append("**考虑过的方案**:")
                    for alt in d.alternatives:
                        sections.append(f"  - {alt}")
                sections.append("")

        findings = self.get_by_type(MemoryType.RESEARCH_FINDING)
        if findings:
            sections.append("## 研究发现\n")
            for f in sorted(findings, key=lambda n: n.created_at):
                sections.append(f"### {f.title}")
                sections.append(f"{f.content}\n")

        constraints = self.get_by_type(MemoryType.CONSTRAINT)
        if constraints:
            sections.append("## 约束条件\n")
            for c in sorted(constraints, key=lambda n: n.created_at):
                sections.append(f"- **[{c.priority.upper()}] {c.title}**: {c.content}\n")

        rejected = self.get_rejected_alternatives()
        if rejected:
            sections.append("## 已拒绝的方案\n")
            for r in rejected:
                sections.append(f"### {r.title}")
                sections.append(f"{r.content}\n")

        questions = self.get_open_questions()
        if questions:
            sections.append("## 待解决问题\n")
            for q in questions:
                sections.append(f"- **{q.title}**: {q.content}\n")

        assumptions = self.get_by_type(MemoryType.ASSUMPTION)
        if assumptions:
            sections.append("## 关键假设\n")
            for a in assumptions:
                status = "已验证" if a.resolved else "未验证"
                sections.append(f"- [{status}] **{a.title}**: {a.content}\n")

        changes = self.get_by_type(MemoryType.CHANGE_LOG)
        if changes:
            sections.append("## 变更记录\n")
            for c in sorted(changes, key=lambda n: n.created_at, reverse=True):
                sections.append(f"- **{c.title}**: {c.content}\n")

        return "\n".join(sections) if sections else "No conversation memory recorded yet."

    def get_memory_snapshot(self) -> dict:
        """Full snapshot for persistence."""
        return {
            "feature_name": self.feature_name,
            "session_id": self.session_id,
            "snapshot_time": datetime.now().isoformat(),
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
            "decision_chains": {
                cid: [n.to_dict() for n in chain.nodes]
                for cid, chain in self.decision_chains.items()
            },
        }

    @classmethod
    def from_snapshot(cls, data: dict, project_root: Path) -> "ConversationMemory":
        memory = cls(data["feature_name"], project_root)
        memory.session_id = data.get("session_id", "")

        for nid, node_data in data.get("nodes", {}).items():
            memory.nodes[nid] = MemoryNode.from_dict(node_data)

        for cid, chain_nodes in data.get("decision_chains", {}).items():
            chain = DecisionChain(cid)
            for node_data in chain_nodes:
                node = MemoryNode.from_dict(node_data)
                chain.nodes.append(node)
            memory.decision_chains[cid] = chain

        return memory

    def _add_node(self, mem_type: MemoryType, title: str, content: str,
                  **kwargs) -> MemoryNode:
        node_id = hashlib.sha256(
            f"{mem_type.value}:{title}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        now = datetime.now().isoformat()

        node = MemoryNode(
            id=node_id,
            type=mem_type,
            title=title,
            content=content,
            rationale=kwargs.get("rationale", ""),
            alternatives=kwargs.get("alternatives", []),
            source_session=self.session_id,
            created_at=now,
            updated_at=now,
            resolved=kwargs.get("resolved", False),
            priority=kwargs.get("priority", "medium"),
            tags=kwargs.get("tags", []),
            related_ids=kwargs.get("related_ids", []),
            decision_chain_id=kwargs.get("decision_chain_id", ""),
        )

        self.nodes[node_id] = node
        self._new_nodes.add(node_id)
        return node

    @property
    def pending_changes(self) -> bool:
        return len(self._edited_nodes) > 0 or len(self._new_nodes) > 0

    def get_changed_since(self, timestamp: str) -> list[MemoryNode]:
        return [n for n in self.nodes.values() if n.updated_at > timestamp]


@dataclass
class RequirementCapture:
    title: str
    description: str
    priority: str = "medium"
    acceptance_criteria: list = field(default_factory=list)
    dependencies: list = field(default_factory=list)
    source: str = ""


@dataclass
class DesignDecision:
    title: str
    decision: str
    rationale: str
    alternatives_considered: list = field(default_factory=list)
    tradeoffs: list = field(default_factory=list)
    impact_areas: list = field(default_factory=list)


@dataclass
class ResearchFinding:
    title: str
    finding: str
    source: str
    relevance: str = "medium"
    action_items: list = field(default_factory=list)


@dataclass
class DiscussionPoint:
    title: str
    discussion: str
    conclusion: str = ""
    participants: list = field(default_factory=list)
    resolved: bool = False
