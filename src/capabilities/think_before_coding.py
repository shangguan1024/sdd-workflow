"""
ThinkBeforeCoding Capability

基于 Andrej Karpathy 原则的"思考优先"机制。

核心原则:
1. State assumptions explicitly - 显式声明假设
2. Present multiple interpretations - 呈现多方案
3. Push back when warranted - 必要时反驳
4. Stop when confused - 困惑时停下来
"""

from pathlib import Path
from typing import TYPE_CHECKING, Dict, Any, List

if TYPE_CHECKING:
    from ..director import ExecutionContext

from .base import Capability, CapabilityResult


class ThinkBeforeCodingCapability(Capability):
    """
    ThinkBeforeCoding Capability
    
    在设计/实现之前，强制 AI 进行深度思考：
    1. 显式声明假设
    2. 呈现多方案并对比
    3. 识别潜在问题并主动提问
    4. 定义明确的成功标准
    """
    
    def __init__(self):
        super().__init__("think-before-coding")
    
    def execute(self, context: "ExecutionContext") -> CapabilityResult:
        """执行 Think Before Coding"""
        try:
            feature_name = context.feature_name
            
            # 1. 显式声明假设
            assumptions = self._extract_assumptions(context)
            
            # 2. 呈现多方案
            alternatives = self._present_alternatives(context)
            
            # 3. 识别潜在问题
            concerns = self._identify_concerns(context)
            
            # 4. 定义成功标准
            success_criteria = self._define_success_criteria(context)
            
            # 5. 检查是否需要 push back
            pushback = self._check_pushback_needed(context)
            
            # 更新 context
            context.metadata["think_before_coding_completed"] = True
            context.metadata["assumptions"] = assumptions
            context.metadata["alternatives"] = alternatives
            context.metadata["concerns"] = concerns
            context.metadata["success_criteria"] = success_criteria
            context.metadata["pushback_needed"] = pushback
            
            # 生成思考报告
            report = self._generate_think_report(
                context, assumptions, alternatives, concerns, 
                success_criteria, pushback
            )
            
            # 保存报告
            feature_dir = context.feature_dir
            report_file = feature_dir / "think_before_coding.md"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            report_file.write_text(report, encoding="utf-8")
            
            context.metadata["think_report_path"] = str(report_file)
            
            # 检查是否需要用户确认
            needs_confirmation = len(pushback["items"]) > 0 or len(concerns["questions"]) > 0
            
            return CapabilityResult(
                success=True,
                message="Think Before Coding completed",
                artifacts={
                    "think_report": str(report_file),
                    "assumptions": assumptions,
                    "alternatives": alternatives,
                    "concerns": concerns,
                    "success_criteria": success_criteria,
                    "pushback_needed": pushback,
                    "needs_user_confirmation": needs_confirmation,
                },
            )
            
        except Exception as e:
            return CapabilityResult(
                success=False,
                message=f"Think Before Coding failed: {e}",
            )
    
    def _extract_assumptions(self, context: "ExecutionContext") -> Dict[str, Any]:
        """提取并显式声明假设"""
        feature_name = context.feature_name
        
        assumptions = {
            "stated": [],
            "hidden": [],
            "uncertain": [],
        }
        
        # 从 feature 描述中提取假设
        user_input = context.metadata.get("user_input", "")
        feature_desc = context.metadata.get("feature_description", "")
        
        # 常见的隐含假设模式
        assumption_patterns = [
            ("现有代码支持这个功能", "需要验证现有代码是否支持"),
            ("用户需要这个功能", "需要确认目标用户"),
            ("性能不是问题", "需要定义性能要求"),
            ("向后兼容", "需要确认兼容范围"),
            ("安全不是问题", "需要安全评估"),
        ]
        
        for assumption, verification in assumption_patterns:
            if assumption in user_input or assumption in feature_desc:
                assumptions["stated"].append({
                    "assumption": assumption,
                    "verification": verification,
                })
            elif any(word in user_input.lower() for word in ["应该", "可能", "假设"]):
                assumptions["uncertain"].append({
                    "assumption": f"可能的假设: {assumption}",
                    "verification": f"需要澄清: {verification}",
                })
        
        return assumptions
    
    def _present_alternatives(self, context: "ExecutionContext") -> Dict[str, Any]:
        """呈现多个方案"""
        alternatives = {
            "options": [],
            "recommended": None,
            "rejected": [],
        }
        
        feature_name = context.feature_name
        
        # 至少提供 2-3 个方案
        # 方案 1: 最小化方案
        alternatives["options"].append({
            "name": "最小化方案",
            "description": "只实现核心功能，最少代码",
            "pros": ["快速实现", "风险低", "容易回滚"],
            "cons": ["功能有限", "可能需要后续扩展"],
            "effort": "low",
        })
        
        # 方案 2: 标准方案
        alternatives["options"].append({
            "name": "标准方案",
            "description": "完整实现，包含错误处理和日志",
            "pros": ["功能完整", "可维护性好"],
            "cons": ["实现时间较长", "复杂度较高"],
            "effort": "medium",
        })
        
        # 方案 3: 扩展方案
        alternatives["options"].append({
            "name": "扩展方案",
            "description": "包含所有可能的功能和配置选项",
            "pros": ["功能最全面"],
            "cons": ["过度设计", "维护成本高", "复杂性高"],
            "effort": "high",
        })
        
        return alternatives
    
    def _identify_concerns(self, context: "ExecutionContext") -> Dict[str, Any]:
        """识别潜在问题"""
        concerns = {
            "technical": [],
            "scope": [],
            "questions": [],
        }
        
        feature_name = context.feature_name
        
        # 常见的问题检查点
        concern_checks = [
            {
                "category": "technical",
                "question": "这个功能是否与现有架构兼容？",
                "if_yes": "需要检查模块依赖",
                "if_no": "需要架构变更",
            },
            {
                "category": "scope",
                "question": "这个功能的边界是否清晰？",
                "if_yes": "可以明确定义任务",
                "if_no": "需要先澄清范围",
            },
            {
                "category": "technical",
                "question": "是否有性能要求需要考虑？",
                "if_yes": "需要在设计中添加性能指标",
                "if_no": "按默认性能要求实现",
            },
            {
                "category": "questions",
                "question": "成功标准是什么？",
                "if_yes": "需要定义可测试的验收条件",
                "if_no": "必须先定义成功标准",
            },
        ]
        
        for check in concern_checks:
            concerns[check["category"]].append({
                "question": check["question"],
                "response_needed": check["if_no"],
            })
        
        return concerns
    
    def _define_success_criteria(self, context: "ExecutionContext") -> Dict[str, Any]:
        """定义明确的成功标准"""
        success_criteria = {
            "must_have": [],
            "should_have": [],
            "nice_to_have": [],
            "verification_method": [],
        }
        
        feature_name = context.feature_name
        
        # 必须有
        success_criteria["must_have"] = [
            "功能可正常运行",
            "有对应的单元测试",
            "符合 Constitution 规则",
        ]
        
        # 应该有
        success_criteria["should_have"] = [
            "有集成测试",
            "有文档说明",
        ]
        
        # 最好有
        success_criteria["nice_to_have"] = [
            "性能在可接受范围内",
            "有示例代码",
        ]
        
        # 验证方法
        success_criteria["verification_method"] = [
            "所有单元测试通过",
            "cargo clippy 无警告",
            "用户验收通过",
        ]
        
        return success_criteria
    
    def _check_pushback_needed(self, context: "ExecutionContext") -> Dict[str, Any]:
        """检查是否需要主动反驳/提问"""
        pushback = {
            "needed": False,
            "items": [],
        }
        
        feature_name = context.feature_name
        user_input = context.metadata.get("user_input", "")
        
        # Pushback 触发条件
        pushback_triggers = [
            {
                "pattern": "直接",
                "message": "建议先进行 Understanding，而不是直接开始实现",
            },
            {
                "pattern": "简单",
                "message": "即使看起来简单，也需要先理解现有代码",
            },
            {
                "pattern": "应该",
                "message": "使用'应该'可能表示不确定，建议澄清",
            },
        ]
        
        for trigger in pushback_triggers:
            if trigger["pattern"] in user_input:
                pushback["needed"] = True
                pushback["items"].append(trigger["message"])
        
        return pushback
    
    def _generate_think_report(
        self,
        context: "ExecutionContext",
        assumptions: Dict,
        alternatives: Dict,
        concerns: Dict,
        success_criteria: Dict,
        pushback: Dict,
    ) -> str:
        """生成 Think Before Coding 报告"""
        feature_name = context.feature_name
        
        report = f"""# Think Before Coding Report: {feature_name}

> ⚠️ **重要**: 在开始设计/实现之前，必须完成深度思考。

---

## 1. 显式声明假设

### 已声明的假设
"""
        
        if assumptions["stated"]:
            for a in assumptions["stated"]:
                report += f"""**假设**: {a['assumption']}
**验证方法**: {a['verification']}

"""
        else:
            report += "_暂无明确声明的假设_\n\n"
        
        report += "### 不确定的假设\n"
        if assumptions["uncertain"]:
            for a in assumptions["uncertain"]:
                report += f"- {a['assumption']} → {a['verification']}\n"
        else:
            report += "_所有关键假设已验证_\n"
        
        report += """

---

## 2. 多方案对比

| 方案 | 描述 | 优点 | 缺点 | 工作量 |
|------|------|------|------|--------|
"""
        
        for option in alternatives["options"]:
            report += f"| {option['name']} | {option['description']} | {', '.join(option['pros'])} | {', '.join(option['cons'])} | {option['effort']} |\n"
        
        report += f"""

**推荐方案**: {alternatives.get('recommended', '待分析')}
**推荐理由**: (需要根据实际情况补充)

---

## 3. 潜在问题识别

### 技术问题
"""
        
        for c in concerns["technical"]:
            report += f"- ❓ {c['question']}\n  → {c['response_needed']}\n"
        
        report += "\n### 范围问题\n"
        for c in concerns["scope"]:
            report += f"- ❓ {c['question']}\n  → {c['response_needed']}\n"
        
        report += "\n### 需要澄清的问题\n"
        for c in concerns["questions"]:
            report += f"- ❓ {c['question']}\n"
        
        report += """

---

## 4. 成功标准

### 必须有 (Must Have)
"""
        for criterion in success_criteria["must_have"]:
            report += f"- [ ] {criterion}\n"
        
        report += "\n### 应该有 (Should Have)\n"
        for criterion in success_criteria["should_have"]:
            report += f"- [ ] {criterion}\n"
        
        report += "\n### 最好有 (Nice to Have)\n"
        for criterion in success_criteria["nice_to_have"]:
            report += f"- [ ] {criterion}\n"
        
        report += "\n### 验证方法\n"
        for method in success_criteria["verification_method"]:
            report += f"- ✅ {method}\n"
        
        report += """

---

## 5. Pushback 检查
"""
        
        if pushback["needed"]:
            report += "⚠️ **需要主动提问/反驳**:\n"
            for item in pushback["items"]:
                report += f"- {item}\n"
        else:
            report += "✅ **无需 pushback，可以继续**\n"
        
        report += """

---

## 6. 思考检查清单

在继续之前，确认以下问题已回答：

- [ ] 我理解用户真正想要的是什么吗？
- [ ] 我是否声明了所有关键假设？
- [ ] 我是否呈现了多个方案并给出了推荐？
- [ ] 我是否识别了所有潜在问题？
- [ ] 我是否定义了明确的成功标准？
- [ ] 我是否需要向用户提问以澄清问题？

**如果任何一个问题回答是"否"，请先回答这些问题再继续。**
"""
        
        return report