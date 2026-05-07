"""
Nexus-Map Integration Module

深度集成nexus-map架构知识图谱

提供：
- NexusMapIntegrator: 集成器主类
- 自动生成.nexus-map/
- 架构知识查询
"""

from .integrator import NexusMapIntegrator

__all__ = [
    "NexusMapIntegrator",
]