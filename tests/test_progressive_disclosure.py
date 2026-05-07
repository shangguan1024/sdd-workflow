"""
测试脚本 - 验证Progressive Disclosure功能

验证：
1. MemoryIndex生成
2. MemoryTimeline获取
3. MemoryNode完整详情获取
4. Token成本统计
5. Director集成
"""

import json
import sys
from pathlib import Path
from datetime import datetime

_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

print("="*60)
print("Progressive Disclosure 功能验证测试")
print("="*60)
print()

def test_memory_index_generation():
    """测试1: MemoryIndex生成"""
    print("测试1: MemoryIndex生成")
    print("-"*60)
    
    from src.memory import ConversationMemory, MemoryType, ProgressiveDisclosure
    
    memory = ConversationMemory("test-feature", Path("/tmp"))
    
    # 添加几个MemoryNode
    memory.add_requirement("需求1", "支持SQLite数据库", priority="high")
    memory.add_design_decision("决策1", "选择SQLite作为数据库", "SQLite轻量且无需额外服务", priority="high")
    memory.add_research_finding("发现1", "SQLite性能测试结果")
    memory.add_constraint("约束1", "必须支持事务", priority="high")
    
    # 创建ProgressiveDisclosure
    disclosure = ProgressiveDisclosure(memory)
    
    # 获取Layer 1索引
    indices = disclosure.get_index(limit=10)
    
    if len(indices) > 0:
        print(f"[PASS] Generated {len(indices)} MemoryIndex entries")
        
        # 打印索引表
        index_table = disclosure.format_index_table(indices)
        print()
        print(index_table[:500])
        print()
        
        # 检查第一个索引
        first_idx = indices[0]
        print(f"First index: ID={first_idx.id[:8]}, Type={first_idx.type}, Title={first_idx.title}")
        
        # Token估算
        total_tokens = sum(idx.estimate_tokens() for idx in indices)
        print(f"Token estimate: ~{total_tokens} tokens")
        
        print("[PASS] MemoryIndex generation successful")
    else:
        print("[FAIL] No indices generated")
    
    print()

def test_memory_timeline():
    """测试2: MemoryTimeline获取"""
    print("测试2: MemoryTimeline获取")
    print("-"*60)
    
    from src.memory import ConversationMemory, ProgressiveDisclosure
    
    memory = ConversationMemory("test-feature", Path("/tmp"))
    
    # 添加节点（模拟时间序列）
    memory.add_requirement("需求1", "这是一个需求", priority="high")
    memory.add_design_decision("决策1", "这是一个决策", "基于需求1", priority="high")
    memory.add_constraint("约束1", "这是一个约束", priority="medium")
    
    disclosure = ProgressiveDisclosure(memory)
    
    # 先获取索引
    indices = disclosure.get_index(limit=10)
    
    if indices:
        # 选择第一个节点的ID
        first_id = indices[0].id
        
        # 获取Layer 2时间线
        timelines = disclosure.get_timeline(around_id=first_id)
        
        if len(timelines) > 0:
            print(f"[PASS] Generated {len(timelines)} MemoryTimeline entries")
            
            # 打印时间线
            timeline_content = disclosure.format_timeline_context(timelines)
            print()
            print(timeline_content[:500])
            print()
            
            print("[PASS] MemoryTimeline generation successful")
        else:
            print("[FAIL] No timelines generated")
    else:
        print("[FAIL] No indices to get timeline around")
    
    print()

def test_full_details():
    """测试3: Full Details获取"""
    print("测试3: Full Details获取")
    print("-"*60)
    
    from src.memory import ConversationMemory, ProgressiveDisclosure
    
    memory = ConversationMemory("test-feature", Path("/tmp"))
    
    # 添加节点
    memory.add_requirement("需求1", "支持SQLite数据库", priority="high")
    memory.add_design_decision(
        "决策1",
        "选择SQLite作为数据库",
        "SQLite轻量、嵌入式、无需额外服务进程，适合单机应用",
        alternatives=["PostgreSQL: 功能强大但需独立服务", "MongoDB: 灵活但不适合关系型数据"],
        priority="high"
    )
    
    disclosure = ProgressiveDisclosure(memory)
    
    # 先获取索引
    indices = disclosure.get_index(limit=10)
    
    if indices:
        # 选择所有节点ID
        ids = [idx.id for idx in indices[:2]]
        
        # 获取Layer 3完整详情
        nodes = disclosure.get_full_details(ids)
        
        if len(nodes) > 0:
            print(f"[PASS] Retrieved {len(nodes)} full MemoryNode details")
            
            # 打印详情
            details_content = disclosure.format_full_details(nodes)
            print()
            print(details_content[:800])
            print()
            
            # 检查第一个节点
            first_node = nodes[0]
            print(f"First node: Title={first_node.title}, Content length={len(first_node.content)}")
            
            if first_node.alternatives:
                print(f"Alternatives: {len(first_node.alternatives)} options")
            
            print("[PASS] Full details retrieval successful")
        else:
            print("[FAIL] No nodes retrieved")
    else:
        print("[FAIL] No indices to get details for")
    
    print()

