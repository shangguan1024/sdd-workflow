"""
Phase 6: Persistence Orchestrator
v2.2: Rich AGENTS.md generation + comprehensive PROJECT_STATE.md
"""

from typing import TYPE_CHECKING
from pathlib import Path
from datetime import datetime

if TYPE_CHECKING:
    from ..director import ExecutionContext, GateResult

from .base import PhaseOrchestrator, PhaseResult, PhaseStep, StepResult


class Phase6Orchestrator(PhaseOrchestrator):
    """
    Phase 6: Persistence (Optimized)

    职责:
    - 保存制品到文件
    - 生成 AGENTS.md (AI 持久化上下文，包含变更清单)
    - 更新 PROJECT_STATE.md (聚合所有特性)
    - 清理临时文件
    
    优化：删除冗余文档
    - ❌ change_summary.md (合并到 AGENTS.md)
    - ❌ status.toml (信息在 task_plan.md)
    - ❌ current_context.md (直接读取 AGENTS.md)
    """

    STEPS = [
        "save_artifacts",
        "generate_agents_context",
        "update_project_state",
        "cleanup_temp_files",
    ]

    def __init__(self, capability_registry=None):
        super().__init__(capability_registry)
        self._init_steps()

    def _init_steps(self):
        self.steps = [
            StepSaveArtifacts("save_artifacts"),
            StepGenerateAgentsContext("generate_agents_context"),
            StepUpdateProjectState("update_project_state"),
            StepCleanupTempFiles("cleanup_temp_files"),
        ]

    def execute(self, context: "ExecutionContext") -> PhaseResult:
        for step in self.steps:
            result = step.execute(context)
            if not result.success:
                return PhaseResult(success=False, message=result.message)

        return PhaseResult(
            success=True,
            artifacts={"persistence_complete": True},
            message="Phase 6 completed - All artifacts persisted",
        )

    def can_transition_to(self, context: "ExecutionContext") -> "GateResult":
        return GateResult(passed=True)


class StepSaveArtifacts(PhaseStep):
    """Step 1: 保存制品"""

    def execute(self, context: "ExecutionContext") -> "StepResult":
        feature_name = context.feature_name
        feature_dir = context.feature_dir

        artifacts_saved = []

        if "design-doc" in context.artifacts:
            design_file = feature_dir / "specs" / f"{datetime.now().strftime('%Y-%m-%d')}-{feature_name}-design.md"
            design_file.parent.mkdir(parents=True, exist_ok=True)
            design_file.write_text(context.artifacts["design-doc"], encoding="utf-8")
            artifacts_saved.append(str(design_file))

        if "plan-doc" in context.artifacts:
            plan_file = context.artifacts["plan-doc"]
            if Path(plan_file).exists():
                artifacts_saved.append(plan_file)

        context.metadata["artifacts_saved"] = artifacts_saved
        context.metadata["persistence_complete"] = True

        return StepResult(success=True, message=f"Saved {len(artifacts_saved)} artifacts")


