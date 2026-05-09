"""
Context Monitor Tests
Test context monitoring, threshold detection, and refresh mechanisms
"""


from pathlib import Path
from tempfile import TemporaryDirectory


class TestContextMonitorImports:
    """Test ContextMonitor imports correctly"""
    
    def test_context_monitor_imports(self):
        """Test ContextMonitor can be imported"""
        from src.context_monitor import ContextMonitor
        assert ContextMonitor is not None
    
    def test_context_monitor_dependencies(self):
        """Test ContextMonitor dependencies"""
        from src.context_monitor import (
            ContextMonitor,
            ContextThresholds,
        )
        
        assert ContextMonitor is not None
        assert ContextThresholds is not None


class TestContextThresholds:
    """Test context threshold configuration"""
    
    def test_thresholds_defaults(self):
        """Test default threshold values"""
        from src.context_monitor import ContextThresholds
        
        thresholds = ContextThresholds()
        
        assert thresholds.file_edits_soft_limit > 0
        assert thresholds.file_edits_hard_limit > thresholds.file_edits_soft_limit
        assert thresholds.token_soft_limit > 0
        assert thresholds.token_hard_limit > thresholds.token_soft_limit
    
    def test_thresholds_custom_values(self):
        """Test custom threshold values"""
        from src.context_monitor import ContextThresholds
        
        thresholds = ContextThresholds(
            file_edits_soft_limit=50,
            file_edits_hard_limit=100,
            token_soft_limit=100000,
            token_hard_limit=200000,
        )
        
        assert thresholds.file_edits_soft_limit == 50
        assert thresholds.file_edits_hard_limit == 100
        assert thresholds.token_soft_limit == 100000
        assert thresholds.token_hard_limit == 200000


class TestContextMonitorMethods:
    """Test ContextMonitor methods"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        
        from src.context_monitor import ContextMonitor
        self.monitor = ContextMonitor(self.project_root)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir.name, ignore_errors=True)
    
    def test_record_edit(self):
        """Test record_edit method"""
        assert hasattr(self.monitor, 'record_edit')
        
        self.monitor.record_edit("test_file.py")
        
        assert "test_file.py" in self.monitor.per_file_edits
        assert self.monitor.per_file_edits["test_file.py"] == 1
    
    def test_record_task(self):
        """Test record_task method"""
        assert hasattr(self.monitor, 'record_task')
        
        self.monitor.record_task("test_task")
        
        assert self.monitor.task_count == 1
    
    def test_should_refresh(self):
        """Test should_refresh method"""
        assert hasattr(self.monitor, 'should_refresh')
        
        should_refresh, reason = self.monitor.should_refresh()
        
        assert isinstance(should_refresh, bool)
        assert isinstance(reason, str)
    
    def test_check_thresholds(self):
        """Test check_thresholds method"""
        assert hasattr(self.monitor, 'check_thresholds')
        
        # Initially should not exceed thresholds
        exceeds, level = self.monitor.check_thresholds()
        
        assert isinstance(exceeds, bool)
        assert level in ["none", "soft", "hard"]


class TestContextMonitorThresholds:
    """Test ContextMonitor threshold detection"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        
        from src.context_monitor import ContextMonitor, ContextThresholds
        
        # Use low thresholds for testing
        thresholds = ContextThresholds(
            file_edits_soft_limit=2,
            file_edits_hard_limit=4,
            token_soft_limit=1000,
            token_hard_limit=2000,
        )
        
        self.monitor = ContextMonitor(self.project_root, thresholds)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir.name, ignore_errors=True)
    
    def test_soft_threshold_detection(self):
        """Test soft threshold detection"""
        # Edit same file 2 times (soft limit)
        self.monitor.record_edit("test.py")
        self.monitor.record_edit("test.py")
        
        should_refresh, reason = self.monitor.should_refresh()
        
        assert should_refresh == True
        assert "soft" in reason.lower()
    
    def test_hard_threshold_detection(self):
        """Test hard threshold detection"""
        # Edit same file 4 times (hard limit)
        for i in range(4):
            self.monitor.record_edit("test.py")
        
        should_refresh, reason = self.monitor.should_refresh()
        
        assert should_refresh == True
        assert "hard" in reason.lower()
    
    def test_multiple_files_tracking(self):
        """Test tracking edits across multiple files"""
        self.monitor.record_edit("file1.py")
        self.monitor.record_edit("file2.py")
        self.monitor.record_edit("file3.py")
        
        assert len(self.monitor.per_file_edits) == 3
        assert sum(self.monitor.per_file_edits.values()) == 3


class TestContextMonitorIntegration:
    """Test ContextMonitor integration with context"""
    
    def test_inject_refresh(self):
        """Test inject_refresh method"""
        from src.context_monitor import ContextMonitor
        from src.director import ExecutionContext
        
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            feature_dir = project_root / "docs" / "features" / "test"
            feature_dir.mkdir(parents=True, exist_ok=True)
            
            monitor = ContextMonitor(project_root)
            context = ExecutionContext(
                project_root=project_root,
                feature_name="test",
                feature_dir=feature_dir,
                capability=None,
            )
            context.metadata = {}
            
            monitor.inject_refresh(context)
            
            assert "_context_refreshed" in context.metadata


class TestContextMonitorStatistics:
    """Test ContextMonitor statistics"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        
        from src.context_monitor import ContextMonitor
        self.monitor = ContextMonitor(self.project_root)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir.name, ignore_errors=True)
    
    def test_get_statistics(self):
        """Test get_statistics method"""
        if hasattr(self.monitor, 'get_statistics'):
            stats = self.monitor.get_statistics()
            
            assert isinstance(stats, dict)
            assert "total_edits" in stats or "file_count" in stats
    
    def test_reset_statistics(self):
        """Test reset method"""
        self.monitor.record_edit("test.py")
        self.monitor.record_task("task1")
        
        if hasattr(self.monitor, 'reset'):
            self.monitor.reset()
            
            assert self.monitor.total_edits == 0 or len(self.monitor.per_file_edits) == 0
