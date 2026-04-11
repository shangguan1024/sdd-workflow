"""
Phase Orchestrator 基类
"""

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..director import ExecutionContext, GateResult


class PhaseOrchestrator(ABC):
    """
    Phase Orchestrator 基类
    
    Layer 2 职责:
    - 定义每个 Phase 的标准流程
    - 管理 Phase 内的 Step
    - 调用 Capability 执行具体任务
    - 触发 Checkpoint
    """
    
    def __init__(self, capability_registry=None):
        self.capability_registry = capability_registry
        self.steps = []
    
    @abstractmethod
    def execute(self, context: ExecutionContext) -> PhaseResult:
        """
        执行 Phase
        
        Args:
            context: 执行上下文
            
        Returns:
            PhaseResult: Phase 执行结果
        """
        pass
    
    def can_transition_to(self, context: ExecutionContext) -> GateResult:
        """
        检查是否可以进入下一 Phase
        
        Args:
            context: 执行上下文
            
        Returns:
            GateResult: Gate 评估结果
        """
        return GateResult(passed=True)
    
    def _execute_steps(self, context: ExecutionContext) -> PhaseResult:
        """
        执行所有 Step
        
        Args:
            context: 执行上下文
            
        Returns:
            PhaseResult: Step 执行结果
        """
        for step in self.steps:
            result = step.execute(context)
            if not result.success:
                return result
        
        return PhaseResult(success=True)
    
    def _save_checkpoint(self, context: ExecutionContext, step_name: str):
        """
        保存 Checkpoint
        
        Args:
            context: 执行上下文
            step_name: 当前 Step 名称
        """
        import json
        from pathlib import Path
        
        checkpoint_dir = context.feature_dir / ".sdd"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        checkpoint = {
            "feature_name": context.feature_name,
            "step": step_name,
            "metadata": context.metadata,
        }
        
        (checkpoint_dir / "checkpoint.json").write_text(json.dumps(checkpoint, indent=2))


class PhaseStep(ABC):
    """Phase Step 基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def execute(self, context: ExecutionContext) -> StepResult:
        """
        执行 Step
        
        Args:
            context: 执行上下文
            
        Returns:
            StepResult: Step 执行结果
        """
        pass


class StepResult:
    """Step 执行结果"""
    
    def __init__(
        self,
        success: bool,
        message: str = "",
        details: dict = None,
    ):
        self.success = success
        self.message = message
        self.details = details or {}


class PhaseResult:
    """Phase 执行结果"""
    
    def __init__(
        self,
        success: bool,
        artifacts: dict = None,
        message: str = "",
    ):
        self.success = success
        self.artifacts = artifacts or {}
        self.message = message
