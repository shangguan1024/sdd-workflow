#Requires -Version 5.1
<#
.SYNOPSIS
  Install sdd-workflow for Claude Code and/or opencode on a new machine.

.DESCRIPTION
  Clones the two source repos (plugin engine + skill), builds the engine,
  and wires up the requested platform(s):

    opencode : junction skill into ~/.config/opencode/skills/sdd-workflow
               + register plugin in ~/.config/opencode/opencode.json
    claude   : copy claude/ shell into ~/.claude/skills/sdd-workflow
               + junction engine + merge hooks into ~/.claude/settings.json

  Sub-skills are shared by both platforms via ~/.agents/skills/ (npx skills add).

.PARAMETER Target
  One of: claude, opencode, both (default both).

.PARAMETER InstallRoot
  Directory where the two git repos are cloned. Default: D:\sdd-workflow.

.PARAMETER SkipSubskills
  Skip installing/junctioning the dependency sub-skills (useful for offline
  verification). Default: false.
#>
param(
  [ValidateSet("claude", "opencode", "both")]
  [string]$Target = "both",

  [string]$InstallRoot = "D:\sdd-workflow",

  [switch]$SkipSubskills,

  [switch]$SkipFetch
)

$ErrorActionPreference = "Stop"

$PLUGIN_REPO = "https://github.com/shangguan1024/sdd-workflow-plugin.git"
$SKILL_REPO  = "https://github.com/shangguan1024/sdd-workflow.git"

$pluginDir = Join-Path $InstallRoot "sdd-workflow-plugin"
$skillDir  = Join-Path $InstallRoot "sdd-workflow"

# ---- helper functions -------------------------------------------------------

function Test-Command([string]$Name) {
  return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Write-Step([string]$Msg) {
  Write-Host "==> $Msg" -ForegroundColor Cyan
}

function Write-Ok([string]$Msg) {
  Write-Host "    [OK] $Msg" -ForegroundColor Green
}

function Write-Warn([string]$Msg) {
  Write-Host "    [WARN] $Msg" -ForegroundColor Yellow
}

function Ensure-Dir([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
  }
}

function New-Junction([string]$Link, [string]$Target) {
  if (Test-Path -LiteralPath $Link) {
    Write-Ok "junction exists: $Link"
    return
  }
  Ensure-Dir (Split-Path -Parent $Link)
  cmd /c mklink /J "$Link" "$Target" | Out-Null
  if (Test-Path -LiteralPath $Link) {
    Write-Ok "junction: $Link -> $Target"
  } else {
    throw "Failed to create junction: $Link"
  }
}

function Read-JsonFile([string]$Path, $Default) {
  if (-not (Test-Path -LiteralPath $Path)) { return $Default }
  $raw = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
  # strip trailing commas (tolerate JSONC)
  $raw = $raw -replace ',\s*(?=[}\]])', ''
  try { return ($raw | ConvertFrom-Json) } catch { return $Default }
}

function Write-JsonFile([string]$Path, $Object) {
  Ensure-Dir (Split-Path -Parent $Path)
  $json = $Object | ConvertTo-Json -Depth 50
  [System.IO.File]::WriteAllText($Path, $json + "`n", (New-Object System.Text.UTF8Encoding($false)))
}

function Clone-Or-Pull([string]$RepoUrl, [string]$Dest) {
  if (Test-Path -LiteralPath (Join-Path $Dest ".git")) {
    Write-Ok "pull existing repo: $Dest"
    git -C $Dest pull --ff-only 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Warn "pull failed (continuing with existing copy): $Dest" }
  } else {
    Write-Ok "clone: $RepoUrl"
    git clone $RepoUrl $Dest
    if ($LASTEXITCODE -ne 0) { throw "git clone failed: $RepoUrl" }
  }
}

# ---- 1. pre-flight ----------------------------------------------------------

Write-Step "Pre-flight checks"
foreach ($cmd in @("git", "node", "npm")) {
  if (-not (Test-Command $cmd)) { throw "Missing required command: $cmd" }
}
Write-Ok "git/node/npm present"

