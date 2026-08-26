# SDD-Workflow Installation Guide (Agent-Readable)

> Read and executed by an AI agent. The agent asks the user to confirm destructive steps.

## 快速开始（推荐：install.ps1 一键部署）

`install.ps1` 同时支持 Claude Code 与 opencode。先获取它（二选一）：

**方式 A：只下载脚本（不 clone 仓库）**
```powershell
Invoke-WebRequest https://raw.githubusercontent.com/shangguan1024/sdd-workflow/main/install.ps1 -OutFile install.ps1
```

**方式 B：clone 整个 skill 仓库**
```powershell
git clone https://github.com/shangguan1024/sdd-workflow.git
cd sdd-workflow
```

然后运行（脚本会自动 clone 引擎仓库到 InstallRoot）：
```powershell
.\install.ps1 -Target both     -InstallRoot D:\sdd-workflow   # 两个都装（默认）
.\install.ps1 -Target claude   -InstallRoot D:\sdd-workflow   # 只装 Claude Code
.\install.ps1 -Target opencode -InstallRoot D:\sdd-workflow   # 只装 opencode
.\install.ps1 -Target claude   -SkipSubskills                 # 离线验证（跳过子技能下载）
```

脚本自动完成：clone 两个 repo → 构建引擎 → 按平台接线（opencode.json `plugin` / Claude Code `settings.json` hooks）→ 安装子技能。核心引擎 `dist/` 与子技能（`~/.agents/skills/`）被两个平台共享。

> 以下手动步骤供逐条执行（不依赖 install.ps1）或排查用。

## What this installs

### Core components (cloned into `$INSTALL_ROOT`)

| Component | Repo | Location |
|-----------|------|----------|
| Plugin | https://github.com/shangguan1024/sdd-workflow-plugin.git | `$INSTALL_ROOT/sdd-workflow-plugin/` |
| Skill  | https://github.com/shangguan1024/sdd-workflow.git          | `$INSTALL_ROOT/sdd-workflow-skill/`  |

### Dependency skills (9, installed to `~/.agents/skills/` via `npx skills add`)

**Primary (one per phase):**

| Skill | Phase | Source repo |
|-------|-------|-------------|
| `comprehensive-research-agent` | 0 | `muratcankoylan/agent-skills-for-context-engineering` |
| `brainstorming` | 1 | `obra/superpowers` |
| `writing-plans` | 2 | `obra/superpowers` |
| `subagent-driven-development` | 3 | `obra/superpowers` |
| `verification-before-completion` | 4 | `obra/superpowers` |
| `requesting-code-review` | 5 | `obra/superpowers` |
| `memory-systems` | 6 | `muratcankoylan/agent-skills-for-context-engineering` |

**Additional:**

| Skill | Phase | Source repo |
|-------|-------|-------------|
| `code-review-quality` | 3 | `proffesor-for-testing/agentic-qe` |
| `receiving-code-review` | 5 | `obra/superpowers` |

**After install:** SDD skill is junctioned into `~/.config/opencode/skills/sdd-workflow` (auto-discovered); plugin is registered in `opencode.json` (config-driven); 9 dependency skills land in `~/.agents/skills/<name>/` (auto-discovered).

---

## Step 0 — Resolve variables (ASK USER)

| Variable | Suggested | Required |
|----------|-----------|----------|
| `INSTALL_ROOT` | Windows: `D:\sdd-workflow` ; Linux/macOS: `~/sdd-workflow` | YES — ask user to confirm or override |

Auto-detected: `OPENCODE_DIR` = `~/.config/opencode`, `PLATFORM` = `windows` / `linux`.

If `INSTALL_ROOT` exists and is non-empty, ask user: (a) reuse, (b) overwrite, (c) pick another path.

## Step 1 — Pre-flight

```bash
git --version
npm --version
```

Abort if either fails.

## Step 2 — Clone both repos

```bash
git clone https://github.com/shangguan1024/sdd-workflow-plugin.git "$INSTALL_ROOT/sdd-workflow-plugin"
git clone https://github.com/shangguan1024/sdd-workflow.git          "$INSTALL_ROOT/sdd-workflow-skill"
```

If target exists and is a git repo → `git -C <dir> pull` instead of reclone.

## Step 3 — Build the plugin

```bash
cd "$INSTALL_ROOT/sdd-workflow-plugin"
npm install --no-audit --no-fund
npm run build
```

Verify `dist/index.js` exists; abort if missing.

## Step 4 — Skill symlink

Target: `~/.config/opencode/skills/sdd-workflow` → `$INSTALL_ROOT/sdd-workflow-skill`

### 4a. Ensure parent + handle existing target

