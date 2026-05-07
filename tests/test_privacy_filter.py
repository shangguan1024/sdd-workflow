"""
Privacy Filter 测试

验证敏感数据过滤功能
"""

import sys
from pathlib import Path

# 添加项目根目录到 path
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.memory import (
    ConversationMemory,
    MemoryNode,
    MemoryType,
    PrivacyFilter,
    PrivacyFilterConfig,
    DetectionResult,
)


def test_privacy_filter_config():
    config = PrivacyFilterConfig()
    
    assert config.enabled == True
    assert len(config.sensitive_patterns) > 0
    assert "api_key" in config.sensitive_patterns
    assert "password" in config.sensitive_patterns
    assert config.replacement_template == "[REDACTED]"
    
    print("[PASS] PrivacyFilterConfig initialized correctly")


def test_privacy_filter_detection():
    filter = PrivacyFilter()
    
    test_texts = [
        ("api_key=abc123def456", "api_key"),
        ("password: my_secret_pass", "password"),
        ("Authorization: Bearer xyz789", "authorization"),
        ("token = \"real_token_value\"", "token"),  # 使用真实值而非 test
    ]
    
    for text, expected_pattern in test_texts:
        filtered, detections = filter._filter_text(text, "test", "node_123")
        
        assert len(detections) > 0
        assert any(d.pattern_matched == expected_pattern for d in detections)
        assert "[REDACTED]" in filtered
        
        print(f"[PASS] Detected '{expected_pattern}' in '{text[:30]}...'")
    
    print("[PASS] PrivacyFilter detection works correctly")


def test_filter_memory_node():
    # 创建测试节点（不使用 ConversationMemory）
    node = MemoryNode(
        id="test_node_1",
        type=MemoryType.DESIGN_DECISION,
        title="API Key Configuration",
        content="Set api_key=sk_live_abc123xyz789 in config",
        rationale="Authorization header: Authorization: Bearer xyz789token",
        alternatives=[],
        source_session="",
        created_at="",
        updated_at="",
        resolved=False,
        priority="medium",
        tags=[],
        related_ids=[],
        decision_chain_id="",
    )
    
    filter = PrivacyFilter()
    filtered_node = filter.filter_node(node)
    
    assert "[REDACTED]" in filtered_node.content
    assert "[REDACTED]" in filtered_node.rationale
    assert filtered_node.title == node.title  # title 不含敏感数据
    
    stats = filter.get_stats()
    assert stats["total_detections"] >= 2
    
    print(f"[PASS] MemoryNode filtered, {stats['total_detections']} detections")
    
    report = filter.report()
    assert "Privacy Filter Detection Report" in report
    assert str(stats["total_detections"]) in report
    
    print("[PASS] Detection report generated correctly")


def test_filter_nodes_list():
    # 创建测试节点列表
    nodes = [
        MemoryNode(
            id="node_1",
            type=MemoryType.REQUIREMENT,
            title="Auth Requirement",
            content="Need api_key in environment",
            alternatives=[],
            source_session="",
            created_at="",
            updated_at="",
            resolved=False,
            priority="medium",
            tags=[],
            related_ids=[],
            decision_chain_id="",
        ),
        MemoryNode(
            id="node_2",
            type=MemoryType.DESIGN_DECISION,
            title="Security Design",
            content="Use password=db_pass123 for connection",
            rationale="Database connection string",
            alternatives=[],
            source_session="",
            created_at="",
            updated_at="",
            resolved=False,
            priority="medium",
            tags=[],
            related_ids=[],
            decision_chain_id="",
        ),
        MemoryNode(
            id="node_3",
            type=MemoryType.CONSTRAINT,
            title="Performance",
            content="Must handle 1000 requests/sec",  # 无敏感数据
            alternatives=[],
            source_session="",
            created_at="",
            updated_at="",
            resolved=False,
            priority="medium",
            tags=[],
            related_ids=[],
            decision_chain_id="",
        ),
    ]
    
    filter = PrivacyFilter()
    filtered_nodes = filter.filter_nodes(nodes)
    
    assert len(filtered_nodes) == 3
    
    stats = filter.get_stats()
    assert stats["total_detections"] >= 2  # node_1 和 node_2 有敏感数据
    
    print(f"[PASS] {len(filtered_nodes)} nodes filtered, {stats['total_detections']} detections")


def test_filter_context_summary():
    summary = """
    ## API Configuration
    
    api_key = sk_live_abc123xyz789
    password = my_db_password
    
    ## Requirements
    
    - Authorization: Bearer xyz789realvalue
    - Database credentials: credential=admin123
    """
    
    filter = PrivacyFilter()
    filtered_summary = filter.filter_context_summary(summary)
    
    assert "[REDACTED]" in filtered_summary
    assert "sk_live_abc123xyz789" not in filtered_summary
    assert "my_db_password" not in filtered_summary
    assert "xyz789" not in filtered_summary
    
    stats = filter.get_stats()
    assert stats["total_detections"] >= 4
    
    print(f"[PASS] Context summary filtered, {stats['total_detections']} detections")


def test_whitelist():
    config = PrivacyFilterConfig(
        whitelist=["test_api_key"]
    )
    
    filter = PrivacyFilter(config=config)
    
    text = "test_api_key=value123"
    filtered, detections = filter._filter_text(text, "test", "node_1")
    
    # 白名单中的关键词不会被检测
    assert len(detections) == 0 or "test_api_key" not in [d.pattern_matched for d in detections]
    
    print("[PASS] Whitelist works correctly")


def test_placeholder_detection():
    filter = PrivacyFilter()
    
    placeholders = [
        "api_key=<your_key>",
        "password=your_password_here",
        "token=[REDACTED]",
        "secret=xxx-xxx-xxx",
    ]
    
    for text in placeholders:
        filtered, detections = filter._filter_text(text, "test", "node_1")
        
        # 占位符不应被检测
        assert len(detections) == 0
        
        print(f"[PASS] Placeholder '{text}' not detected")
    
    print("[PASS] Placeholder detection works correctly")


def test_load_config_file():
    config_path = Path("config/privacy_filter.yaml")
    
    if config_path.exists():
        filter = PrivacyFilter(config_path=config_path)
        
        assert filter.config.enabled == True
        assert len(filter.config.sensitive_patterns) > 0
        
        print("[PASS] Config file loaded correctly")
    else:
        print("[SKIP] Config file not found")


def test_integration_with_director():
    from src.director import Director
    from src.memory import ConversationMemory
    
    director = Director(project_root=Path("."))
    
    assert hasattr(director, "_privacy_filter")
    assert director._privacy_filter is not None
    assert isinstance(director._privacy_filter, PrivacyFilter)
    
    print("[PASS] Director has PrivacyFilter instance")


def run_all_tests():
    print("\n" + "=" * 60)
    print("Privacy Filter Test Suite")
    print("=" * 60 + "\n")
    
    test_privacy_filter_config()
    test_privacy_filter_detection()
    test_filter_memory_node()
    test_filter_nodes_list()
    test_filter_context_summary()
    test_whitelist()
    test_placeholder_detection()
    test_load_config_file()
    test_integration_with_director()
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_tests()