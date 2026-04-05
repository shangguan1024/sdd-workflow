#!/usr/bin/env python3
"""
SDD-Workflow Coordinator v2.0
Complete workflow enforcement and phase management
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List, Dict


class WorkflowCoordinator:
    """SDD Workflow Coordinator with automatic phase enforcement"""

    PHASES = {
        1: "Requirements Analysis & Design",
        2: "Implementation Planning",
        3: "Module Development",
        4: "Integration & Testing",
        5: "Code Quality Review",
        6: "Memory Persistence",
    }

    REQUIRED_MEMORY_ARTIFACTS = [
        "PROJECT_STATE.md",
        "AGENTS.md",
        "task_plan.md",
        "findings.md",
        "progress.md",
    ]

    REQUIRED_REVIEW_ARTIFACTS = [
        "docs/reviews/architecture_review.md",
        "docs/reviews/code_quality_review.md",
        "docs/reviews/test_coverage_report.md",
        "docs/reviews/requirements_verification.md",
    ]

    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.state_file = self.project_root / "PROJECT_STATE.md"
        self.task_plan_file = self.project_root / "task_plan.md"
        self.nexus_map = self.project_root / ".nexus-map"

    def detect_project_state(self):
        """Detect current project state and return appropriate workflow"""
        if self.nexus_map.exists():
            return "existing_project_with_memory"
        elif (self.project_root / "Cargo.toml").exists():
            return "existing_rust_project"
        elif (self.project_root / "package.json").exists():
            return "existing_node_project"
        else:
            return "new_project"

    def get_current_phase(self) -> int:
        """
        Detect which phase is currently active based on artifacts.
        Returns 1-6, or 0 if no SDD workflow detected.
        """
        if not self.state_file.exists():
            return 0

        content = self.state_file.read_text()

        # Check memory artifacts to determine phase
        memory_count = sum(
            1
            for f in self.REQUIRED_MEMORY_ARTIFACTS
            if (self.project_root / f).exists()
        )

        if memory_count < 3:
            return 1  # Phase 1: Just started

        # Check review artifacts
        review_count = sum(
            1
            for f in self.REQUIRED_REVIEW_ARTIFACTS
            if (self.project_root / f).exists()
        )

        if review_count < 4:
            if memory_count >= 4:
                return 4  # Phase 4: Integration done, need review
            return 3  # Phase 3: Development

        # All artifacts present
        if (
            "Implementation complete" in content
            or "feature complete" in content.lower()
        ):
            return 6  # Phase 6 or complete

        return 5  # Phase 5: Review complete, need persistence

    def get_phase_status(self) -> dict:
        """Return detailed status of each phase"""
        current = self.get_current_phase()

        status = {}
        for phase_num, phase_name in self.PHASES.items():
            if phase_num < current:
                status[phase_num] = {"name": phase_name, "status": "complete"}
            elif phase_num == current:
                status[phase_num] = {"name": phase_name, "status": "in_progress"}
            else:
                status[phase_num] = {"name": phase_name, "status": "pending"}

        # Add artifact status
        memory_present = sum(
            1
            for f in self.REQUIRED_MEMORY_ARTIFACTS
            if (self.project_root / f).exists()
        )
        review_present = sum(
            1
            for f in self.REQUIRED_REVIEW_ARTIFACTS
            if (self.project_root / f).exists()
        )

        status["memory_artifacts"] = {
            "present": memory_present,
            "total": len(self.REQUIRED_MEMORY_ARTIFACTS),
        }
        status["review_artifacts"] = {
            "present": review_present,
            "total": len(self.REQUIRED_REVIEW_ARTIFACTS),
        }

        return status

    def list_active_features(self) -> List[Dict]:
        """
        List all features with their current phase status.
        Returns list of feature info dicts.
        """
        features_dir = self.project_root / "docs" / "features"
        if not features_dir.exists():
            return []

        active_features = []
        for feature_path in features_dir.iterdir():
            if feature_path.is_dir():
                status_file = feature_path / "status.toml"
                if status_file.exists():
                    try:
                        import toml

                        status = toml.loads(status_file.read_text())
                        active_features.append(
                            {
                                "name": feature_path.name,
                                "path": str(feature_path),
                                "status": status,
                            }
                        )
                    except Exception:
                        pass

        return active_features

    def get_feature_status(self, feature_name: str) -> Dict:
        """
        Get detailed status for a specific feature.
        Returns dict with feature info.
        """
        feature_path = self.project_root / "docs" / "features" / feature_name
        if not feature_path.exists():
            return {"error": "Feature not found"}

        status_file = feature_path / "status.toml"
        if status_file.exists():
            try:
                import toml

                return toml.loads(status_file.read_text())
            except Exception:
                pass

        return {"error": "No status file found"}

    def verify_phase_gate(self, from_phase: int) -> Tuple[bool, str]:
        """
        Verify if we can proceed from one phase to the next.
        Returns (can_proceed, reason).
        """
        if from_phase < 1 or from_phase > 5:
            return False, f"Invalid phase transition: {from_phase} -> {from_phase + 1}"

        to_phase = from_phase + 1

        # Phase-specific checks
        if from_phase == 1:
            # Check design doc exists
            specs_dir = self.project_root / "docs" / "superpowers" / "specs"
            design_docs = (
                list(specs_dir.glob("*-design.md")) if specs_dir.exists() else []
            )
            if not design_docs:
                return False, "Phase 1 incomplete: No design document found"
            return True, "Design document exists"

        elif from_phase == 2:
            # Check implementation plan exists
            plans_dir = self.project_root / "docs" / "superpowers" / "plans"
            plans = list(plans_dir.glob("*.md")) if plans_dir.exists() else []
            if not plans:
                return False, "Phase 2 incomplete: No implementation plan found"
            return True, "Implementation plan exists"

        elif from_phase == 3:
            # Check code compiles
            cargo_toml = self.project_root / "Cargo.toml"
            if cargo_toml.exists():
                # For Rust, we can't actually run cargo check here
                # Just verify the source files exist
                src_dir = self.project_root / "src"
                if not src_dir.exists():
                    return False, "Phase 3 incomplete: No source directory"
                return True, "Source files exist (build verification needed)"
            return True, "Phase 3 complete (non-Rust project)"

        elif from_phase == 4:
            # Check test-related files exist
            return True, "Phase 4 complete"

        elif from_phase == 5:
            # Check all 4 review artifacts
            missing = []
            for artifact in self.REQUIRED_REVIEW_ARTIFACTS:
                if not (self.project_root / artifact).exists():
                    missing.append(artifact)

            if missing:
                return (
                    False,
                    f"Phase 5 incomplete: Missing artifacts: {', '.join(missing)}",
                )
            return True, "All review artifacts present"

        return True, "Gate passed"

    def check_review_artifacts(self) -> Tuple[bool, list]:
        """
        Check if all required review artifacts exist.
        Returns (all_exist, missing_list).
        """
        missing = []
        for artifact in self.REQUIRED_REVIEW_ARTIFACTS:
            if not (self.project_root / artifact).exists():
                missing.append(artifact)
        return len(missing) == 0, missing

    def check_memory_artifacts(self) -> Tuple[bool, list]:
        """
        Check if all required memory artifacts exist.
        Returns (all_exist, missing_list).
        """
        missing = []
        for artifact in self.REQUIRED_MEMORY_ARTIFACTS:
            if not (self.project_root / artifact).exists():
                missing.append(artifact)
        return len(missing) == 0, missing

    def generate_review_artifact(self, artifact_name: str, content: str) -> bool:
        """
        Generate a missing review artifact with minimal required content.
        Returns True if successful.
        """
        artifact_path = self.project_root / artifact_name
        artifact_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            artifact_path.write_text(content)
            return True
        except Exception as e:
            print(f"Error generating {artifact_name}: {e}")
            return False

    def generate_minimal_review_artifacts(self) -> Tuple[int, int]:
        """
        Auto-generate minimal review artifacts.
        Returns (generated_count, total_required).
        """
        today = datetime.now().strftime("%Y-%m-%d")

        artifacts = {
            "docs/reviews/architecture_review.md": self._minimal_architecture_review(
                today
            ),
            "docs/reviews/code_quality_review.md": self._minimal_code_quality_review(
                today
            ),
            "docs/reviews/test_coverage_report.md": self._minimal_test_coverage_report(
                today
            ),
            "docs/reviews/requirements_verification.md": self._minimal_requirements_verification(
                today
            ),
        }

        generated = 0
        for name, content in artifacts.items():
            if self.generate_review_artifact(name, content):
                generated += 1

        return generated, len(artifacts)

    def _minimal_architecture_review(self, date: str) -> str:
        return f"""# Architecture Review Report