```powershell
# Windows
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.config\opencode\skills" | Out-Null
$target = "$env:USERPROFILE\.config\opencode\skills\sdd-workflow"
if (Test-Path -LiteralPath $target) {
    $item = Get-Item -LiteralPath $target
    if ($item.LinkType) {
        $item.Delete()                                  # junction/symlink: delete link only
    } else {
        # real folder — ASK USER "delete and continue? (y/n)"
        # if y: Remove-Item -LiteralPath $target -Recurse -Force
        # if n: abort
    }
}
```
```bash
# Linux/macOS
mkdir -p "$HOME/.config/opencode/skills"
target="$HOME/.config/opencode/skills/sdd-workflow"
[ -L "$target" ] && rm -f "$target"
if [ -d "$target" ]; then
    # real folder — ASK USER "delete and continue? (y/n)"
    # if y: rm -rf "$target"
    # if n: abort
fi
```

### 4b. Create the link

```powershell
# Windows — junction (/J) does NOT require admin
cmd /c mklink /J "$env:USERPROFILE\.config\opencode\skills\sdd-workflow" "$INSTALL_ROOT\sdd-workflow-skill"
```
```bash
# Linux/macOS — symlink
ln -sfn "$INSTALL_ROOT/sdd-workflow-skill" "$HOME/.config/opencode/skills/sdd-workflow"
```

### 4c. Verify

```powershell
Test-Path "$env:USERPROFILE\.config\opencode\skills\sdd-workflow\SKILL.md"
```
```bash
test -f "$HOME/.config/opencode/skills/sdd-workflow/SKILL.md"
```

## Step 5 — Register plugin in `opencode.json`

Plugin entry value: `$INSTALL_ROOT/sdd-workflow-plugin/dist/index.js` (use forward slashes in JSON even on Windows).

### 5a. Merge plugin array (tolerates JSONC trailing commas on input, writes strict JSON)

```powershell
# Windows
$jsonPath = "$env:USERPROFILE\.config\opencode\opencode.json"
if (-not (Test-Path -LiteralPath $jsonPath)) {
    '{"$schema":"https://opencode.ai/config.json"}' | Out-File -FilePath $jsonPath -Encoding utf8
}
$raw    = Get-Content -LiteralPath $jsonPath -Raw
$config = ($raw -replace ',\s*(?=[}\]])', '') | ConvertFrom-Json
$pluginEntry = "$INSTALL_ROOT/sdd-workflow-plugin/dist/index.js" -replace '\\','/'
$config | Add-Member -NotePropertyName plugin -NotePropertyValue @($pluginEntry) -Force
$out = $config | ConvertTo-Json -Depth 20
[System.IO.File]::WriteAllText($jsonPath, $out + "`n", (New-Object System.Text.UTF8Encoding($false)))
```
```bash
# Linux/macOS (jq; fallback: python3 -c "import json,pathlib; ...")
jq --arg p "$INSTALL_ROOT/sdd-workflow-plugin/dist/index.js" '.plugin = [$p]' \
   "$HOME/.config/opencode/opencode.json" > tmp && mv tmp "$HOME/.config/opencode/opencode.json"
```

### 5b. Do NOT add `skills.paths` — the Step 4 symlink already auto-discovers the skill.

### 5c. If `opencode.jsonc` exists alongside `opencode.json`

ASK USER "delete `opencode.jsonc` so `opencode.json` is the single source of truth? (y/n)". If `y`, delete directly (no backup). If `n`, abort.

```powershell
# Windows
Remove-Item -LiteralPath "$env:USERPROFILE\.config\opencode\opencode.jsonc" -Force
```
```bash
# Linux/macOS
rm -f "$HOME/.config/opencode/opencode.jsonc"
```

## Step 6 — Install 9 dependency skills

```bash
# Primary skills (one per phase)
npx skills add https://github.com/muratcankoylan/agent-skills-for-context-engineering --skill comprehensive-research-agent
npx skills add https://github.com/obra/superpowers --skill brainstorming
npx skills add https://github.com/obra/superpowers --skill writing-plans
npx skills add https://github.com/obra/superpowers --skill subagent-driven-development
npx skills add https://github.com/obra/superpowers --skill verification-before-completion
npx skills add https://github.com/obra/superpowers --skill requesting-code-review
npx skills add https://github.com/muratcankoylan/agent-skills-for-context-engineering --skill memory-systems

# Additional skills
npx skills add https://github.com/proffesor-for-testing/agentic-qe --skill code-review-quality
npx skills add https://github.com/obra/superpowers --skill receiving-code-review
```

Verify each lands in `~/.agents/skills/<name>/`. For installing any other skill later, see `npx skills --help` or <https://www.skills.sh/docs>.

## Step 7 — Final verification

```powershell
# Windows
Test-Path "$INSTALL_ROOT\sdd-workflow-plugin\dist\index.js"
Test-Path "$env:USERPROFILE\.config\opencode\skills\sdd-workflow\SKILL.md"
(Get-Content "$env:USERPROFILE\.config\opencode\opencode.json" -Raw) -match 'sdd-workflow-plugin/dist/index.js'
```
```bash
# Linux/macOS
test -f "$INSTALL_ROOT/sdd-workflow-plugin/dist/index.js"
test -f "$HOME/.config/opencode/skills/sdd-workflow/SKILL.md"
grep -q 'sdd-workflow-plugin/dist/index.js' "$HOME/.config/opencode/opencode.json"
```

## Step 8 — Tell user to restart opencode

The agent CANNOT restart opencode itself (would kill the agent's own process). Instruct user:

```
Install complete. Restart opencode to load:

    quit
    opencode

