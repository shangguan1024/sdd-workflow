"""
Error Recovery System - 增强的错误恢复机制

提供:
- 错误分类和诊断
- 自动恢复策略
- 重试机制
- 错误报告和日志

v1.0: 基础实现
"""

from __future__ import annotations

import sys
import traceback
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable, TYPE_CHECKING
import json

if TYPE_CHECKING:
    from ..director import ExecutionContext


class ErrorSeverity(Enum):
    """错误严重程度"""
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"


class ErrorCategory(Enum):
    """错误分类"""
    FILE_IO = "file_io"
    NETWORK = "network"
    PROCESS = "process"
    VALIDATION = "validation"
    STATE = "state"
    DEPENDENCY = "dependency"
    USER_INPUT = "user_input"
    TIMEOUT = "timeout"
    RESOURCE = "resource"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """
    错误上下文
    
    记录错误发生时的完整上下文信息
    """
    phase: str
    step: str
    feature_name: str
    timestamp: str
    operation: str
    file_path: Optional[str] = None
    tool_name: Optional[str] = None
    user_action: Optional[str] = None
    additional_context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_context is None:
            self.additional_context = {}
    
    def to_dict(self) -> dict:
        return {
            "phase": self.phase,
            "step": self.step,
            "feature_name": self.feature_name,
            "timestamp": self.timestamp,
            "operation": self.operation,
            "file_path": self.file_path,
            "tool_name": self.tool_name,
            "user_action": self.user_action,
            "additional_context": self.additional_context,
        }


@dataclass
class ErrorRecord:
    """
    错误记录
    
    包含完整的错误信息和诊断数据
    """
    error_id: str
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    exception_type: str
    exception_message: str
    traceback_str: str
    context: ErrorContext
    recovery_attempted: bool = False
    recovery_successful: bool = False
    recovery_strategy: Optional[str] = None
    operation_callable: Optional[Callable] = None
    
    def to_dict(self) -> dict:
        return {
            "error_id": self.error_id,
            "severity": self.severity.value,
            "category": self.category.value,
            "message": self.message,
            "exception_type": self.exception_type,
            "exception_message": self.exception_message,
            "traceback": self.traceback_str,
            "context": self.context.to_dict(),
            "recovery_attempted": self.recovery_attempted,
            "recovery_successful": self.recovery_successful,
            "recovery_strategy": self.recovery_strategy,
        }


class RecoveryStrategy(Enum):
    """恢复策略"""
    RETRY = "retry"
    SKIP = "skip"
    FALLBACK = "fallback"
    ABORT = "abort"
    MANUAL = "manual"
    CHECKPOINT = "checkpoint"