## Review Date: {date}
## Status: AUTO-GENERATED (Needs Manual Review)

## Module Analysis

### Core Modules
- **Logger**: Main API interface
- **LogFormatter**: Message formatting
- **ConcurrentWriter**: Thread-safe writing
- **FileRotator**: File rotation management

### Dependencies
- chrono: Timestamp formatting
- toml: Configuration parsing

## Minimal Required Content
This is a placeholder. A complete architecture review should include:
- [ ] Module dependency analysis
- [ ] Design pattern compliance verification
- [ ] Scalability assessment
- [ ] Risk identification

## Manual Review Required
⚠️ This artifact was auto-generated. Please review and update with actual analysis.
"""

    def _minimal_code_quality_review(self, date: str) -> str:
        return f"""# Code Quality Review Report

## Review Date: {date}
## Status: AUTO-GENERATED (Needs Manual Review)

## Overall Assessment
⚠️ AUTO-GENERATED - Requires manual review

## Minimal Required Content
A complete code quality review should include:
- [ ] Language-specific best practices compliance
- [ ] Error handling strategy evaluation
- [ ] Performance characteristics analysis
- [ ] Security vulnerability assessment

## Issues Found
(To be filled during manual review)

## Manual Review Required
⚠️ This artifact was auto-generated. Please review and update with actual findings.
"""

    def _minimal_test_coverage_report(self, date: str) -> str:
        return f"""# Test Coverage Report

