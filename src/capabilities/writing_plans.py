"""
Writing Plans Capability
"""

from .base import Capability, CapabilityResult


class WritingPlansCapability(Capability):
    """Writing Plans Capability"""
    
    def __init__(self):
        super().__init__("writing-plans")
    
    def execute(self, context: "ExecutionContext") -> CapabilityResult:
        """执行 Writing Plans"""
        context.metadata["writing_plans_executed"] = True
        return CapabilityResult(
            success=True,
            message="Writing Plans completed",
        )
