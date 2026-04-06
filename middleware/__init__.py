"""
Middleware 基类和常用中间件实现
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable, Any
import yaml


@dataclass
class MiddlewareResult:
    allowed: bool = True
    message: Optional[str] = None
    suggestion: Optional[str] = None
    requires_confirmation: bool = False
    confirmation_options: Optional[list[str]] = None
    add_to_context: bool = False
    error: Optional[str] = None


class Middleware(ABC):
    """Middleware 基类"""

    @abstractmethod
    def before_action(self, context: dict) -> MiddlewareResult:
        """在操作前执行"""
        pass

    @abstractmethod
    def after_action(self, context: dict, result: Any) -> MiddlewareResult:
        """在操作后执行"""
        pass


class PhaseGateMiddleware(Middleware):
    """Phase Gate 检查中间件"""

    def __init__(self, constitution_dir: Path, config_path: Path | None = None):
        self.constitution_dir = constitution_dir
        self.config_path = (
            config_path
            or constitution_dir / ".." / "config" / "constitution_enforcer.yaml"
        )
        self._init_enforcer()

    def _init_enforcer(self):
        try:
            from scripts.constitution_enforcer import ConstitutionEnforcer

            self.enforcer = ConstitutionEnforcer(
                self.constitution_dir, self.config_path
            )
        except ImportError:
            self.enforcer = None

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


class LoopDetectionMiddleware(Middleware):
    """Doom Loop 检测中间件"""

    def __init__(self, config_path: Path | None = None):
        self.config_path = (
            config_path
            or Path(__file__).parent.parent / "config" / "loop_detection.yaml"
        )
        self.config = self._load_config()
        self.file_edit_counts: dict[str, dict] = {}

    def _load_config(self) -> dict:
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return {
            "loop_detection": {
                "enabled": True,
                "thresholds": {"warning_threshold": 5, "hard_limit": 15},
            }
        }

    def record_edit(self, file_path: str, session_id: str):
        """记录文件编辑"""
        cfg = self.config.get("loop_detection", {})
        if not cfg.get("enabled", True):
            return

        thresholds = cfg.get("thresholds", {})
        warning_threshold = thresholds.get("warning_threshold", 5)
        hard_limit = thresholds.get("hard_limit", 15)
        ignore_patterns = cfg.get("ignore_patterns", [])

        for pattern in ignore_patterns:
            if pattern in file_path:
                return

        if file_path not in self.file_edit_counts:
            self.file_edit_counts[file_path] = {
                "count": 0,
                "session_id": session_id,
                "history": [],
            }

        state = self.file_edit_counts[file_path]
        state["count"] += 1

        return self.check_loop(file_path)

    def check_loop(self, file_path: str) -> MiddlewareResult:
        """检查是否进入 doom loop"""
        cfg = self.config.get("loop_detection", {})
        thresholds = cfg.get("thresholds", {})
        warning_threshold = thresholds.get("warning_threshold", 5)
        hard_limit = thresholds.get("hard_limit", 15)

        if file_path not in self.file_edit_counts:
            return MiddlewareResult(allowed=True)

        count = self.file_edit_counts[file_path]["count"]

        if count >= hard_limit:
            return MiddlewareResult(
                allowed=False,
                message=f"⚠️ 硬性限制: {file_path} 已编辑 {count} 次",
                suggestion="建议重新审视方案，可能需要回退或改变方向",
                requires_confirmation=True,
                confirmation_options=["reconsider", "reset", "continue"],
            )

        if count >= warning_threshold:
            return MiddlewareResult(
                allowed=True,
                message=f"⚠️ 建议关注: {file_path} 已编辑 {count} 次",
                suggestion="考虑是否在正确的方向上",
                add_to_context=True,
            )

        return MiddlewareResult(allowed=True)

    def reset(self, file_path: str | None = None, session_id: str | None = None):
        """重置计数"""
        if file_path:
            self.file_edit_counts.pop(file_path, None)
        elif session_id:
            self.file_edit_counts = {
                k: v
                for k, v in self.file_edit_counts.items()
                if v.get("session_id") != session_id
            }
        else:
            self.file_edit_counts.clear()

    def before_action(self, context: dict) -> MiddlewareResult:
        return MiddlewareResult(allowed=True)

    def after_action(self, context: dict, result: Any) -> MiddlewareResult:
        tool_name = context.get("tool_name", "")

        if tool_name in ["write_file", "edit_file", "str_replace"]:
            file_path = context.get("file_path", "")
            session_id = context.get("session_id", "")

            if file_path:
                result = self.record_edit(file_path, session_id)
                return result if result else MiddlewareResult(allowed=True)

        return MiddlewareResult(allowed=True)


class ArtifactCompleteMiddleware(Middleware):
    """Phase 5 制品完整性检查中间件"""

    def __init__(
        self, project_root: Path | None = None, config_path: Path | None = None
    ):
        self.project_root = project_root or Path.cwd()
        self.config_path = (
            config_path
            or Path(__file__).parent.parent / "config" / "artifact_checker.yaml"
        )
        self._init_checker()

    def _init_checker(self):
        try:
            from scripts.artifact_checker import ArtifactChecker

            self.checker = ArtifactChecker(self.config_path)
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
