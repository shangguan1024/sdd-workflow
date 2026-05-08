# Changelog

All notable changes to SDD-Workflow will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-05-08

### Added
- **Document Structure Optimization**: Reduced from 17 to 7 required documents (59% reduction)
  - `findings.md` now serves as unified decision record for all phases
  - `architecture_review.md` includes requirements verification (merged)
  - `code_quality_review.md` includes test coverage (merged)
  - Deleted: research.md, think_before_coding.md, plan-doc.md, progress.md, status.toml, test_coverage_report.md, requirements_verification.md, change_summary.md
- **Project Configuration Files**:
  - `pyproject.toml` - Modern Python project configuration
  - `ruff.toml` - Ruff lint and format configuration
  - `mypy.ini` - MyPy type checking configuration
  - `.pre-commit-config.yaml` - Pre-commit hooks
  - `.gitignore` - Updated with standard Python patterns
- **Documentation**:
  - `README.md` - Quick start guide and full documentation
  - `CHANGELOG.md` - Version history
  - `docs/engineering_analysis_report.md` - Complete engineering analysis
  - `docs/p0_fix_summary.md` - P0 issues fix summary
  - `docs/document_merge_plan_complete.md` - Document merge plan

### Fixed
- **ISSUE-001**: PhaseCompressionMiddleware now uses findings.md instead of deleted files
- **ISSUE-002**: Required review artifacts reduced to 2 (from 4)
- **ISSUE-003**: Context Monitor uses findings.md as unified data source
- **ISSUE-004**: Director no longer references status.toml or progress.md
- **ISSUE-005**: Phase 6 cleaned up redundant code
- **ISSUE-006**: Test workflow updated for new document structure

### Changed
- Phase 0 outputs merged into `findings.md` Phase 0 section
- Phase 2 outputs merged into `findings.md` Phase 2 section + `task_plan.md`
- Phase 5 outputs merged into 2 review documents (instead of 4)
- Phase 6 outputs simplified to AGENTS.md + conversation_memory.json
- `src/constants.py` - Added REQUIRED_ARTIFACTS_PER_FEATURE
- `middleware/__init__.py` - Updated PHASE_SUMMARY_MAP
- `config/artifact_checker.yaml` - Updated for optimized document structure

### Removed
- **Deleted Documents** (10 total):
  - research.md (merged into findings.md Phase 0)
  - think_before_coding.md (merged into findings.md Phase 0)
  - plan-doc.md (merged into findings.md + task_plan.md Phase 2)
  - progress.md (merged into findings.md)
  - status.toml (information in task_plan.md)
  - test_coverage_report.md (merged into code_quality_review.md)
  - requirements_verification.md (merged into architecture_review.md)
  - change_summary.md (merged into AGENTS.md)
  - checkpoint.json (internal file, not user-facing)
  - current_context.md (use AGENTS.md directly)

## [2.0.0] - 2026-05-07

### Added
- **Checkpoint Mechanism**: Multi-layer checkpoint persistence
  - Real-time sync (30s interval)
  - Phase-level checkpoints
  - Crash recovery support
- **Conversation Memory**: Cross-session decision memory persistence
- **Quality Harness**: Automated quality assessment pipeline
  - Collectors: code metrics, test coverage, complexity
  - Gate Engine: configurable quality gates
  - Reporter: Markdown format reports
- **Error Recovery**: Enhanced error recovery mechanism
  - Error classification and diagnosis
  - Automatic recovery strategies
  - Retry mechanism
- **Middleware Hooks**: 
  - PhaseGateMiddleware - Constitution compliance check
  - LoopDetectionMiddleware - Doom loop detection
  - ArtifactCompleteMiddleware - Artifact completeness check
  - PhaseCompressionMiddleware - Phase boundary compression
- **Nexus Map Integration**: Codebase architecture auto-analysis
- **Progressive Disclosure**: Context progressive loading
- **Privacy Filter**: Sensitive data auto-filtering
- **Context Monitor**: Context refresh and injection

### Changed
- Director refactored to support middleware hooks
- Phase orchestrators updated with context refresh checks
- Test coverage improved (8 test files)

## [1.0.0] - 2026-04-01

### Added
- **6-Phase Workflow**: 
  - Phase 0: Research & Understanding
  - Phase 1: Requirements Analysis & Design
  - Phase 2: Implementation Planning
  - Phase 3: Module Development
  - Phase 4: Integration & Testing
  - Phase 5: Code Quality Review
  - Phase 6: Memory Persistence
- **Phase Gate System**: Forced execution with developer confirmation
- **Constitution Enforcer**: Design/plan/code compliance check
- **Artifact Checker**: Review artifacts completeness check
- **CLI Commands**: init, start, resume, status, complete
- **17 Document Structure**: Initial document structure (now deprecated)

### Security
- Privacy filter for sensitive data

---

## Version Comparison

| Version | Documents | Review Artifacts | Features | Fixes |
|---------|-----------|------------------|----------|-------|
| 2.1.0 | 7 | 2 | +5 config files | 6 P0 fixes |
| 2.0.0 | 17 | 4 | +10 major features | - |
| 1.0.0 | 17 | 4 | 6-phase workflow | - |

---

[2.1.0]: https://github.com/shangguan1024/sdd-workflow/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/shangguan1024/sdd-workflow/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/shangguan1024/sdd-workflow/releases/tag/v1.0.0