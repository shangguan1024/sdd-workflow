"""
SDD Workflow Entry Point
便捷工作流入口
"""

from pathlib import Path
from typing import Optional

from .director import Director, Phase
from .checkpoint import CheckpointManager
from .quality import QualityHarness, get_profile
from .rules import RuleParser


class SDDWorkflow:
    """
    SDD Workflow 便捷入口
    
    整合 Director、Checkpoint、Quality Harness
    提供单一入口点
    """
    
    def __init__(
        self,
        project_root: Path = Path("."),
        quality_profile: str = "standard",
    ):
        self.project_root = project_root
        self.director = Director(project_root)
        self.checkpoint_manager = CheckpointManager(project_root)
        self.quality_harness = QualityHarness(project_root, get_profile(quality_profile))
        self.rule_parser = RuleParser()
    
    def init(self, **kwargs) -> bool:
        """初始化项目"""
        from .cli import InitCommand
        
        command = InitCommand(**kwargs)
        result = self.director.initialize(command)
        return result.success
    
    def start(self, feature_name: str, capability: str = "brainstorming", **kwargs) -> bool:
        """开始特性开发"""
        from .cli import StartCommand
        
        command = StartCommand(feature=feature_name, capability=capability, **kwargs)
        result = self.director.start_feature(command)
        return result.success
    
    def resume(self, feature_name: Optional[str] = None, **kwargs) -> bool:
        """恢复特性开发"""
        from .cli import ResumeCommand
        
        command = ResumeCommand(feature=feature_name, **kwargs)
        result = self.director.resume_feature(command)
        return result.success
    
    def status(self, feature_name: Optional[str] = None, verbose: bool = False, **kwargs) -> dict:
        """获取状态"""
        from .cli import StatusCommand
        
        command = StatusCommand(feature=feature_name, verbose=verbose, **kwargs)
        result = self.director.show_status(command)
        
        return {
            "success": result.success,
            "message": result.message,
            "details": result.details,
        }
    
    def complete(self, **kwargs) -> bool:
        """完成工作流"""
        from .cli import CompleteCommand
        
        command = CompleteCommand(**kwargs)
        result = self.director.complete(command)
        return result.success
    
    def run_quality_assessment(self, feature_name: str, phase: str = "development") -> dict:
        """运行质量评估"""
        from .director import ExecutionContext
        
        context = ExecutionContext(
            project_root=self.project_root,
            feature_name=feature_name,
            feature_dir=self.project_root / "docs" / "features" / feature_name,
        )
        
        return self.quality_harness.run_assessment(feature_name, phase, context)
    
    def load_rules(self, rule_files: list) -> dict:
        """加载规则文件"""
        return self.rule_parser.parse_multiple(rule_files)
