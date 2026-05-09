"""
Phase Integration Tests
Test Phase 1-6 orchestration and checkpoint mechanisms
"""

from pathlib import Path
from tempfile import TemporaryDirectory


class TestPhaseOrchestrators:
    """Test all Phase Orchestrators"""
    
    def test_phase1_imports(self):
        """Test Phase 1 imports correctly"""
        from src.phases.phase1 import Phase1Orchestrator
        assert Phase1Orchestrator is not None
        assert hasattr(Phase1Orchestrator, 'execute')
        assert hasattr(Phase1Orchestrator, '_save_phase_checkpoint')
    
    def test_phase2_imports(self):
        """Test Phase 2 imports correctly"""
        from src.phases.phase2 import Phase2Orchestrator
        assert Phase2Orchestrator is not None
        assert hasattr(Phase2Orchestrator, 'execute')
        assert hasattr(Phase2Orchestrator, '_save_phase_checkpoint')
    
    def test_phase3_imports(self):
        """Test Phase 3 imports correctly"""
        from src.phases.phase3 import Phase3Orchestrator
        assert Phase3Orchestrator is not None
        assert hasattr(Phase3Orchestrator, 'execute')
        assert hasattr(Phase3Orchestrator, '_save_phase_checkpoint')
    
    def test_phase4_imports(self):
        """Test Phase 4 imports correctly"""
        from src.phases.phase4 import Phase4Orchestrator
        assert Phase4Orchestrator is not None
        assert hasattr(Phase4Orchestrator, 'execute')
        assert hasattr(Phase4Orchestrator, '_save_phase_checkpoint')
    
    def test_phase5_imports(self):
        """Test Phase 5 imports correctly"""
        from src.phases.phase5 import Phase5Orchestrator
        assert Phase5Orchestrator is not None
        assert hasattr(Phase5Orchestrator, 'execute')
        assert hasattr(Phase5Orchestrator, '_save_phase_checkpoint')
    
    def test_phase6_imports(self):
        """Test Phase 6 imports correctly"""
        from src.phases.phase6 import Phase6Orchestrator
        assert Phase6Orchestrator is not None
        assert hasattr(Phase6Orchestrator, 'execute')
        assert hasattr(Phase6Orchestrator, '_save_phase_checkpoint')
    
    def test_phase_steps_count(self):
        """Test each Phase has expected number of Steps"""
        from src.phases.phase1 import Phase1Orchestrator
        from src.phases.phase2 import Phase2Orchestrator
        from src.phases.phase3 import Phase3Orchestrator
        from src.phases.phase4 import Phase4Orchestrator
        from src.phases.phase5 import Phase5Orchestrator
        from src.phases.phase6 import Phase6Orchestrator
        
        p1 = Phase1Orchestrator()
        p2 = Phase2Orchestrator()
        p3 = Phase3Orchestrator()
        p4 = Phase4Orchestrator()
        p5 = Phase5Orchestrator()
        p6 = Phase6Orchestrator()
        
        assert len(p1.steps) == 9  # Phase 1 has 9 Steps
        assert len(p2.steps) == 6  # Phase 2 has 6 Steps (including constitution_check)
        assert len(p3.steps) == 6  # Phase 3 has 6 Steps (including constitution_check)
        assert len(p4.steps) == 6  # Phase 4 has 6 Steps
        assert len(p5.steps) == 2  # Phase 5 has 2 Steps
        assert len(p6.steps) == 4  # Phase 6 has 4 Steps


class TestCheckpointMechanism:
    """Test checkpoint saving mechanism"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        self.feature_dir = self.project_root / "docs" / "features" / "test-feature"
        self.feature_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir.name, ignore_errors=True)
    
    def test_base_checkpoint_method(self):
        """Test _save_phase_checkpoint method exists"""
        from src.phases.base import PhaseOrchestrator
        
        assert hasattr(PhaseOrchestrator, '_save_phase_checkpoint')
        assert hasattr(PhaseOrchestrator, '_save_checkpoint')
    
    def test_checkpoint_directory_creation(self):
        """Test checkpoint directory is created"""
        from src.phases.base import PhaseOrchestrator
        from src.director import ExecutionContext
        
        context = ExecutionContext(
            project_root=self.project_root,
            feature_name="test-feature",
            feature_dir=self.feature_dir,
            capability=None,
        )
        context.metadata = {"test": "data"}
        context.artifacts = {"artifact1": "value1"}
        
        orchestrator = Phase1Orchestrator()
        orchestrator._save_phase_checkpoint(context, "test_phase")
        
        checkpoint_dir = self.feature_dir / ".sdd"
        assert checkpoint_dir.exists()
        assert (checkpoint_dir / "test_phase_checkpoint.json").exists()
        assert (checkpoint_dir / "checkpoint.json").exists()
    
    def test_checkpoint_content(self):
        """Test checkpoint contains expected data"""
        import json
        from src.phases.base import PhaseOrchestrator
        from src.director import ExecutionContext
        
        context = ExecutionContext(
            project_root=self.project_root,
            feature_name="test-feature",
            feature_dir=self.feature_dir,
            capability=None,
        )
        context.metadata = {"test_key": "test_value"}
        context.artifacts = {"artifact_key": "artifact_value"}
        
        orchestrator = Phase1Orchestrator()
        orchestrator._save_phase_checkpoint(context, "phase2")
        
        checkpoint_file = self.feature_dir / ".sdd" / "phase2_checkpoint.json"
        checkpoint_data = json.loads(checkpoint_file.read_text())
        
        assert checkpoint_data["version"] == "2.2"
        assert checkpoint_data["phase"] == "phase2"
        assert checkpoint_data["feature_name"] == "test-feature"
        assert "timestamp" in checkpoint_data
        assert checkpoint_data["metadata"]["test_key"] == "test_value"
        assert checkpoint_data["artifacts"]["artifact_key"] == "artifact_value"


class TestPhaseSteps:
    """Test Phase Step execution"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        self.feature_dir = self.project_root / "docs" / "features" / "test-feature"
        self.feature_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir.name, ignore_errors=True)
    
    def test_phase_step_inheritance(self):
        """Test all Steps inherit from PhaseStep"""
        from src.phases.base import PhaseStep
        
        from src.phases.phase1 import (
            StepExploreContext,
            StepAnalyzeExistingCode,
            StepGatherRequirements,
        )
        
        steps = [StepExploreContext, StepAnalyzeExistingCode, StepGatherRequirements]
        
        for step_class in steps:
            assert issubclass(step_class, PhaseStep)
    
    def test_step_result_structure(self):
        """Test StepResult structure"""
        from src.phases.base import StepResult
        
        result = StepResult(success=True, message="Test", details={"key": "value"})
        
        assert result.success == True
        assert result.message == "Test"
        assert result.details["key"] == "value"
    
    def test_phase_result_structure(self):
        """Test PhaseResult structure"""
        from src.phases.base import PhaseResult
        
        result = PhaseResult(
            success=True,
            artifacts={"artifact": "value"},
            message="Phase complete"
        )
        
        assert result.success == True
        assert result.artifacts["artifact"] == "value"
        assert result.message == "Phase complete"