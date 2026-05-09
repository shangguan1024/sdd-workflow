"""
Loop Detection Middleware
Doom Loop检测中间件
"""

from pathlib import Path
from typing import Any
import yaml

from .base import Middleware, MiddlewareResult


class LoopDetectionMiddleware(Middleware):
    """Doom Loop 检测中间件"""

    def __init__(self, config_path: Path | None = None, config_manager=None):
        self._config_manager = config_manager
        
        if config_manager:
            self.config = config_manager.load("loop_detection")
        else:
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
                message=(
                    f"🛑 硬性限制: {file_path} 已编辑 {count} 次。"
                    f"上下文可能已严重偏离原始需求。"
                ),
                suggestion=(
                    "请: 1) 重新阅读 research.md 中的需求 2) 检查设计文档"
                    " 3) 确认当前实现方向是否正确 4) 考虑是否需要回退"
                ),
                requires_confirmation=True,
                confirmation_options=["reconsider", "reset", "continue"],
            )

        if count >= warning_threshold:
            return MiddlewareResult(
                allowed=True,
                message=(
                    f"⚠️ 热点文件: {file_path} 已编辑 {count} 次。"
                    f"建议: 1) 确认实现方向正确 2) 检查需求和设计是否仍然一致"
                ),
                suggestion=(
                    "如果继续编辑同一文件，建议先刷新上下文"
                    "（检查 research.md 中的需求和约束是否仍然被满足）"
                ),
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