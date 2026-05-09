"""
Phase Compression Middleware
Phase 边界压缩中间件
"""

from pathlib import Path
from typing import Any

from .base import Middleware, MiddlewareResult


class PhaseCompressionMiddleware(Middleware):
    """
    Phase 边界压缩中间件。

    在 Phase 转换时检查当前 Phase 的结构化摘要是否已写入对应文件。
    如果没有，阻止进入下一 Phase，要求 AI 先生成摘要。

    摘要映射（优化后的文档结构）:
        Understanding → 1: findings.md 包含 "## Phase 0: Research"
        1 → 2: findings.md 包含 "## Phase 1: Design Summary"
        2 → 3: findings.md 包含 "## Phase 2: Plan Summary"
        3 → 4: findings.md 包含 "## Phase 3: Implementation Summary"
        4 → 5: findings.md 包含 "## Phase 4: Test Summary"
        5 → 6: findings.md 包含 "## Phase 5: Review Summary"
    """

    PHASE_SUMMARY_MAP = {
        0: {"file": "findings.md", "marker": "## Phase 0: Research"},
        1: {"file": "findings.md", "marker": "## Phase 1: Design Summary"},
        2: {"file": "findings.md", "marker": "## Phase 2: Plan Summary"},
        3: {"file": "findings.md", "marker": "## Phase 3: Implementation Summary"},
        4: {"file": "findings.md", "marker": "## Phase 4: Test Summary"},
        5: {"file": "findings.md", "marker": "## Phase 5: Review Summary"},
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
                    f"⚠️ Phase {from_phase} 边界压缩未完成。\n"
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
            missing_elements = [w.replace("可能缺少: ", "") for w in quality["warnings"]]
            return MiddlewareResult(
                allowed=True,
                message=(
                    f"ℹ️ Phase {from_phase} 摘要已存在，但缺少关键内容:\n"
                    + "\n".join(f"  - 缺少: {w}" for w in quality["warnings"])
                ),
                suggestion=(
                    f"建议补充以下内容后再继续:\n"
                    + "\n".join(f"  - {e}" for e in missing_elements)
                ),
                requires_confirmation=True,
                confirmation_options=["补充内容", "继续（不补充）"],
                add_to_context=True,
            )

        return MiddlewareResult(
            allowed=True,
            message=f"✅ Phase {from_phase} 边界压缩已完成 ({check['expected_file']})",
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
        alt_markers = {
            "## Phase 0: Research": ["## Phase 0", "## Research", "## 研究"],
            "## Phase 1: Design Summary": ["## Phase 1", "## Design", "## 设计"],
            "## Phase 2: Plan Summary": ["## Phase 2", "## Plan", "## 计划"],
            "## Phase 3: Implementation Summary": ["## Phase 3", "## Implementation", "## 实现"],
            "## Phase 4: Test Summary": ["## Phase 4", "## Test", "## 测试"],
            "## Phase 5: Review Summary": ["## Phase 5", "## Review", "## 审查"],
        }
        alt_marker_list = alt_markers.get(expected_marker, [expected_marker])

        if expected_marker.lower() in content.lower() or any(alt.lower() in content.lower() for alt in alt_marker_list):
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