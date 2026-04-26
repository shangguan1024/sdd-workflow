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


class PhaseCompressionMiddleware(Middleware):
    """
    Phase 边界压缩中间件。

    在 Phase 转换时检查当前 Phase 的结构化摘要是否已写入对应文件。
    如果没有，阻止进入下一 Phase，要求 AI 先生成摘要。

    摘要映射:
        Understanding → 1: research.md 包含 "## 结论"
        1 → 2: findings.md 包含 "## Design Summary"
        2 → 3: findings.md 包含 "## Plan Summary"
        3 → 4: progress.md 包含 "## Implementation Summary"
        4 → 5: progress.md 包含 "## Test Summary"
        5 → 6: progress.md 包含 "## Review Summary"
    """

    PHASE_SUMMARY_MAP = {
        1: {"file": "research.md", "marker": "## 结论"},
        2: {"file": "findings.md", "marker": "## Design Summary"},
        3: {"file": "findings.md", "marker": "## Plan Summary"},
        4: {"file": "progress.md", "marker": "## Implementation Summary"},
        5: {"file": "progress.md", "marker": "## Test Summary"},
        6: {"file": "progress.md", "marker": "## Review Summary"},
    }

    REQUIRED_ELEMENTS = [
        "完成了什么",
        "关键决策",
        "问题",
        "待解决",
        "下一阶段",
    ]

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()

    def before_action(self, context: dict) -> MiddlewareResult:
        from_phase = context.get("from_phase", 0)
        feature_name = context.get("feature_name", "")

        if from_phase <= 0 or not feature_name:
            return MiddlewareResult(allowed=True)

        check = self._check_summary_exists(context, from_phase)
        if not check["exists"]:
            return MiddlewareResult(
                allowed=False,
                message=(
                    f"\u26a0\ufe0f Phase {from_phase} 边界压缩未完成。\n"
                    f"文件 `{check['expected_file']}` 中缺少 `{check['expected_marker']}` 章节。\n"
                    f"请在进入下一阶段前生成 Phase {from_phase} 的结构化摘要。"
                ),
                suggestion=(
                    f"将以下 5 项内容追加到 {check['expected_file']} 的 {check['expected_marker']} 章节:\n"
                    "1. 本阶段完成了什么\n"
                    "2. 关键决策\n"
                    "3. 发现的问题\n"
                    "4. 待后续解决的问题\n"
                    "5. 下一阶段注意事项"
                ),
                requires_confirmation=True,
                confirmation_options=["generate_summary", "skip_compression"],
            )

        quality = self._check_summary_quality(check["content"])
        if quality["warnings"]:
            return MiddlewareResult(
                allowed=True,
                message=(
                    f"\u2139\ufe0f Phase {from_phase} 摘要已存在，但可以更完善:\n"
                    + "\n".join(f"  - {w}" for w in quality["warnings"])
                ),
                add_to_context=True,
            )

        return MiddlewareResult(
            allowed=True,
            message=f"\u2705 Phase {from_phase} 边界压缩已完成 ({check['expected_file']})",
        )

    def after_action(self, context: dict, result: Any) -> MiddlewareResult:
        return MiddlewareResult(allowed=True)

    def _check_summary_exists(self, context: dict, from_phase: int) -> dict:
        spec = self.PHASE_SUMMARY_MAP.get(from_phase)
        if not spec:
            return {"exists": True, "expected_file": "", "expected_marker": "", "content": ""}

        feature_name = context.get("feature_name", "")
        feature_dir = self.project_root / "docs" / "features" / feature_name
        target_file = feature_dir / spec["file"]
        expected_marker = spec["marker"]

        if not target_file.exists():
            return {
                "exists": False,
                "expected_file": f"docs/features/{feature_name}/{spec['file']}",
                "expected_marker": expected_marker,
                "content": "",
            }

        content = target_file.read_text(encoding="utf-8")
        alt_marker = "## Conclusions" if expected_marker == "## 结论" else expected_marker

        if expected_marker.lower() in content.lower() or alt_marker.lower() in content.lower():
            return {
                "exists": True,
                "expected_file": f"docs/features/{feature_name}/{spec['file']}",
                "expected_marker": expected_marker,
                "content": content,
            }

        return {
            "exists": False,
            "expected_file": f"docs/features/{feature_name}/{spec['file']}",
            "expected_marker": expected_marker,
            "content": content,
        }

    def _check_summary_quality(self, content: str) -> dict:
        warnings = []
        content_lower = content.lower()

        element_keywords = {
            "完成了什么": ["完成", "done", "completed", "achieved"],
            "关键决策": ["决策", "decision", "决定", "选择"],
            "问题": ["问题", "issue", "problem", "bug"],
            "待解决": ["待解决", "pending", "todo", "后续"],
            "下一阶段": ["下一", "next", "后续阶段", "注意事项"],
        }

        for element, keywords in element_keywords.items():
            found = any(kw in content_lower for kw in keywords)
            if not found:
                warnings.append(f"可能缺少: {element}")

        return {"warnings": warnings}

