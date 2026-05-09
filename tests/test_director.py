"""
Director Tests
Test Director state machine, workflow orchestration, and error recovery
"""


from pathlib import Path
from tempfile import TemporaryDirectory


class TestDirectorImports:
    """Test Director imports correctly"""
    
    def test_director_imports(self):
        """Test Director can be imported"""
        from src.director import Director
        assert Director is not None
    
    def test_director_dependencies(self):
        """Test Director dependencies are imported"""
        from src.director import (
            Director,
            Result,
            ExecutionContext,
            GateController,
            Phase,
        )
        
        assert Director is not None
        assert Result is not None
        assert ExecutionContext is not None
        assert GateController is not None
        assert Phase is not None
    
    def test_director_modules_integration(self):
        """Test Director integrates new modules"""
        from src.director import Director
        
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            director = Director(project_root)
            
            # Check new modules are initialized
            assert hasattr(director, '_memory_manager')
            assert hasattr(director, '_context_injector')
            assert hasattr(director, '_project_initializer')


class TestDirectorCommands:
    """Test Director command handling"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir.name, ignore_errors=True)
    
    def test_init_command(self):
        """Test Director init command"""
        from src.director import Director
        from src.cli import InitCommand
        
        director = Director(self.project_root)
        command = InitCommand(path=self.project_root, template="standard")
        
        result = director.initialize(command)
        
        assert result is not None
        assert hasattr(result, 'success')
        assert hasattr(result, 'message')
    
    def test_complete_command_with_feature(self):
        """Test CompleteCommand accepts feature parameter"""
        from src.cli import CompleteCommand
        
        command = CompleteCommand(feature="test-feature")
        
        assert command.args["feature"] == "test-feature"
    
    def test_complete_command_without_feature(self):
        """Test CompleteCommand works without feature"""
        from src.cli import CompleteCommand
        
        command = CompleteCommand()
        
        assert command.args.get("feature") is None


class TestDirectorStateMachine:
    """Test Director state machine"""
    
    def test_phase_enum(self):
        """Test Phase enum values"""
        from src.director import Phase
        
        assert hasattr(Phase, 'REQUIREMENTS')
        assert hasattr(Phase, 'PLANNING')
        assert hasattr(Phase, 'DEVELOPMENT')
        assert hasattr(Phase, 'INTEGRATION')
        assert hasattr(Phase, 'REVIEW')
        assert hasattr(Phase, 'PERSISTENCE')
    
    def test_gate_controller(self):
        """Test GateController initialization"""
        from src.director import GateController
        
        controller = GateController()
        
        assert hasattr(controller, 'check_gate')
        assert hasattr(controller, 'record_gate')
    
    def test_execution_context(self):
        """Test ExecutionContext structure"""
        from src.director import ExecutionContext
        
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            feature_dir = project_root / "docs" / "features" / "test"
            feature_dir.mkdir(parents=True, exist_ok=True)
            
            context = ExecutionContext(
                project_root=project_root,
                feature_name="test",
                feature_dir=feature_dir,
                capability=None,
            )
            
            assert context.project_root == project_root
            assert context.feature_name == "test"
            assert hasattr(context, 'metadata')
            assert hasattr(context, 'artifacts')


class TestDirectorErrorRecovery:
    """Test Director error recovery integration"""
    
    def test_error_recovery_manager_initialization(self):
        """Test ErrorRecoveryManager is initialized"""
        from src.director import Director
        
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            director = Director(project_root)
            
            assert hasattr(director, '_error_recovery_manager')
    
    def test_error_severity_levels(self):
        """Test ErrorSeverity enum exists"""
        from src.error_recovery import ErrorSeverity
        
        assert hasattr(ErrorSeverity, 'ERROR')
        assert hasattr(ErrorSeverity, 'WARNING')
        assert hasattr(ErrorSeverity, 'CRITICAL')


class TestDirectorMemoryIntegration:
    """Test Director memory management integration"""
    
    def test_memory_manager_initialization(self):
        """Test MemoryManager is initialized"""
        from src.director import Director
        
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            director = Director(project_root)
            
            assert hasattr(director, '_memory_manager')
            assert director._memory_manager is not None
    
    def test_memory_manager_methods(self):
        """Test MemoryManager has expected methods"""
        from src.memory_manager import MemoryManager
        
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            manager = MemoryManager(project_root)
            
            assert hasattr(manager, 'load_or_create_memory')
            assert hasattr(manager, 'save_memory_silent')
            assert hasattr(manager, 'get_memory_timeline')
            assert hasattr(manager, 'get_memory_full_details')


class TestDirectorContextInjection:
    """Test Director context injection integration"""
    
    def test_context_injector_initialization(self):
        """Test ContextInjector is initialized"""
        from src.director import Director
        
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            director = Director(project_root)
            
            assert hasattr(director, '_context_injector')
    
    def test_context_injector_methods(self):
        """Test ContextInjector has expected methods"""
        from src.context_injector import ContextInjector
        
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Mock dependencies
            from src.memory.privacy_filter import PrivacyFilter
            privacy_filter = PrivacyFilter(project_root)
            
            injector = ContextInjector(project_root, privacy_filter)
            
            assert hasattr(injector, 'inject_memory_context')
            assert hasattr(injector, '_inject_core_principles')


class TestDirectorProjectInitialization:
    """Test Director project initialization integration"""
    
    def test_project_initializer_methods(self):
        """Test ProjectInitializer has expected methods"""
        from src.project_initializer import ProjectInitializer
        
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            initializer = ProjectInitializer(project_root)
            
            assert hasattr(initializer, 'create_directory_structure')
            assert hasattr(initializer, 'initialize_constitution')
            assert hasattr(initializer, 'initialize_feature_artifacts')