class ErrorRecoveryManager:
    """
    错误恢复管理器
    
    功能:
    1. 捕获和分类错误
    2. 自动选择恢复策略
    3. 执行恢复操作
    4. 记录错误历史
    5. 生成错误报告
    """
    
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self._error_history: List[ErrorRecord] = []
        self._recovery_handlers: Dict[ErrorCategory, Callable] = {}
        self._current_context: Optional["ExecutionContext"] = None
        
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """注册默认恢复处理器"""
        self._recovery_handlers[ErrorCategory.FILE_IO] = self._handle_file_io_error
        self._recovery_handlers[ErrorCategory.PROCESS] = self._handle_process_error
        self._recovery_handlers[ErrorCategory.VALIDATION] = self._handle_validation_error
        self._recovery_handlers[ErrorCategory.STATE] = self._handle_state_error
        self._recovery_handlers[ErrorCategory.TIMEOUT] = self._handle_timeout_error
    
    def set_context(self, context: "ExecutionContext"):
        """设置当前执行上下文"""
        self._current_context = context
    
    def capture_error(
        self,
        exception: Exception,
        operation: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        category: ErrorCategory = None,
        file_path: str = None,
        tool_name: str = None,
        operation_callable: Callable = None,
    ) -> ErrorRecord:
        """
        捕获错误
        
        Args:
            exception: 异常对象
            operation: 正在执行的操作
            severity: 错误严重程度
            category: 错误分类（可选，自动推断）
            file_path: 相关文件路径
            tool_name: 相关工具名称
            operation_callable: 可重试的操作函数
        
        Returns:
            ErrorRecord: 错误记录
        """
        if category is None:
            category = self._classify_error(exception)
        
        error_id = f"err_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        context = self._build_error_context(operation, file_path, tool_name)
        
        record = ErrorRecord(
            error_id=error_id,
            severity=severity,
            category=category,
            message=self._generate_message(exception, operation),
            exception_type=type(exception).__name__,
            exception_message=str(exception),
            traceback_str=traceback.format_exc(),
            context=context,
            operation_callable=operation_callable,
        )
        
        self._error_history.append(record)
        self._persist_error(record)
        
        return record
    
    def _classify_error(self, exception: Exception) -> ErrorCategory:
        """自动分类错误"""
        exception_name = type(exception).__name__
        
        if exception_name in ["FileNotFoundError", "PermissionError", "IOError", "OSError"]:
            return ErrorCategory.FILE_IO
        
        if exception_name in ["TimeoutError", "subprocess.TimeoutExpired"]:
            return ErrorCategory.TIMEOUT
        
        if exception_name in ["CalledProcessError", "RuntimeError"]:
            return ErrorCategory.PROCESS
        
        if exception_name in ["ValueError", "TypeError", "KeyError", "AttributeError"]:
            return ErrorCategory.VALIDATION
        
        if exception_name in ["StateError", "IntegrityError"]:
            return ErrorCategory.STATE
        
        if exception_name in ["ImportError", "ModuleNotFoundError"]:
            return ErrorCategory.DEPENDENCY
        
        return ErrorCategory.UNKNOWN
    
    def _build_error_context(
        self,
        operation: str,
        file_path: Optional[str],
        tool_name: Optional[str],
    ) -> ErrorContext:
        """构建错误上下文"""
        if self._current_context:
            return ErrorContext(
                phase=str(self._current_context.phase),
                step=self._current_context.current_step,
                feature_name=self._current_context.feature_name,
                timestamp=datetime.now().isoformat(),
                operation=operation,
                file_path=file_path,
                tool_name=tool_name,
            )
        
        return ErrorContext(
            phase="unknown",
            step="unknown",
            feature_name="unknown",
            timestamp=datetime.now().isoformat(),
            operation=operation,
            file_path=file_path,
            tool_name=tool_name,
        )
    
    def _generate_message(self, exception: Exception, operation: str) -> str:
        """生成用户友好的错误消息"""
        exception_name = type(exception).__name__
        
        return f"Error during '{operation}': {exception_name} - {str(exception)}"
    
    def attempt_recovery(
        self,
        error_record: ErrorRecord,
        strategy: RecoveryStrategy = None,
    ) -> bool:
        """
        尝试错误恢复
        
        Args:
            error_record: 错误记录
            strategy: 指定的恢复策略（可选，自动选择）
        
        Returns:
            bool: 恢复是否成功
        """
        if strategy is None:
            strategy = self._select_strategy(error_record)
        
        error_record.recovery_attempted = True
        error_record.recovery_strategy = strategy.value
        
        handler = self._recovery_handlers.get(error_record.category)
        
        if handler:
            try:
                success = handler(error_record, strategy)
                error_record.recovery_successful = success
                return success
            except Exception:
                error_record.recovery_successful = False
                return False
        
        return False
    
    def _select_strategy(self, error_record: ErrorRecord) -> RecoveryStrategy:
        """自动选择恢复策略"""
        severity = error_record.severity
        category = error_record.category
        
        if severity == ErrorSeverity.FATAL:
            return RecoveryStrategy.ABORT
        
        if severity == ErrorSeverity.WARNING:
            return RecoveryStrategy.SKIP
        
        if category == ErrorCategory.FILE_IO:
            return RecoveryStrategy.RETRY
        
        if category == ErrorCategory.TIMEOUT:
            return RecoveryStrategy.RETRY
        
        if category == ErrorCategory.STATE:
            return RecoveryStrategy.CHECKPOINT
        
        if category == ErrorCategory.VALIDATION:
            return RecoveryStrategy.MANUAL
        
        return RecoveryStrategy.FALLBACK
    
    def _handle_file_io_error(
        self,
        error_record: ErrorRecord,
        strategy: RecoveryStrategy,
    ) -> bool:
        """处理文件 I/O 错误"""
        if strategy == RecoveryStrategy.RETRY:
            return self._retry_operation(error_record)
        
        if strategy == RecoveryStrategy.SKIP:
            return True
        
        return False
    
    def _handle_process_error(
        self,
        error_record: ErrorRecord,
        strategy: RecoveryStrategy,
    ) -> bool:
        """处理进程错误"""
        if strategy == RecoveryStrategy.RETRY:
            return self._retry_operation(error_record)
        
        if strategy == RecoveryStrategy.FALLBACK:
            return True
        
        return False
    
    def _handle_validation_error(
        self,
        error_record: ErrorRecord,
        strategy: RecoveryStrategy,
    ) -> bool:
        """处理验证错误"""
        if strategy == RecoveryStrategy.MANUAL:
            self._request_user_intervention(error_record)
            return False
        
        return False
    
    def _handle_state_error(
        self,
        error_record: ErrorRecord,
        strategy: RecoveryStrategy,
    ) -> bool:
        """处理状态错误"""
        if strategy == RecoveryStrategy.CHECKPOINT:
            return self._restore_from_checkpoint(error_record)
        
        return False
    
    def _handle_timeout_error(
        self,
        error_record: ErrorRecord,
        strategy: RecoveryStrategy,
    ) -> bool:
        """处理超时错误"""
        if strategy == RecoveryStrategy.RETRY:
            return self._retry_operation(error_record)
        
        return False
    
    def _retry_operation(self, error_record: ErrorRecord) -> bool:
        """重试操作"""
        retry_count = 0
        
        operation_callable = error_record.operation_callable
        if not operation_callable:
            print(f"No retryable operation stored for: {error_record.context.operation}")
            return False
        
        while retry_count < self.MAX_RETRIES:
            retry_count += 1
            
            print(f"Retrying ({retry_count}/{self.MAX_RETRIES}): {error_record.context.operation}")
            
            import time
            time.sleep(self.RETRY_DELAY)
            
            try:
                result = operation_callable()
                print(f"✅ Retry successful: {error_record.context.operation}")
                return True
            except Exception as e:
                print(f"⚠️ Retry failed: {e}")
                continue
        
        return False
    
    def _restore_from_checkpoint(self, error_record: ErrorRecord) -> bool:
        """从 checkpoint 恢复"""
        print(f"Attempting to restore from checkpoint...")
        
        feature_name = error_record.context.feature_name
        checkpoint_file = self.project_root / "docs" / "features" / feature_name / ".sdd" / "checkpoint.json"
        
        if checkpoint_file.exists():
            print(f"Checkpoint found: {checkpoint_file}")
            print("Manual restore required. Use: sdd resume")
            return True
        
        return False
    
    def _request_user_intervention(self, error_record: ErrorRecord):
        """请求用户干预"""
        print("\n" + "=" * 60)
        print("ERROR: Manual intervention required")
        print("=" * 60)
        print(f"\nError ID: {error_record.error_id}")
        print(f"Category: {error_record.category.value}")
        print(f"Severity: {error_record.severity.value}")
        print(f"\nMessage: {error_record.message}")
        print(f"\nContext:")
        print(f"  Phase: {error_record.context.phase}")
        print(f"  Step: {error_record.context.step}")
        print(f"  Operation: {error_record.context.operation}")
        if error_record.context.file_path:
            print(f"  File: {error_record.context.file_path}")
        print("\n" + "=" * 60)
    
    def _persist_error(self, error_record: ErrorRecord):
        """持久化错误记录"""
        error_log_dir = self.project_root / ".sdd" / "error_logs"
        error_log_dir.mkdir(parents=True, exist_ok=True)
        
        error_file = error_log_dir / f"{error_record.error_id}.json"
        error_file.write_text(
            json.dumps(error_record.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    
    def get_error_history(self) -> List[ErrorRecord]:
        """获取错误历史"""
        return self._error_history.copy()
    
    def get_recent_errors(self, limit: int = 10) -> List[ErrorRecord]:
        """获取最近的错误"""
        return self._error_history[-limit:]
    
    def generate_error_report(self) -> str:
        """生成错误报告"""
        lines = []
        lines.append("## SDD-Workflow Error Report")
        lines.append("")
        
        if not self._error_history:
            lines.append("No errors recorded.")
            return "\n".join(lines)
        
        lines.append(f"**Total errors:** {len(self._error_history)}")
        lines.append("")
        
        severity_count: Dict[ErrorSeverity, int] = {}
        category_count: Dict[ErrorCategory, int] = {}
        
        for error in self._error_history:
            severity_count[error.severity] = severity_count.get(error.severity, 0) + 1
            category_count[error.category] = category_count.get(error.category, 0) + 1
        
        lines.append("**Errors by severity:**")
        for severity, count in sorted(severity_count.items(), key=lambda x: -x[1]):
            lines.append(f"  - {severity.value}: {count}")
        lines.append("")
        
        lines.append("**Errors by category:**")
        for category, count in sorted(category_count.items(), key=lambda x: -x[1]):
            lines.append(f"  - {category.value}: {count}")
        lines.append("")
        
        lines.append("**Recent errors:**")
        for error in self.get_recent_errors(5):
            lines.append(f"  - [{error.severity.value}] {error.category.value}: {error.message[:80]}")
            if error.recovery_attempted:
                recovery_status = "SUCCESS" if error.recovery_successful else "FAILED"
                lines.append(f"    Recovery: {error.recovery_strategy} ({recovery_status})")
        
        return "\n".join(lines)


def with_error_recovery(
    operation_name: str,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    auto_recovery: bool = True,
):
    """
    错误恢复装饰器
    
    自动捕获错误并尝试恢复
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                manager = ErrorRecoveryManager(Path("."))
                
                error_record = manager.capture_error(
                    exception=e,
                    operation=operation_name,
                    severity=severity,
                )
                
                if auto_recovery:
                    success = manager.attempt_recovery(error_record)
                    
                    if success:
                        return func(*args, **kwargs)
                
                raise
        return wrapper
    return decorator