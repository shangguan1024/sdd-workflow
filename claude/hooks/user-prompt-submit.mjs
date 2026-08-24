#!/usr/bin/env node
// UserPromptSubmit hook: 复刻 opencode 插件 experimental.chat.system.transform 的
// phase prompt 注入。每次用户提交 prompt 时，注入当前 SDD phase 的骨架、技能指令与
// 上下文文件提示。对未初始化 sdd 的项目自动放行。
import { readFileSync, existsSync } from "fs"
import { join, dirname } from "path"
import { fileURLToPath } from "url"

const __dirname = dirname(fileURLToPath(import.meta.url))
const SKILL_ROOT = join(__dirname, "..")
const ALL_SKILLS_DIR = join(__dirname, "..", "..") // ~/.claude/skills
const ENGINE_BIN = join(SKILL_ROOT, "engine", "bin", "sdd.js")

const PHASE_NAMES = {
  0: "Research & Requirement Clarification",
  1: "Requirements & Design",
  2: "Implementation Planning",
  3: "Module Development",
  4: "Integration & Testing",
  5: "Code Quality Review",
  6: "Memory Persistence",
  7: "Completed",
}

const DEFAULT_SKILLS = {
  0: ["comprehensive-research-agent"],
  1: ["brainstorming"],
  2: ["writing-plans"],
  3: ["subagent-driven-development"],
  4: ["verification-before-completion"],
  5: ["requesting-code-review"],
  6: ["memory-systems"],
}

const DEFAULT_ADDITIONAL = {
  3: ["code-review-quality"],
  5: ["code-review-quality"],
}

const SKILL_DESCRIPTIONS = {
  "comprehensive-research-agent": "研究 + 需求澄清（向用户提问 feature 概览、需求规格、性能、核心模块）",
  brainstorming: "实现前的设计探索、需求细化",
  "writing-plans": "任务分解、写实施计划",
  "subagent-driven-development": "并行子代理开发",
  "verification-before-completion": "完成前强制验证",
  "requesting-code-review": "请求代码评审",
  "memory-systems": "跨会话记忆持久化",
  "code-review-quality": "上下文驱动的代码质量评审",
}

function readStdin() {
  try {
    const raw = readFileSync(0, "utf-8")
    return raw.trim() ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function loadState(projectDir) {
  const stateFile = join(projectDir, ".sdd", "state.json")
  if (!existsSync(stateFile)) return null
  try {
    return JSON.parse(readFileSync(stateFile, "utf-8"))
  } catch {
    return null
  }
}

function loadPhaseConfig(projectDir, phase) {
  const configFile = join(projectDir, ".sdd", "workflow_config.json")
  if (!existsSync(configFile)) return null
  try {
    const config = JSON.parse(readFileSync(configFile, "utf-8"))
    return (config.phases ?? []).find((p) => p.id === phase) ?? null
  } catch {
    return null
  }
}

function skillExists(name) {
  return existsSync(join(ALL_SKILLS_DIR, name, "SKILL.md"))
}

function getSkills(phase, projectDir) {
  const userPhase = loadPhaseConfig(projectDir, phase)
  if (userPhase && Array.isArray(userPhase.skills) && userPhase.skills.length > 0) {
    return { primary: userPhase.skills, additional: userPhase.additional_skills ?? [] }
  }
  return {
    primary: DEFAULT_SKILLS[phase] ?? [],
    additional: (userPhase && Array.isArray(userPhase.additional_skills) && userPhase.additional_skills.length > 0)
      ? userPhase.additional_skills
      : (DEFAULT_ADDITIONAL[phase] ?? []),
  }
}

function buildSkillInstruction(phase, projectDir) {
  const { primary, additional } = getSkills(phase, projectDir)
  const lines = []

  lines.push(`## SDD-Workflow 指令（Phase ${phase}: ${PHASE_NAMES[phase]}）`)
  lines.push("")
  lines.push(`Step 1: 用 Read 工具读取 skill 文档，了解本 phase 的任务/Gate/产出：`)
  lines.push(`  ${join(SKILL_ROOT, "phases-reference.md")}`)
  lines.push("")
  lines.push("Step 2: 调用本 phase 的主技能（如可用）：")
  for (const name of primary) {
    if (skillExists(name)) {
      lines.push(`  → 使用 "${name}" 技能（${SKILL_DESCRIPTIONS[name] ?? "自定义技能"}）`)
    } else {
      lines.push(`  → 技能 "${name}" 未安装，按 phases-reference.md 的 Phase ${phase} 内置步骤执行`)
    }
  }
  lines.push("")
  if (additional.length > 0) {
    lines.push("Step 3: 附加技能（先询问用户是否需要调用）：")
    for (const name of additional) {
      lines.push(`  - ${name}${skillExists(name) ? "" : "（未安装）"}`)
    }
    lines.push("")
  }
  lines.push(`Step 4: 执行 Phase ${phase} 任务（按 phases-reference.md 指导）。`)
  lines.push("")
  lines.push("Step 5: Gate 检查：")
  lines.push(`  node "${ENGINE_BIN}" gate ${phase + 1} check`)
  lines.push(`  node "${ENGINE_BIN}" gate ${phase + 1} approve` + (phase < 7 ? `   # 用户确认后追加 --confirmed true` : ""))
  return lines.join("\n")
}

function buildFileHints(projectDir, featureName) {
  const files = []
  if (existsSync(join(projectDir, "AGENTS.md"))) files.push("- AGENTS.md")
  if (featureName) {
    const featureDir = join(projectDir, "docs", "features", featureName)
    for (const f of ["findings.md", "task_plan.md", "design.md"]) {
      if (existsSync(join(featureDir, f))) files.push(`- docs/features/${featureName}/${f}`)
    }
  }
  if (existsSync(join(projectDir, "CONSTITUTION", "core.md"))) files.push("- CONSTITUTION/core.md")
  if (files.length === 0) return ""
  return `\nContext files（需要时用 Read 读取，不要全量注入）:\n${files.join("\n")}`
}

function main() {
  const input = readStdin()
  if (!input) process.exit(0)

  const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd()
  const state = loadState(projectDir)
  if (!state) process.exit(0) // 未初始化，放行

  const phase = state.currentPhase ?? 0
  if (phase === 0 && !state.featureName) {
    // 已 init 但未 start feature：不注入（避免干扰 init 流程）
    process.exit(0)
  }
  if (phase >= 7) process.exit(0) // COMPLETED

  const skeleton = `## SDD-Workflow (Phase ${phase}: ${PHASE_NAMES[phase]})\n**Current Feature**: ${state.featureName || "Not set"}`
  const instruction = buildSkillInstruction(phase, projectDir)
  const fileHints = buildFileHints(projectDir, state.featureName)

  const text = [skeleton, instruction, fileHints].filter(Boolean).join("\n\n")

  process.stdout.write(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "UserPromptSubmit",
        additionalContext: text,
      },
    })
  )
  process.exit(0)
}

main()