# ---- 2. clone repos ---------------------------------------------------------

if ($SkipFetch) {
  Write-Step "Skipping fetch (assuming repos already present)"
} else {
  Write-Step "Fetching source repos into $InstallRoot"
  Ensure-Dir $InstallRoot
  Clone-Or-Pull $PLUGIN_REPO $pluginDir
  Clone-Or-Pull $SKILL_REPO $skillDir
}

# ---- 3. build engine --------------------------------------------------------

$pluginEntry = Join-Path $pluginDir "dist\index.js"
if (Test-Path -LiteralPath $pluginEntry) {
  Write-Ok "engine already built: $pluginEntry"
} elseif ($SkipFetch) {
  throw "SkipFetch set but engine not built: $pluginEntry"
} else {
  Write-Step "Building engine ($pluginDir)"
  Push-Location $pluginDir
  try {
    npm install --no-audit --no-fund | Out-Null
    npm run build | Out-Null
  } finally {
    Pop-Location
  }
  if (-not (Test-Path -LiteralPath $pluginEntry)) {
    throw "Engine build failed: $pluginEntry missing"
  }
  Write-Ok "engine built: $pluginEntry"
}

# ---- 4. opencode ------------------------------------------------------------

if ($Target -in @("opencode", "both")) {
  Write-Step "Install opencode"

  $ocSkillsDir = Join-Path $env:USERPROFILE ".config\opencode\skills"
  $ocSkillLink = Join-Path $ocSkillsDir "sdd-workflow"
  New-Junction $ocSkillLink $skillDir

  $ocJson = Join-Path $env:USERPROFILE ".config\opencode\opencode.json"
  $config = Read-JsonFile $ocJson @{}
  $pluginForward = ($pluginEntry -replace '\\', '/')
  $config | Add-Member -NotePropertyName plugin -NotePropertyValue @($pluginForward) -Force
  Write-JsonFile $ocJson $config
  Write-Ok "opencode.json plugin -> $pluginForward"
}

# ---- 5. claude --------------------------------------------------------------