Verify after restart:
    sdd_status
    sdd_init template=standard
    sdd_start feature=<your-feature-name>
```

---

## Claude Code 部署（手动参考）

对应 `install.ps1 -Target claude` 的 claude 分支。核心引擎与子技能与 opencode 共享（上面的 Step 2/3/6 已就绪）。

### C1. 复制外壳到 `~/.claude/skills/sdd-workflow/`

```powershell
$src = "$INSTALL_ROOT\sdd-workflow"   # skill repo
$dst = "$env:USERPROFILE\.claude\skills\sdd-workflow"
New-Item -ItemType Directory -Force -Path $dst | Out-Null
Copy-Item "$src\claude\SKILL.claude.md" "$dst\SKILL.md" -Force
Copy-Item "$src\claude\phases-reference.md" "$dst\phases-reference.md" -Force
Copy-Item "$src\claude\USAGE.md" "$dst\USAGE.md" -Force
Copy-Item "$src\claude\hooks" "$dst\hooks" -Recurse -Force
Copy-Item "$src\design-doc-template.md","$src\interface-example.md","$src\dependency-example.md","$src\visualization-guide.md" "$dst" -Force
Copy-Item "$src\templates" "$dst\templates" -Recurse -Force
```

### C2. Junction 引擎（与 opencode 共享）

```powershell
cmd /c mklink /J "$dst\engine" "$INSTALL_ROOT\sdd-workflow-plugin"
```

### C3. 替换占位符

把 `$dst` 下 `SKILL.md`、`phases-reference.md`、`USAGE.md`、`hooks\*.mjs` 里的 `__SDD_CLAUDE_DIR__` 替换为 `$dst`（正斜杠）。

### C4. Merge hooks 进 `~/.claude/settings.json`

读 `claude\settings.hooks.json`（替换占位符后），把其三组 hook（PreToolUse/PostToolUse/UserPromptSubmit）合并进 `~/.claude/settings.json` 的 `hooks` 键（保留其他键）。

### C5. Junction 子技能到 `~/.claude/skills/`

对 8 个顶层子技能（brainstorming、writing-plans、subagent-driven-development、verification-before-completion、requesting-code-review、code-review-quality、systematic-debugging、test-driven-development）：

```powershell
cmd /c mklink /J "$env:USERPROFILE\.claude\skills\brainstorming" "$env:USERPROFILE\.agents\skills\brainstorming"
# ... 其余同理
```

`comprehensive-research-agent`、`memory-systems` 若为嵌套安装（在 `context-engineering-collection` 内），需从嵌套路径单独 junction 或单独 `npx skills add` 到顶层。

### C6. 重启 Claude Code

Hooks 需会话启动时加载；重启后在新会话验证：`/sdd-workflow` 或说「用 SDD 开发某功能」。

---

## Rollback

1. Delete skill junction/symlink (NOT the target dir):
   - Windows: `(Get-Item "$env:USERPROFILE\.config\opencode\skills\sdd-workflow").Delete()`
   - Linux/macOS: `rm -f "$HOME/.config/opencode/skills/sdd-workflow"`
2. Remove `plugin` entry from `opencode.json`
3. Optionally `npx skills remove <name>` for each of the 9 dependency skills — **ask user first** (shared across workflows)
4. Optionally delete `$INSTALL_ROOT`

## Update

```bash
# Plugin (rebuild after pull)
git -C "$INSTALL_ROOT/sdd-workflow-plugin" pull
cd "$INSTALL_ROOT/sdd-workflow-plugin" && npm install --no-audit --no-fund && npm run build

# Skill (no build needed)
git -C "$INSTALL_ROOT/sdd-workflow-skill" pull

# All 9 dependency skills
npx skills update
```

Restart opencode after.

---

## File affected summary

| Path | Action |
|------|--------|
| `$INSTALL_ROOT/sdd-workflow-plugin/` | `git clone` + `npm install` (adds `node_modules/`) + `npm run build` (adds `dist/`) |
| `$INSTALL_ROOT/sdd-workflow-skill/` | `git clone` |
| `~/.config/opencode/skills/sdd-workflow` | Junction/symlink to `$INSTALL_ROOT/sdd-workflow-skill`. If a real folder previously occupied this path, deleted only after user confirms (Step 4a) |
| `~/.config/opencode/opencode.json` | `plugin` array set/overwritten. Other keys (`provider`, `$schema`, ...) preserved |
| `~/.config/opencode/opencode.jsonc` | Deleted if existed and user confirmed in Step 5c. No backup |
| `~/.agents/skills/<name>/` (×9) | Created by `npx skills add` for each dependency skill |
| `~/.agents/packages/<owner>/<repo>/` (×3) | Source repo cache, shared across skills from same repo |
| `~/.agents/.skill-lock.json` | Updated by `npx skills add` to track installed skills |

No other files touched. No backups created. No git commits. No global npm packages installed.
