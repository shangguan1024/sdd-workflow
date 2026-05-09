"""
Middleware Base Classes
Middleware基类和结果类定义
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class MiddlewareResult:
    """Middleware执行结果"""
    allowed: bool = True
    message: Optional[str] = None
    suggestion: Optional[str] = None
    requires_confirmation: bool = False
    confirmation_options: Optional[list[str]] = None
    add_to_context: bool = False
    error: Optional[str] = None


class Middleware(ABC):
    """Middleware 基类"""

    @abstractmethod
    def before_action(self, context: dict) -> MiddlewareResult:
        """在操作前执行"""
        pass

    @abstractmethod
    def after_action(self, context: dict, result: Any) -> MiddlewareResult:
        """在操作后执行"""
        pass