def test_token_stats():
    """测试4: Token成本统计"""
    print("测试4: Token成本统计")
    print("-"*60)
    
    from src.memory import ConversationMemory, ProgressiveDisclosure
    
    memory = ConversationMemory("test-feature", Path("/tmp"))
    
    # 添加大量节点（模拟真实场景）
    for i in range(20):
        memory.add_requirement(f"需求{i}", f"功能{i}", priority="high" if i < 5 else "medium")
    
    disclosure = ProgressiveDisclosure(memory)
    
    # 使用三层检索
    indices = disclosure.get_index(limit=15)
    if indices:
        timelines = disclosure.get_timeline(around_id=indices[0].id)
        nodes = disclosure.get_full_details([indices[0].id])
    
    # 获取token统计
    token_stats = disclosure.get_token_stats()
    
    print("Token Statistics:")
    for key, value in token_stats.items():
        print(f"   {key}: {value}")
    
    if token_stats["total_used"] > 0:
        print("[PASS] Token stats calculated")
        
        if token_stats.get("savings_estimate"):
            print(f"[PASS] Savings estimate: {token_stats['savings_estimate']}")
    else:
        print("[FAIL] No token usage recorded")
    
    print()

def test_director_integration():
    """测试5: Director集成"""
    print("测试5: Director集成Progressive Disclosure")
    print("-"*60)
    
    from src.director import Director, ExecutionContext
    
    project_root = Path(_project_root / "test_temp_pd")
    project_root.mkdir(parents=True, exist_ok=True)
    
    director = Director(project_root)
    
    feature_name = "test-pd"
    feature_dir = project_root / "docs" / "features" / feature_name
    feature_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建context
    context = ExecutionContext(
        project_root=project_root,
        feature_name=feature_name,
        feature_dir=feature_dir,
        capability=None,
    )
    
    # 初始化memory
    director._memory = director._load_or_create_memory(feature_name)
    director._memory.add_requirement("测试需求", "这是一个测试需求", priority="high")
    director._memory.add_design_decision("测试决策", "这是一个测试决策", "测试理由", priority="high")
    
    # 测试Progressive Disclosure注入
    director.inject_memory_context(context, feature_name, use_progressive_disclosure=True)
    
    # 验证注入结果
    if context.metadata.get("progressive_disclosure_enabled"):
        print("[PASS] Progressive Disclosure enabled in context")
        
        if context.metadata.get("injected_context"):
            injected = context.metadata["injected_context"]
            print(f"[PASS] Context injected ({len(injected)} chars)")
            
            if "Memory Index" in injected:
                print("[PASS] Memory Index table present in injected context")
            else:
                print("[FAIL] Memory Index table not found")
        else:
            print("[FAIL] No context injected")
        
        # 检查token统计
        token_stats = context.metadata.get("progressive_disclosure_token_stats")
        if token_stats:
            print(f"[PASS] Token stats recorded: {token_stats}")
        else:
            print("[FAIL] No token stats")
        
        # 测试Layer 2方法
        disclosure = context.metadata.get("progressive_disclosure_instance")
        if disclosure:
            indices = disclosure.get_index(limit=5)
            if indices:
                timeline = director.get_memory_timeline(context, indices[0].id)
                if timeline:
                    print("[PASS] get_memory_timeline() method works")
                else:
                    print("[FAIL] get_memory_timeline() failed")
                
                # 测试Layer 3方法
                details = director.get_memory_full_details(context, [indices[0].id])
                if details:
                    print("[PASS] get_memory_full_details() method works")
                else:
                    print("[FAIL] get_memory_full_details() failed")
            else:
                print("[FAIL] No indices to test with")
        else:
            print("[FAIL] Progressive Disclosure instance not in context")
    else:
        print("[FAIL] Progressive Disclosure not enabled")
    
    # 测试传统方式（向后兼容）
    context2 = ExecutionContext(
        project_root=project_root,
        feature_name=feature_name,
        feature_dir=feature_dir,
        capability=None,
    )
    
    director.inject_memory_context(context2, feature_name, use_progressive_disclosure=False)
    
    if not context2.metadata.get("progressive_disclosure_enabled"):
        print("[PASS] Full context injection (backward compatible) works")
    else:
        print("[FAIL] Full injection mode should not have progressive enabled")
    
    print()

def test_comparison():
    """测试6: 对比Progressive Disclosure vs 全量注入"""
    print("测试6: Progressive Disclosure vs 全量注入对比")
    print("-"*60)
    
    from src.memory import ConversationMemory, ProgressiveDisclosure
    
    memory = ConversationMemory("test-feature", Path("/tmp"))
    
    # 添加20个节点
    for i in range(20):
        memory.add_requirement(f"需求{i}", f"这是一个很长的需求描述，包含很多细节信息{i}", priority="medium")
        memory.add_design_decision(f"决策{i}", f"这是一个很长的设计决策内容{i}", f"理由{i}: 这是一个很长的决策理由{i}", priority="medium")
    
    disclosure = ProgressiveDisclosure(memory)
    
    # Progressive Disclosure方式
    indices = disclosure.get_index(limit=15)
    pd_tokens = disclosure.get_token_stats()["total_used"]
    
    # 全量注入估算
    full_tokens = sum(
        len(n.content) // 4 + len(n.rationale) // 4 + 20
        for n in memory.nodes.values()
    )
    
    print(f"Progressive Disclosure (Layer 1): ~{pd_tokens} tokens")
    print(f"Full Context Injection (estimated): ~{full_tokens} tokens")
    
    if full_tokens > 0:
        savings_percent = (1 - pd_tokens / full_tokens) * 100
        print(f"Savings: {savings_percent:.1f}%")
        
        if savings_percent > 50:
            print("[PASS] Progressive Disclosure saves significant tokens")
        else:
            print("[WARN] Savings not significant (may be small dataset)")
    else:
        print("[FAIL] Could not estimate full tokens")
    
    print()

def main():
    test_memory_index_generation()
    test_memory_timeline()
    test_full_details()
    test_token_stats()
    test_director_integration()
    test_comparison()
    
    print("="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    main()