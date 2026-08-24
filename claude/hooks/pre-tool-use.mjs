#!/usr/bin/env node
// PreToolUse hook: 复刻 opencode 插件 tool.execute.before 的 phase-gate 中间件。
// 强制 phase gate：Phase 0 阻塞 bash/edit，Phase 1 阻塞 bash，write 受路径限制，
// 并做 loop detection 与 artifact/compression 检查。
// 对未初始化 sdd 的项目（无 .sdd/state.json）自动放行，零副作用。
import { readFileSync, existsSync } from "fs"
import { join, dirname } from "path"
import { fileURLToPath } from "url"

const __dirname = dirname(fileURLToPath(import.meta.url))

const BLOCKED_TOOLS_BY_PHASE = {
  0: ["bash", "edit"],
  1: ["bash"],
  2: [],
  3: [],
  4: [],
  5: [],
  6: [],
}

const DEFAULT_ALLOWED_PATHS = {
  0: ["docs/features/{feature}/"],
  1: ["docs/features/{feature}/"],
  2: ["docs/features/{feature}/"],
  3: [],
  4: [],
  5: ["docs/features/{feature}/reviews/"],
  6: [],
}

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

const PHASE_SUMMARY_MAP = {
  0: { file: "findings.md", marker: "## Phase 0: Requirement Clarification" },
  1: { file: "findings.md", marker: "## Phase 1: Design Summary" },
  2: { file: "findings.md", marker: "## Phase 2: Plan Summary" },
  3: { file: "findings.md", marker: "## Phase 3: Implementation Summary" },
  4: { file: "findings.md", marker: "## Phase 4: Test Summary" },
  5: { file: "findings.md", marker: "## Phase 5: Review Summary" },
}

const ALT_MARKERS = {
  "## Phase 0: Requirement Clarification": ["## Phase 0", "## Requirement Clarification"],
  "## Phase 1: Design Summary": ["## Phase 1", "## Design"],
  "## Phase 2: Plan Summary": ["## Phase 2", "## Plan"],
  "## Phase 3: Implementation Summary": ["## Phase 3", "## Implementation"],
  "## Phase 4: Test Summary": ["## Phase 4", "## Test"],
  "## Phase 5: Review Summary": ["## Phase 5", "## Review"],
}

function readStdin() {
  try {
    const raw = readFileSync(0, "utf-8")
    return raw.trim() ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function deny(reason) {
  process.stdout.write(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: reason,
      },
    })
  )
  process.exit(0)
}

function allow(additionalContext) {
  if (additionalContext) {
    process.stdout.write(
      JSON.stringify({
        hookSpecificOutput: {
          hookEventName: "PreToolUse",
          permissionDecision: "allow",
          additionalContext,
        },
      })
    )
  }
  process.exit(0)
}

function getAllowedPaths(phase, projectDir) {
  const configFile = join(projectDir, ".sdd", "workflow_config.json")
  if (existsSync(configFile)) {
    try {
      const config = JSON.parse(readFileSync(configFile, "utf-8"))
      const p = (config.phases ?? []).find((x) => x.id === phase)
      if (p && Array.isArray(p.allowed_tools_paths)) {
        return p.allowed_tools_paths
      }
    } catch {}
  }
  return DEFAULT_ALLOWED_PATHS[phase] ?? []
}

function isPathAllowed(targetPath, allowedPaths, featureName) {
  const normalized = targetPath.replace(/\\/g, "/")
  for (const pattern of allowedPaths) {
    if (normalized.includes(pattern.replace("{feature}", featureName))) {
      return true
    }
  }
  return false
}

