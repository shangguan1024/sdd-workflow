"""
SDD-Workflow v2.0
分层模块化架构

Architecture:
- Layer 0: CLI (命令行入口)
- Layer 1: Director (主状态机、Gate 控制)
- Layer 2: Phase Orchestrators (阶段流程定义)
- Layer 3: Capabilities (具体能力接口)

Modules:
- checkpoint: Checkpoint 持久化机制
- quality: Quality Harness Pipeline
- rules: MD/YAML 多格式规则支持
"""

__version__ = "2.0.0"
__author__ = "opencode team"

from .cli import CLI, Command, InitCommand, StartCommand, ResumeCommand, StatusCommand, CompleteCommand, Result
from .director import Director, Phase, StateMachine, GateController, Gate, GateResult, ExecutionContext, CapabilityRegistry
from .constants import PHASES, REQUIRED_REVIEW_ARTIFACTS, REQUIRED_MEMORY_ARTIFACTS

from .phases import PhaseOrchestrator, PhaseResult
from .context_monitor import ContextMonitor

from .quality import (
    QualityHarness,
    CodeMetricsCollector,
    TestCoverageCollector,
    ComplexityCollector,
    ConventionCollector,
    GateEngine,
    QualityReporter,
    QualityProfile,
    get_profile,
    list_profiles,
)

from .rules import (
    RuleParser,
    parse_rule_file,
    MarkdownRuleParser,
    YamlRuleParser,
    Rule,
    RuleSet,
)

__all__ = [
    # Core
    "CLI",
    "Director",
    "Phase",
    "PHASES",
    # CLI
    "Command",
    "InitCommand",
    "StartCommand",
    "ResumeCommand",
    "StatusCommand",
    "CompleteCommand",
    "Result",
    # Director
    "StateMachine",
    "GateController",
    "Gate",
    "GateResult",
    "ExecutionContext",
    "CapabilityRegistry",
    # Phases
    "PhaseOrchestrator",
    "PhaseResult",
    # Context Monitor
    "ContextMonitor",
    # Constants
    "REQUIRED_REVIEW_ARTIFACTS",
    "REQUIRED_MEMORY_ARTIFACTS",
    # Quality
    "QualityHarness",
    "CodeMetricsCollector",
    "TestCoverageCollector",
    "ComplexityCollector",
    "ConventionCollector",
    "GateEngine",
    "QualityReporter",
    "QualityProfile",
    "get_profile",
    "list_profiles",
    # Rules
    "RuleParser",
    "parse_rule_file",
    "MarkdownRuleParser",
    "YamlRuleParser",
    "Rule",
    "RuleSet",
]
