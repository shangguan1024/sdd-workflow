"""
Nexus-Map Integration Module
深度集成nexus-map架构知识图谱

功能：
1. 自动生成.nexus-map/（调用nexus-mapper）
2. 加载现有.nexus-map/内容
3. 提供架构知识查询接口
4. 模块依赖分析
5. 影响半径分析

v1.0: 基础实现
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..director import ExecutionContext


class NexusMapIntegrator:
    """
    Nexus-Map 集成器
    
    负责：
    - 调用nexus-mapper生成架构图谱
    - 加载.nexus-map/内容
    - 提供架构知识查询
    - 注入架构上下文到ExecutionContext
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.nexus_map_dir = project_root / ".nexus-map"
        
        # 缓存加载的内容
        self._index_content = None
        self._systems_content = None
        self._module_graph = None
        self._concept_model = None
    
    def exists(self) -> bool:
        """检查nexus-map是否存在"""
        return self.nexus_map_dir.exists()
    
    def generate_if_missing(self, context: Optional[ExecutionContext] = None) -> bool:
        """
        如果nexus-map不存在，调用nexus-mapper生成
        
        Args:
            context: 执行上下文（可选）
        
        Returns:
            bool: 是否成功生成
        """
        if self.exists():
            return True
        
        print("[INFO] .nexus-map/ not found. Attempting to generate...")
        
        try:
            # 尝试调用nexus-mapper skill
            result = subprocess.run(
                ["nexus-mapper", "--generate"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            if result.returncode == 0:
                print("[OK] nexus-map generated successfully")
                return True
            else:
                print(f"[WARN] nexus-mapper failed: {result.stderr}")
                # 创建基础结构
                self._create_basic_structure()
                return False
        
        except subprocess.TimeoutExpired:
            print("[WARN] nexus-mapper timeout (120s)")
            self._create_basic_structure()
            return False
        
        except FileNotFoundError:
            print("[WARN] nexus-mapper not found. Creating basic structure...")
            self._create_basic_structure()
            return False
    
    def _create_basic_structure(self):
        """创建基础的nexus-map结构"""
        self.nexus_map_dir.mkdir(parents=True, exist_ok=True)
        
        # INDEX.md
        index_content = """# Nexus-Map INDEX

## Architecture Overview

This is a basic nexus-map structure. For full architecture analysis, 
install nexus-mapper skill and run:

```
nexus-mapper --generate
```

## Known Modules

(List modules here after running nexus-mapper)

## Change Hotspots

(List frequently changed files here)
"""
        (self.nexus_map_dir / "INDEX.md").write_text(index_content, encoding="utf-8")
        
        # systems.md
        systems_content = """# Systems Overview

## Core Systems

(Describe core systems here)

## Dependencies

(Map system dependencies here)
"""
        (self.nexus_map_dir / "systems.md").write_text(systems_content, encoding="utf-8")
        
        print("[OK] Basic .nexus-map/ structure created")
    
    def load_content(self) -> Dict[str, Any]:
        """
        加载nexus-map内容
        
        Returns:
            Dict: 包含INDEX.md, systems.md, module-graph.md等内容的字典
        """
        if not self.exists():
            return {}
        
        content = {}
        
        # 加载INDEX.md
        index_file = self.nexus_map_dir / "INDEX.md"
        if index_file.exists():
            self._index_content = index_file.read_text(encoding="utf-8")
            content["INDEX.md"] = self._index_content
        
        # 加载systems.md
        systems_file = self.nexus_map_dir / "systems.md"
        if systems_file.exists():
            self._systems_content = systems_file.read_text(encoding="utf-8")
            content["systems.md"] = self._systems_content
        
        # 加载module-graph.md
        graph_file = self.nexus_map_dir / "module-graph.md"
        if graph_file.exists():
            self._module_graph = graph_file.read_text(encoding="utf-8")
            content["module-graph.md"] = self._module_graph
        
        # 加载concept_model.json
        model_file = self.nexus_map_dir / "concept_model.json"
        if model_file.exists():
            try:
                self._concept_model = json.loads(model_file.read_text(encoding="utf-8"))
                content["concept_model.json"] = self._concept_model
            except json.JSONDecodeError:
                pass
        
        # 加载module-specs目录
        specs_dir = self.nexus_map_dir / "module-specs"
        if specs_dir.exists():
            content["module-specs"] = {}
            for spec_file in specs_dir.glob("*.md"):
                module_name = spec_file.stem
                content["module-specs"][module_name] = spec_file.read_text(encoding="utf-8")
        
        return content
    
    def get_architecture_summary(self) -> str:
        """
        获取架构摘要（用于注入上下文）
        
        Returns:
            str: 架构摘要Markdown内容
        """
        if not self.exists():
            return "No nexus-map found. Run nexus-mapper to generate architecture knowledge."
        
        content = self.load_content()
        
        summary_parts = ["## Nexus-Map Architecture Knowledge\n"]
        
        # INDEX摘要
        if "INDEX.md" in content:
            index = content["INDEX.md"]
            # 提取前500字符作为摘要
            summary_parts.append(f"### Architecture Overview\n\n{index[:500]}...\n\n")
        
        # Systems摘要
        if "systems.md" in content:
            systems = content["systems.md"]
            summary_parts.append(f"### Systems Overview\n\n{systems[:500]}...\n\n")
        
        # Module Graph摘要
        if "module-graph.md" in content:
            graph = content["module-graph.md"]
            summary_parts.append(f"### Module Dependencies\n\n{graph[:500]}...\n\n")
        
        # Module Specs列表
        if "module-specs" in content:
            specs = content["module-specs"]
            summary_parts.append("### Module Specifications\n\n")
            summary_parts.append("| Module | Spec File |\n")
            summary_parts.append("|--------|----------|\n")
            for module_name in specs.keys():
                summary_parts.append(f"| {module_name} | module-specs/{module_name}.md |\n")
            summary_parts.append("\n")
        
        # 添加使用提示
        summary_parts.extend([
            "---\n\n",
            "**Usage:**\n",
            "- Use `query_module_dependencies(module_name)` to analyze dependencies\n",
            "- Use `query_impact_radius(file_path)` to assess change impact\n",
            "- Use `get_module_spec(module_name)` to retrieve full module specification\n",
        ])
        
        return "".join(summary_parts)
    
    def query_module_dependencies(self, module_name: str) -> Dict[str, Any]:
        """
        查询模块依赖关系
        
        Args:
            module_name: 模块名称
        
        Returns:
            Dict: 包含依赖关系的信息
        """
        if not self.exists():
            return {"error": "nexus-map not found"}
        
        # 从module-graph中解析依赖
        if self._module_graph:
            deps = self._parse_dependencies_from_graph(module_name)
            if deps:
                return deps
        
        # 从module-specs中查找
        spec_file = self.nexus_map_dir / "module-specs" / f"{module_name}.md"
        if spec_file.exists():
            spec_content = spec_file.read_text(encoding="utf-8")
            deps = self._parse_dependencies_from_spec(spec_content)
            return deps
        
        return {"error": f"Module {module_name} not found in nexus-map"}
    
    def query_impact_radius(self, file_path: str) -> Dict[str, Any]:
        """
        查询文件变更的影响半径
        
        Args:
            file_path: 文件路径
        
        Returns:
            Dict: 包含影响范围的信息
        """
        if not self.exists():
            return {"error": "nexus-map not found"}
        
        # 简化实现：基于文件名推断模块
        module_name = self._infer_module_from_path(file_path)
        
        # 查找依赖该模块的其他模块
        dependents = self._find_dependents(module_name)
        
        return {
            "file": file_path,
            "module": module_name,
            "dependents": dependents,
            "impact_level": "high" if len(dependents) > 5 else "medium" if len(dependents) > 2 else "low",
        }
    
    def get_module_spec(self, module_name: str) -> Optional[str]:
        """
        获取模块完整规格
        
        Args:
            module_name: 模块名称
        
        Returns:
            Optional[str]: 模块规格内容，不存在返回None
        """
        if not self.exists():
            return None
        
        spec_file = self.nexus_map_dir / "module-specs" / f"{module_name}.md"
        if spec_file.exists():
            return spec_file.read_text(encoding="utf-8")
        
        return None
    
    def inject_to_context(self, context: ExecutionContext):
        """
        将nexus-map内容注入到ExecutionContext
        
        Args:
            context: 执行上下文
        """
        # 生成架构摘要
        summary = self.get_architecture_summary()
        
        # 注入到metadata
        context.metadata["nexus_map_loaded"] = True
        context.metadata["nexus_map_summary"] = summary
        
        # 加载完整内容
        content = self.load_content()
        context.metadata["nexus_map_content"] = content
        
        # 注入到injected_context
        if "injected_context" in context.metadata:
            context.metadata["injected_context"] += f"\n\n---\n\n{summary}"
        else:
            context.metadata["injected_context"] = summary
        
        print("[OK] Nexus-map architecture knowledge injected to context")
    
    def _parse_dependencies_from_graph(self, module_name: str) -> Dict[str, Any]:
        """从module-graph.md解析依赖关系"""
        if not self._module_graph:
            return {}
        
        # 简化解析：查找包含module_name的行
        deps = []
        for line in self._module_graph.splitlines():
            if module_name in line and "->" in line:
                # 提取依赖关系
                parts = line.split("->")
                if len(parts) == 2:
                    dep = parts[1].strip()
                    deps.append(dep)
        
        return {
            "module": module_name,
            "dependencies": deps,
            "source": "module-graph.md",
        }
    
    def _parse_dependencies_from_spec(self, spec_content: str) -> Dict[str, Any]:
        """从模块规格文件解析依赖关系"""
        deps = []
        
        # 查找Dependencies章节
        for line in spec_content.splitlines():
            if line.startswith("- ") and "depends on" in line.lower():
                dep = line[2:].strip()
                deps.append(dep)
        
        return {
            "dependencies": deps,
            "source": "module-spec",
        }
    
    def _infer_module_from_path(self, file_path: str) -> str:
        """从文件路径推断模块名"""
        # 简化实现：使用路径的第一级目录作为模块名
        parts = Path(file_path).parts
        
        if len(parts) >= 2:
            # src/module_name 或 module_name
            if parts[0] == "src":
                return parts[1] if len(parts) > 1 else "unknown"
            return parts[0]
        
        return "unknown"
    
    def _find_dependents(self, module_name: str) -> List[str]:
        """查找依赖该模块的其他模块"""
        if not self._module_graph:
            return []
        
        dependents = []
        for line in self._module_graph.splitlines():
            if "->" in line and module_name in line.split("->")[-1]:
                # 其他模块依赖该模块
                dependent = line.split("->")[0].strip()
                if dependent != module_name:
                    dependents.append(dependent)
        
        return dependents
    
    def analyze_feature_compatibility(self, feature_description: str) -> Dict[str, Any]:
        """
        分析特性与现有架构的兼容性
        
        Args:
            feature_description: 特性描述
        
        Returns:
            Dict: 兼容性分析结果
        """
        if not self.exists():
            return {"compatible": True, "reason": "No nexus-map found"}
        
        # 加载架构知识
        content = self.load_content()
        
        # 简化实现：基于关键词匹配
        related_modules = []
        
        # 从INDEX中查找相关模块
        if "INDEX.md" in content:
            index = content["INDEX.md"]
            # 提取模块名（简化：查找以模块名格式的文本）
            for line in index.splitlines():
                if "module" in line.lower() or "system" in line.lower():
                    # 提取可能的关键词
                    words = line.split()
                    for word in words:
                        if len(word) > 3 and word not in ["module", "system", "the", "for", "and"]:
                            related_modules.append(word)
        
        return {
            "feature": feature_description,
            "related_modules": related_modules[:10],  # 最多10个
            "compatibility": "high",  # 简化：默认高兼容性
            "warnings": [],  # 暂无警告
            "recommendations": [
                "Review related module specifications before implementation",
                "Check module dependencies for potential conflicts",
            ],
        }