function checkCompression(phase, featureName, projectDir) {
  if (phase <= 0 || !featureName) return null
  const spec = PHASE_SUMMARY_MAP[phase - 1]
  if (!spec) return null

  const targetFile = join(projectDir, "docs", "features", featureName, spec.file)
  if (!existsSync(targetFile)) {
    return `Phase ${phase - 1} 边界压缩未完成：缺少 ${spec.file} 中的 ${spec.marker} 小节。`
  }
  const content = readFileSync(targetFile, "utf-8")
  const lower = content.toLowerCase()
  if (!lower.includes(spec.marker.toLowerCase())) {
    const alts = ALT_MARKERS[spec.marker] ?? [spec.marker]
    const found = alts.some((alt) => lower.includes(alt.toLowerCase()))
    if (!found) {
      return `${spec.file} 中缺少 '${spec.marker}'。请先生成结构化 summary。`
    }
  }
  return null
}

function checkArtifacts(phase, featureName, projectDir) {
  if (phase === 5 || phase === 6) {
    const reviewArtifacts = [
      `docs/features/${featureName}/reviews/architecture_review.md`,
      `docs/features/${featureName}/reviews/code_quality_review.md`,
    ]
    const missing = reviewArtifacts.filter((p) => !existsSync(join(projectDir, p)))
    if (missing.length > 0) {
      return `缺少 ${missing.length} 个 review 工件：${missing.join(", ")}`
    }
  }
  if (phase === 6) {
    const missing = ["PROJECT_STATE.md", "AGENTS.md"].filter(
      (a) => !existsSync(join(projectDir, a))
    )
    if (missing.length > 0) {
      return `缺少 memory 工件：${missing.join(", ")}`
    }
  }
  return null
}

function main() {
  const input = readStdin()
  if (!input) process.exit(0)

  const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd()
  const stateFile = join(projectDir, ".sdd", "state.json")
  if (!existsSync(stateFile)) process.exit(0) // 未初始化，放行

  let state
  try {
    state = JSON.parse(readFileSync(stateFile, "utf-8"))
  } catch {
    process.exit(0)
  }

  const phase = state.currentPhase ?? 0
  if (phase >= 7) process.exit(0) // COMPLETED，放行
  // 未 start feature（featureName 空）时放行：init 后尚未开发的僵尸状态，不应锁死工具
  if (phase === 0 && !state.featureName) process.exit(0)

  const toolName = (input.tool_name || "").toLowerCase()
  const toolInput = input.tool_input || {}
  const featureName = state.featureName || ""

  // 1) phase gate：工具阻塞
  const blockedTools = BLOCKED_TOOLS_BY_PHASE[phase] ?? []
  if (blockedTools.includes(toolName)) {
    deny(
      `Phase ${phase}（${PHASE_NAMES[phase]}）：不允许使用 ${toolName}。必须先完成当前 phase 的 gate 检查。`
    )
  }

  // 2) write 路径限制
  if (toolName === "write") {
    const targetPath = toolInput.file_path || toolInput.filePath || ""
    const allowedPaths = getAllowedPaths(phase, projectDir)
    if (allowedPaths.length > 0 && !isPathAllowed(targetPath, allowedPaths, featureName)) {
      deny(
        `Phase ${phase}：不允许写入 '${targetPath}'。仅允许写入: ${allowedPaths.join(", ")}`
      )
    }
  }

  // 3) phase compression（进入 phase >=1 前，findings.md 需有上一 phase 的 summary）
  const compressionMsg = checkCompression(phase, featureName, projectDir)
  if (compressionMsg) deny(compressionMsg)

  // 4) artifact 检查（Phase 5/6 需 review / memory 工件）
  const artifactMsg = checkArtifacts(phase, featureName, projectDir)
  if (artifactMsg) deny(artifactMsg)

  // 5) loop detection（edit/write）
  if (toolName === "edit" || toolName === "write") {
    const filePath = toolInput.file_path || toolInput.filePath || ""
    if (filePath) {
      const count = state.perFileEdits?.[filePath] ?? 0
      if (count >= 15) {
        deny(`硬限制：${filePath} 已编辑 ${count} 次，上下文可能已偏离原始需求。`)
      }
      if (count >= 5) {
        allow(`警告：${filePath} 已编辑 ${count} 次，请确认实现方向是否仍正确。`)
      }
    }
  }

  allow()
}

main()