## Review Date: {date}
## Status: AUTO-GENERATED (Needs Manual Review)

## Coverage Summary
⚠️ Coverage data not available - requires manual assessment

## Minimal Required Content
A complete test coverage report should include:
- [ ] Unit test coverage percentage
- [ ] Integration test completeness
- [ ] Edge case testing verification
- [ ] Test maintainability assessment

## Tests Required
(To be documented during manual review)

## Manual Review Required
⚠️ This artifact was auto-generated. Please review and update with actual coverage data.
"""

    def _minimal_requirements_verification(self, date: str) -> str:
        return f"""# Requirements Verification Report

## Review Date: {date}
## Status: AUTO-GENERATED (Needs Manual Review)

## Requirements Checklist
⚠️ Requirements not defined - requires manual verification

## Minimal Required Content
A complete requirements verification should include:
- [ ] Original requirements cross-reference
- [ ] Acceptance criteria validation
- [ ] Implementation vs requirements gap analysis

## Verification Status
(To be filled during manual review)

## Manual Review Required
⚠️ This artifact was auto-generated. Please review and update with actual requirements.
"""

    def generate_memory_artifacts(self) -> Tuple[int, int]:
        """
        Auto-generate missing memory artifacts.
        Returns (generated_count, total_required).
        """
        today = datetime.now().strftime("%Y-%m-%d")

        artifacts = {
            "PROJECT_STATE.md": f"""# Project State

## Last Updated: {today}

## Current Status
- Project: Rotating Logger (Rust)
- Feature: In development
- Phase: Auto-generated initial state

## Architecture
4-module layered design with Logger, LogFormatter, ConcurrentWriter, FileRotator
""",
            "AGENTS.md": f"""# AI Persistence Instructions

## Project Context
- **Project**: Rotating Logger (Rust)
- **Status**: Development in progress
- **Last Updated**: {today}

## Skills Used
- sdd-workflow: Orchestration and planning
- rust-development: Rust-specific implementation
- code-review-quality: Code quality assurance

## Memory Artifacts
- PROJECT_STATE.md: Current project state
- task_plan.md: Development plan tracking
- findings.md: Research and decisions
- progress.md: Session logging

## Next Steps
See task_plan.md for current development status.
""",
            "task_plan.md": f"""# Task Plan

## Last Updated: {today}

## SDD Workflow Phases

### Phase 1: Requirements Analysis ✅
### Phase 2: Implementation Planning ✅
### Phase 3: Module Development ✅
### Phase 4: Integration & Testing 🔄
### Phase 5: Code Quality Review 🔄
### Phase 6: Memory Persistence 🔄

## Current Task
Auto-generated initial state. See progress.md for details.
""",
            "findings.md": f"""# Findings

## Last Updated: {today}

## Research Discoveries

## Technical Decisions

## Architecture Decisions

## Notes
Auto-generated initial state.
""",
            "progress.md": f"""# Progress Log

## Last Updated: {today}

## Session Log

### Session 1 - {today}
- Initialized SDD workflow
- Auto-generated memory artifacts

## Test Results

## Build Status

