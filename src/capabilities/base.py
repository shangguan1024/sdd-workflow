"""
Capability 基类
"""

from abc import ABC, abstractmethod


class Capability(ABC):
    """Capability 基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def execute(self, context: "ExecutionContext") -> "CapabilityResult":
        """执行 Capability"""
        pass


class CapabilityResult:
    """Capability 执行结果"""
    
    def __init__(self, success: bool, message: str = "", artifacts: dict = None):
        self.success = success
        self.message = message
        self.artifacts = artifacts or {}
