"""
TraceCollector: 收集 session 执行轨迹
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
import json
import uuid


@dataclass
class PhaseTransition:
    from_phase: int
    to_phase: int
    gate_checked: bool
    human_approved: bool
    timestamp: str


@dataclass
class ViolationRecord:
    phase: int
    rule_id: str
    description: str
    timestamp: str


@dataclass
class HumanIntervention:
    phase: int
    action: str
    reason: str
    timestamp: str


@dataclass
class ErrorRecord:
    error_type: str
    message: str
    timestamp: str


@dataclass
class SessionTrace:
    session_id: str
    task: str
    feature: str
    start_time: str
    phases_completed: list = field(default_factory=list)
    violations: list = field(default_factory=list)
    human_interventions: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    end_time: Optional[str] = None
    outcome: Optional[str] = None

    def to_dict(self) -> dict:
        def serialize(obj):
            if hasattr(obj, "__dataclass_fields__"):
                return {k: serialize(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [serialize(item) for item in obj]
            else:
                return obj

        return serialize(self)


class TraceCollector:
    """收集 session 执行轨迹"""

    def __init__(self, storage_dir: Path = None):
        self.storage_dir = storage_dir or Path.cwd() / ".sdd" / "traces"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.in_progress_dir = self.storage_dir / "in_progress"
        self.completed_dir = self.storage_dir / "completed"
        self.in_progress_dir.mkdir(exist_ok=True)
        self.completed_dir.mkdir(exist_ok=True)
        self._current_trace: Optional[SessionTrace] = None

    def start_session(self, task: str, feature: str) -> str:
        """开始新 session"""
        session_id = str(uuid.uuid4())[:8]

        self._current_trace = SessionTrace(
            session_id=session_id,
            task=task,
            feature=feature,
            start_time=datetime.now().isoformat(),
            phases_completed=[],
            violations=[],
            human_interventions=[],
            errors=[],
            end_time=None,
            outcome=None,
        )

        self._save_trace(self._current_trace, "in_progress")
        return session_id

    def record_phase_transition(
        self, from_phase: int, to_phase: int, gate_checked: bool, human_approved: bool
    ):
        """记录 phase 转换"""
        if not self._current_trace:
            return

        self._current_trace.phases_completed.append(
            PhaseTransition(
                from_phase=from_phase,
                to_phase=to_phase,
                gate_checked=gate_checked,
                human_approved=human_approved,
                timestamp=datetime.now().isoformat(),
            )
        )
        self._save_trace(self._current_trace, "in_progress")

    def record_violation(self, phase: int, rule_id: str, description: str):
        """记录 Constitution 违规"""
        if not self._current_trace:
            return

        self._current_trace.violations.append(
            ViolationRecord(
                phase=phase,
                rule_id=rule_id,
                description=description,
                timestamp=datetime.now().isoformat(),
            )
        )
        self._save_trace(self._current_trace, "in_progress")

    def record_human_intervention(self, phase: int, action: str, reason: str):
        """记录人工干预"""
        if not self._current_trace:
            return

        self._current_trace.human_interventions.append(
            HumanIntervention(
                phase=phase,
                action=action,
                reason=reason,
                timestamp=datetime.now().isoformat(),
            )
        )
        self._save_trace(self._current_trace, "in_progress")

    def record_error(self, error_type: str, message: str):
        """记录错误"""
        if not self._current_trace:
            return

        self._current_trace.errors.append(
            ErrorRecord(
                error_type=error_type,
                message=message,
                timestamp=datetime.now().isoformat(),
            )
        )
        self._save_trace(self._current_trace, "in_progress")

    def end_session(self, outcome: str):
        """结束 session"""
        if not self._current_trace:
            return

        self._current_trace.end_time = datetime.now().isoformat()
        self._current_trace.outcome = outcome

        self._save_trace(self._current_trace, "completed")
        self._current_trace = None

    def _save_trace(self, trace: SessionTrace, status: str):
        """保存 trace"""
        if status == "in_progress":
            path = self.in_progress_dir / f"{trace.session_id}.json"
        else:
            path = self.completed_dir / f"{trace.session_id}.json"

        with open(path, "w") as f:
            json.dump(trace.to_dict(), f, indent=2)

    def load_traces(
        self, status: str = "completed", limit: int = 100
    ) -> list[SessionTrace]:
        """加载 traces"""
        dir_path = self.completed_dir if status == "completed" else self.in_progress_dir

        traces = []
        for path in sorted(
            dir_path.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True
        )[:limit]:
            with open(path) as f:
                data = json.load(f)
                traces.append(self._dict_to_trace(data))

        return traces

    def _dict_to_trace(self, data: dict) -> SessionTrace:
        """将字典转换为 SessionTrace"""
        phases = []
        for p in data.get("phases_completed", []):
            phases.append(PhaseTransition(**p))

        violations = [ViolationRecord(**v) for v in data.get("violations", [])]
        interventions = [
            HumanIntervention(**i) for i in data.get("human_interventions", [])
        ]
        errors = [ErrorRecord(**e) for e in data.get("errors", [])]

        return SessionTrace(
            session_id=data["session_id"],
            task=data["task"],
            feature=data["feature"],
            start_time=data["start_time"],
            phases_completed=phases,
            violations=violations,
            human_interventions=interventions,
            errors=errors,
            end_time=data.get("end_time"),
            outcome=data.get("outcome"),
        )

    def get_stats(self, traces: list[SessionTrace] = None) -> dict:
        """获取统计信息"""
        if traces is None:
            traces = self.load_traces()

        if not traces:
            return {"total_sessions": 0}

        stats = {
            "total_sessions": len(traces),
            "success": len([t for t in traces if t.outcome == "success"]),
            "partial": len([t for t in traces if t.outcome == "partial"]),
            "failed": len([t for t in traces if t.outcome == "failed"]),
            "gate_skips": 0,
            "human_overrides": 0,
            "violations_count": 0,
        }

        for trace in traces:
            for pt in trace.phases_completed:
                if not pt.gate_checked:
                    stats["gate_skips"] += 1

            stats["human_overrides"] += len(trace.human_interventions)
            stats["violations_count"] += len(trace.violations)

        return stats
