"""
Config Manager
统一配置管理器，避免配置路径硬编码

职责：
1. 集中管理所有配置文件路径
2. 提供配置加载和验证
3. 支持默认配置fallback
4. 支持配置覆盖和合并
"""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """
    Config Manager - 统一配置管理
    
    集中管理所有配置文件，避免硬编码路径。
    """
    
    CONFIG_FILES = {
        "privacy_filter": "config/privacy_filter.yaml",
        "loop_detection": "config/loop_detection.yaml",
        "artifact_checker": "config/artifact_checker.yaml",
        "constitution_enforcer": "config/constitution_enforcer.yaml",
        "error_recovery": "config/error_recovery.yaml",
        "understanding": "config/understanding.yaml",
        "quality": "config/quality.yaml",
        "context_monitor": "config/context_monitor.yaml",
    }
    
    DEFAULT_CONFIGS = {
        "privacy_filter": {
            "enabled": True,
            "patterns": {
                "secrets": ["password", "secret", "token", "key", "credential"],
                "personal": ["email", "phone", "name", "address"],
            },
        },
        "loop_detection": {
            "enabled": True,
            "max_repetitions": 3,
            "max_same_file_edits": 10,
            "max_same_response": 2,
        },
        "artifact_checker": {
            "enabled": True,
            "required_artifacts": {
                "phase5": ["architecture_review.md", "code_quality_review.md"],
                "phase6": ["AGENTS.md", "PROJECT_STATE.md"],
            },
        },
        "constitution_enforcer": {
            "enabled": True,
            "strict_mode": False,
            "rules_dir": "CONSTITUTION",
        },
        "error_recovery": {
            "enabled": True,
            "max_retry_attempts": 3,
            "retry_delay_seconds": 5,
            "log_errors": True,
        },
        "understanding": {
            "enabled": True,
            "anti_superficiality": {
                "min_codebase_words": 50,
                "min_technical_words": 80,
                "min_constraints_words": 40,
                "min_solutions_words": 80,
            },
        },
        "quality": {
            "enabled": True,
            "profile": "standard",
            "thresholds": {
                "development": 70,
                "integration": 70,
                "review": 80,
            },
        },
        "context_monitor": {
            "enabled": True,
            "thresholds": {
                "file_edits_soft_limit": 20,
                "file_edits_hard_limit": 50,
                "token_soft_limit": 80000,
                "token_hard_limit": 100000,
            },
        },
    }
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self._config_cache: Dict[str, Any] = {}
    
    def load(self, config_name: str) -> Dict[str, Any]:
        """
        加载配置
        
        Args:
            config_name: 配置名称（如"privacy_filter"）
            
        Returns:
            配置字典
        """
        if config_name in self._config_cache:
            return self._config_cache[config_name]
        
        config_path = self.get_config_path(config_name)
        
        if config_path.exists():
            try:
                with open(config_path, encoding="utf-8") as f:
                    config = yaml.safe_load(f) or {}
                    self._config_cache[config_name] = config
                    return config
            except Exception as e:
                print(f"[ConfigManager] Failed to load {config_name}: {e}")
                return self.get_default_config(config_name)
        
        return self.get_default_config(config_name)
    
    def get_config_path(self, config_name: str) -> Path:
        """
        获取配置文件路径
        
        Args:
            config_name: 配置名称
            
        Returns:
            配置文件完整路径
        """
        relative_path = self.CONFIG_FILES.get(config_name)
        if relative_path:
            return self.project_root / relative_path
        
        return self.project_root / "config" / f"{config_name}.yaml"
    
    def get_default_config(self, config_name: str) -> Dict[str, Any]:
        """
        获取默认配置
        
        Args:
            config_name: 配置名称
            
        Returns:
            默认配置字典
        """
        return self.DEFAULT_CONFIGS.get(config_name, {})
    
    def save(self, config_name: str, config: Dict[str, Any]) -> Path:
        """
        保存配置
        
        Args:
            config_name: 配置名称
            config: 配置内容
            
        Returns:
            保存的文件路径
        """
        config_path = self.get_config_path(config_name)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        self._config_cache[config_name] = config
        
        return config_path
    
    def merge(self, config_name: str, overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并配置（覆盖部分配置）
        
        Args:
            config_name: 配置名称
            overrides: 要覆盖的配置项
            
        Returns:
            合合后的配置
        """
        base_config = self.load(config_name)
        merged_config = {**base_config, **overrides}
        
        self._config_cache[config_name] = merged_config
        
        return merged_config
    
    def validate(self, config_name: str, config: Dict[str, Any]) -> bool:
        """
        验证配置
        
        Args:
            config_name: 配置名称
            config: 配置内容
            
        Returns:
            是否有效
        """
        default_config = self.get_default_config(config_name)
        
        if not default_config:
            return True
        
        required_keys = set(default_config.keys())
        provided_keys = set(config.keys())
        
        missing_keys = required_keys - provided_keys
        
        if missing_keys:
            print(f"[ConfigManager] {config_name} missing keys: {missing_keys}")
            return False
        
        return True
    
    def list_available_configs(self) -> list:
        """
        列出所有可用配置
        
        Returns:
            配置名称列表
        """
        configs = []
        
        for config_name in self.CONFIG_FILES.keys():
            config_path = self.get_config_path(config_name)
            if config_path.exists():
                configs.append(config_name)
        
        return configs
    
    def reload(self, config_name: str) -> Dict[str, Any]:
        """
        重新加载配置（清除缓存）
        
        Args:
            config_name: 配置名称
            
        Returns:
            配置内容
        """
        if config_name in self._config_cache:
            del self._config_cache[config_name]
        
        return self.load(config_name)
    
    def reload_all(self):
        """
        重新加载所有配置
        """
        self._config_cache.clear()
    
    def get(self, config_name: str, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            config_name: 配置名称
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        config = self.load(config_name)
        return config.get(key, default)
    
    def set(self, config_name: str, key: str, value: Any):
        """
        设置配置项
        
        Args:
            config_name: 配置名称
            key: 配置键
            value: 配置值
        """
        config = self.load(config_name)
        config[key] = value
        self._config_cache[config_name] = config


def get_config_manager(project_root: Path) -> ConfigManager:
    """
    获取ConfigManager实例
    
    Args:
        project_root: 项目根目录
        
    Returns:
        ConfigManager实例
    """
    return ConfigManager(project_root)