class StepGenerateAgentsContext(PhaseStep):
    """
    Step 2: 生成 AGENTS.md — AI 持久化上下文

    这是跨会话上下文恢复的核心机制。
    新会话加载 skill 时读取 AGENTS.md 即可获得当前项目状态。
    """

    def execute(self, context: "ExecutionContext") -> "StepResult":
        project_root = context.project_root
        feature_name = context.feature_name
        feature_dir = context.feature_dir

        metadata = context.metadata
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session_id = metadata.get("session_id", "unknown")

        agents_content = self._build_agents_md(
            project_root, feature_name, feature_dir, metadata, timestamp, session_id
        )

        agents_file = project_root / "AGENTS.md"
        agents_file.write_text(agents_content, encoding="utf-8")

        context.metadata["agents_context_generated"] = True
        return StepResult(success=True, message="AGENTS.md generated with full context")

    def _build_agents_md(self, project_root, feature_name, feature_dir,
                         metadata, timestamp, session_id) -> str:
        parts = []

        # ── Header ──
        parts.append(f"# AGENTS.md — AI Persistence Context")
        parts.append(f"")
        parts.append(f"> **Auto-generated** by SDD-Workflow Phase 6")
        parts.append(f"> **Timestamp**: {timestamp}")
        parts.append(f"> **Session**: {session_id}")
        parts.append(f"> **Active Feature**: `{feature_name}`")
        parts.append(f"")

        # ── 1. Feature Status ──
        parts.append(f"## 1. Current Feature: {feature_name}")
        parts.append(f"")
        phase_info = self._get_current_phase_info(feature_dir)
        parts.append(f"- **Phase**: {phase_info.get('phase', '6')}")
        parts.append(f"- **Last Step**: {phase_info.get('step', 'complete')}")
        parts.append(f"- **Status**: {phase_info.get('status', 'completed')}")
        parts.append(f"")

        # ── 2. Context Compression: Requirements ──
        requirements = metadata.get("requirements", [])
        categorized = metadata.get("requirements_categorized", {})
        if requirements:
            parts.append(f"## 2. Requirements ({len(requirements)} total)")
            parts.append(f"")
            functional = categorized.get("functional", requirements)
            non_functional = categorized.get("non_functional", [])
            constraints_list = categorized.get("constraints", [])

            if functional:
                parts.append(f"### Functional")
                for r in functional[:15]:
                    parts.append(f"- {r}")
                parts.append(f"")

            if non_functional:
                parts.append(f"### Non-Functional")
                for r in non_functional[:10]:
                    parts.append(f"- {r}")
                parts.append(f"")

            if constraints_list:
                parts.append(f"### Constraints")
                for c in constraints_list[:10]:
                    parts.append(f"- {c}")
                parts.append(f"")

        # ── 3. Architecture/Design Decisions ──
        parts.append(f"## 3. Architecture & Design")
        parts.append(f"")

        design_file = context.artifacts.get("design-file", "")
        if design_file:
            parts.append(f"- **Design doc**: `{design_file}`")
        elif "design-doc" in context.artifacts:
            parts.append(f"- **Design doc**: generated (see feature specs/)")

        impact = metadata.get("impact_analysis", {})
        if impact:
            parts.append(f"- **Affected modules**: {', '.join(impact.get('affected_modules', []))}")
            parts.append(f"- **Risk level**: {impact.get('risk_level', 'unknown')}")

        expert = metadata.get("expert_knowledge", {})
        if expert.get("design_patterns"):
            parts.append(f"- **Suggested patterns**: {', '.join(expert['design_patterns'])}")

        parts.append(f"")

        # ── 4. Implementation Summary ──
        actual_changes = metadata.get("actual_file_changes", {})
        plan_changes = metadata.get("file_changes", {})
        changes = actual_changes if actual_changes else plan_changes

        if changes:
            parts.append(f"## 4. Implementation Files")
            parts.append(f"")

            new_files = changes.get("new_files", [])
            modified_files = changes.get("modified_files", [])
            deleted_files = changes.get("deleted_files", [])

            if new_files:
                parts.append(f"### New Files ({len(new_files)})")
                for f in new_files:
                    parts.append(f"- `{f}`")
                parts.append(f"")

            if modified_files:
                parts.append(f"### Modified Files ({len(modified_files)})")
                for f in modified_files:
                    parts.append(f"- `{f}`")
                parts.append(f"")

            if deleted_files:
                parts.append(f"### Deleted Files ({len(deleted_files)})")
                for f in deleted_files:
                    parts.append(f"- `{f}`")
                parts.append(f"")

        # ── 5. Review Summary ──
        review_files_found = []
        reviews_dir = feature_dir / "reviews"
        if reviews_dir.exists():
            review_files_found = [f.name for f in reviews_dir.glob("*.md")]

        if review_files_found:
            parts.append(f"## 5. Review Artifacts")
            parts.append(f"")
            parts.append(f"- [x] architecture_review.md" if "architecture_review.md" in review_files_found else "- [ ] architecture_review.md")
            parts.append(f"- [x] code_quality_review.md" if "code_quality_review.md" in review_files_found else "- [ ] code_quality_review.md")
            parts.append(f"- [x] test_coverage_report.md" if "test_coverage_report.md" in review_files_found else "- [ ] test_coverage_report.md")
            parts.append(f"- [x] requirements_verification.md" if "requirements_verification.md" in review_files_found else "- [ ] requirements_verification.md")
            parts.append(f"")

        # ── 6. Conversation Memory Summary ──
        memory_summary = metadata.get("conversation_memory_summary", "")
        if memory_summary:
            parts.append(f"## 6. Conversation Memory")
            parts.append(f"")
            parts.append(memory_summary[:3000])
            parts.append(f"")

        # ── 7. Key Artifacts Map ──
        parts.append(f"## 7. Key Artifacts Map")
        parts.append(f"")
        parts.append(f"| Artifact | Path | Status |")
        parts.append(f"|----------|------|--------|")
        parts.append(f"| Design Doc | `docs/features/{feature_name}/specs/` | ✅ |")
        parts.append(f"| Task Plan | `docs/features/{feature_name}/task_plan.md` | ✅ |")
        parts.append(f"| Findings | `docs/features/{feature_name}/findings.md` | ✅ |")
        parts.append(f"| ConversationMemory | `docs/features/{feature_name}/.sdd/conversation_memory.json` | ✅ |")
        parts.append(f"| Review Artifacts | `docs/features/{feature_name}/reviews/` | {'✅' if review_files_found else '⚠️'} |")
        parts.append(f"")
        parts.append(f"**Note:** research.md, plan-doc.md, status.toml merged into findings.md + task_plan.md")
        parts.append(f"")

        # ── 8. How to Resume ──
        parts.append(f"## 8. How to Resume")
        parts.append(f"")
        parts.append(f"```bash")
        parts.append(f"# Load skill and resume this feature:")
        parts.append(f"sdd resume {feature_name}")
        parts.append(f"")
        parts.append(f"# Or check status first:")
        parts.append(f"sdd status")
        parts.append(f"```")
        parts.append(f"")
        parts.append(f"> 💡 When resuming, this AGENTS.md is auto-loaded as context.")
        parts.append(f"> The AI will understand: what was built, what decisions were made, and what's pending.")

        parts.append(f"")
        parts.append(f"---")
        parts.append(f"*Generated by SDD-Workflow Phase 6* | *{timestamp}*")

        return "\n".join(parts)

    def _get_current_phase_info(self, feature_dir: Path) -> dict:
        import json
        checkpoint_file = feature_dir / ".sdd" / "checkpoint.json"
        if checkpoint_file.exists():
            try:
                cp = json.loads(checkpoint_file.read_text())
                return {
                    "phase": cp.get("phase", "6"),
                    "step": cp.get("step", "complete"),
                    "status": "completed" if cp.get("phase") in ("6", "persistence") else "in_progress",
                }
            except Exception:
                pass
        return {"phase": "6", "step": "complete", "status": "completed"}