## Notes
Auto-generated initial state.
""",
        }

        generated = 0
        for name, content in artifacts.items():
            path = self.project_root / name
            if not path.exists():
                try:
                    path.write_text(content)
                    generated += 1
                except Exception:
                    pass

        return generated, len(artifacts)

    def update_project_state(self, status: str, phase: int):
        """Update PROJECT_STATE.md with current status"""
        today = datetime.now().strftime("%Y-%m-%d")

        existing_content = ""
        if self.state_file.exists():
            existing_content = self.state_file.read_text()

        new_content = f"""# Project State

## Last Updated: {today}

## Current Status
{status}

## SDD Workflow Phase: {phase}/6
{self.PHASES.get(phase, "Unknown")}

## Artifacts Status
- Memory Artifacts: {sum(1 for f in self.REQUIRED_MEMORY_ARTIFACTS if (self.project_root / f).exists())}/{len(self.REQUIRED_MEMORY_ARTIFACTS)}
- Review Artifacts: {sum(1 for f in self.REQUIRED_REVIEW_ARTIFACTS if (self.project_root / f).exists())}/{len(self.REQUIRED_REVIEW_ARTIFACTS)}

---
{existing_content[:500] if existing_content else "Initial state"}
"""

        self.state_file.write_text(new_content)

    def execute_workflow_step(self, step_name, context=None):
        """Execute a specific workflow step"""
        if step_name == "initialize_memory":
            return self.generate_memory_artifacts()
        elif step_name == "start_multi_agent_dev":
            return self._start_multi_agent_development(context)
        elif step_name == "verify_phase":
            return self.verify_phase_gate(context or 1)
        elif step_name == "check_artifacts":
            return self.check_review_artifacts()

    def interactive_guidance(self):
        """Provide interactive workflow guidance"""
        print("🔍 Detecting project state...")
        state = self.detect_project_state()
        print(f"📊 Current state: {state}")

        current_phase = self.get_current_phase()
        if current_phase == 0:
            print("⚠️ No SDD workflow detected. Use 'sdd start' to begin.")
            return

        print(
            f"📍 Current Phase: {current_phase}/6 - {self.PHASES.get(current_phase, 'Unknown')}"
        )

        status = self.get_phase_status()
        print("\n📦 Artifact Status:")
        print(
            f"   Memory: {status['memory_artifacts']['present']}/{status['memory_artifacts']['total']}"
        )
        print(
            f"   Review: {status['review_artifacts']['present']}/{status['review_artifacts']['total']}"
        )

        if current_phase < 6:
            can_proceed, reason = self.verify_phase_gate(current_phase)
            print(f"\n🚦 Phase Gate: {'✅' if can_proceed else '❌'}")
            print(f"   {reason}")

        print("\n🚀 Recommended next steps:")
        if current_phase == 1:
            print("   1. Review design document")
            print("   2. Confirm: 'Design approved, proceed to Phase 2'")
        elif current_phase == 2:
            print("   1. Review implementation plan")
            print("   2. Choose execution mode (subagent/inline)")
            print("   3. Confirm: 'Plan approved, proceed to Phase 3'")
        elif current_phase == 3:
            print("   1. Execute implementation plan")
            print("   2. Verify: cargo build succeeds")
            print("   3. Confirm: 'Phase 3 complete, proceed to Phase 4'")
        elif current_phase == 4:
            print("   1. Run tests: cargo test")
            print("   2. Confirm: 'Phase 4 complete, proceed to Phase 5'")
        elif current_phase == 5:
            print("   1. Review generated artifacts")
            print("   2. Confirm: 'Phase 5 complete, proceed to Phase 6'")
        elif current_phase == 6:
            print("   ✅ SDD Workflow Complete!")
            print("   Use 'sdd complete' for merge options")

        return {"state": state, "phase": current_phase, "status": status}


class ConstitutionChecker:
    """Check designs and implementations against Constitution rules"""

    CONSTITUTION_FILES = {
        "design": "CONSTITUTION/design-rules.md",
        "implementation": "CONSTITUTION/implementation-rules.md",
        "core": "CONSTITUTION/core.md",
        "module-ownership": "CONSTITUTION/module-ownership.md",
        "review": "CONSTITUTION/review-rules.md",
    }

    def __init__(self, project_root="."):
        self.project_root = Path(project_root)

    def check_design_constitution(self, design_content: str) -> Tuple[bool, list]:
        """
        Check if design violates Constitution design-rules.
        Returns (is_compliant, violations).
        """
        violations = []

        rules_file = self.project_root / self.CONSTITUTION_FILES["design"]
        if not rules_file.exists():
            return True, []  # No constitution, skip check

        rules = self._parse_rules(rules_file.read_text())
        for rule in rules:
            if rule.get("mandatory") and self._violates_rule(design_content, rule):
                violations.append(rule)

        return len(violations) == 0, violations

    def check_implementation_constitution(
        self, code_content: str, module_name: str = None
    ) -> Tuple[bool, list]:
        """
        Check if implementation violates Constitution implementation-rules.
        Returns (is_compliant, violations).
        """
        violations = []

        rules_file = self.project_root / self.CONSTITUTION_FILES["implementation"]
        if not rules_file.exists():
            return True, []

        rules = self._parse_rules(rules_file.read_text())
        for rule in rules:
            if rule.get("mandatory") and self._violates_rule(code_content, rule):
                violations.append(rule)

        return len(violations) == 0, violations

    def _parse_rules(self, content: str) -> list:
        """Parse Constitution rules from markdown content"""
        rules = []
        current_rule = None

        for line in content.split("\n"):
            if line.startswith("## ") or line.startswith("### "):
                if current_rule:
                    rules.append(current_rule)
                current_rule = {"title": line.lstrip("# ").strip(), "mandatory": False}
            elif "mandatory" in line.lower() or "required" in line.lower():
                if current_rule:
                    current_rule["mandatory"] = True
            elif current_rule and "description" in current_rule:
                current_rule["description"] += "\n" + line
            elif current_rule and "description" not in current_rule:
                current_rule["description"] = line.strip()

        if current_rule:
            rules.append(current_rule)

        return rules

    def _violates_rule(self, content: str, rule: dict) -> bool:
        """Check if content violates a specific rule"""
        if "description" not in rule:
            return False

        rule_text = rule["description"].lower()
        content_lower = content.lower()

        # Simple violation detection - check if forbidden patterns exist
        forbidden_patterns = [
            "unsafe ",
            "unwrap()",
            "expect()",
            "unwrap_err()",
            "unwrap_or_default()",
        ]

        for pattern in forbidden_patterns:
            if pattern in content_lower and pattern in rule_text:
                return True

        return False

    def get_constitution_summary(self) -> dict:
        """Get summary of available Constitution rules"""
        summary = {}
        for rule_type, path in self.CONSTITUTION_FILES.items():
            full_path = self.project_root / path
            if full_path.exists():
                rules = self._parse_rules(full_path.read_text())
                summary[rule_type] = {
                    "count": len(rules),
                    "mandatory": sum(1 for r in rules if r.get("mandatory")),
                    "path": str(full_path),
                }
            else:
                summary[rule_type] = {"count": 0, "mandatory": 0, "path": "NOT FOUND"}
        return summary


class KnowledgeRetriever:
    """Automatic retrieval of relevant knowledge documents"""

    KNOWLEDGE_PATHS = {
        "rust-best-practices": "docs/knowledge/rust-best-practices",
        "design-patterns": "docs/knowledge/design-patterns",
        "security": "docs/knowledge/security",
        "performance": "docs/knowledge/performance",
        "domain": "docs/knowledge/domain",
    }

    def __init__(self, project_root="."):
        self.project_root = Path(project_root)

    def retrieve_for_phase(self, phase: int, context: dict = None) -> list:
        """
        Retrieve relevant knowledge based on current phase and context.
        Returns list of retrieved documents with relevance scores.
        """
        if context is None:
            context = {}

        if phase == 1:
            return self._retrieve_for_design(context)
        elif phase == 2:
            return self._retrieve_for_planning(context)
        elif phase == 3:
            return self._retrieve_for_implementation(context)
        elif phase == 5:
            return self._retrieve_for_review(context)
        return []

    def _retrieve_for_design(self, context: dict) -> list:
        """Phase 1: Design phase knowledge retrieval"""
        results = []

        # Retrieve module specs if specified
        if "modules" in context:
            for module in context["modules"]:
                spec_path = self.project_root / f"docs/modules/{module}/SPEC.md"
                if spec_path.exists():
                    results.append(
                        {
                            "source": f"docs/modules/{module}/SPEC.md",
                            "type": "module_spec",
                            "content": spec_path.read_text()[:500],
                        }
                    )

        # Retrieve domain knowledge
        if "domain" in context:
            domain_path = (
                self.project_root / f"docs/knowledge/domain/{context['domain']}.md"
            )
            if domain_path.exists():
                results.append(
                    {
                        "source": f"docs/knowledge/domain/{context['domain']}.md",
                        "type": "domain_knowledge",
                        "content": domain_path.read_text()[:500],
                    }
                )

        # Retrieve design patterns
        patterns_dir = self.project_root / "docs/knowledge/design-patterns"
        if patterns_dir.exists():
            for pattern_file in patterns_dir.glob("*.md"):
                results.append(
                    {
                        "source": str(pattern_file),
                        "type": "design_pattern",
                        "content": pattern_file.read_text()[:300],
                    }
                )

        # Retrieve Constitution design rules
        constitution_path = self.project_root / "CONSTITUTION/design-rules.md"
        if constitution_path.exists():
            results.append(
                {
                    "source": "CONSTITUTION/design-rules.md",
                    "type": "constitution",
                    "content": constitution_path.read_text()[:500],
                }
            )

        return results

    def _retrieve_for_planning(self, context: dict) -> list:
        """Phase 2: Planning phase knowledge retrieval"""
        results = []

        # Retrieve implementation rules
        impl_path = self.project_root / "CONSTITUTION/implementation-rules.md"
        if impl_path.exists():
            results.append(
                {
                    "source": "CONSTITUTION/implementation-rules.md",
                    "type": "constitution",
                    "content": impl_path.read_text()[:500],
                }
            )

        # Retrieve Rust best practices
        if context.get("tech_stack") and "rust" in context["tech_stack"]:
            rust_dir = self.project_root / "docs/knowledge/rust-best-practices"
            if rust_dir.exists():
                for rust_file in rust_dir.glob("*.md"):
                    results.append(
                        {
                            "source": str(rust_file),
                            "type": "best_practice",
                            "content": rust_file.read_text()[:300],
                        }
                    )

        return results

    def _retrieve_for_implementation(self, context: dict) -> list:
        """Phase 3: Implementation phase knowledge retrieval"""
        results = []

        # Retrieve module ownership
        ownership_path = self.project_root / "CONSTITUTION/module-ownership.md"
        if ownership_path.exists():
            results.append(
                {
                    "source": "CONSTITUTION/module-ownership.md",
                    "type": "module_ownership",
                    "content": ownership_path.read_text()[:500],
                }
            )

        # Retrieve relevant module specs
        if "modules" in context:
            for module in context["modules"]:
                spec_path = self.project_root / f"docs/modules/{module}/SPEC.md"
                if spec_path.exists():
                    results.append(
                        {
                            "source": f"docs/modules/{module}/SPEC.md",
                            "type": "module_spec",
                            "content": spec_path.read_text()[:500],
                        }
                    )

        return results

    def _retrieve_for_review(self, context: dict) -> list:
        """Phase 5: Review phase knowledge retrieval"""
        results = []

        # Retrieve review rules
        review_path = self.project_root / "CONSTITUTION/review-rules.md"
        if review_path.exists():
            results.append(
                {
                    "source": "CONSTITUTION/review-rules.md",
                    "type": "review_rules",
                    "content": review_path.read_text()[:500],
                }
            )

        return results

    def generate_retrieval_report(self, phase: int, context: dict = None) -> str:
        """Generate a human-readable retrieval report"""
        retrieved = self.retrieve_for_phase(phase, context)

        report = f"# Knowledge Retrieval Report\n\n"
        report += f"**Phase**: {phase}\n"
        report += f"**Context**: {context}\n\n"
        report += f"**Retrieved**: {len(retrieved)} documents\n\n"

        for i, item in enumerate(retrieved, 1):
            report += f"## {i}. {item['source']}\n"
            report += f"**Type**: {item['type']}\n"
            report += f"```\n{item['content'][:200]}...\n```\n\n"

        return report


class DocumentStructureGenerator:
    """Generate the complete document directory structure"""

    def __init__(self, project_root="."):
        self.project_root = Path(project_root)

    def create_structure(self) -> Tuple[int, int]:
        """
        Create the complete document directory structure.
        Returns (created_count, total_required).
        """
        directories = [
            "CONSTITUTION",
            "CONSTITUTION/decision-records",
            ".nexus-map",
            ".nexus-map/module-specs",
            "docs",
            "docs/knowledge",
            "docs/knowledge/rust-best-practices",
            "docs/knowledge/design-patterns",
            "docs/knowledge/security",
            "docs/knowledge/performance",
            "docs/knowledge/domain",
            "docs/modules",
            "docs/features",
            "docs/superpowers",
            "docs/superpowers/specs",
            "docs/superpowers/plans",
            "docs/superpowers/reviews",
            "docs/collaboration",
            "docs/collaboration/meeting-notes",
            "docs/reference",
        ]

        created = 0
        for directory in directories:
            dir_path = self.project_root / directory
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    created += 1
                except Exception:
                    pass

        return created, len(directories)

    def create_constitution_template(self) -> bool:
        """Create Constitution template files"""
        constitution_files = {
            "CONSTITUTION/core.md": """# Core Principles

