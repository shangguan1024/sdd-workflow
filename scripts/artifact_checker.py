"""
ArtifactChecker: 检查 4 个审查制品是否完整
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml


@dataclass
class ArtifactDef:
    name: str
    path: str
    required_sections: list[str]


@dataclass
class ArtifactResult:
    name: str
    exists: bool
    sections_found: list[str] = field(default_factory=list)
    missing_sections: list[str] = field(default_factory=list)
    valid: bool = False


@dataclass
class ArtifactCheckResult:
    complete: bool
    artifacts: list[ArtifactResult] = field(default_factory=list)
    missing_count: int = 0


class ArtifactChecker:
    def __init__(self, config_path: Path | None = None):
        self.config_path = (
            config_path
            or Path(__file__).parent.parent / "config" / "artifact_checker.yaml"
        )
        self.config = self._load_config()
        self.required_artifacts = self._load_artifacts()

    def _load_config(self) -> dict:
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return {
            "artifact_checker": {
                "enabled": True,
                "auto_generate": True,
                "required_artifacts": [],
            }
        }

    def _load_artifacts(self) -> list[ArtifactDef]:
        artifacts = []

        config_artifacts = self.config.get("artifact_checker", {}).get(
            "required_artifacts", []
        )

        for cfg in config_artifacts:
            artifacts.append(
                ArtifactDef(
                    name=cfg.get("name", ""),
                    path=cfg.get("path", ""),
                    required_sections=cfg.get("required_sections", []),
                )
            )

        return artifacts

    def check(self, project_root: Path) -> ArtifactCheckResult:
        """检查所有制品"""
        results = []
        missing_count = 0

        for artifact in self.required_artifacts:
            result = self._check_artifact(project_root / artifact.path, artifact)
            results.append(result)
            if not result.valid:
                missing_count += 1

        return ArtifactCheckResult(
            complete=all(r.valid for r in results),
            artifacts=results,
            missing_count=missing_count,
        )

    def _check_artifact(self, path: Path, artifact: ArtifactDef) -> ArtifactResult:
        if not path.exists():
            return ArtifactResult(
                name=artifact.name,
                exists=False,
                sections_found=[],
                missing_sections=artifact.required_sections,
                valid=False,
            )

        content = path.read_text()
        sections_found = [
            section
            for section in artifact.required_sections
            if section.lower() in content.lower()
        ]
        missing = [
            section
            for section in artifact.required_sections
            if section not in sections_found
        ]

        return ArtifactResult(
            name=artifact.name,
            exists=True,
            sections_found=sections_found,
            missing_sections=missing,
            valid=len(missing) == 0,
        )

    def get_missing_artifacts(self, project_root: Path) -> list[ArtifactDef]:
        """返回缺失的制品定义"""
        check_result = self.check(project_root)
        missing = []

        for result in check_result.artifacts:
            if not result.exists:
                for artifact in self.required_artifacts:
                    if artifact.name == result.name:
                        missing.append(artifact)
                        break

        return missing


class ArtifactReportFormatter:
    @staticmethod
    def format(result: ArtifactCheckResult) -> str:
        lines = ["## Phase 5 Gate Check", "", "Review Artifacts:", ""]
        lines.append("| Artifact | Status | Sections |")
        lines.append("|----------|--------|----------|")

        for a in result.artifacts:
            status = "✅" if a.valid else ("⚠️" if a.exists else "❌")
            found = f"{len(a.sections_found)}/{len(a.sections_found) + len(a.missing_sections)}"
            lines.append(f"| {a.name} | {status} | {found} |")

        lines.append("")

        if result.complete:
            lines.append("✅ All review artifacts present")
        else:
            lines.append(f"❌ Missing {result.missing_count} artifact(s)")

        return "\n".join(lines)
