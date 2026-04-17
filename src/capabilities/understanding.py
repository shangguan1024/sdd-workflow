"""
Understanding Capability

深入研究阶段 - 在设计之前强制理解现有系统和相关原理
"""

from pathlib import Path
from typing import TYPE_CHECKING, Dict, Any, List

if TYPE_CHECKING:
    from ..director import ExecutionContext

from .base import Capability, CapabilityResult


class UnderstandingCapability(Capability):
    """
    Understanding Capability
    
    深入研究阶段 - 在设计之前必须完成的研究工作
    
    职责:
    - 分析现有代码库架构
    - 研究相关技术原理
    - 识别约束条件
    - 引用权威来源
    - Anti-Superficiality 检查
    """
    
    def __init__(self):
        super().__init__("understanding")
    
    def execute(self, context: "ExecutionContext") -> CapabilityResult:
        """执行 Understanding 阶段"""
        try:
            feature_name = context.feature_name
            feature_dir = context.feature_dir
            
            # 1. Think Before Coding - 思考优先
            from .think_before_coding import ThinkBeforeCodingCapability
            think_cap = ThinkBeforeCodingCapability()
            think_result = think_cap.execute(context)
            
            # 如果需要用户确认，先暂停
            if think_result.artifacts.get("needs_user_confirmation"):
                context.metadata["think_report_path"] = think_result.artifacts.get("think_report_path")
                context.metadata["pushback_needed"] = think_result.artifacts.get("pushback_needed")
                context.metadata["think_before_coding_pending"] = True
            
            # 2. 分析现有代码库
            codebase_analysis = self._analyze_codebase(context)
            
            # 3. 研究技术原理
            technical_research = self._research_technical_principles(context)
            
            # 4. 识别约束条件
            constraints = self._identify_constraints(context)
            
            # 5. 分析类似方案
            similar_solutions = self._analyze_similar_solutions(context)
            
            # 6. Anti-Superficiality 自检
            depth_check = self._anti_superficiality_check(
                codebase_analysis, technical_research, constraints, similar_solutions
            )
            
            # 7. 生成研究报告
            research_report = self._generate_research_report(
                context, codebase_analysis, technical_research, 
                constraints, similar_solutions, depth_check
            )
            
            # 保存研究报告
            research_file = feature_dir / "research.md"
            research_file.parent.mkdir(parents=True, exist_ok=True)
            research_file.write_text(research_report, encoding="utf-8")
            
            # 更新 context
            context.metadata["understanding_completed"] = True
            context.metadata["research_report_path"] = str(research_file)
            context.metadata["codebase_analysis"] = codebase_analysis
            context.metadata["technical_research"] = technical_research
            context.metadata["constraints"] = constraints
            context.metadata["similar_solutions"] = similar_solutions
            context.metadata["depth_check"] = depth_check
            
            # 检查深度
            if not depth_check["passed"]:
                return CapabilityResult(
                    success=False,
                    message=f"Understanding 阶段未通过深度检查: {depth_check['issues']}",
                    artifacts={
                        "research_report": str(research_file),
                        "depth_check_failed": True,
                    },
                )
            
            return CapabilityResult(
                success=True,
                message="Understanding 阶段完成",
                artifacts={
                    "research_report": str(research_file),
                    "codebase_analysis": codebase_analysis,
                    "technical_research": technical_research,
                    "constraints": constraints,
                    "similar_solutions": similar_solutions,
                    "depth_check": depth_check,
                },
            )
            
        except Exception as e:
            return CapabilityResult(
                success=False,
                message=f"Understanding 阶段失败: {e}",
            )
    
    def _analyze_codebase(self, context: "ExecutionContext") -> Dict[str, Any]:
        """分析现有代码库架构"""
        project_root = context.project_root
        feature_name = context.feature_name
        
        analysis = {
            "existing_modules": [],
            "related_files": [],
            "architecture_patterns": [],
            "dependencies": [],
        }
        
        # 查找相关模块
        src_dir = project_root / "src"
        if src_dir.exists():
            for py_file in src_dir.rglob("*.py"):
                rel_path = str(py_file.relative_to(project_root))
                # 简单关键词匹配
                if any(kw in rel_path.lower() for kw in [feature_name.lower(), "core", "api", "main"]):
                    analysis["related_files"].append(rel_path)
        
        # 分析模块结构
        if (project_root / "src").exists():
            modules = [d.name for d in (project_root / "src").iterdir() if d.is_dir() and not d.name.startswith("__")]
            analysis["existing_modules"] = modules
        
        # 查找依赖配置
        for config_file in ["Cargo.toml", "package.json", "pyproject.toml", "requirements.txt"]:
            if (project_root / config_file).exists():
                analysis["dependencies"].append(config_file)
        
        return analysis
    
    def _research_technical_principles(self, context: "ExecutionContext") -> Dict[str, Any]:
        """研究相关技术原理"""
        feature_name = context.feature_name
        
        research = {
            "core_principles": [],
            "key_concepts": [],
            "references": [],
            "sources": [],
        }
        
        # 这个需要在实际使用中由 AI 填充
        # 这里提供结构框架
        research["core_principles"] = [
            f"需要研究 {feature_name} 的核心原理",
        ]
        
        research["key_concepts"] = [
            "技术选型依据",
            "设计模式选择",
            "数据流和状态管理",
        ]
        
        research["references"] = [
            "官方文档",
            "相关规范(spec)",
            "最佳实践",
        ]
        
        return research
    
    def _identify_constraints(self, context: "ExecutionContext") -> Dict[str, Any]:
        """识别约束条件"""
        constraints = {
            "performance": [],
            "security": [],
            "compatibility": [],
            "resource": [],
            "regulatory": [],
        }
        
        # 框架约束
        constraints["compatibility"].append("需要考虑向后兼容性")
        constraints["compatibility"].append("需要考虑现有 API 变更影响")
        
        return constraints
    
    def _analyze_similar_solutions(self, context: "ExecutionContext") -> Dict[str, Any]:
        """分析类似方案"""
        solutions = {
            "existing_approaches": [],
            "pros_cons": [],
            "lessons_learned": [],
        }
        
        # 框架
        solutions["existing_approaches"].append("需要研究现有的解决方案")
        solutions["pros_cons"].append({
            "approach": "方案 A",
            "pros": [],
            "cons": [],
        })
        
        return solutions
    
    def _anti_superficiality_check(
        self, 
        codebase: Dict, 
        technical: Dict, 
        constraints: Dict,
        solutions: Dict
    ) -> Dict[str, Any]:
        """
        Anti-Superficiality 检查
        
        确保分析足够深入，而非浅尝辄止
        """
        issues = []
        
        # 检查 1: 代码库分析是否完整
        if len(codebase.get("related_files", [])) == 0:
            issues.append("未识别任何相关代码文件 - 可能遗漏了现有实现")
        
        if len(codebase.get("existing_modules", [])) == 0:
            issues.append("未识别现有模块 - 可能缺少架构理解")
        
        # 检查 2: 技术原理是否研究
        principles = technical.get("core_principles", [])
        if len(principles) == 0 or "需要研究" in str(principles):
            issues.append("技术原理未深入研究 - 只是框架而非具体内容")
        
        # 检查 3: 约束条件是否识别
        all_constraints = (
            constraints.get("performance", []) +
            constraints.get("security", []) +
            constraints.get("compatibility", [])
        )
        if len(all_constraints) < 2:
            issues.append("约束条件识别不足 - 可能遗漏重要限制因素")
        
        # 检查 4: 类似方案分析
        if len(solutions.get("pros_cons", [])) == 0:
            issues.append("未分析类似方案 - 缺少对比参考")
        
        passed = len(issues) == 0
        
        return {
            "passed": passed,
            "issues": issues,
            "checks": {
                "codebase_analysis": len(codebase.get("related_files", [])) > 0,
                "technical_research": len(principles := technical.get("core_principles", [])) > 0 and "需要研究" not in str(principles),
                "constraints_identified": len(all_constraints) >= 2,
                "similar_solutions_analyzed": len(solutions.get("pros_cons", [])) > 0,
            },
        }
    
    def _generate_research_report(
        self,
        context: "ExecutionContext",
        codebase: Dict,
        technical: Dict,
        constraints: Dict,
        solutions: Dict,
        depth_check: Dict
    ) -> str:
        """生成研究报告"""
        feature_name = context.feature_name
        
        report = f"""# Understanding Report: {feature_name}

> ⚠️ **重要**: 此报告是进入 Phase 1 (Design) 的前置条件。未完成深度研究的方案设计将被视为不合格。

## 深度检查状态

| 检查项 | 状态 |
|--------|------|
| 代码库分析 | {"✅" if depth_check["checks"]["codebase_analysis"] else "❌"} |
| 技术原理研究 | {"✅" if depth_check["checks"]["technical_research"] else "❌"} |
| 约束条件识别 | {"✅" if depth_check["checks"]["constraints_identified"] else "❌"} |
| 类似方案分析 | {"✅" if depth_check["checks"]["similar_solutions_analyzed"] else "❌"} |

{"## ⚠️ 深度检查未通过问题\n\n" + "\n".join(f"- {issue}" for issue in depth_check["issues"]) + "\n" if depth_check["issues"] else ""}

## 1. 代码库分析

### 现有模块
"""
        
        if codebase.get("existing_modules"):
            for module in codebase["existing_modules"]:
                report += f"- `{module}`\n"
        else:
            report += "_未识别到现有模块_\n"
        
        report += "\n### 相关文件\n"
        if codebase.get("related_files"):
            for f in codebase["related_files"][:10]:
                report += f"- `{f}`\n"
        else:
            report += "_未识别到相关文件_\n"
        
        report += "\n### 架构模式\n"
        if codebase.get("architecture_patterns"):
            for pattern in codebase["architecture_patterns"]:
                report += f"- {pattern}\n"
        else:
            report += "_待深入分析_\n"
        
        report += "\n### 依赖配置\n"
        if codebase.get("dependencies"):
            for dep in codebase["dependencies"]:
                report += f"- `{dep}`\n"
        else:
            report += "_未找到依赖配置文件_\n"
        
        report += f"""

## 2. 技术原理研究

### 核心原理
"""
        
        principles = technical.get("core_principles", [])
        if principles and "需要研究" not in str(principles):
            for principle in principles:
                report += f"- {principle}\n"
        else:
            report += "_⚠️ 需要深入研究具体的技术原理_\n"
        
        report += "\n### 关键概念\n"
        for concept in technical.get("key_concepts", []):
            report += f"- {concept}\n"
        
        report += "\n### 参考来源\n"
        for ref in technical.get("references", []):
            report += f"- {ref}\n"
        
        report += """

## 3. 约束条件

### 性能约束
"""
        for c in constraints.get("performance", []):
            report += f"- {c}\n"
        
        report += "\n### 安全约束\n"
        for c in constraints.get("security", []):
            report += f"- {c}\n"
        
        report += "\n### 兼容性约束\n"
        for c in constraints.get("compatibility", []):
            report += f"- {c}\n"
        
        report += "\n### 资源约束\n"
        for c in constraints.get("resource", []):
            report += f"- {c}\n"
        
        report += f"""

## 4. 类似方案分析

### 现有方案
"""
        for solution in solutions.get("existing_approaches", []):
            report += f"- {solution}\n"
        
        report += "\n### 方案对比\n"
        for pc in solutions.get("pros_cons", []):
            report += f"""
#### {pc.get("approach", "方案")}
- 优点: {", ".join(pc.get("pros", [])) or "待分析"}
- 缺点: {", ".join(pc.get("cons", [])) or "待分析"}
"""
        
        report += "\n### 经验教训\n"
        for lesson in solutions.get("lessons_learned", []):
            report += f"- {lesson}\n"
        
        report += f"""

## 5. Anti-Superficiality 声明

在完成此研究报告时，我确认：

- [ ] 已分析现有代码库，不是简单假设"没有现有代码"
- [ ] 已研究技术原理，引用了权威来源
- [ ] 已识别约束条件，不是简单忽略限制因素
- [ ] 已分析类似方案，不是只考虑一种可能
- [ ] 已理解问题本质，而非表面症状

**如果任何一项未勾选，说明研究还不够深入，需要继续补充。**

---

**研究报告生成时间**: 深度分析驱动设计，而非快速给出表面方案。
"""
        
        return report