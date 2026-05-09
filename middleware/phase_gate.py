"""
Phase Gate Middleware
Constitution强制检查中间件
"""

from pathlib import Path
from typing import Any

from .base import Middleware, MiddlewareResult


class PhaseGateMiddleware(Middleware):
    """Phase Gate 检查中间件"""

    def __init__(
        self, 
        constitution_dir: Path, 
        config_path: Path | None = None,
        config_manager=None
    ):
        self.constitution_dir = constitution_dir
        self._config_manager = config_manager
        
        if not config_manager:
            self.config_path = (
                config_path
                or constitution_dir / ".." / "config" / "constitution_enforcer.yaml"
            )
        
        self._init_enforcer()

    def _init_enforcer(self):
        try:
            from scripts.constitution_enforcer import ConstitutionEnforcer

            self.enforcer = ConstitutionEnforcer(
                self.constitution_dir, 
                config_path=None if self._config_manager else self.config_path,
                config_manager=self._config_manager
            )
        except ImportError as e:
            raise RuntimeError(
                f"ConstitutionEnforcer is required for Phase Gates but failed to import: {e}. "
                "Please ensure scripts/constitution_enforcer.py exists and is importable."
            )

    def before_action(self, context: dict) -> MiddlewareResult:
        phase = context.get("phase", 0)

        if self.enforcer is None:
            return MiddlewareResult(allowed=True)

        content = context.get("content", "")

        if phase == 1:
            result = self.enforcer.check_design(content)
        elif phase == 2:
            result = self.enforcer.check_plan(content)
        elif phase == 3:
            result = self.enforcer.check_code(content)
        else:
            return MiddlewareResult(allowed=True)

        if result.passed:
            return MiddlewareResult(
                allowed=True, message="✅ Constitution 合规检查通过"
            )

        from scripts.constitution_enforcer import ViolationFormatter

        formatted = ViolationFormatter.format(result)

        return MiddlewareResult(
            allowed=False,
            message=formatted,
            suggestion="必须修复违规才能继续",
            requires_confirmation=True,
            confirmation_options=["fix", "explain", "override"],
        )

    def after_action(self, context: dict, result: Any) -> MiddlewareResult:
        return MiddlewareResult(allowed=True)