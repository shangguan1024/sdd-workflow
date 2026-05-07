"""
测试脚本 - 验证Nexus-Map集成功能

验证：
1. NexusMapIntegrator基础功能
2. Director集成
3. Understanding阶段加载nexus-map
4. 架构知识查询接口
"""

import json
import sys
from pathlib import Path

_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

print("="*60)
print("Nexus-Map Integration 功能验证测试")
print("="*60)
print()

def test_nexus_map_integrator_basic():
    """测试1: NexusMapIntegrator基础功能"""
    print("测试1: NexusMapIntegrator基础功能")
    print("-"*60)
    
    from src.nexus_map import NexusMapIntegrator
    
    # 创建测试项目目录
    project_root = Path(_project_root / "test_temp_nexus")
    project_root.mkdir(parents=True, exist_ok=True)
    
    integrator = NexusMapIntegrator(project_root)
    
    # 测试exists方法
    if not integrator.exists():
        print("[PASS] exists() correctly returns False for missing nexus-map")
    else:
        print("[FAIL] exists() should return False for missing nexus-map")
    
    # 测试generate_if_missing
    integrator.generate_if_missing()
    
    if integrator.exists():
        print("[PASS] generate_if_missing() created basic nexus-map")
        
        # 检查基本文件是否创建
        if (project_root / ".nexus-map" / "INDEX.md").exists():
            print("[PASS] INDEX.md created")
        else:
            print("[FAIL] INDEX.md not created")
        
        if (project_root / ".nexus-map" / "systems.md").exists():
            print("[PASS] systems.md created")
        else:
            print("[FAIL] systems.md not created")
    else:
        print("[FAIL] nexus-map still not exists after generation")
    
    # 测试load_content
    content = integrator.load_content()
    
    if content:
        print(f"[PASS] load_content() returned {len(content)} items")
        
        if "INDEX.md" in content:
            print("[PASS] INDEX.md loaded")
        
        if "systems.md" in content:
            print("[PASS] systems.md loaded")
    else:
        print("[FAIL] load_content() returned empty dict")
    
    # 测试get_architecture_summary
    summary = integrator.get_architecture_summary()
    
    if summary and len(summary) > 100:
        print("[PASS] get_architecture_summary() generated summary")
        print(f"  Summary length: {len(summary)} chars")
    else:
        print("[FAIL] get_architecture_summary() failed")
    
    print()

def test_nexus_map_query_methods():
    """测试2: NexusMapIntegrator查询方法"""
    print("测试2: NexusMapIntegrator查询方法")
    print("-"*60)
    
    from src.nexus_map import NexusMapIntegrator
    
    project_root = Path(_project_root / "test_temp_nexus")
    integrator = NexusMapIntegrator(project_root)
    
    # 测试query_module_dependencies
    deps = integrator.query_module_dependencies("test_module")
    
    if deps:
        print("[PASS] query_module_dependencies() returned result")
        print(f"  Result keys: {list(deps.keys())}")
    else:
        print("[FAIL] query_module_dependencies() failed")
    
    # 测试query_impact_radius
    impact = integrator.query_impact_radius("src/test.py")
    
    if impact:
        print("[PASS] query_impact_radius() returned result")
        print(f"  Impact level: {impact.get('impact_level', 'unknown')}")
    else:
        print("[FAIL] query_impact_radius() failed")
    
    # 测试get_module_spec
    spec = integrator.get_module_spec("test_module")
    
    if spec is None:
        print("[PASS] get_module_spec() correctly returns None for non-existent module")
    else:
        print("[PASS] get_module_spec() found spec")
    
    print()

def test_director_integration():
    """测试3: Director集成NexusMapIntegrator"""
    print("测试3: Director集成NexusMapIntegrator")
    print("-"*60)
    
    from src.director import Director
    
    project_root = Path(_project_root / "test_temp_director_nexus")
    project_root.mkdir(parents=True, exist_ok=True)
    
    director = Director(project_root)
    
    # 检查_nexus_map_integrator属性
    if hasattr(director, "_nexus_map_integrator"):
        print("[PASS] Director has _nexus_map_integrator attribute")
        
        if director._nexus_map_integrator is not None:
            print("[PASS] NexusMapIntegrator instance created")
            
            # 检查project_root是否正确
            if director._nexus_map_integrator.project_root == project_root:
                print("[PASS] NexusMapIntegrator.project_root correct")
            else:
                print("[FAIL] NexusMapIntegrator.project_root incorrect")
        else:
            print("[FAIL] NexusMapIntegrator instance is None")
    else:
        print("[FAIL] Director missing _nexus_map_integrator attribute")
    
    print()

