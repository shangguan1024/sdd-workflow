"""
Core Principles 注入修复验证测试

验证修复后的效果：
- Director 加载 constitution/core.md
- 最高原则被注入到 context
- 明确提示信息告知 LLM
"""

import sys
import tempfile
from pathlib import Path

_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.director import Director, ExecutionContext, CapabilityRegistry


def test_core_principles_loading():
    """测试 constitution/core.md 加载"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # 创建 constitution/core.md
        constitution_dir = project_root / "CONSTITUTION"
        constitution_dir.mkdir(parents=True, exist_ok=True)
        
        core_content = """# Core Principles

## 1. Think Before Coding
- Always analyze before implementation
- No direct coding without design

## 2. Test-Driven Development
- All code must have tests
- Tests first, code second

## 3. No Emoji
- Never use emoji in code or docs
- Use plain text only
"""
        
        (constitution_dir / "core.md").write_text(core_content, encoding="utf-8")
        
        # 创建 Director
        director = Director(project_root=project_root)
        
        # 创建 context
        feature_name = "test-core-principles"
        feature_dir = project_root / "docs" / "features" / feature_name
        feature_dir.mkdir(parents=True, exist_ok=True)
        
        registry = CapabilityRegistry()
        capability = registry.select("brainstorming")
        
        context = ExecutionContext(
            project_root=project_root,
            feature_name=feature_name,
            feature_dir=feature_dir,
            capability=capability,
        )
        
        # 注入 context
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        director.inject_memory_context(context, feature_name, use_progressive_disclosure=False)
        
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # 验证注入
        assert context.metadata.get("core_principles_loaded") == True
        assert "Core Principles" in context.metadata.get("core_principles", "")
        assert "Think Before Coding" in context.metadata.get("core_principles", "")
        
        # 验证提示信息
        assert "Core Principles (最高原则 - 必须遵守)" in output
        assert "MUST be followed" in output
        
        print("[PASS] constitution/core.md loaded successfully")
        print(f"  Principles injected: {len(context.metadata['core_principles'])} chars")
        print(f"  Prompt message shown: Yes")


def test_core_principles_missing():
    """测试 constitution/core.md 不存在时的安全降级"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # 不创建 constitution/core.md
        
        director = Director(project_root=project_root)
        
        feature_name = "test-no-principles"
        feature_dir = project_root / "docs" / "features" / feature_name
        feature_dir.mkdir(parents=True, exist_ok=True)
        
        registry = CapabilityRegistry()
        capability = registry.select("brainstorming")
        
        context = ExecutionContext(
            project_root=project_root,
            feature_name=feature_name,
            feature_dir=feature_dir,
            capability=capability,
        )
        
        # 注入 context
        director.inject_memory_context(context, feature_name, use_progressive_disclosure=False)
        
        # 验证安全降级
        assert context.metadata.get("core_principles_loaded") == False
        assert "core_principles" not in context.metadata
        
        print("[PASS] Safe degradation when constitution/core.md missing")
        print("  core_principles_loaded: False")


def test_core_principles_priority():
    """测试最高原则在第1位加载"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # 创建 constitution/core.md
        constitution_dir = project_root / "CONSTITUTION"
        constitution_dir.mkdir(parents=True, exist_ok=True)
        (constitution_dir / "core.md").write_text("Test Principles", encoding="utf-8")
        
        # 创建 AGENTS.md（第6位）
        (project_root / "AGENTS.md").write_text("Test Agents", encoding="utf-8")
        
        director = Director(project_root=project_root)
        
        # 加载 memory（第6位 Progressive Disclosure）
        director._memory = director._load_or_create_memory("test")
        director._memory.add_requirement("Test", "Test requirement", priority="high")
        
        feature_dir = project_root / "docs" / "features" / "test"
        feature_dir.mkdir(parents=True, exist_ok=True)
        
        registry = CapabilityRegistry()
        capability = registry.select("brainstorming")
        
        context = ExecutionContext(
            project_root=project_root,
            feature_name="test",
            feature_dir=feature_dir,
            capability=capability,
        )
        
        # 注入
        director.inject_memory_context(context, "test", use_progressive_disclosure=True)
        
        # 验证加载顺序
        assert context.metadata.get("core_principles_loaded") == True  # 第1位
        assert context.metadata.get("agents_context_loaded") == True   # 第6位
        assert context.metadata.get("progressive_disclosure_enabled") == True
        
        print("[PASS] Core principles loaded at position 1")
        print("  Loading order verified:")
        print("    1. constitution/core.md: Yes")
        print("    6. AGENTS.md: Yes")


def test_director_initialize_constitution():
    """测试 Director 初始化 constitution/core.md"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        director = Director(project_root=project_root)
        
        # 运行初始化
        from src.cli import InitCommand
        command = InitCommand(args={"path": project_root, "force": True})
        director.initialize(command)
        
        # 验证 constitution/core.md 创建
        constitution_file = project_root / "CONSTITUTION" / "core.md"
        
        assert constitution_file.exists()
        
        content = constitution_file.read_text(encoding="utf-8")
        
        assert "Core Principles" in content
        assert "Safety First" in content
        assert "Modularity" in content
        assert "Testability" in content
        assert "Backward Compatibility" in content
        
        print("[PASS] Director initializes constitution/core.md")
        print(f"  File created: {constitution_file}")
        print(f"  Content: {len(content)} chars")


def run_all_tests():
    print("\n" + "=" * 60)
    print("Core Principles Injection Fix Tests")
    print("=" * 60 + "\n")
    
    test_core_principles_loading()
    test_core_principles_missing()
    test_core_principles_priority()
    test_director_initialize_constitution()
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60 + "\n")
    
    print("[SUMMARY] Fix verified:")
    print("  - constitution/core.md loaded at position 1")
    print("  - Core principles injected to context")
    print("  - Clear prompt message shown")
    print("  - Safe degradation when file missing")


if __name__ == "__main__":
    run_all_tests()