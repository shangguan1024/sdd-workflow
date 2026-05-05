"""
Shared constants for SDD-Workflow.
Single source of truth for artifact paths.
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
    "docs/reviews/test_coverage_report.md",
    "docs/reviews/requirements_verification.md",
]

FEATURE_ARTIFACTS = [
    "task_plan.md",
    "findings.md",
    "progress.md",
]