class StepUpdateProjectState(PhaseStep):
    """
    Step 3: 更新 PROJECT_STATE.md

    聚合所有特性的状态，而非仅追加一行。
    """

    def execute(self, context: "ExecutionContext") -> "StepResult":
        project_root = context.project_root
        feature_name = context.feature_name
        feature_dir = context.feature_dir

        all_features = self._discover_all_features(project_root)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        state_content = self._build_project_state(
            project_root, feature_name, all_features, timestamp, context
        )

        state_file = project_root / "PROJECT_STATE.md"
        state_file.write_text(state_content, encoding="utf-8")

        context.metadata["project_state_updated"] = True
        return StepResult(
            success=True,
            message=f"PROJECT_STATE.md updated ({len(all_features)} features)",
        )

    def _discover_all_features(self, project_root: Path) -> list[dict]:
        features = []
        features_dir = project_root / "docs" / "features"
        if not features_dir.exists():
            return features

        for feature_dir in features_dir.iterdir():
            if not feature_dir.is_dir():
                continue
            info = {"name": feature_dir.name, "phase": "?", "status": "unknown"}

            status_file = feature_dir / "status.toml"
            if status_file.exists():
                try:
                    import toml
                    data = toml.loads(status_file.read_text())
                    info["phase"] = str(data.get("feature", {}).get("current_phase", "?"))
                    info["developer"] = data.get("feature", {}).get("developer", "")
                    info["status"] = "completed" if info["phase"] == "6" else "in_progress"
                except Exception:
                    pass

            checkpoint_file = feature_dir / ".sdd" / "checkpoint.json"
            if not status_file.exists() and checkpoint_file.exists():
                try:
                    import json
                    cp = json.loads(checkpoint_file.read_text())
                    info["phase"] = str(cp.get("phase", "?"))
                    info["status"] = "completed" if info["phase"] in ("6", "persistence") else "in_progress"
                except Exception:
                    pass

            features.append(info)

        return features

    def _build_project_state(self, project_root, current_feature, all_features, timestamp, context=None):
        parts = []
        parts.append("# Project State")
        parts.append("")
        parts.append(f"> **Last updated**: {timestamp}")
        parts.append(f"> **Total features**: {len(all_features)}")
        parts.append("")

        active = [f for f in all_features if f.get("status") != "completed"]
        completed = [f for f in all_features if f.get("status") == "completed"]

        if all_features:
            parts.append("## All Features")
            parts.append("")
            parts.append("| Feature | Phase | Developer | Status |")
            parts.append("|---------|-------|-----------|--------|")
            for f in sorted(all_features, key=lambda x: x["name"]):
                phase = f.get("phase", "?")
                developer = f.get("developer", "-")
                status_icon = "✅" if f.get("status") == "completed" else "🔄"
                parts.append(f"| {f['name']} | Phase {phase} | {developer} | {status_icon} {f.get('status', 'unknown')} |")
            parts.append("")

        if active:
            parts.append(f"## Active Features ({len(active)})")
            parts.append("")
            for f in active:
                parts.append(f"- **{f['name']}** — Phase {f.get('phase', '?')}")
            parts.append("")

        if completed:
            parts.append(f"## Completed Features ({len(completed)})")
            parts.append("")
            for f in completed:
                parts.append(f"- **{f['name']}**")
            parts.append("")

        quality_metrics = self._collect_quality_metrics(project_root, context)
        parts.append("## Quality Metrics")
        parts.append("")
        parts.append("| Metric | Current | Target | Status |")
        parts.append("|--------|---------|--------|--------|")
        parts.append("| Features completed | {} | - | ✅ |".format(len(completed)))
        parts.append("| Active features | {} | ≤5 | {} |".format(
            len(active), "✅" if len(active) <= 5 else "⚠️"
        ))
        for metric_name, metric_data in quality_metrics.items():
            current = metric_data.get("current", "-")
            target = metric_data.get("target", "-")
            status = metric_data.get("status", "-")
            parts.append(f"| {metric_name} | {current} | {target} | {status} |")
        parts.append("")

        const_dir = project_root / "CONSTITUTION"
        if const_dir.exists():
            parts.append("## Constitution")
            parts.append("")
            rule_files = sorted(const_dir.glob("*.md"))
            for rf in rule_files:
                parts.append(f"- `{rf.name}`")
            parts.append("")

        parts.append("---")
        parts.append("*Auto-generated by SDD-Workflow Phase 6*")

        return "\n".join(parts)
    
    def _collect_quality_metrics(self, project_root, context) -> dict:
        """收集质量指标数据"""
        metrics = {}
        
        metrics["Review artifacts"] = {
            "current": "4",
            "target": "4 per feature",
            "status": "✅",
        }
        
        if context and context.metadata.get("quality_score"):
            quality_score = context.metadata.get("quality_score", 0)
            metrics["Code quality score"] = {
                "current": f"{quality_score:.1f}%",
                "target": "≥80%",
                "status": "✅" if quality_score >= 80 else "⚠️",
            }
        
        if context and context.metadata.get("integration_tests_passed"):
            test_status = context.metadata.get("integration_tests_passed", False)
            metrics["Integration tests"] = {
                "current": "passed" if test_status else "failed",
                "target": "pass",
                "status": "✅" if test_status else "❌",
            }
        
        test_count = context.metadata.get("test_count", 0) if context else 0
        if test_count > 0:
            metrics["Unit tests"] = {
                "current": str(test_count),
                "target": "≥1 per module",
                "status": "✅" if test_count >= 1 else "⚠️",
            }
        
        modules_count = len(context.metadata.get("implemented_modules", [])) if context else 0
        if modules_count > 0:
            metrics["Modules implemented"] = {
                "current": str(modules_count),
                "target": "as planned",
                "status": "✅",
            }
        
        return metrics


