"""
Artifact Complete Middleware
Phase 5 制品完整性检查中间件
"""

from pathlib import Path
from typing import Any

import yaml

from .base import Middleware, MiddlewareResult


class ArtifactCompleteMiddleware(Middleware):
    """Phase 5 制品完整性检查中间件"""

    def __init__(
        self, 
        project_root: Path | None = None, 
        config_path: Path | None = None,
        config_manager=None
    ):
        self.project_root = project_root or Path.cwd()
        self._config_manager = config_manager
        
        if not config_manager:
            self.config_path = (
                config_path
                or Path(__file__).parent.parent / "config" / "artifact_checker.yaml"
            )
        
        self._init_checker()

    def _init_checker(self):
        try:
            from scripts.artifact_checker import ArtifactChecker

            self.checker = ArtifactChecker(
                config_path=None if self._config_manager else self.config_path,
                config_manager=self._config_manager
            )
        except ImportError:
            self.checker = None

    def check(self) -> MiddlewareResult:
        """检查 Phase 5 制品完整性"""
        if self.checker is None:
            return MiddlewareResult(allowed=True)

        result = self.checker.check(self.project_root)

        if result.complete:
            from scripts.artifact_checker import ArtifactReportFormatter

            report = ArtifactReportFormatter.format(result)
            return MiddlewareResult(allowed=True, message=report)

        cfg = self.config_path.parent / "artifact_checker.yaml"
        if cfg.exists():
            with open(cfg) as f:
                config = yaml.safe_load(f)

            if config.get("artifact_checker", {}).get("auto_generate", True):
                return MiddlewareResult(
                    allowed=True,
                    message=f"⚠️ Missing {result.missing_count} artifact(s), auto-generating...",
                    suggestion="将自动生成缺失的制品",
                )

        from scripts.artifact_checker import ArtifactReportFormatter

        report = ArtifactReportFormatter.format(result)

        return MiddlewareResult(
            allowed=False,
            message=report,
            suggestion="必须先生成完整的审查制品",
            requires_confirmation=True,
            confirmation_options=["generate", "skip"],
        )

    def before_action(self, context: dict) -> MiddlewareResult:
        phase = context.get("phase")

        if phase == 6:
            return self.check()

        return MiddlewareResult(allowed=True)

    def after_action(self, context: dict, result: Any) -> MiddlewareResult:
        return MiddlewareResult(allowed=True)