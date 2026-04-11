"""
SDD-Workflow v2.0 Module Tests
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test all module imports"""
    print("=" * 60)
    print("Testing Module Imports")
    print("=" * 60)
    
    tests = [
        ("CLI", "from src.cli import CLI"),
        ("Director", "from src.director import Director, Phase"),
        ("PhaseOrchestrator", "from src.phases import PhaseOrchestrator, Phase1Orchestrator"),
        ("CheckpointManager", "from src.checkpoint import CheckpointManager"),
        ("QualityHarness", "from src.quality import QualityHarness"),
        ("RuleParser", "from src.rules import RuleParser, Rule, RuleSet"),
        ("SDDWorkflow", "from src.workflow import SDDWorkflow"),
        ("Full Export", "from src import *"),
    ]
    
    results = []
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"  [PASS] {name}")
            results.append(True)
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            results.append(False)
    
    return all(results)


def test_basic_functionality():
    """Test basic functionality"""
    print("\n" + "=" * 60)
    print("Testing Basic Functionality")
    print("=" * 60)
    
    results = []
    
    # Test CLI parsing
    try:
        from src.cli import CLI
        cli = CLI()
        cmd = cli.parse(["help"])
        assert cmd.name == "help"
        print("  [PASS] CLI parsing")
        results.append(True)
    except Exception as e:
        print(f"  [FAIL] CLI parsing: {e}")
        results.append(False)
    
    # Test Director initialization
    try:
        from src.director import Director, Phase
        director = Director(Path("."))
        assert director.state_machine is not None
        assert director.gate_controller is not None
        print("  [PASS] Director initialization")
        results.append(True)
    except Exception as e:
        print(f"  [FAIL] Director initialization: {e}")
        results.append(False)
    
    # Test PhaseOrchestrator
    try:
        from src.phases import Phase1Orchestrator
        orch = Phase1Orchestrator()
        assert len(orch.steps) > 0
        print(f"  [PASS] Phase1Orchestrator ({len(orch.steps)} steps)")
        results.append(True)
    except Exception as e:
        print(f"  [FAIL] Phase1Orchestrator: {e}")
        results.append(False)
    
    # Test StateMachine
    try:
        from src.director import StateMachine, Phase
        sm = StateMachine()
        assert sm.get_current() == Phase.INIT
        assert sm.can_transition(Phase.INIT, Phase.REQUIREMENTS)
        print("  [PASS] StateMachine")
        results.append(True)
    except Exception as e:
        print(f"  [FAIL] StateMachine: {e}")
        results.append(False)
    
    # Test GateController
    try:
        from src.director import GateController, Phase, GateResult
        gc = GateController()
        result = gc.evaluate(Phase.INIT, Phase.REQUIREMENTS, None)
        assert result.passed == True
        print("  [PASS] GateController")
        results.append(True)
    except Exception as e:
        print(f"  [FAIL] GateController: {e}")
        results.append(False)
    
    # Test CheckpointManager
    try:
        from src.checkpoint import CheckpointManager
        cm = CheckpointManager(Path("."))
        print("  [PASS] CheckpointManager")
        results.append(True)
    except Exception as e:
        print(f"  [FAIL] CheckpointManager: {e}")
        results.append(False)
    
    # Test QualityProfile
    try:
        from src.quality import get_profile
        profile = get_profile("standard")
        assert profile.name == "standard"
        print("  [PASS] QualityProfile")
        results.append(True)
    except Exception as e:
        print(f"  [FAIL] QualityProfile: {e}")
        results.append(False)
    
    # Test Rule model
    try:
        from src.rules import Rule, RuleSet, RuleType, Severity
        rule = Rule(
            id="test-rule",
            name="Test Rule",
            description="A test rule",
            type=RuleType.CODING_CONVENTION,
            severity=Severity.WARNING,
            patterns=[r"\bprint\s*\("],
        )
        assert rule.id == "test-rule"
        print("  [PASS] Rule model")
        results.append(True)
    except Exception as e:
        print(f"  [FAIL] Rule model: {e}")
        results.append(False)
    
    return all(results)


def test_rule_parsing():
    """Test rule parsing (without yaml)"""
    print("\n" + "=" * 60)
    print("Testing Rule Parsing")
    print("=" * 60)
    
    results = []
    
    # Test Rule.matches
    try:
        from src.rules import Rule, RuleType, Severity
        rule = Rule(
            id="no-print",
            name="No Print",
            description="Do not use print",
            type=RuleType.CODING_CONVENTION,
            severity=Severity.ERROR,
            patterns=[r"print\s*\("],
        )
        
        matches = rule.matches("print('hello')")
        assert len(matches) > 0
        print(f"  [PASS] Rule.matches (found {len(matches)} matches)")
        results.append(True)
    except Exception as e:
        print(f"  [FAIL] Rule.matches: {e}")
        results.append(False)
    
    # Test RuleSet
    try:
        from src.rules import RuleSet, Rule, RuleType, Severity
        ruleset = RuleSet(
            id="test-ruleset",
            name="Test Ruleset",
            rules=[
                Rule("rule1", "Rule 1", "Desc 1"),
                Rule("rule2", "Rule 2", "Desc 2"),
            ]
        )
        assert len(ruleset.rules) == 2
        assert ruleset.get_rule("rule1") is not None
        assert ruleset.filter_by_type(RuleType.CODING_CONVENTION) is not None
        print("  [PASS] RuleSet operations")
        results.append(True)
    except Exception as e:
        print(f"  [FAIL] RuleSet: {e}")
        results.append(False)
    
    return all(results)


def main():
    """Main function"""
    print("\nSDD-Workflow v2.0 Module Tests")
    print("=" * 60)
    
    all_passed = True
    
    if not test_imports():
        all_passed = False
    
    if not test_basic_functionality():
        all_passed = False
    
    if not test_rule_parsing():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[PASS] All tests passed")
        return 0
    else:
        print("[FAIL] Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
