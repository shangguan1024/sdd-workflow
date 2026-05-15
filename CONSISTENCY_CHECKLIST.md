# Documentation Consistency Checklist (v2.2)

## Single Authority Principle

**SKILL.md = 唯一核心定义文件**

Other files must:
- Reference SKILL.md (not redefine)
- Extend details (not duplicate)
- Use consistent terminology

---

## Consistency Dimensions

### 1. Phase Numbering
- ✅ All files use **Phase 0-6** (7 phases)
- ✅ No "Phase 0-7" anywhere
- ✅ Phase sequence: 0 → 1 → 2 → 3 → 4 → 5 → 6

### 2. Gate Descriptions
- ✅ SKILL.md Phase 1 Gate: "Design + Decomposition Approved"
- ✅ SKILL.md Phase 5 Gate: "All 4 Artifacts Verified"
- ✅ phases-reference.md only references, not redefine

### 3. Document Paths
- ✅ All use `<feature>` format (template variable)
- ✅ No `{feature}` or `$feature` variants
- ✅ Path pattern: `docs/features/<feature>/`

### 4. Part Numbering
- ✅ SKILL.md: "Part 1.x-4.x"
- ✅ design-doc-template.md: uses Part 1.1, Part 2.1, Part 3.1
- ✅ No "Part 1-4" in references

### 5. No Duplicate Definitions
- ✅ Phase table: Only in SKILL.md (lines 35-43)
- ✅ phases-reference.md: references only
- ✅ Each concept defined in ONE file

### 6. Visualization Strategy
- ✅ All interaction diagrams use **PlantUML** (both architecture and module internal)
- ✅ Mermaid only for non-interaction diagrams (Flowchart, State Diagram)
- ✅ No Mermaid Sequence Diagram for interactions
- ✅ SKILL.md, design-doc-template.md, visualization-guide.md consistent

---

## Validation Commands

```bash
# Check Phase numbering
grep -r "Phase 0-7" . --include="*.md"
# Expected: No matches

# Check Gate descriptions
grep -r "Design Approved" SKILL.md
# Expected: "Design + Decomposition Approved"

grep -r "Review Artifacts Verified" SKILL.md
# Expected: "All 4 Artifacts Verified"

# Check doc paths
grep -r "{feature}" . --include="*.md"
# Expected: Only in git logs (history), not in current docs

# Check Part references
grep -r "Part 1-4" . --include="*.md"
# Expected: Only "Part 1.x-4.x" in SKILL.md

# Check visualization strategy
grep -r "Mermaid Sequence" . --include="*.md"
# Expected: No matches (all interaction diagrams use PlantUML)
```

---

## Last Convergence (2026-05-15)

**Fixed Issues:**
1. SKILL.md Gate descriptions unified
2. phases-reference.md duplicate table removed
3. README.md doc path format unified
4. SKILL.md Part reference corrected
5. Visualization strategy unified (PlantUML for all interactions)

**Commit:** 1be4895
**Status:** ✅ Convergence achieved