if ($Target -in @("claude", "both")) {
  Write-Step "Install Claude Code"

  $claudeSkillDir = Join-Path $env:USERPROFILE ".claude\skills\sdd-workflow"
  $claudeForward = ($claudeSkillDir -replace '\\', '/')

  # 5a. copy claude shell + shared docs
  if (Test-Path -LiteralPath $claudeSkillDir) {
    Write-Warn "claude skill dir exists; overwriting shell files"
  }
  Ensure-Dir $claudeSkillDir

  $claudeShell = Join-Path $skillDir "claude"
  Copy-Item (Join-Path $claudeShell "SKILL.claude.md") (Join-Path $claudeSkillDir "SKILL.md") -Force
  Copy-Item (Join-Path $claudeShell "phases-reference.md") (Join-Path $claudeSkillDir "phases-reference.md") -Force
  Copy-Item (Join-Path $claudeShell "USAGE.md") (Join-Path $claudeSkillDir "USAGE.md") -Force
  Copy-Item (Join-Path $claudeShell "hooks") (Join-Path $claudeSkillDir "hooks") -Recurse -Force

  foreach ($f in @("design-doc-template.md", "interface-example.md", "dependency-example.md", "visualization-guide.md")) {
    Copy-Item (Join-Path $skillDir $f) (Join-Path $claudeSkillDir $f) -Force
  }
  Copy-Item (Join-Path $skillDir "templates") (Join-Path $claudeSkillDir "templates") -Recurse -Force

  # 5b. junction engine (share with opencode)
  New-Junction (Join-Path $claudeSkillDir "engine") $pluginDir

  # 5c. replace __SDD_CLAUDE_DIR__ placeholder in copied files
  $files = @("SKILL.md", "phases-reference.md", "USAGE.md") + (Get-ChildItem (Join-Path $claudeSkillDir "hooks") -Filter "*.mjs" | ForEach-Object { "hooks\" + $_.Name })
  foreach ($f in $files) {
    $p = Join-Path $claudeSkillDir $f
    if (Test-Path -LiteralPath $p) {
      $content = [System.IO.File]::ReadAllText($p, [System.Text.Encoding]::UTF8)
      $content = $content -replace '__SDD_CLAUDE_DIR__', $claudeForward
      [System.IO.File]::WriteAllText($p, $content, (New-Object System.Text.UTF8Encoding($false)))
    }
  }
  Write-Ok "placeholder replaced with $claudeForward"

  # 5d. merge hooks into settings.json
  $settingsPath = Join-Path $env:USERPROFILE ".claude\settings.json"
  $settings = Read-JsonFile $settingsPath @{}
  $hooksTemplatePath = Join-Path $claudeShell "settings.hooks.json"
  $hooksRaw = Get-Content -LiteralPath $hooksTemplatePath -Raw
  $hooksRaw = $hooksRaw -replace '__SDD_CLAUDE_DIR__', $claudeForward
  $hooks = ($hooksRaw | ConvertFrom-Json)
  $settings | Add-Member -NotePropertyName hooks -NotePropertyValue $hooks -Force
  Write-JsonFile $settingsPath $settings
  Write-Ok "settings.json hooks merged"
}

# ---- 6. sub-skills ----------------------------------------------------------

if (-not $SkipSubskills) {
  Write-Step "Install sub-skills (shared via ~/.agents/skills)"

  $skills = @(
    @{ name = "comprehensive-research-agent";  repo = "https://github.com/muratcankoylan/agent-skills-for-context-engineering" },
    @{ name = "brainstorming";                 repo = "https://github.com/obra/superpowers" },
    @{ name = "writing-plans";                 repo = "https://github.com/obra/superpowers" },
    @{ name = "subagent-driven-development";   repo = "https://github.com/obra/superpowers" },
    @{ name = "verification-before-completion"; repo = "https://github.com/obra/superpowers" },
    @{ name = "requesting-code-review";        repo = "https://github.com/obra/superpowers" },
    @{ name = "memory-systems";                repo = "https://github.com/muratcankoylan/agent-skills-for-context-engineering" },
    @{ name = "code-review-quality";           repo = "https://github.com/proffesor-for-testing/agentic-qe" },
    @{ name = "systematic-debugging";          repo = "https://github.com/obra/superpowers" },
    @{ name = "test-driven-development";       repo = "https://github.com/obra/superpowers" }
  )
  foreach ($s in $skills) {
    try {
      Write-Ok "npx skills add $($s.repo) --skill $($s.name)"
      npx --yes skills add $($s.repo) --skill $($s.name) | Out-Null
    } catch {
      Write-Warn "failed to install skill '$($s.name)' (continuing)"
    }
  }

  # junction sub-skills for Claude Code
  if ($Target -in @("claude", "both")) {
    $agentsSkills = Join-Path $env:USERPROFILE ".agents\skills"
    $claudeSkills = Join-Path $env:USERPROFILE ".claude\skills"
    foreach ($s in $skills) {
      $src = Join-Path $agentsSkills $s.name
      if (Test-Path -LiteralPath (Join-Path $src "SKILL.md")) {
        New-Junction (Join-Path $claudeSkills $s.name) $src
      } else {
        Write-Warn "skill not found at top level (nested install?): $($s.name) -> $src"
      }
    }
  }
}

# ---- 7. summary -------------------------------------------------------------

Write-Host ""
Write-Host "================ install complete ================" -ForegroundColor Green
Write-Host "Target:        $Target"
Write-Host "InstallRoot:   $InstallRoot"
Write-Host "Engine:        $pluginEntry"
if ($Target -in @("opencode", "both")) {
  Write-Host "opencode:      $ocSkillLink ; opencode.json updated"
}
if ($Target -in @("claude", "both")) {
  Write-Host "claude:        $claudeSkillDir ; settings.json hooks merged"
}
Write-Host ""
Write-Host "Restart opencode / Claude Code to load."
Write-Host "Verify: node `"$($claudeForward)/engine/bin/sdd.js`" --help"
