"""
Understanding Capability
v2.2: Real anti-superficiality validation, no placeholder content.

深入研究阶段 - 在设计之前强制理解现有系统和相关原理。
Python 代码提供结构框架和数据扫描，实际分析内容由 LLM 根据 SKILL.md 指引填充。
"""

from pathlib import Path
from typing import TYPE_CHECKING, Dict, Any, List

if TYPE_CHECKING:
    from ..director import ExecutionContext

from .base import Capability, CapabilityResult


# ── Patterns that indicate superficial / placeholder content ──
PLACEHOLDER_PATTERNS = [
    "需要研究",
    "待分析",
    "待深入",
    "需要补充",
    "需要分析",
    "TBD",
    "TODO",
    "方案 A",
    "方案 B",
    "方案 C",
    "最小化方案",
    "标准方案",
    "扩展方案",
]

# ── Minimum word counts for depth validation ──
MIN_CODEBASE_WORDS = 50
MIN_TECHNICAL_WORDS = 80
MIN_CONSTRAINTS_WORDS = 40
MIN_SOLUTIONS_WORDS = 80

# ── File extensions to scan for code analysis ──
CODE_EXTENSIONS = {
    ".py", ".rs", ".go", ".ts", ".tsx", ".js", ".jsx",
    ".java", ".kt", ".swift", ".c", ".cpp", ".h", ".hpp",
    ".rb", ".php", ".cs", ".scala", ".clj",
}


