"""
Context Monitor - mid-phase context usage tracking and refresh.

Addresses context window overflow during long phases (especially Phase 3).
When edit/task thresholds are exceeded, generates a compact context refresh
summary and prints it to stdout so the LLM re-acquires critical requirements
and design decisions that may have been pushed out of the context window.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .director import ExecutionContext


class ContextMonitor:
    """
    Tracks context usage within a phase and triggers context refresh
    when thresholds are exceeded, preventing context loss during
    long development sessions.
    """

    DEFAULT_THRESHOLDS = {
        "edits_between_refresh": 20,
        "tasks_between_refresh": 3,
        "same_file_warning": 5,
        "same_file_hard_limit": 15,
    }

    def __init__(self, thresholds: Dict[str, int] = None):
        self.edit_count = 0
        self.task_count = 0
        self.last_refresh_at_edit = 0
        self.last_refresh_at_task = 0
        self.refresh_count = 0
        self.per_file_edits: Dict[str, int] = {}
        self.thresholds = thresholds or dict(self.DEFAULT_THRESHOLDS)
        self.refresh_history: List[Dict] = []

    # ── tracking ──

    def record_edit(self, file_path: str):
        self.edit_count += 1
        self.per_file_edits[file_path] = self.per_file_edits.get(file_path, 0) + 1

    def record_task(self, task_name: str = ""):
        self.task_count += 1

    def reset(self):
        self.edit_count = 0
        self.task_count = 0
        self.last_refresh_at_edit = 0
        self.last_refresh_at_task = 0
        self.refresh_count = 0
        self.per_file_edits.clear()
        self.refresh_history.clear()

    # ── threshold checks ──

    def should_refresh(self) -> tuple:
        """Returns (should_refresh: bool, reason: str)"""
        edits_since = self.edit_count - self.last_refresh_at_edit
        tasks_since = self.task_count - self.last_refresh_at_task

        if edits_since >= self.thresholds["edits_between_refresh"]:
            return True, (
                f"编辑阈值触发: {edits_since} 次编辑未刷新上下文 "
                f"(阈值: {self.thresholds['edits_between_refresh']})"
            )

        if tasks_since >= self.thresholds["tasks_between_refresh"]:
            return True, (
                f"Task 阈值触发: {tasks_since} 个 task 未刷新上下文 "
                f"(阈值: {self.thresholds['tasks_between_refresh']})"
            )

        for fp, count in self.per_file_edits.items():
            if count >= self.thresholds["same_file_warning"]:
                return True, (
                    f"热点文件触发: `{fp}` 已编辑 {count} 次，"
                    f"建议刷新上下文并检查方向是否正确"
                )

        return False, ""

    def mark_refreshed(self):
        self.last_refresh_at_edit = self.edit_count
        self.last_refresh_at_task = self.task_count
        self.refresh_count += 1
        self.refresh_history.append({
            "at_edit": self.edit_count,
            "at_task": self.task_count,
            "time": datetime.now().isoformat(),
        })

    # ── context refresh generation ──

    def generate_refresh(self, context: "ExecutionContext") -> str:
        """Generate compact context injection (~500-800 words)."""
        feature_name = context.feature_name
        feature_dir = context.feature_dir

        lines = []
        sep = "=" * 60
        sub = "─" * 60

        lines.append(f"\n{sep}")
        lines.append(f"  🔄 CONTEXT REFRESH #{self.refresh_count + 1}")
        lines.append(f"  编辑: {self.edit_count} | Task: {self.task_count}")
        lines.append(sep)
        lines.append("")

        # 1. Feature goal
        lines.append("## 🎯 特性目标")
        task_plan = feature_dir / "task_plan.md"
        if task_plan.exists():
            content = task_plan.read_text(encoding="utf-8")
            non_header = [l.strip() for l in content.split("\n")
                          if l.strip() and not l.strip().startswith("#")]
            if non_header:
                lines.append(" ".join(non_header[:2])[:400])
        lines.append(f"Feature: {feature_name}")
        lines.append("")

        # 2. Key requirements & constraints from findings.md
        findings_file = feature_dir / "findings.md"
        if findings_file.exists():
            lines.append("## 📋 关键需求与约束")
            content = findings_file.read_text(encoding="utf-8")
            extracted = self._extract_section(content, [
                "## Phase 0: Research", "## Research", "## 关键需求",
                "## Requirements", "## 约束", "## Constraints",
            ], max_chars=500)
            if extracted:
                lines.append(extracted)
            else:
                lines.append("（见 findings.md Phase 0）")
            lines.append("")

        # 3. Design decisions from spec
        design_content = self._read_design_spec(feature_dir)
        if design_content:
            lines.append("## 🏗️ 架构设计决策")
            extracted = self._extract_section(design_content, [
                "## Architecture", "## 架构", "## Module Design",
                "## Overview", "## 概述",
            ], max_chars=400)
            if extracted:
                lines.append(extracted)
            else:
                lines.append(design_content[:300])
            lines.append("")

        # 4. Current progress (from findings.md)
        findings_file = feature_dir / "findings.md"
        if findings_file.exists():
            lines.append("## 📍 当前进度")
            content = findings_file.read_text(encoding="utf-8")
            # Extract the latest Phase section
            phase_sections = []
            for marker in ["## Phase 3:", "## Phase 4:", "## Phase 5:"]:
                idx = content.find(marker)
                if idx >= 0:
                    phase_sections.append(content[idx:])
            if phase_sections:
                # Use the latest phase section (last 400 chars)
                latest = phase_sections[-1]
                lines.append(latest[:400].strip())
            else:
                # Use Accomplished section if no phase progress
                accomplished = self._extract_section(content, ["## Accomplished"], max_chars=400)
                if accomplished:
                    lines.append(accomplished)
            lines.append("")

        # 5. Hot files
        hot_files = [(fp, c) for fp, c in self.per_file_edits.items()
                     if c >= self.thresholds["same_file_warning"]]
        if hot_files:
            lines.append("## ⚠️ 高频编辑文件")
            for fp, count in sorted(hot_files, key=lambda x: -x[1]):
                lines.append(f"  - `{fp}` ({count} 次编辑)")
            lines.append("")

        # 6. All modified files summary
        if self.per_file_edits:
            lines.append("## 📝 本阶段编辑的文件")
            for fp, count in sorted(self.per_file_edits.items(), key=lambda x: -x[1])[:10]:
                flag = " ⚠️" if count >= self.thresholds["same_file_warning"] else ""
                lines.append(f"  - `{fp}` ({count} 次){flag}")
            lines.append("")

        # 7. Checkpoint reminder
        lines.append("## ⚠️ 请确认")
        lines.append("以上需求和设计决策是否仍然一致？当前实现方向是否正确？")
        lines.append("如有偏离，请先修正方向再继续。")
        lines.append("")
        lines.append(sub)
        lines.append("  END OF CONTEXT REFRESH")
        lines.append(sub)
        lines.append("")

        return "\n".join(lines)

    def _extract_section(self, content: str, markers: List[str],
                         max_chars: int = 500) -> str:
        """Extract the first matching section from markdown content."""
        for marker in markers:
            idx = content.find(marker)
            if idx >= 0:
                # Find next heading or end
                next_idx = content.find("\n## ", idx + len(marker))
                if next_idx < 0:
                    next_idx = min(idx + max_chars, len(content))
                else:
                    next_idx = min(next_idx, idx + max_chars)
                return content[idx:next_idx].strip()
        return ""

    def _read_design_spec(self, feature_dir: Path) -> Optional[str]:
        """Read the design spec file if it exists."""
        specs_dir = feature_dir / "specs"
        if not specs_dir.exists():
            return None
        design_files = sorted(specs_dir.glob("*-design.md"), reverse=True)
        if design_files:
            return design_files[0].read_text(encoding="utf-8")
        return None

    # ── injection ──

    def inject_refresh(self, context: "ExecutionContext") -> str:
        """
        Inject context refresh into the conversation.
        Prints to stdout (LLM sees this in bash output) and saves to file.
        """
        summary = self.generate_refresh(context)

        # stdout → LLM sees this
        print(summary)

        # Save to file for record
        refresh_dir = context.feature_dir / ".sdd" / "refreshes"
        refresh_dir.mkdir(parents=True, exist_ok=True)
        refresh_file = refresh_dir / f"refresh_{self.refresh_count + 1:03d}.md"
        refresh_file.write_text(summary, encoding="utf-8")

        self.mark_refreshed()
        self._save_state(context)

        return summary

    def force_refresh(self, context: "ExecutionContext", reason: str = "") -> str:
        """Force a context refresh regardless of thresholds."""
        if reason:
            print(f"\n  ℹ️  上下文刷新原因: {reason}\n")
        return self.inject_refresh(context)

    # ── persistence ──

    def _save_state(self, context: "ExecutionContext"):
        state_file = context.feature_dir / ".sdd" / "context_monitor.json"
        state_file.write_text(json.dumps(self.get_state(), indent=2,
                                          ensure_ascii=False))

    def get_state(self) -> dict:
        return {
            "edit_count": self.edit_count,
            "task_count": self.task_count,
            "last_refresh_at_edit": self.last_refresh_at_edit,
            "last_refresh_at_task": self.last_refresh_at_task,
            "refresh_count": self.refresh_count,
            "per_file_edits": self.per_file_edits,
            "refresh_history": self.refresh_history,
        }

    @classmethod
    def from_state(cls, state: dict) -> "ContextMonitor":
        monitor = cls()
        monitor.edit_count = state.get("edit_count", 0)
        monitor.task_count = state.get("task_count", 0)
        monitor.last_refresh_at_edit = state.get("last_refresh_at_edit", 0)
        monitor.last_refresh_at_task = state.get("last_refresh_at_task", 0)
        monitor.refresh_count = state.get("refresh_count", 0)
        monitor.per_file_edits = state.get("per_file_edits", {})
        monitor.refresh_history = state.get("refresh_history", [])
        return monitor
