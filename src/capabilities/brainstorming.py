"""
Brainstorming Capability
"""

from .base import Capability, CapabilityResult


class BrainstormingCapability(Capability):
    """Brainstorming Capability"""
    
    def __init__(self):
        super().__init__("brainstorming")
    
    def execute(self, context: "ExecutionContext") -> CapabilityResult:
        """执行 Brainstorming"""
        context.metadata["brainstorming_executed"] = True
        return CapabilityResult(
            success=True,
            message="Brainstorming completed",
        )
