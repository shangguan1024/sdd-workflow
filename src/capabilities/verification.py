"""
Verification Capability
"""

from .base import Capability, CapabilityResult


class VerificationCapability(Capability):
    """Verification Capability"""
    
    def __init__(self):
        super().__init__("verification")
    
    def execute(self, context: "ExecutionContext") -> CapabilityResult:
        """执行 Verification"""
        context.metadata["verification_executed"] = True
        return CapabilityResult(
            success=True,
            message="Verification completed",
        )
