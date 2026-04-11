"""
Quality Profile
质量配置定义
"""

from typing import Dict, Any, Optional


class QualityProfile:
    """
    质量配置
    
    定义不同场景的质量阈值和权重
    """
    
    def __init__(
        self,
        name: str,
        thresholds: Dict[str, float],
        weights: Dict[str, float],
    ):
        self.name = name
        self.thresholds = thresholds
        self.weights = weights
    
    def get_threshold(self, metric: str) -> float:
        """获取指标阈值"""
        return self.thresholds.get(metric, 70.0)
    
    def get_weight(self, metric: str) -> float:
        """获取指标权重"""
        return self.weights.get(metric, 1.0)


PROFILES: Dict[str, QualityProfile] = {
    "standard": QualityProfile(
        name="standard",
        thresholds={
            "code_quality": 70.0,
            "test_coverage": 60.0,
            "complexity": 10.0,
            "convention": 70.0,
        },
        weights={
            "code_metrics": 1.5,
            "test_coverage": 1.5,
            "complexity": 1.0,
            "convention": 1.0,
        },
    ),
    "strict": QualityProfile(
        name="strict",
        thresholds={
            "code_quality": 85.0,
            "test_coverage": 80.0,
            "complexity": 7.0,
            "convention": 85.0,
        },
        weights={
            "code_metrics": 2.0,
            "test_coverage": 2.0,
            "complexity": 1.5,
            "convention": 1.5,
        },
    ),
    "relaxed": QualityProfile(
        name="relaxed",
        thresholds={
            "code_quality": 50.0,
            "test_coverage": 40.0,
            "complexity": 15.0,
            "convention": 50.0,
        },
        weights={
            "code_metrics": 1.0,
            "test_coverage": 1.0,
            "complexity": 0.5,
            "convention": 0.5,
        },
    ),
}


def get_profile(name: str) -> QualityProfile:
    """
    获取质量配置
    
    Args:
        name: 配置名称
        
    Returns:
        QualityProfile 对象
    """
    return PROFILES.get(name, PROFILES["standard"])


def list_profiles() -> list:
    """列出所有可用配置"""
    return list(PROFILES.keys())
