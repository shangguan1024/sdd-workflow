"""
Project Initializer - Project and feature initialization

负责：
- _create_directory_structure
- _initialize_config_files
- _initialize_constitution
- _initialize_memory_artifacts
- _initialize_feature_artifacts

Extracted from director.py for better modularity.
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cli import InitCommand


class ProjectInitializer:
    """
    Project Initializer - 项目初始化器
    
    负责：
    1. 创建目录结构
    2. 初始化配置文件
    3. 初始化 Constitution
    4. 初始化 Memory artifacts
    5. 初始化 Feature artifacts
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def create_directory_structure(self, project_root: Path):
        """
        创建项目目录结构
        
        Args:
            project_root: 项目根目录
        """
        directories = [
            ".sdd",
            "CONSTITUTION",
            ".nexus-map",
            "docs/knowledge",
            "docs/modules",
            "docs/features",
            "docs/collaboration",
        ]
        
        for dir_path in directories:
            (project_root / dir_path).mkdir(parents=True, exist_ok=True)
    
    def initialize_config_files(self, project_root: Path, command: InitCommand):
        """
        初始化配置文件
        
        Args:
            project_root: 项目根目录
            command: InitCommand instance
        """
        import yaml
        
        config = {
            "project": {
                "name": project_root.name,
                "type": command.args.get("template", "standard"),
                "complexity": "medium",
            },
            "harness": {"enabled": True},
        }
        
        config_path = project_root / ".sdd" / "project.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(yaml.dump(config))
    
    def initialize_constitution(self, project_root: Path):
        """
        初始化 Constitution 文件
        
        Args:
            project_root: 项目根目录
        """
        const_dir = project_root / "CONSTITUTION"
        const_dir.mkdir(parents=True, exist_ok=True)
        
        templates = {
            "core.md": """# Core Principles

## 1. Safety First
- All user input must be validated
- No sensitive info in logs
- Secrets never in code or commits

## 2. Modularity
- Modules communicate via explicit interfaces
- Single responsibility per module
- Dependencies flow downward

## 3. Testability
- All public APIs must have tests
- Test coverage >= 80% for new code
- Integration tests for critical paths

## 4. Backward Compatibility
- No breaking changes to public APIs
- Deprecation warnings before removal

## 5. Code Quality
- No dead code or unused imports
- Consistent naming conventions
- Documentation for all public APIs
""",
            "design-rules.md": """# Design Rules

## DESIGN-001: Single Responsibility
Each module/class has one clear purpose.

## DESIGN-002: Interface Segregation
Keep interfaces minimal and focused.

## DESIGN-003: Dependency Direction
Dependencies flow from high-level to low-level.

## DESIGN-004: No Circular Dependencies
Module A cannot depend on B if B depends on A.

## DESIGN-005: API Documentation
All public APIs must have docstrings with:
- Purpose
- Parameters
- Return values
- Exceptions
""",
            "implementation-rules.md": """# Implementation Rules

## IMPL-001: Error Handling
All error paths must be handled explicitly.
No silent failures.

## IMPL-002: Test Coverage
New code requires unit tests.
Modified code requires updated tests.

## IMPL-003: Logging Standards
Use structured logging with context.
Log levels: DEBUG, INFO, WARNING, ERROR.

## IMPL-004: Code Comments
Comments explain "why", not "what".
No redundant comments.
""",
            "review-rules.md": """# Review Rules

## REVIEW-001: Incremental Review
Phase 5 reviews only files changed in current feature.

## REVIEW-002: Quality Gates
- Linting must pass
- Tests must pass
- Coverage >= threshold

## REVIEW-003: Constitution Compliance
All changes must comply with constitution rules.

## REVIEW-004: Change Summary
Phase 6 must document:
- What changed
- Why changed
- Impact radius
- Rollback plan
""",
            "workflow-rules.md": """# Workflow Rules

## WORKFLOW-001: Understanding Phase
Mandatory before design. No skipping.

## WORKFLOW-002: Phase Gates
Each phase requires gate passage before next.

## WORKFLOW-003: Checkpoint Persistence
Checkpoint saved at phase boundaries.

## WORKFLOW-004: Error Recovery
Errors must be captured and recovered.

## WORKFLOW-005: Memory Persistence
Session context persisted in AGENTS.md.
""",
        }
        
        for filename, content in templates.items():
            (const_dir / filename).write_text(content, encoding="utf-8")
    
    def initialize_memory_artifacts(self, project_root: Path):
        """
        初始化 Memory artifacts
        
        Args:
            project_root: 项目根目录
        """
        state_content = """# Project State

## Features

No active features.

## Quality Metrics

| Metric | Current | Target |
|--------|---------|--------|
"""
        (project_root / "PROJECT_STATE.md").write_text(state_content)
        
        agents_content = """# AI Agent Context

No active session.
"""
        (project_root / "AGENTS.md").write_text(agents_content)
    
    def initialize_feature_artifacts(self, feature_dir: Path, feature_name: str):
        """
        初始化 Feature artifacts
        
        Args:
            feature_dir: Feature 目录
            feature_name: Feature 名称
        """
        findings = f"""# Findings: {feature_name}

## Goal
{feature_name}

## Instructions

## Discoveries

## Accomplished

## Relevant files / directories

## 下一步

---

*Initialized: Phase 0*

---

## Phase 0: Research

**Status**: ⏳ Pending

---

*Generated by SDD-Workflow Phase 0*
"""
        
        task_plan = f"""# Task Plan: {feature_name}

## Overview

**Feature**: {feature_name}

---

## Phase 1: Requirements Analysis [PENDING]

---

## Phase 2: Implementation Planning [PENDING]

---

## Phase 3: Module Development [PENDING]

---

## Phase 4: Integration & Testing [PENDING]

---

## Phase 5: Code Quality Review [PENDING]

---

## Phase 6: Memory Persistence [PENDING]

---

## Notes
"""
        (feature_dir / "findings.md").write_text(findings)
        (feature_dir / "task_plan.md").write_text(task_plan)
        
        sdd_dir = feature_dir / ".sdd"
        sdd_dir.mkdir(parents=True, exist_ok=True)
    
    def initialize_all(self, project_root: Path, command: InitCommand):
        """
        执行完整初始化流程
        
        Args:
            project_root: 项目根目录
            command: InitCommand instance
        """
        self.create_directory_structure(project_root)
        self.initialize_config_files(project_root, command)
        self.initialize_constitution(project_root)
        self.initialize_memory_artifacts(project_root)
    
    def is_initialized(self, path: Path) -> bool:
        """
        检查项目是否已初始化
        
        Args:
            path: 项目路径
            
        Returns:
            bool: 是否已初始化
        """
        return (
            (path / "CONSTITUTION").exists()
            or (path / ".sdd").exists()
            or (path / "PROJECT_STATE.md").exists()
        )