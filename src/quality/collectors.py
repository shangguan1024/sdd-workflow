"""
Collectors
质量数据收集器
"""

from pathlib import Path
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class Collector(ABC):
    """Collector 基类"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    @abstractmethod
    def collect(self, feature_name: str, context: "ExecutionContext") -> Dict[str, Any]:
        """收集质量数据"""
        pass


class CodeMetricsCollector(Collector):
    """代码指标收集器"""
    
    def collect(self, feature_name: str, context: "ExecutionContext") -> Dict[str, Any]:
        """收集代码指标"""
        feature_dir = self.project_root / "docs" / "features" / feature_name
        
        file_count = sum(1 for _ in feature_dir.rglob("*.py") if _.is_file()) if feature_dir.exists() else 0
        
        return {
            "success": True,
            "metrics": {
                "file_count": file_count,
                "total_lines": self._count_lines(feature_dir),
            },
            "score": 100 if file_count > 0 else 50,
        }
    
    def _count_lines(self, directory: Path) -> int:
        """计算代码行数"""
        total = 0
        for py_file in directory.rglob("*.py"):
            if py_file.is_file():
                try:
                    total += len(py_file.read_text(encoding="utf-8").splitlines())
                except:
                    pass
        return total


class TestCoverageCollector(Collector):
    """测试覆盖率收集器"""
    
    def collect(self, feature_name: str, context: "ExecutionContext") -> Dict[str, Any]:
        """收集测试覆盖率"""
        feature_dir = self.project_root / "docs" / "features" / feature_name
        
        test_files = list(feature_dir.rglob("test_*.py")) if feature_dir.exists() else []
        source_files = list(feature_dir.rglob("*.py")) if feature_dir.exists() else []
        
        source_files = [f for f in source_files if "test_" not in f.name]
        
        coverage = 0
        if source_files:
            coverage = min(100, (len(test_files) / max(len(source_files), 1)) * 100)
        
        return {
            "success": True,
            "metrics": {
                "test_files": len(test_files),
                "source_files": len(source_files),
                "coverage_percent": coverage,
            },
            "score": coverage,
        }


class ComplexityCollector(Collector):
    """复杂度收集器"""
    
    def collect(self, feature_name: str, context: "ExecutionContext") -> Dict[str, Any]:
        """收集代码复杂度"""
        feature_dir = self.project_root / "docs" / "features" / feature_name
        
        complexity_scores = []
        
        if feature_dir.exists():
            for py_file in feature_dir.rglob("*.py"):
                if py_file.is_file() and "test_" not in py_file.name:
                    try:
                        complexity = self._calculate_complexity(py_file)
                        complexity_scores.append(complexity)
                    except:
                        pass
        
        avg_complexity = sum(complexity_scores) / max(len(complexity_scores), 1)
        
        score = max(0, 100 - (avg_complexity * 10))
        
        return {
            "success": True,
            "metrics": {
                "avg_complexity": avg_complexity,
                "max_complexity": max(complexity_scores) if complexity_scores else 0,
                "files_analyzed": len(complexity_scores),
            },
            "score": score,
        }
    
    def _calculate_complexity(self, file_path: Path) -> int:
        """计算文件复杂度（简化版）"""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            
            complexity = 0
            for line in lines:
                stripped = line.strip()
                if stripped.startswith(("if ", "elif ", "for ", "while ", "except:")):
                    complexity += 1
                elif stripped.startswith("def "):
                    complexity += 1
            
            return complexity
        except:
            return 0


class ConventionCollector(Collector):
    """代码规范收集器"""
    
    def collect(self, feature_name: str, context: "ExecutionContext") -> Dict[str, Any]:
        """收集代码规范遵守情况"""
        feature_dir = self.project_root / "docs" / "features" / feature_name
        
        convention_issues = []
        
        if feature_dir.exists():
            for py_file in feature_dir.rglob("*.py"):
                if py_file.is_file() and "test_" not in py_file.name:
                    issues = self._check_conventions(py_file)
                    convention_issues.extend(issues)
        
        score = max(0, 100 - (len(convention_issues) * 5))
        
        return {
            "success": True,
            "metrics": {
                "issues_found": len(convention_issues),
                "issues": convention_issues[:10],
            },
            "score": score,
        }
    
    def _check_conventions(self, file_path: Path) -> list:
        """检查代码规范"""
        issues = []
        
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                if len(line) > 120:
                    issues.append(f"{file_path.name}:{i}: Line too long ({len(line)} chars)")
                
                if line.rstrip() != line and "    " not in line:
                    pass
                
                if line.strip().startswith("#") and not line.strip().startswith("# "):
                    issues.append(f"{file_path.name}:{i}: Missing space after #")
            
            if not content.endswith("\n"):
                issues.append(f"{file_path.name}: Missing trailing newline")
                
        except:
            pass
        
        return issues
