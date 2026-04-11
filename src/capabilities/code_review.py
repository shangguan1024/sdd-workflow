"""
Code Review Capability
"""

from .base import Capability, CapabilityResult


class CodeReviewCapability(Capability):
    """Code Review Capability"""
    
    def __init__(self):
        super().__init__("code-review")
    
    def execute(self, context: "ExecutionContext") -> CapabilityResult:
        """执行 Code Review"""
        context.metadata["code_review_executed"] = True
        return CapabilityResult(
            success=True,
            message="Code Review completed",
        )