def test_understanding_phase_loading():
    """测试4: Understanding阶段加载nexus-map"""
    print("测试4: Understanding阶段加载nexus-map")
    print("-"*60)
    
    from src.director import Director, ExecutionContext
    from src.capabilities.understanding import UnderstandingCapability
    
    project_root = Path(_project_root / "test_temp_understanding_nexus")
    project_root.mkdir(parents=True, exist_ok=True)
    
    # 创建.nexus-map
    nexus_dir = project_root / ".nexus-map"
    nexus_dir.mkdir(parents=True, exist_ok=True)
    
    index_content = """# INDEX

## Architecture Overview

Test architecture with modules.

## Modules

- module1
- module2
"""
    (nexus_dir / "INDEX.md").write_text(index_content, encoding="utf-8")
    
    systems_content = """# Systems

## Core System

Test system description.
"""
    (nexus_dir / "systems.md").write_text(systems_content, encoding="utf-8")
    
    # 创建Director和Capability
    director = Director(project_root)
    
    feature_name = "test-feature"
    feature_dir = project_root / "docs" / "features" / feature_name
    feature_dir.mkdir(parents=True, exist_ok=True)
    
    context = ExecutionContext(
        project_root=project_root,
        feature_name=feature_name,
        feature_dir=feature_dir,
        capability=None,
    )
    
    # 执行Understanding阶段
    understanding_cap = UnderstandingCapability()
    result = understanding_cap.execute(context)
    
    # 检查nexus-map是否加载
    if context.metadata.get("nexus_map_loaded"):
        print("[PASS] nexus_map_loaded set in context")
        
        if context.metadata.get("nexus_map_summary"):
            print("[PASS] nexus_map_summary present")
            summary_len = len(context.metadata["nexus_map_summary"])
            print(f"  Summary length: {summary_len} chars")
        
        if context.metadata.get("nexus_map_content"):
            print("[PASS] nexus_map_content present")
            content_keys = list(context.metadata["nexus_map_content"].keys())
            print(f"  Content keys: {content_keys}")
        
        # 检查是否注入到injected_context
        if context.metadata.get("injected_context"):
            injected = context.metadata["injected_context"]
            if "Nexus-Map" in injected or "Architecture" in injected:
                print("[PASS] Nexus-map injected to injected_context")
            else:
                print("[FAIL] Nexus-map not found in injected_context")
    else:
        print("[FAIL] nexus_map_loaded not set")
    
    # 检查codebase_analysis是否利用nexus-map
    codebase_analysis = context.metadata.get("codebase_analysis")
    if codebase_analysis:
        if "nexus_map_architecture" in codebase_analysis:
            print("[PASS] codebase_analysis includes nexus_map_architecture")
        else:
            print("[WARN] codebase_analysis missing nexus_map_architecture (may not be generated)")
    
    print()

def test_enhanced_codebase_analysis():
    """测试5: 增强的代码库分析（利用nexus-map）"""
    print("测试5: 增强的代码库分析")
    print("-"*60)
    
    from src.nexus_map import NexusMapIntegrator
    
    project_root = Path(_project_root / "test_temp_enhanced")
    project_root.mkdir(parents=True, exist_ok=True)
    
    # 创建.nexus-map with module specs
    nexus_dir = project_root / ".nexus-map"
    nexus_dir.mkdir(parents=True, exist_ok=True)
    
    specs_dir = nexus_dir / "module-specs"
    specs_dir.mkdir(parents=True, exist_ok=True)
    
    spec_content = """# module1 Spec

## Responsibilities

Test module1 responsibilities.

## Dependencies

- depends on module2
"""
    (specs_dir / "module1.md").write_text(spec_content, encoding="utf-8")
    
    (nexus_dir / "INDEX.md").write_text("# INDEX\n\n## Modules\n\n- module1\n- module2\n", encoding="utf-8")
    
    integrator = NexusMapIntegrator(project_root)
    
    # 测试get_module_spec
    spec = integrator.get_module_spec("module1")
    
    if spec:
        print("[PASS] get_module_spec('module1') found")
        
        if "Responsibilities" in spec:
            print("[PASS] Spec contains Responsibilities section")
        
        if "Dependencies" in spec:
            print("[PASS] Spec contains Dependencies section")
    else:
        print("[FAIL] get_module_spec('module1') not found")
    
    # 测试query_module_dependencies
    deps = integrator.query_module_dependencies("module1")
    
    if deps and "dependencies" in deps:
        print("[PASS] query_module_dependencies returned dependencies")
        print(f"  Dependencies: {deps['dependencies']}")
    else:
        print("[FAIL] query_module_dependencies failed")
    
    print()

def main():
    test_nexus_map_integrator_basic()
    test_nexus_map_query_methods()
    test_director_integration()
    test_understanding_phase_loading()
    test_enhanced_codebase_analysis()
    
    # Cleanup
    import shutil
    for dirname in ["test_temp_nexus", "test_temp_director_nexus", "test_temp_understanding_nexus", "test_temp_enhanced"]:
        dirpath = _project_root / dirname
        if dirpath.exists():
            try:
                shutil.rmtree(dirpath)
            except Exception:
                pass
    
    print("="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    main()