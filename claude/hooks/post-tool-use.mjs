#!/usr/bin/env node
// PostToolUse hook: 复刻 opencode 插件 tool.execute.after 的 context monitor。
// 对 Edit/Write 累加 edit 计数，达到阈值（20 edits 或单文件 >=5）时注入 context refresh。
// 对未初始化 sdd 的项目自动放行。
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs"
import { join, dirname } from "path"
import { fileURLToPath } from "url"

const __dirname = dirname(fileURLToPath(import.meta.url))

const EDITS_BETWEEN_REFRESH = 20
const SAME_FILE_WARNING = 5

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
    return { state: JSON.parse(readFileSync(stateFile, "utf-8")), stateFile }
  } catch {
    return null
  }
}

function saveState(state, stateFile) {
  try {
    mkdirSync(join(stateFile, ".."), { recursive: true })
    writeFileSync(stateFile, JSON.stringify(state, null, 2), "utf-8")
  } catch {}
}

function extractSection(content, markers, maxChars) {
  for (const marker of markers) {
    const idx = content.indexOf(marker)
    if (idx >= 0) {
      const nextIdx = content.indexOf("\n## ", idx + marker.length)
      const end = nextIdx < 0 ? Math.min(idx + maxChars, content.length) : Math.min(nextIdx, idx + maxChars)
      return content.slice(idx, end).trim()
    }
  }
  return ""
}

function generateRefresh(state, projectDir) {
  const sep = "=".repeat(60)
  const lines = []
  lines.push(`\n${sep}`)
  lines.push(`  CONTEXT REFRESH #${(state.refreshCount ?? 0) + 1}`)
  lines.push(`  Edits: ${state.editCount ?? 0} | Tasks: ${state.taskCount ?? 0}`)
  lines.push(sep)
  lines.push("")
  lines.push("## Feature Goal")
  lines.push(`Feature: ${state.featureName || "N/A"}`)

  const findingsFile = join(projectDir, "docs", "features", state.featureName || "", "findings.md")
  if (state.featureName && existsSync(findingsFile)) {
    lines.push("\n## Key Requirements & Constraints")
    const content = readFileSync(findingsFile, "utf-8")
    const section = extractSection(
      content,
      ["## Phase 0: Requirement Clarification", "## Requirement Clarification"],
      500
    )
    if (section) lines.push(section)
  }

  const hotFiles = Object.entries(state.perFileEdits ?? {})
    .filter(([, c]) => c >= SAME_FILE_WARNING)
    .sort(([, a], [, b]) => b - a)
  if (hotFiles.length > 0) {
    lines.push("\n## Hot Files")
    for (const [fp, count] of hotFiles) lines.push(`  - ${fp} (${count} edits)`)
  }

  lines.push("\n## Verify")
  lines.push("需求与设计决策是否仍一致？实现方向是否正确？")
  lines.push(sep)
  return lines.join("\n")
}

function main() {
  const input = readStdin()
  if (!input) process.exit(0)

  const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd()
  const loaded = loadState(projectDir)
  if (!loaded) process.exit(0) // 未初始化，放行

  const { state, stateFile } = loaded
  const toolName = (input.tool_name || "").toLowerCase()
  const toolInput = input.tool_input || {}

  // recordEdit（仅 edit/write）
  if (toolName === "edit" || toolName === "write") {
    const filePath = toolInput.file_path || toolInput.filePath || ""
    if (filePath) {
      state.editCount = (state.editCount ?? 0) + 1
      state.perFileEdits = state.perFileEdits ?? {}
      state.perFileEdits[filePath] = (state.perFileEdits[filePath] ?? 0) + 1
      saveState(state, stateFile)
    }
  }

  // shouldRefresh
  const editsSince = (state.editCount ?? 0) - (state.lastRefreshAtEdit ?? 0)
  let needRefresh = editsSince >= EDITS_BETWEEN_REFRESH
  if (!needRefresh) {
    for (const count of Object.values(state.perFileEdits ?? {})) {
      if (count >= SAME_FILE_WARNING) {
        needRefresh = true
        break
      }
    }
  }

  if (!needRefresh) process.exit(0)

  // markRefreshed + 注入 refresh 内容
  state.lastRefreshAtEdit = state.editCount ?? 0
  state.lastRefreshAtTask = state.taskCount ?? 0
  state.refreshCount = (state.refreshCount ?? 0) + 1
  state.refreshHistory = state.refreshHistory ?? []
  state.refreshHistory.push({
    atEdit: state.editCount ?? 0,
    atTask: state.taskCount ?? 0,
    time: new Date().toISOString(),
  })
  saveState(state, stateFile)

  const refreshText = generateRefresh(state, projectDir)
  process.stdout.write(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PostToolUse",
        additionalContext: refreshText,
      },
    })
  )
  process.exit(0)
}

main()