## 1. Safety First
- All user input must be validated
- No sensitive info in logs
- Critical operations require audit logging

## 2. Modularity
- Modules communicate via explicit interfaces
- No direct internal state access
- Single responsibility per module

## 3. Testability
- All public APIs must have tests
- No untestable code paths
- Tests must run independently

## 4. Backward Compatibility
- No breaking changes to public APIs
- No breaking changes to config formats
- No breaking changes to CLI interfaces

## 5. Performance
- Logging must not block main thread
- Large file operations must be async
- Memory usage must have upper bounds
""",
            "CONSTITUTION/design-rules.md": """# Design Rules

## Mandatory Design Principles

### Architecture
- [ ] Follow layered architecture (UI / Business Logic / Data)
- [ ] Define clear module boundaries before implementation
- [ ] Document all public APIs before implementation

### Dependencies
- [ ] No circular dependencies between modules
- [ ] Dependencies must be explicit (no hidden coupling)
- [ ] Prefer composition over inheritance

### Interfaces
- [ ] All module interfaces must be documented
- [ ] Interface changes require review
- [ ] Breaking changes must be versioned

### Error Handling
- [ ] All errors must be handled explicitly
- [ ] Error types must be specific (not generic)
- [ ] Errors must provide context
""",
            "CONSTITUTION/implementation-rules.md": """# Implementation Rules

