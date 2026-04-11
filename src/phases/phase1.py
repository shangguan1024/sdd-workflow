"""
Phase 1: Requirements Analysis Orchestrator
需求分析阶段
"""

from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..director import ExecutionContext, GateResult

from .base import PhaseOrchestrator, PhaseResult, PhaseStep


class Phase1Orchestrator(PhaseOrchestrator):
    """
    Phase 1: Requirements Analysis
    
    职责:
    - 探索项目上下文
    - 分析存量代码
    - 收集需求
    - 生成设计方案
    - Constitution 合规检查
    - 用户审批
    """
    
    STEPS = [
        "explore_context",
        "analyze_existing_code",
        "gather_requirements",
        "generate_design",
        "impact_analysis",
        "expert_knowledge",
        "constitution_check",
        "user_approval",
    ]
    
    def __init__(self, capability_registry=None):
        super().__init__(capability_registry)
        self._init_steps()
    
    def _init_steps(self):
        """初始化 Steps"""
        self.steps = [
            StepExploreContext("explore_context"),
            StepAnalyzeExistingCode("analyze_existing_code"),
            StepGatherRequirements("gather_requirements"),
            StepGenerateDesign("generate_design"),
            StepImpactAnalysis("impact_analysis"),
            StepExpertKnowledge("expert_knowledge"),
            StepConstitutionCheck("constitution_check"),
            StepUserApproval("user_approval"),
        ]
    
    def execute(self, context: ExecutionContext) -> PhaseResult:
        """执行 Phase 1"""
        try:
            # 调用 brainstorming Capability
            capability = context.capability
            if capability:
                result = capability.execute(context)
                if not result.success:
                    return PhaseResult(success=False, message=result.message)
            
            # 执行 Steps
            for step in self.steps:
                result = step.execute(context)
                if not result.success:
                    return PhaseResult(success=False, message=result.message)
                
                # 每个 Step 完成后保存 Checkpoint
                self._save_checkpoint(context, step.name)
            
            return PhaseResult(
                success=True,
                artifacts={"design-doc": context.artifacts.get("design-doc")},
                message="Phase 1 completed successfully",
            )
            
        except Exception as e:
            return PhaseResult(success=False, message=f"Phase 1 failed: {e}")
    
    def can_transition_to(self, context: ExecutionContext) -> GateResult:
        """检查是否可以进入 Phase 2"""
        required_artifacts = ["design-doc"]
        
        for artifact in required_artifacts:
            if artifact not in context.artifacts:
                return GateResult(
                    passed=False,
                    message=f"Missing required artifact: {artifact}",
                    blockers=[artifact],
                )
        
        # 检查用户是否已批准
        if not context.metadata.get("design_approved"):
            return GateResult(
                passed=False,
                message="Design not approved by user",
                blockers=["user_approval"],
            )
        
        return GateResult(passed=True)


class StepExploreContext(PhaseStep):
    """Step 1: 探索项目上下文"""
    
    def execute(self, context: ExecutionContext) -> "StepResult":
        """探索项目上下文"""
        # TODO: 实现项目上下文探索逻辑
        # - 扫描项目结构
        # - 识别现有模块
        # - 加载 .nexus-map/
        
        context.metadata["explore_context_completed"] = True
        return StepResult(success=True, message="Context explored")


class StepAnalyzeExistingCode(PhaseStep):
    """Step 2: 分析存量代码"""
    
    def execute(self, context: ExecutionContext) -> "StepResult":
        """分析存量代码，识别可复用组件"""
        # TODO: 实现存量代码分析
        # - 识别相关模块
        # - 找到可复用组件
        # - 分析架构违规
        
        context.metadata["existing_code_analysis_completed"] = True
        return StepResult(success=True, message="Existing code analyzed")


class StepGatherRequirements(PhaseStep):
    """Step 3: 收集需求"""
    
    def execute(self, context: ExecutionContext) -> "StepResult":
        """收集需求"""
        # TODO: 实现需求收集
        # - 与用户对话收集需求
        # - 解析需求
        # - 分类和去重
        
        context.metadata["requirements_collected"] = True
        return StepResult(success=True, message="Requirements gathered")


class StepGenerateDesign(PhaseStep):
    """Step 4: 生成设计"""
    
    def execute(self, context: ExecutionContext) -> "StepResult":
        """生成设计方案"""
        # TODO: 实现设计生成
        # - 基于需求生成设计
        # - 编写设计文档
        
        design_doc = f"""# Design: {context.feature_name}

## Overview

## Requirements

## Architecture

## Implementation Plan

## Verification
"""
        context.artifacts["design-doc"] = design_doc
        return StepResult(success=True, message="Design generated")


class StepImpactAnalysis(PhaseStep):
    """Step 5: 影响分析"""
    
    def execute(self, context: ExecutionContext) -> "StepResult":
        """分析设计变更对系统的影响"""
        # TODO: 实现影响分析
        # - 识别受影响的模块
        # - 评估回归风险
        # - 生成缓解策略
        
        context.metadata["impact_analysis_completed"] = True
        return StepResult(success=True, message="Impact analysis completed")


class StepExpertKnowledge(PhaseStep):
    """Step 6: 专家经验融入"""
    
    def execute(self, context: ExecutionContext) -> "StepResult":
        """融入专家经验和最佳实践"""
        # TODO: 实现专家经验融入
        # - 查询知识库
        # - 应用设计模式
        # - 避免常见陷阱
        
        context.metadata["expert_knowledge_integrated"] = True
        return StepResult(success=True, message="Expert knowledge integrated")


class StepConstitutionCheck(PhaseStep):
    """Step 7: Constitution 检查"""
    
    def execute(self, context: ExecutionContext) -> "StepResult":
        """检查设计是否符合 Constitution"""
        # TODO: 实现 Constitution 合规检查
        # - 加载 Constitution 规则
        # - 检查设计合规性
        # - 报告违规
        
        context.metadata["constitution_compliant"] = True
        return StepResult(success=True, message="Constitution check passed")


class StepUserApproval(PhaseStep):
    """Step 8: 用户审批"""
    
    def execute(self, context: ExecutionContext) -> "StepResult":
        """等待用户审批"""
        # 注意: 用户审批是异步的，这里只是标记需要审批
        # 实际审批由 CLI 层处理
        
        if context.metadata.get("design_approved"):
            return StepResult(success=True, message="Design approved")
        else:
            # 标记需要用户审批
            context.metadata["awaiting_user_approval"] = True
            return StepResult(
                success=True,
                message="Design ready for user approval",
            )
