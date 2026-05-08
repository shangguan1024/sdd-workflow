"""
Shared constants for SDD-Workflow.
Single source of truth for artifact paths.

Note: REQUIRED_REVIEW_ARTIFACTS paths match config/artifact_checker.yaml
The yaml file contains additional configuration (required_sections).
"""

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
]

REQUIRED_REVIEW_ARTIFACTS = [
    "docs/reviews/architecture_review.md",
    "docs/reviews/code_quality_review.md",
]

REQUIRED_ARTIFACTS_PER_FEATURE = [
    "docs/features/{feature}/findings.md",
    "docs/features/{feature}/design-doc.md",
    "docs/features/{feature}/task_plan.md",
    "docs/features/{feature}/.sdd/conversation_memory.json",
]
