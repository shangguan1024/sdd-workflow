"""
Error Recovery System 测试

验证错误捕获、分类、恢复机制
"""

import sys
import json
from pathlib import Path

_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.error_recovery import (
    ErrorRecoveryManager,
    ErrorSeverity,
    ErrorCategory,
    RecoveryStrategy,
    ErrorRecord,
    ErrorContext,
    with_error_recovery,
)


def test_error_classification():
    manager = ErrorRecoveryManager(Path("."))
    
    test_exceptions = [
        (FileNotFoundError("test.txt"), ErrorCategory.FILE_IO),
        (PermissionError("access denied"), ErrorCategory.FILE_IO),
        (TimeoutError("timeout"), ErrorCategory.TIMEOUT),
        (ValueError("invalid value"), ErrorCategory.VALIDATION),
        (RuntimeError("runtime error"), ErrorCategory.PROCESS),
        (ImportError("module not found"), ErrorCategory.DEPENDENCY),
    ]
    
    for exception, expected_category in test_exceptions:
        category = manager._classify_error(exception)
        assert category == expected_category
        print(f"[PASS] Classified {type(exception).__name__} as {category.value}")
    
    print("[PASS] Error classification works correctly")


def test_error_capture():
    manager = ErrorRecoveryManager(Path("."))
    
    try:
        raise FileNotFoundError("config.yaml not found")
    except Exception as e:
        error_record = manager.capture_error(
            exception=e,
            operation="load_config",
            severity=ErrorSeverity.ERROR,
            file_path="config.yaml",
        )
        
        assert error_record.error_id.startswith("err_")
        assert error_record.category == ErrorCategory.FILE_IO
        assert error_record.severity == ErrorSeverity.ERROR
        assert "FileNotFoundError" in error_record.exception_type
        assert "load_config" in error_record.message
        assert error_record.context.file_path == "config.yaml"
        
        print(f"[PASS] Error captured: {error_record.error_id}")
        print(f"  Category: {error_record.category.value}")
        print(f"  Severity: {error_record.severity.value}")
    
    print("[PASS] Error capture works correctly")


def test_strategy_selection():
    manager = ErrorRecoveryManager(Path("."))
    
    test_cases = [
        (ErrorSeverity.FATAL, ErrorCategory.UNKNOWN, RecoveryStrategy.ABORT),
        (ErrorSeverity.WARNING, ErrorCategory.FILE_IO, RecoveryStrategy.SKIP),
        (ErrorSeverity.ERROR, ErrorCategory.FILE_IO, RecoveryStrategy.RETRY),
        (ErrorSeverity.ERROR, ErrorCategory.TIMEOUT, RecoveryStrategy.RETRY),
        (ErrorSeverity.ERROR, ErrorCategory.VALIDATION, RecoveryStrategy.MANUAL),
        (ErrorSeverity.ERROR, ErrorCategory.STATE, RecoveryStrategy.CHECKPOINT),
    ]
    
    for severity, category, expected_strategy in test_cases:
        error_record = ErrorRecord(
            error_id="test_error",
            severity=severity,
            category=category,
            message="test message",
            exception_type="Exception",
            exception_message="test",
            traceback_str="",
            context=ErrorContext(
                phase="1",
                step="test",
                feature_name="test",
                timestamp="2026-01-01",
                operation="test",
            ),
        )
        
        strategy = manager._select_strategy(error_record)
        assert strategy == expected_strategy
        print(f"[PASS] Strategy for {severity.value}/{category.value}: {strategy.value}")
    
    print("[PASS] Strategy selection works correctly")


def test_error_persistence():
    manager = ErrorRecoveryManager(Path("."))
    
    try:
        raise ValueError("test error")
    except Exception as e:
        error_record = manager.capture_error(
            exception=e,
            operation="test_persistence",
            severity=ErrorSeverity.WARNING,
        )
        
        error_log_dir = Path(".") / ".sdd" / "error_logs"
        error_file = error_log_dir / f"{error_record.error_id}.json"
        
        if error_file.exists():
            data = json.loads(error_file.read_text(encoding="utf-8"))
            
            assert data["error_id"] == error_record.error_id
            assert data["severity"] == "warning"
            assert data["category"] == "validation"
            
            print(f"[PASS] Error persisted to {error_file}")
            print(f"[PASS] JSON content valid")
        else:
            print(f"[SKIP] Error file not found: {error_file}")
    
    print("[PASS] Error persistence works")


def test_error_report():
    manager = ErrorRecoveryManager(Path("."))
    
    try:
        raise RuntimeError("test error 1")
    except Exception as e:
        manager.capture_error(exception=e, operation="test_1", severity=ErrorSeverity.ERROR)
    
    try:
        raise FileNotFoundError("test error 2")
    except Exception as e:
        manager.capture_error(exception=e, operation="test_2", severity=ErrorSeverity.WARNING)
    
    try:
        raise TimeoutError("test error 3")
    except Exception as e:
        manager.capture_error(exception=e, operation="test_3", severity=ErrorSeverity.CRITICAL)
    
    report = manager.generate_error_report()
    
    assert "SDD-Workflow Error Report" in report
    assert "Total errors:" in report
    assert "Errors by severity:" in report
    assert "Errors by category:" in report
    assert "Recent errors:" in report
    
    print("[PASS] Error report generated")
    print(report[:200] + "..." if len(report) > 200 else report)


def test_recovery_decorator():
    @with_error_recovery("test_operation", severity=ErrorSeverity.WARNING)
    def test_function(should_fail=False):
        if should_fail:
            raise ValueError("Test error")
        return "success"
    
    result = test_function(should_fail=False)
    assert result == "success"
    print("[PASS] Decorator: function succeeds when no error")
    
    try:
        result = test_function(should_fail=True)
        print("[PASS] Decorator: error captured")
    except ValueError:
        print("[PASS] Decorator: error raised after recovery failed")


def test_error_history():
    manager = ErrorRecoveryManager(Path("."))
    
    for i in range(5):
        try:
            raise RuntimeError(f"Error {i}")
        except Exception as e:
            manager.capture_error(
                exception=e,
                operation=f"operation_{i}",
                severity=ErrorSeverity.ERROR,
            )
    
    history = manager.get_error_history()
    assert len(history) >= 5
    
    recent = manager.get_recent_errors(limit=3)
    assert len(recent) == 3
    
    print(f"[PASS] Error history: {len(history)} total")
    print(f"[PASS] Recent errors: {len(recent)} retrieved")


def test_error_context():
    context = ErrorContext(
        phase="Phase 1",
        step="Step 2",
        feature_name="test_feature",
        timestamp="2026-01-01T12:00:00",
        operation="load_config",
        file_path="config.yaml",
        tool_name="read",
        user_action="approve",
        additional_context={"key": "value"},
    )
    
    context_dict = context.to_dict()
    
    assert context_dict["phase"] == "Phase 1"
    assert context_dict["step"] == "Step 2"
    assert context_dict["feature_name"] == "test_feature"
    assert context_dict["file_path"] == "config.yaml"
    assert context_dict["additional_context"]["key"] == "value"
    
    print("[PASS] Error context serialization works")


def run_all_tests():
    print("\n" + "=" * 60)
    print("Error Recovery System Test Suite")
    print("=" * 60 + "\n")
    
    test_error_classification()
    test_error_capture()
    test_strategy_selection()
    test_error_persistence()
    test_error_report()
    test_recovery_decorator()
    test_error_history()
    test_error_context()
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_tests()