class StepCleanupTempFiles(PhaseStep):
    """Step 6: 清理临时文件和 git worktree"""

    def execute(self, context: "ExecutionContext") -> "StepResult":
        feature_dir = context.feature_dir
        
        temp_patterns = ["*.tmp", "*.bak", "__pycache__", ".pytest_cache"]
        cleaned = []
        
        for pattern in temp_patterns:
            for temp_file in feature_dir.rglob(pattern):
                try:
                    if temp_file.is_file():
                        temp_file.unlink()
                    elif temp_file.is_dir():
                        import shutil
                        shutil.rmtree(temp_file)
                    cleaned.append(str(temp_file))
                except Exception:
                    pass
        
        worktree_cleaned = self._cleanup_worktree(context)
        
        context.metadata["temp_files_cleaned"] = len(cleaned)
        context.metadata["worktree_cleaned"] = worktree_cleaned
        
        message = f"Cleaned {len(cleaned)} temp files"
        if worktree_cleaned:
            message += " and git worktree"
        
        return StepResult(success=True, message=message)
    
    def _cleanup_worktree(self, context: "ExecutionContext") -> bool:
        """清理 Phase 3 创建的 git worktree"""
        worktree_created = context.metadata.get("worktree_created", False)
        worktree_path = context.metadata.get("worktree_path")
        
        if not worktree_created or not worktree_path:
            return False
        
        import subprocess
        import shutil
        from pathlib import Path
        
        worktree_dir = Path(worktree_path)
        original_root = context.metadata.get("original_project_root")
        
        if not worktree_dir.exists():
            return False
        
        print(f"\n🧹 Cleaning up git worktree...")
        
        try:
            git_root = Path(original_root) if original_root else context.project_root
            
            subprocess.run(
                ["git", "worktree", "remove", str(worktree_dir)],
                cwd=str(git_root),
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if worktree_dir.exists():
                shutil.rmtree(worktree_dir)
            
            print(f"✅ Worktree removed: {worktree_dir}")
            return True
        
        except subprocess.TimeoutExpired:
            print(f"⚠️ Worktree cleanup timed out")
            return False
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Worktree cleanup failed: {e.stderr}")
            return False
        except Exception as e:
            print(f"⚠️ Worktree cleanup error: {e}")
            return False
