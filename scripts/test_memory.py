"""
Tests for ConversationMemory, MemoryPersistence, MemoryRecovery.
Validates the multi-turn conversation memory system.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from memory.conversation import (
    ConversationMemory,
    MemoryNode,
    MemoryType,
    DecisionChain,
)
from memory.persistence import MemoryPersistence
from memory.recovery import MemoryRecovery


class TestConversationMemory:
    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.memory = ConversationMemory("test-feature", self.temp_dir)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_requirement(self):
        self.memory.start_session("session-001")
        node = self.memory.add_requirement(
            "支持自定义日志格式",
            "用户需要可以通过配置文件自定义日志输出格式",
            priority="high",
            tags=["logging", "config"],
        )

        assert node.id is not None
        assert node.type == MemoryType.REQUIREMENT
        assert node.title == "支持自定义日志格式"
        assert node.priority == "high"
        assert "config" in node.tags
        assert node.source_session == "session-001"

        reqs = self.memory.get_requirements()
        assert len(reqs) == 1
        assert reqs[0].id == node.id

    def test_add_design_decision_with_chain(self):
        self.memory.start_session("session-001")

        node1 = self.memory.add_design_decision(
            "使用策略模式实现格式解析",
            "采用策略模式，每种格式实现 Formatter 接口",
            rationale="易于扩展新格式，符合开闭原则",
            alternatives=["工厂模式", "配置驱动"],
            decision_chain_id="format-strategy",
        )

        chain = self.memory.get_decision_chain("format-strategy")
        assert chain is not None
        assert len(chain.nodes) == 1

        node2 = self.memory.add_design_decision(
            "使用解析器组合模式替代策略模式",
            "改用解析器组合模式实现格式解析",
            rationale="更灵活的组合方式，允许嵌套格式",
            alternatives=["保持策略模式", "函数式管道"],
            decision_chain_id="format-strategy",
        )

        assert len(chain.nodes) == 2
        trace = chain.trace()
        assert len(trace) == 2
        assert trace[0]["decision"] == "采用策略模式，每种格式实现 Formatter 接口"
        assert trace[1]["decision"] == "改用解析器组合模式实现格式解析"

    def test_add_and_resolve_question(self):
        self.memory.start_session("session-002")

        q = self.memory.add_open_question(
            "性能目标是什么",
            "日志写入的吞吐量目标是多少条/秒?",
            tags=["performance"],
        )

        assert q.type == MemoryType.OPEN_QUESTION
        assert not q.resolved

        resolved = self.memory.resolve_question(q.id, "目标: 10000 条/秒")
        assert resolved

        updated = self.memory.nodes[q.id]
        assert updated.resolved
        assert updated.rationale == "目标: 10000 条/秒"

        open_qs = self.memory.get_open_questions()
        assert len(open_qs) == 0

    def test_add_rejected_alternative(self):
        self.memory.start_session("session-003")

        node = self.memory.add_rejected_alternative(
            "使用宏生成格式代码",
            "通过 Rust 宏在编译期生成格式解析代码",
            rejection_reason="编译时间增加 3 倍，调试困难",
            tags=["macro", "perf"],
        )

        rejected = self.memory.get_rejected_alternatives()
        assert len(rejected) == 1
        assert "宏" in rejected[0].title
        assert "编译时间增加" in rejected[0].content

    def test_get_context_summary(self):
        self.memory.start_session("session-004")

        self.memory.add_requirement(
            "需求A", "详细描述A", priority="high"
        )
        self.memory.add_design_decision(
            "决策1", "采用方案X",
            rationale="性能最优",
            alternatives=["方案Y", "方案Z"],
        )
        self.memory.add_open_question("问题1", "如何实现X?")
        self.memory.add_assumption("假设1", "数据库可用", validated=True)

        summary = self.memory.get_context_summary()
        assert "需求A" in summary
        assert "决策1" in summary
        assert "方案X" in summary
        assert "方案Y" in summary
        assert "问题1" in summary
        assert "假设1" in summary

    def test_memory_snapshot_roundtrip(self):
        self.memory.start_session("session-005")

        self.memory.add_requirement("R1", "需求1")
        self.memory.add_design_decision(
            "D1", "决策1", rationale="理由",
            decision_chain_id="chain-1",
        )
        self.memory.add_research_finding("F1", "发现1")
        self.memory.add_constraint("C1", "约束1", priority="high")

        snapshot = self.memory.get_memory_snapshot()
        assert snapshot["feature_name"] == "test-feature"
        assert len(snapshot["nodes"]) == 5
        assert "chain-1" in snapshot["decision_chains"]

        restored = ConversationMemory.from_snapshot(snapshot, self.temp_dir)
        assert len(restored.nodes) == 5
        assert len(restored.get_requirements()) == 1
        assert len(restored.get_design_decisions()) == 1
        assert len(restored.get_decision_chain("chain-1").nodes) == 1

        req = restored.get_requirements()[0]
        assert req.title == "R1"
        assert req.content == "需求1"

    def test_search_memory(self):
        self.memory.start_session("session-006")

        self.memory.add_requirement("日志格式", "支持JSON和文本格式")
        self.memory.add_requirement("性能", "吞吐量 > 10000/s")
        self.memory.add_design_decision("格式引擎", "使用template engine")

        results = self.memory.search("JSON")
        assert len(results) == 1
        assert results[0].title == "日志格式"

        results = self.memory.search("性能")
        assert len(results) == 1

        results = self.memory.search("template")
        assert len(results) == 1

    def test_unresolved_nodes_tracking(self):
        self.memory.start_session("session-007")

        self.memory.add_open_question("Q1", "问题1")
        self.memory.add_open_question("Q2", "问题2")
        q3 = self.memory.add_open_question("Q3", "问题3")
        self.memory.resolve_question(q3.id, "答案3")

        unresolved = self.memory.get_unresolved_nodes()
        assert len(unresolved) == 2

    def test_update_node(self):
        self.memory.start_session("session-008")

        node = self.memory.add_requirement("R1", "原始描述")
        updated = self.memory.update_node(
            node.id,
            content="更新后的描述",
            priority="high",
        )

        assert updated
        refreshed = self.memory.nodes[node.id]
        assert refreshed.content == "更新后的描述"
        assert refreshed.priority == "high"

    def test_delete_node(self):
        self.memory.start_session("session-008")

        node = self.memory.add_requirement("temp", "临时需求")
        assert node.id in self.memory.nodes

        deleted = self.memory.delete_node(node.id)
        assert deleted
        assert node.id not in self.memory.nodes

    def test_add_change_log(self):
        self.memory.start_session("session-009")

        log = self.memory.add_change_log(
            "需求变更: 格式从 JSON 改为 YAML",
            "用户反馈 JSON 格式可读性差，改为 YAML",
            tags=["change", "format"],
        )

        changes = self.memory.get_by_type(MemoryType.CHANGE_LOG)
        assert len(changes) == 1
        assert "YAML" in changes[0].content


class TestMemoryPersistence:
    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.persistence = MemoryPersistence(self.temp_dir)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load(self):
        memory = ConversationMemory("test-feature", self.temp_dir)
        memory.start_session("test-session")
        memory.add_requirement("R1", "需求1")
        memory.add_design_decision("D1", "决策1", rationale="理由")

        saved_path = self.persistence.save(memory, "test-feature")
        assert saved_path.exists()

        snapshot = self.persistence.load("test-feature")
        assert snapshot is not None
        assert snapshot["feature_name"] == "test-feature"
        assert len(snapshot["nodes"]) == 3

    def test_history_retention(self):
        memory = ConversationMemory("test-feature", self.temp_dir)
        memory.start_session("s1")
        memory.add_requirement("R1", "第一轮需求")
        self.persistence.save(memory, "test-feature")

        memory.start_session("s2")
        memory.add_design_decision("D1", "第一轮决策")
        self.persistence.save(memory, "test-feature")

        history = self.persistence.list_history("test-feature")
        assert len(history) >= 2

    def test_backup_recovery(self):
        memory = ConversationMemory("test-feature", self.temp_dir)
        memory.start_session("s")
        memory.add_requirement("R1", "test")
        self.persistence.save(memory, "test-feature")

        mem_dir = self.persistence.memory_dir("test-feature")
        main_file = mem_dir / MemoryPersistence.MEMORY_FILE
        main_file.write_text("corrupted json{{{")

        snapshot = self.persistence.load("test-feature")
        assert snapshot is not None
        assert snapshot["feature_name"] == "test-feature"

    def test_exists(self):
        assert not self.persistence.exists("nonexistent")

        memory = ConversationMemory("test-feature", self.temp_dir)
        memory.start_session("s")
        self.persistence.save(memory, "test-feature")

        assert self.persistence.exists("test-feature")

    def test_delete(self):
        memory = ConversationMemory("test-feature", self.temp_dir)
        memory.start_session("s")
        memory.add_requirement("R1", "test")
        self.persistence.save(memory, "test-feature")

        assert self.persistence.exists("test-feature")
        self.persistence.delete("test-feature")

        mem_dir = self.persistence.memory_dir("test-feature")
        main_file = mem_dir / MemoryPersistence.MEMORY_FILE
        backup_file = mem_dir / MemoryPersistence.BACKUP_FILE
        assert not main_file.exists()
        assert not backup_file.exists()


class TestMemoryRecovery:
    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.recovery = MemoryRecovery(self.temp_dir)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_recover_empty(self):
        memory = self.recovery.recover("nonexistent")
        assert memory is None

    def test_recover_or_create(self):
        memory = self.recovery.recover_or_create("new-feature")
        assert memory is not None
        assert memory.feature_name == "new-feature"
        assert len(memory.nodes) == 0

    def test_recover_after_save(self):
        persistence = MemoryPersistence(self.temp_dir)
        memory = ConversationMemory("test-feature", self.temp_dir)
        memory.start_session("s1")
        memory.add_requirement("R1", "需求描述")
        memory.add_design_decision("D1", "设计决策", rationale="原因")
        persistence.save(memory, "test-feature")

        recovered = self.recovery.recover("test-feature")
        assert recovered is not None
        assert recovered.feature_name == "test-feature"
        assert len(recovered.get_requirements()) == 1
        assert len(recovered.get_design_decisions()) == 1

        req = recovered.get_requirements()[0]
        assert req.title == "R1"
        assert req.content == "需求描述"

    def test_merge_sessions(self):
        persistence = MemoryPersistence(self.temp_dir)

        memory1 = ConversationMemory("test-feature", self.temp_dir)
        memory1.start_session("s1")
        memory1.add_requirement("R1", "session1 的需求")
        persistence.save(memory1, "test-feature")

        memory2 = ConversationMemory("test-feature", self.temp_dir)
        memory2.start_session("s2")
        memory2.add_design_decision("D1", "session2 的决策",
                                     rationale="新理由")
        snapshot2 = memory2.get_memory_snapshot()

        merged = self.recovery.merge_sessions("test-feature", snapshot2)
        assert len(merged.get_requirements()) == 1
        assert len(merged.get_design_decisions()) == 1
        assert merged.get_requirements()[0].content == "session1 的需求"
        assert merged.get_design_decisions()[0].content == "session2 的决策"

    def test_get_memory_summary(self):
        persistence = MemoryPersistence(self.temp_dir)
        memory = ConversationMemory("test-feature", self.temp_dir)
        memory.start_session("s1")
        memory.add_requirement("R1", "需求1")
        memory.add_open_question("Q1", "问题1")
        persistence.save(memory, "test-feature")

        summary = self.recovery.get_memory_summary("test-feature")
        assert "test-feature" in summary
        assert "R1" in summary
        assert "Q1" in summary
        assert "Open Questions" in summary


class TestDecisionChain:
    def test_trace_empty(self):
        chain = DecisionChain("chain-1")
        assert chain.trace() == []
        assert chain.latest() is None

    def test_trace_multiple_decisions(self):
        chain = DecisionChain("chain-1")
        from datetime import datetime

        chain.nodes = [
            MemoryNode(
                id="1", type=MemoryType.DESIGN_DECISION,
                title="第一版", content="决策A",
                rationale="简单",
                created_at="2024-01-01T00:00:00",
                source_session="s1",
            ),
            MemoryNode(
                id="2", type=MemoryType.DESIGN_DECISION,
                title="第二版", content="决策B",
                rationale="更优",
                created_at="2024-01-02T00:00:00",
                source_session="s2",
            ),
        ]

        trace = chain.trace()
        assert len(trace) == 2
        assert trace[0]["decision"] == "决策A"
        assert trace[1]["decision"] == "决策B"

        latest = chain.latest()
        assert latest.id == "2"


class TestMultiTurnScenario:
    """Simulate a realistic multi-turn conversation flow."""
    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.recovery = MemoryRecovery(self.temp_dir)
        self.persistence = MemoryPersistence(self.temp_dir)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_multi_turn_workflow(self):
        # ---- Session 1: Initial requirements discussion ----
        memory = self.recovery.recover_or_create("logging-system")
        memory.start_session("s1-init")

        memory.add_requirement(
            "支持异步日志写入",
            "日志写入不应阻塞主业务逻辑",
            priority="high",
        )
        memory.add_requirement(
            "支持日志文件轮转",
            "按大小或时间自动轮转日志文件",
            priority="medium",
        )
        memory.add_constraint(
            "内存上限 100MB",
            "日志缓冲区内存使用不能超过 100MB",
            priority="high",
        )
        memory.add_open_question(
            "异步写入的并发策略",
            "使用 channel 还是 lock-free queue?",
            tags=["concurrency", "design"],
        )
        memory.add_assumption(
            "单进程环境",
            "假设日志系统运行在单进程环境",
            validated=False,
        )

        self.persistence.save(memory, "logging-system")

        # ---- Session 2: Design discussion ----
        memory = self.recovery.recover("logging-system")
        assert memory is not None

        # verify session 1 context is preserved
        reqs = memory.get_requirements()
        assert len(reqs) == 2
        assert reqs[0].title == "支持异步日志写入"

        unanswered = memory.get_open_questions()
        assert len(unanswered) == 1
        assert "并发策略" in unanswered[0].title

        # answer the question and make design decisions
        memory.start_session("s2-design")
        q_id = unanswered[0].id
        memory.resolve_question(q_id, "使用 tokio::mpsc channel，配合批量写入")

        memory.add_design_decision(
            "使用 tokio channel 做异步写入",
            "使用 tokio::mpsc::channel，Writer 消费消息并批量写入",
            rationale="tokio 生态成熟，channel 语义清晰",
            alternatives=["crossbeam channel", "lock-free SPSC queue"],
            decision_chain_id="async-write-strategy",
            tags=["concurrency", "tokio"],
        )
        memory.add_rejected_alternative(
            "lock-free SPSC queue",
            "使用自定义 lock-free SPSC queue",
            rejection_reason="实现复杂度高，维护成本大，性能提升有限",
        )

        self.persistence.save(memory, "logging-system")

        # ---- Session 3: Design refinement ----
        memory = self.recovery.recover("logging-system")
        memory.start_session("s3-refinement")

        # verify all previous context
        assert len(memory.get_requirements()) == 2
        assert len(memory.get_design_decisions()) == 1
        assert len(memory.get_rejected_alternatives()) == 1
        assert len(memory.get_open_questions()) == 0
        assert len(memory.get_unresolved_nodes()) == 0

        # refine design
        chain = memory.get_decision_chain("async-write-strategy")
        assert chain is not None
        assert len(chain.nodes) == 1

        memory.add_design_decision(
            "改用异步批量写入 + backpressure",
            "在 channel 基础上增加 backpressure 机制",
            rationale="防止生产者速度远超消费者导致 OOM",
            decision_chain_id="async-write-strategy",
            tags=["concurrency", "backpressure"],
        )

        assert len(chain.nodes) == 2
        trace = chain.trace()
        assert len(trace) == 2
        assert "tokio" in trace[0]["decision"]
        assert "backpressure" in trace[1]["decision"]

        memory.add_change_log(
            "增加 backpressure 机制",
            "根据 Session 3 讨论，增加背压防止内存溢出",
            tags=["change", "memory"],
        )

        self.persistence.save(memory, "logging-system")

        # ---- Session 4: Verify full context recovery ----
        memory = self.recovery.recover("logging-system")
        memory.start_session("s4-verify")

        summary = memory.get_context_summary()
        assert "支持异步日志写入" in summary
        assert "支持日志文件轮转" in summary
        assert "内存上限 100MB" in summary
        assert "tokio channel" in summary
        assert "backpressure" in summary
        assert "lock-free SPSC queue" in summary
        assert "增加 backpressure 机制" in summary

        # verify search works across sessions
        results = memory.search("backpressure")
        assert len(results) >= 1
        results = memory.search("单进程")
        assert len(results) == 1

        # verify no critical info is lost
        snapshot = memory.get_memory_snapshot()
        assert len(snapshot["nodes"]) >= 9  # requirements + decisions + etc
        assert "async-write-strategy" in snapshot["decision_chains"]


if __name__ == "__main__":
    passed = 0
    failed = 0
    errors = []

    test_classes = [
        TestConversationMemory,
        TestMemoryPersistence,
        TestMemoryRecovery,
        TestDecisionChain,
        TestMultiTurnScenario,
    ]

    for cls in test_classes:
        instance = cls()
        instance.setup_method()
        print(f"\n{'='*60}")
        print(f"Running: {cls.__name__}")
        print(f"{'='*60}")

        for method_name in sorted(dir(instance)):
            if method_name.startswith("test_"):
                method = getattr(instance, method_name)
                try:
                    method()
                    print(f"  ✅ {method_name}")
                    passed += 1
                except Exception as e:
                    print(f"  ❌ {method_name}: {e}")
                    failed += 1
                    errors.append(f"{cls.__name__}.{method_name}: {e}")

        instance.teardown_method()

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    if errors:
        print("\nFailures:")
        for e in errors:
            print(f"  - {e}")
    print(f"{'='*60}")

    sys.exit(1 if failed > 0 else 0)