class UnderstandingCapability(Capability):
    """
    Understanding Capability

    深入研究阶段 - 在设计之前必须完成的研究工作。

    职责:
    - 扫描现有代码库架构（多语言支持）
    - 提供研究框架（实际内容由 LLM 填充）
    - Anti-Superficiality 验证（检查占位文本、内容深度、来源引用）
    """

    def __init__(self):
        super().__init__("understanding")

    def execute(self, context: "ExecutionContext") -> CapabilityResult:
        """执行 Understanding 阶段"""
        try:
            feature_name = context.feature_name
            feature_dir = context.feature_dir

            think_result_artifacts = {}

            # 1. Think Before Coding - 思考优先
            try:
                from .think_before_coding import ThinkBeforeCodingCapability
                think_cap = ThinkBeforeCodingCapability()
                think_result = think_cap.execute(context)

                if think_result.artifacts.get("needs_user_confirmation"):
                    context.metadata["think_report_path"] = \
                        think_result.artifacts.get("think_report_path")
                    context.metadata["pushback_needed"] = \
                        think_result.artifacts.get("pushback_needed")
                    context.metadata["think_before_coding_pending"] = True

                think_result_artifacts = think_result.artifacts
            except Exception as e:
                context.metadata["think_before_coding_error"] = str(e)

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

            # 7. 检查 Think Before Coding 的产出是否停留在占位内容
            platformer_check = self._check_placeholder_content(
                think_result_artifacts, "think_before_coding"
            )
            if platformer_check["has_placeholders"]:
                depth_check["issues"].extend(platformer_check["issues"])
                depth_check["passed"] = False

            # 8. 生成研究报告
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

            if not depth_check["passed"]:
                return CapabilityResult(
                    success=False,
                    message=(
                        f"Understanding 阶段未通过深度检查。"
                        f"发现 {len(depth_check['issues'])} 个问题:\n"
                        + "\n".join(f"  - {i}" for i in depth_check["issues"])
                    ),
                    artifacts={
                        "research_report": str(research_file),
                        "depth_check_failed": True,
                        "issues": depth_check["issues"],
                    },
                )

            return CapabilityResult(
                success=True,
                message="Understanding 阶段完成 - 深度检查通过",
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

    # ─────────────────────────────────────────────────────
    #  Codebase Analysis (多语言支持)
    # ─────────────────────────────────────────────────────

    def _analyze_codebase(self, context: "ExecutionContext") -> Dict[str, Any]:
        """分析现有代码库架构 - 扫描多语言项目"""
        project_root = context.project_root
        feature_name = context.feature_name

        analysis = {
            "project_type": self._detect_project_type(project_root),
            "existing_modules": [],
            "all_source_files": [],
            "related_files": [],
            "key_interfaces": [],
            "architecture_patterns": [],
            "dependencies": [],
            "scan_summary": "",
        }

        all_source_files = self._scan_all_source_files(project_root)
        analysis["all_source_files"] = all_source_files

        modules = self._detect_modules(project_root)
        analysis["existing_modules"] = modules

        related = self._find_related_files(project_root, feature_name, all_source_files)
        analysis["related_files"] = related

        dep_files = self._find_dependency_files(project_root)
        analysis["dependencies"] = dep_files

        patterns = self._detect_architecture_patterns(project_root)
        analysis["architecture_patterns"] = patterns

        analysis["scan_summary"] = (
            f"项目类型: {analysis['project_type']}, "
            f"源文件: {len(all_source_files)} 个, "
            f"模块: {len(modules)} 个, "
            f"相关文件: {len(related)} 个"
        )

        return analysis

    def _detect_project_type(self, root: Path) -> str:
        """检测项目类型"""
        type_markers = {
            "Cargo.toml": "Rust",
            "package.json": "Node.js/TypeScript",
            "go.mod": "Go",
            "pyproject.toml": "Python",
            "setup.py": "Python",
            "requirements.txt": "Python",
            "pom.xml": "Java/Maven",
            "build.gradle": "Java/Gradle",
            "CMakeLists.txt": "C/C++/CMake",
            "Makefile": "C/Make",
        }
        for marker, ptype in type_markers.items():
            if (root / marker).exists():
                return ptype
        return "Unknown"

    def _scan_all_source_files(self, root: Path) -> List[str]:
        """扫描所有源码文件"""
        files = []
        for ext in CODE_EXTENSIONS:
            for f in root.rglob(f"*{ext}"):
                rel = str(f.relative_to(root))
                if not self._is_excluded(rel):
                    files.append(rel)
        return sorted(files)[:100]

    def _is_excluded(self, path: str) -> bool:
        excluded = {"__pycache__", "node_modules", ".git", "target",
                     "venv", ".venv", "dist", "build", ".sdd"}
        parts = Path(path).parts
        return any(e in parts for e in excluded)

    def _detect_modules(self, root: Path) -> List[str]:
        src_dir = root / "src"
        if not src_dir.exists():
            src_dir = root / "lib"
        if not src_dir.exists():
            return []

        modules = []
        for d in sorted(src_dir.iterdir()):
            if d.is_dir() and not d.name.startswith(".") and d.name != "__pycache__":
                modules.append(d.name)
            elif d.is_file() and d.suffix in CODE_EXTENSIONS:
                modules.append(d.stem)

        return modules

    def _find_related_files(self, root: Path, feature_name: str,
                            all_files: List[str]) -> List[str]:
        """根据特性名称查找相关文件"""
        related = []
        feature_lower = feature_name.lower().replace("-", "").replace("_", "")

        for f in all_files:
            f_lower = f.lower().replace("-", "").replace("_", "")
            if feature_lower in f_lower:
                related.append(f)
            elif any(kw in f_lower for kw in ["core", "main", "lib", "mod"]):
                if len(related) < 10:
                    related.append(f)

        return related[:20] if related else all_files[:15]

    def _find_dependency_files(self, root: Path) -> List[str]:
        patterns = [
            "Cargo.toml", "package.json", "go.mod",
            "pyproject.toml", "requirements.txt", "setup.py",
        ]
        return [p for p in patterns if (root / p).exists()]

    def _detect_architecture_patterns(self, root: Path) -> List[str]:
        """检测代码架构模式"""
        patterns = []
        if (root / "src" / "models").exists() or (root / "src" / "entities").exists():
            patterns.append("MVC/分层架构 (检测到 models/entities)")
        if (root / "src" / "services").exists() or (root / "src" / "handlers").exists():
            patterns.append("Service/Handler 模式")
        if list((root / "src").glob("**/mod.rs")) or list((root / "src").glob("**/__init__.py")):
            patterns.append("模块化设计 (检测到 mod.rs/__init__.py)")
        if (root / "tests").exists():
            patterns.append("独立测试目录")
        return patterns

    # ─────────────────────────────────────────────────────
    #  Technical Research Framework
    # ─────────────────────────────────────────────────────

    def _research_technical_principles(self, context: "ExecutionContext") -> Dict[str, Any]:
        """
        技术原理研究框架。

        ⚠️ 此方法不再生成占位内容。
        返回空框架供 LLM 填充。
        """
        return {
            "core_principles": [],
            "key_concepts": [],
            "references": [],
            "sources": [],
            "recommended_areas": self._suggest_research_areas(context),
        }

    def _suggest_research_areas(self, context: "ExecutionContext") -> List[str]:
        """根据项目类型建议研究方向"""
        project_type = self._detect_project_type(context.project_root)
        suggestions = []

        area_map = {
            "Rust": [
                "Rust 所有权模型在相关模块中的应用",
                "trait 和泛型设计模式",
                "async/await 运行时选择",
                "错误处理最佳实践 (thiserror/anyhow)",
            ],
            "Python": [
                "类型注解和 mypy 检查",
                "异步编程 (asyncio) 模式",
                "依赖注入和测试策略",
            ],
            "Node.js/TypeScript": [
                "TypeScript 类型系统设计",
                "异步模式 (Promise/async-await)",
                "包管理和模块组织",
            ],
            "Go": [
                "接口设计惯例",
                "goroutine 和 channel 模式",
                "错误处理惯用法",
            ],
        }

        return area_map.get(project_type, [
            "设计模式选择",
            "数据流和状态管理",
            "错误处理策略",
        ])

    # ─────────────────────────────────────────────────────
    #  Constraints Identification
    # ─────────────────────────────────────────────────────

    def _identify_constraints(self, context: "ExecutionContext") -> Dict[str, Any]:
        """
        识别约束条件。

        ⚠️ 返回空框架。不再预设通用约束。
        通用约束应由 LLM 根据具体场景分析。
        """
        return {
            "performance": [],
            "security": [],
            "compatibility": [],
            "resource": [],
            "regulatory": [],
            "detected_constraints": self._detect_env_constraints(context),
        }

    def _detect_env_constraints(self, context: "ExecutionContext") -> List[str]:
        """检测环境级别的约束"""
        detected = []
        root = context.project_root

        if (root / "CONSTITUTION").exists():
            detected.append("项目有 Constitution 约束 (CONSTITUTION/)")
        if (root / ".nexus-map").exists():
            detected.append("项目有架构知识图谱 (nexus-map)")

        dep_files = self._find_dependency_files(root)
        if dep_files:
            detected.append(f"外部依赖约束 ({', '.join(dep_files)})")

        return detected

    # ─────────────────────────────────────────────────────
    #  Similar Solutions Analysis
    # ─────────────────────────────────────────────────────

    def _analyze_similar_solutions(self, context: "ExecutionContext") -> Dict[str, Any]:
        """
        类似方案分析框架。

        ⚠️ 返回空框架。不再预设"方案 A/B/C"模板。
        """
        return {
            "existing_approaches": [],
            "pros_cons": [],
            "lessons_learned": [],
        }

    # ─────────────────────────────────────────────────────
    #  Anti-Superficiality Validation (核心)
    # ─────────────────────────────────────────────────────

    def _anti_superficiality_check(
        self,
        codebase: Dict,
        technical: Dict,
        constraints: Dict,
        solutions: Dict
    ) -> Dict[str, Any]:
        """
        真实的反浅显检查。

        不再仅检查"字段是否为空"，而是检查：
        1. 内容是否为占位文本
        2. 内容深度是否达标（字数、具体性）
        3. 是否引用了外部来源
        """
        issues = []

        # ── 检查 1: 代码库分析 ──
        related_files = codebase.get("related_files", [])
        all_files = codebase.get("all_source_files", [])
        modules = codebase.get("existing_modules", [])

        if len(related_files) == 0 and len(all_files) > 0:
            issues.append(
                "代码库分析: 项目中有 {} 个源文件，但未识别任何相关文件。"
                "这表明没有根据特性名称进行针对性搜索。".format(len(all_files))
            )
        elif len(related_files) < 3 and len(all_files) >= 3:
            issues.append(
                "代码库分析: 仅识别 {} 个相关文件（共 {} 个源文件）。"
                "分析可能不够全面。".format(len(related_files), len(all_files))
            )

        if len(modules) == 0 and len(all_files) > 0:
            issues.append("代码库分析: 未识别到模块结构。请检查项目组织方式。")

        # ── 检查 2: 技术原理 ──
        principles = technical.get("core_principles", [])
        concepts = technical.get("key_concepts", [])
        references = technical.get("references", [])
        sources = technical.get("sources", [])

        # 检查占位文本
        placeholder_found = self._find_placeholders(technical)
        if placeholder_found:
            issues.append(
                f"技术原理: 发现占位内容 — {placeholder_found}。"
                "请替换为具体的原理分析。"
            )

        # 检查内容深度
        technical_text = str(principles) + " " + str(concepts)
        technical_words = len(technical_text.split())

        if technical_words < MIN_TECHNICAL_WORDS:
            issues.append(
                f"技术原理: 内容不足 ({technical_words} 词，要求 ≥ {MIN_TECHNICAL_WORDS})。"
                "请添加具体的原理说明和概念解释。"
            )

        # 检查外部引用
        total_refs = len(references) + len(sources)
        if total_refs == 0:
            issues.append(
                "技术原理: 未引用任何外部来源。"
                "必须引用官方文档、spec、或权威参考资料。"
            )
        elif total_refs == 1 and "官方文档" in str(references):
            issues.append(
                "技术原理: 引用了泛化的'官方文档'但未指定具体章节或 URL。"
                "请引用具体来源。"
            )

        # ── 检查 3: 约束条件 ──
        all_constraints = (
            constraints.get("performance", []) +
            constraints.get("security", []) +
            constraints.get("compatibility", []) +
            constraints.get("resource", []) +
            constraints.get("regulatory", [])
        )

        constraints_text = " ".join(str(c) for c in all_constraints)
        constraints_words = len(constraints_text.split())

        if constraints_words < MIN_CONSTRAINTS_WORDS:
            issues.append(
                f"约束条件: 内容不足 ({constraints_words} 词，要求 ≥ {MIN_CONSTRAINTS_WORDS})。"
                "请从性能、安全、兼容性、资源等维度分析约束。"
            )

        constraint_placeholders = self._find_placeholders(constraints)
        if constraint_placeholders:
            issues.append(
                f"约束条件: 发现占位内容 — {constraint_placeholders}。"
                "请替换为具体约束。"
            )

        # ── 检查 4: 类似方案分析 ──
        pros_cons = solutions.get("pros_cons", [])
        approaches = solutions.get("existing_approaches", [])

        solution_placeholders = self._find_placeholders(solutions)
        if solution_placeholders:
            issues.append(
                f"方案分析: 发现占位内容 — {solution_placeholders}。"
                "请替换为具体的方案对比。"
            )

        if len(pros_cons) < 2:
            issues.append(
                f"方案分析: 仅 {len(pros_cons)} 个方案被对比（要求 ≥ 2）。"
                "请提供至少 2 个方案的对比分析。"
            )

        total_solution_words = sum(
            len(str(pc).split()) for pc in pros_cons
        ) + len(" ".join(str(a) for a in approaches).split())

        if total_solution_words < MIN_SOLUTIONS_WORDS:
            issues.append(
                f"方案分析: 内容不足 ({total_solution_words} 词，要求 ≥ {MIN_SOLUTIONS_WORDS})。"
                "每个方案必须包含具体的优缺点、适用场景。"
            )

        # ── 检查 5: 方案质量 ──
        for i, pc in enumerate(pros_cons):
            pro_list = pc.get("pros", [])
            con_list = pc.get("cons", [])
            approach = pc.get("approach", f"方案 {i+1}")

            if len(pro_list) < 2:
                issues.append(
                    f"方案分析: '{approach}' 优点不足 2 条。"
                    "请补充具体的优势分析。"
                )
            if len(con_list) < 2:
                issues.append(
                    f"方案分析: '{approach}' 缺点不足 2 条。"
                    "每个方案都必须分析其不足。"
                )

        passed = len(issues) == 0

        return {
            "passed": passed,
            "issues": issues,
            "checks": {
                "codebase_analysis": len(related_files) >= 3,
                "technical_research": (
                    technical_words >= MIN_TECHNICAL_WORDS
                    and not placeholder_found
                    and total_refs > 0
                ),
                "constraints_identified": (
                    constraints_words >= MIN_CONSTRAINTS_WORDS
                    and not self._find_placeholders(constraints)
                ),
                "similar_solutions_analyzed": (
                    len(pros_cons) >= 2
                    and total_solution_words >= MIN_SOLUTIONS_WORDS
                    and not self._find_placeholders(solutions)
                ),
            },
            "word_counts": {
                "technical": technical_words,
                "constraints": constraints_words,
                "solutions": total_solution_words,
            },
            "ref_count": total_refs,
        }

    def _check_placeholder_content(self, artifacts: dict, section: str) -> dict:
        """检查 artifacts 中是否有占位内容"""
        issues = []
        text = str(artifacts)

        found = []
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern in text:
                found.append(pattern)

        if found:
            issues.append(
                f"{section}: 发现 {len(found)} 个占位模式 — "
                f"{', '.join(found[:5])}。"
                "请替换为实际分析内容。"
            )

        return {
            "has_placeholders": len(found) > 0,
            "issues": issues,
            "found_patterns": found,
        }

    def _find_placeholders(self, data: dict) -> str:
        """在字典数据中查找占位文本"""
        text = str(data)
        found = []
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern in text:
                found.append(pattern)
        return ", ".join(found[:3]) if found else ""

    # ─────────────────────────────────────────────────────
    #  Research Report Generation
    # ─────────────────────────────────────────────────────

    def _generate_research_report(
        self,
        context: "ExecutionContext",
        codebase: Dict,
        technical: Dict,
        constraints: Dict,
        solutions: Dict,
        depth_check: Dict
    ) -> str:
        """生成研究报告 —— 研究清单模式，LLM 必须逐项回答"""
        feature_name = context.feature_name
        project_type = codebase.get('project_type', 'Unknown')
        scan_summary = codebase.get('scan_summary', '')
        all_files = codebase.get('all_source_files', [])
        related = codebase.get('related_files', [])
        modules = codebase.get('existing_modules', [])
        patterns = codebase.get('architecture_patterns', [])
        deps = codebase.get('dependencies', [])
        detected = constraints.get('detected_constraints', [])
        areas = technical.get('recommended_areas', [])

        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        def _status(cond): return "\u2705" if cond else "\u274c"
        dc = depth_check.get("checks", {})

        report = f"""# Understanding Report: {feature_name}

> \u26a0\ufe0f **此报告是进入 Phase 1 的前置条件。以下每个问题都必须用具体内容回答，不得留空或使用占位文本。**

**生成时间**: {now}
**项目类型**: {project_type}
**扫描摘要**: {scan_summary}

---

## \u2139\ufe0f 研究清单 — 逐项回答

**回答规范**:
- \U0001f539 每个回答必须 ≥ 50 字
- \U0001f539 禁止使用"需要研究""待分析""方案 A"等占位文本
- \U0001f539 技术引用必须包含 URL 或文档章节号
- \U0001f539 方案对比必须列出具体维度数据

---

## 1. 代码库分析 （{_status(dc.get('codebase_analysis', False))} 通过）

**已扫描到**: {len(all_files)} 个源文件, {len(modules)} 个模块, {len(related)} 个相关文件

**已识别的模块**:
"""
        for m in modules:
            report += f"- `{m}`\n"

        report += f"""
**已识别的相关文件**:
"""
        for f in related[:20]:
            report += f"- `{f}`\n"

        report += f"""
**架构模式**: {', '.join(patterns) if patterns else '待分析'}
**依赖配置**: {', '.join(deps) if deps else '未找到'}

### \u2753 必答问题:

> **Q1.1** 以上相关文件中，哪些会被本特性直接修改？每个文件的修改范围是什么？
>
> **Q1.2** 这些模块之间的依赖关系是怎样的？有循环依赖吗？
>
> **Q1.3** 有没有现成的接口/函数可以复用？列出它们的签名。
>
> **Q1.4** 哪些文件是"不能动"的核心基础设施？

```
（在此回答，删除本行）
```

---

## 2. 技术原理研究 （{_status(dc.get('technical_research', False))} 通过）

**建议研究方向**:
"""
        for area in areas:
            report += f"- {area}\n"

        report += f"""
**最低要求**: ≥ {MIN_TECHNICAL_WORDS} 词, ≥ 2 个外部引用（URL 或文档章节）

### \u2753 必答问题:

> **Q2.1** 本特性涉及的核心技术原理是什么？（具体说明，非"使用 X 框架"这种泛谈）
>
> **Q2.2** 这些技术在 {project_type} 生态中的最佳实践是什么？引用具体文档章节。
>
> **Q2.3** 有哪些常见的反模式或陷阱需要避免？
>
> **Q2.4** 引用的外部来源:

| 来源 URL / 文档章节 | 类型 | 与本特性的关系 |
|------|------|------|
| | | |

```
（在此回答，删除本行）
```

---

## 3. 约束条件分析 （{_status(dc.get('constraints_identified', False))} 通过）

**环境检测到的约束**:
"""
        for d in detected:
            report += f"- {d}\n"

        report += f"""
**最低要求**: ≥ {MIN_CONSTRAINTS_WORDS} 词, 覆盖 ≥ 3 个维度

### \u2753 必答问题:

> **Q3.1** 性能约束：延迟上限？吞吐量要求？内存/CPU 预算？
>
> **Q3.2** 安全约束：哪些输入需要验证？有无敏感数据？权限模型？
>
> **Q3.3** 兼容性约束：API 向后兼容？平台兼容？依赖版本？
>
> **Q3.4** 其他约束：文件大小、并发数、连接数、规范要求？

```
（在此回答，删除本行）
```

---

## 4. 方案对比 （{_status(dc.get('similar_solutions_analyzed', False))} 通过）

**最低要求**: ≥ {MIN_SOLUTIONS_WORDS} 词, ≥ 2 个方案, 每个方案 ≥ 3 条优缺点

### \u2753 必答问题:

> **Q4.1** 实现本特性至少有哪些不同的技术路径？描述每个方案的核心思路。
>
> **Q4.2** 方案对比表（必须有具体数据或评估）:

| 维度 | 方案 1: (名称) | 方案 2: (名称) | 方案 3: (名称，可选) |
|------|------|------|------|
| 实现复杂度 | | | |
| 性能影响 | | | |
| 维护成本 | | | |
| 测试难度 | | | |
| 与现有架构的契合度 | | | |
| 推荐场景 | | | |

> **Q4.3** 你为什么推荐某个方案？给出具体理由。
>
> **Q4.4** 被拒绝的方案为什么不行？

```
（在此回答，删除本行）
```

---

## 5. \u2705 深度自检

在提交研究报告前逐项确认:

- [ ] Q1.1-Q1.4 全部用具体内容回答（有空泛描述 = 不合格）
- [ ] Q2.1-Q2.4 引用了 ≥ 2 个外部来源（无 URL = 不合格）
- [ ] Q3.1-Q3.4 覆盖了 ≥ 3 个约束维度（只有 1-2 条 = 不合格）
- [ ] Q4.1-Q4.4 含 ≥ 2 个方案的详细对比（无具体优缺点 = 不合格）
- [ ] 全文无 "需要研究""待分析""方案 A" 等占位文本
- [ ] 全文 ≥ 400 词

**如果任何一项未勾选 \u2192 返回补充研究，不可进入 Phase 1。**

---
*研究清单生成: {now} | 深度分析驱动设计*
"""
        return report