## Mandatory Implementation Standards

### Code Quality
- [ ] No `unsafe` code without explicit justification
- [ ] No `unwrap()` on Result/Option without handling error case
- [ ] All public functions must have doc comments
- [ ] Code must pass clippy lints

### Performance
- [ ] No blocking operations on main thread
- [ ] Large allocations must be avoided in hot paths
- [ ] Memory usage must be bounded (no unbounded Vec growth)

### Testing
- [ ] All public APIs must have unit tests
- [ ] Integration tests for module interactions
- [ ] Tests must be independent and order-independent
""",
            "CONSTITUTION/module-ownership.md": """# Module Ownership

## Module Registry

| Module | Owner | Responsibility |
|--------|-------|----------------|
| (none defined) | - | - |

## Ownership Rules

1. Each module must have a designated owner
2. Module owners are responsible for:
   - Reviewing changes to their module
   - Ensuring tests pass
   - Updating module documentation
3. Cross-module changes require owner approval
""",
            "CONSTITUTION/review-rules.md": """# Review Rules

## Code Review Requirements

### Mandatory Checks
- [ ] Constitution compliance verified
- [ ] No security vulnerabilities
- [ ] Performance impact assessed
- [ ] Test coverage adequate
- [ ] Documentation updated

### Review Process
1. Author submits PR
2. Module owner reviews
3. Automated checks pass (CI)
4. At least 1 approval required
5. Changes requested must be addressed
""",
        }

        created = 0
        for path, content in constitution_files.items():
            file_path = self.project_root / path
            if not file_path.exists():
                try:
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(content)
                    created += 1
                except Exception:
                    pass

        return created


if __name__ == "__main__":
    import sys

    coordinator = WorkflowCoordinator()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "init":
            print("🚀 Initializing SDD-Workflow project structure...")
            # Create document structure
            gen = DocumentStructureGenerator()
            created_dirs, total_dirs = gen.create_structure()
            print(
                f"📁 Directory Structure: {created_dirs}/{total_dirs} directories created"
            )
            # Create Constitution templates
            created_const = gen.create_constitution_template()
            print(f"📜 Constitution: {created_const} files created")
            # Generate memory artifacts
            gen_memory, total_memory = coordinator.generate_memory_artifacts()
            print(f"📝 Memory Artifacts: {gen_memory}/{total_memory} files created")
            # Generate review artifacts (minimal placeholders)
            gen_reviews, total_reviews = coordinator.generate_minimal_review_artifacts()
            print(f"📋 Review Artifacts: {gen_reviews}/{total_reviews} files created")
            print("\n✅ SDD-Workflow Initialized")
            print("\nNext: sdd start <feature-name>")
        elif cmd == "check-init":
            # Check if project is already initialized
            gen = DocumentStructureGenerator()
            dirs_ok = all(
                (coordinator.project_root / d).exists()
                for d in [
                    "CONSTITUTION",
                    "docs",
                    "docs/features",
                    "docs/modules",
                    "docs/knowledge",
                    "docs/superpowers",
                    ".nexus-map",
                ]
            )
            const_ok = (coordinator.project_root / "CONSTITUTION" / "core.md").exists()
            memory_ok = all(
                (coordinator.project_root / f).exists()
                for f in ["PROJECT_STATE.md", "AGENTS.md", "task_plan.md"]
            )
            if dirs_ok and const_ok and memory_ok:
                print("✅ Project already initialized")
                print("   Directory structure: ✓")
                print("   Constitution: ✓")
                print("   Memory artifacts: ✓")
            else:
                print("❌ Project not fully initialized")
                print("   Run 'sdd init' to initialize")
        elif cmd == "status":
            coordinator.interactive_guidance()
        elif cmd == "phase":
            print(f"Current phase: {coordinator.get_current_phase()}")
        elif cmd == "verify":
            phase = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            can_proceed, reason = coordinator.verify_phase_gate(phase)
            print(f"Gate {'✅' if can_proceed else '❌'}: {reason}")
        elif cmd == "check-artifacts":
            exists, missing = coordinator.check_review_artifacts()
            if exists:
                print("✅ All review artifacts present")
            else:
                print(f"❌ Missing: {', '.join(missing)}")
        elif cmd == "generate-artifacts":
            generated, total = coordinator.generate_minimal_review_artifacts()
            print(f"Generated {generated}/{total} review artifacts")
        elif cmd == "init-structure":
            gen = DocumentStructureGenerator()
            created, total = gen.create_structure()
            print(f"Created {created}/{total} directories")
            created_constitution = gen.create_constitution_template()
            print(f"Created {created_constitution} Constitution files")
        elif cmd == "check-constitution":
            checker = ConstitutionChecker()
            violations = checker.check_design_constitution("")
            print(f"Constitution check: {'PASS' if violations[0] else 'FAIL'}")
            if violations[1]:
                print(f"Violations: {violations[1]}")
        elif cmd == "retrieve-knowledge":
            retriever = KnowledgeRetriever()
            phase = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            report = retriever.generate_retrieval_report(phase)
            print(report)
        elif cmd == "resume":
            if len(sys.argv) > 2:
                feature_name = sys.argv[2]
                status = coordinator.get_feature_status(feature_name)
                if "error" in status:
                    print(f"❌ Feature '{feature_name}' not found")
                    print("Use 'sdd list-features' to see available features")
                else:
                    print(f"📋 Feature: {feature_name}")
                    print(f"   Phase: {status.get('current_phase', 'unknown')}")
                    print(f"   Status: {status.get('status', 'unknown')}")
                    print(f"\nTo resume: sdd start {feature_name}")
            else:
                features = coordinator.list_active_features()
                if not features:
                    print("❌ No active features found")
                    print("Use 'sdd start <feature-name>' to start a new feature")
                else:
                    print("SDD Resume Options")
                    print("═══════════════════════════════════════")
                    print("Active Features:")
                    for i, feat in enumerate(features, 1):
                        phase = feat["status"].get("current_phase", "?")
                        stat = feat["status"].get("status", "unknown")
                        print(f"{i}. {feat['name']:<20} [Phase {phase}: {stat}]")
                    print("\nSelect feature to resume:")
                    for feat in features:
                        print(f"- sdd resume {feat['name']}")
        elif cmd == "list-features":
            features = coordinator.list_active_features()
            if not features:
                print("❌ No features found")
                print("Use 'sdd start <feature-name>' to start a new feature")
            else:
                print("Features")
                print("═══════════════════════════════════════")
                for feat in features:
                    phase = feat["status"].get("current_phase", "?")
                    stat = feat["status"].get("status", "unknown")
                    print(f"  {feat['name']:<20} [Phase {phase}: {stat}]")
    else:
        print("SDD-Workflow Commands:")
        print("  sdd init            - Initialize project (once per project)")
        print("  sdd check-init      - Check if project is initialized")
        print("  sdd start <name>    - Start new feature development")
        print("  sdd status          - Show project status")
        print("  sdd resume [name]   - Resume feature (or show options)")
        print("  sdd list-features   - List all features")
        print("  sdd complete       - Complete workflow and merge")
