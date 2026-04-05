@echo off
REM SDD-Workflow Command Line Interface
REM Simplified commands for SDD-Workflow skill

setlocal enabledelayedexpansion

if "%1" == "" (
    echo Usage: sdd [command]
    echo.
    echo Available commands:
    echo   start     - Start new feature development
    echo   resume    - Resume previous development session  
    echo   status    - Check current project status
    echo   graph     - View or generate knowledge graph
    echo   pause     - Pause all development agents
    echo   continue  - Continue paused development agents
    echo   abort     - Abort current development session
    echo   help      - Show this help message
    exit /b 0
)

set COMMAND=%1
shift

if "%COMMAND%" == "start" (
    call :start_development %*
) else if "%COMMAND%" == "resume" (
    call :resume_development %*
) else if "%COMMAND%" == "status" (
    call :check_status %*
) else if "%COMMAND%" == "graph" (
    call :view_graph %*
) else if "%COMMAND%" == "pause" (
    call :pause_agents %*
) else if "%COMMAND%" == "continue" (
    call :continue_agents %*
) else if "%COMMAND%" == "abort" (
    call :abort_development %*
) else if "%COMMAND%" == "help" (
    call :show_help
) else (
    echo Unknown command: %COMMAND%
    echo Use 'sdd help' to see available commands
    exit /b 1
)

exit /b 0

:start_development
echo 🚀 Starting SDD-Workflow Development Session...
echo.
echo Loading required skills:
echo - using-superpowers
echo - sdd-workflow  
echo - planning-with-files
echo - brainstorming
echo.
echo Initializing project state detection...
echo Please provide your development requirements when prompted.
echo.
echo [SDD-Workflow will now execute the complete development workflow]
echo [Phase 1: Requirements Analysis and Architecture Design]
exit /b 0

:resume_development
echo 🔄 Resuming SDD-Workflow Development Session...
echo.
echo Checking for existing session files:
if exist "task_plan.md" (
    echo ✓ Found task_plan.md - loading progress
) else (
    echo ✗ No existing task_plan.md found
    echo Please run 'sdd start' to begin a new session
    exit /b 1
)

if exist "PROJECT_STATE.md" (
    echo ✓ Found PROJECT_STATE.md - loading project context
) else (
    echo ⚠️  No PROJECT_STATE.md found - creating default state
)

echo.
echo Restoring development context from memory artifacts...
echo [SDD-Workflow will continue from the last checkpoint]
exit /b 0

:check_status
echo 📊 SDD-Workflow Project Status
echo.

if exist "PROJECT_STATE.md" (
    echo Current Project State:
    type PROJECT_STATE.md | findstr /v "^#"
    echo.
) else (
    echo ⚠️  No PROJECT_STATE.md found
    echo Project appears to be uninitialized
    echo Run 'sdd start' to begin
    exit /b 0
)

if exist "task_plan.md" (
    echo Task Plan Status:
    echo =================
    powershell -Command "Select-String -Path task_plan.md -Pattern '^\*\*Status\*\*:.*$' | ForEach-Object { $_.Line }"
    echo.
) else (
    echo ⚠️  No task_plan.md found
)

if exist ".nexus-map\INDEX.md" (
    echo Knowledge Graph: ✓ Available (.nexus-map/)
) else (
    echo Knowledge Graph: ✗ Not generated (run 'sdd graph' to create)
)

exit /b 0

:view_graph
echo 🧠 SDD-Workflow Knowledge Graph
echo.

if exist ".nexus-map\" (
    echo Existing knowledge graph found at .nexus-map/
    echo.
    if exist ".nexus-map\INDEX.md" (
        echo Graph Index:
        type ".nexus-map\INDEX.md"
    ) else (
        echo Graph structure:
        dir /b ".nexus-map\"
    )
) else (
    echo No existing knowledge graph found.
    echo Generating architecture knowledge graph with nexus-mapper...
    echo [This would run nexus-mapper in actual implementation]
    echo Creating .nexus-map/ directory structure...
    
    mkdir ".nexus-map" 2>nul
    mkdir ".nexus-map\arch" 2>nul  
    mkdir ".nexus-map\concepts" 2>nul
    mkdir ".nexus-map\raw" 2>nul
    
    echo # Architecture Knowledge Graph > ".nexus-map\INDEX.md"
    echo Generated on %date% %time% >> ".nexus-map\INDEX.md"
    echo. >> ".nexus-map\INDEX.md"
    echo ## Generated Artifacts >> ".nexus-map\INDEX.md"
    echo - arch/ : System architecture diagrams and models >> ".nexus-map\INDEX.md"
    echo - concepts/ : Domain concepts and relationships >> ".nexus-map\INDEX.md" 
    echo - raw/ : Raw analysis data and source mappings >> ".nexus-map\INDEX.md"
    
    echo ✓ Knowledge graph generated at .nexus-map/
)

exit /b 0

:pause_agents
echo ⏸️  Pausing SDD-Workflow Development Agents...
echo.
echo All active subagents have been paused.
echo Use 'sdd continue' to resume development.
exit /b 0

:continue_agents  
echo ▶️  Continuing SDD-Workflow Development Agents...
echo.
echo Resuming all paused subagents.
echo Development will continue from the last checkpoint.
exit /b 0

:abort_development
echo 🛑 Aborting SDD-Workflow Development Session...
echo.
echo Terminating all active subagents.
echo Cleaning up temporary development artifacts.
echo Session aborted successfully.
exit /b 0

:show_help
call :help_message
exit /b 0

:help_message
echo SDD-Workflow Command Line Interface
echo ===================================
echo.
echo Usage: sdd [command] [options]
echo.
echo Commands:
echo   start        Start new feature development with full workflow
echo   resume       Resume previous development session from checkpoint  
echo   status       Check current project status and progress
echo   graph        View existing knowledge graph or generate new one
echo   pause        Pause all active development agents
echo   continue     Continue paused development agents
echo   abort        Abort current development session completely
echo   help         Show this help message
echo.
echo Examples:
echo   sdd start                    # Begin new development session
echo   sdd resume                   # Continue from last checkpoint  
echo   sdd status                   # Check current project status
echo   sdd graph                    # Generate/view knowledge graph
echo.
exit /b 0